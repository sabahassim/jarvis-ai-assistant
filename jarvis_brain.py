
"""
jarvis_brain.py - Hybrid Cloud + Offline AI Brain
with Persistent SQLite Memory.
"""

import os
import time
import re
from openai import OpenAI
import jarvis_actions
import jarvis_memory

KEYFILE = r"D:\New Volume\saba\AI-Assistants\Jarvis-Secrets\groq.key"

MODELS = [
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "qwen/qwen3.8-27b"
]

_client = None
_cooldown_until = 0.0

SYSTEM_PROMPT = """You are Jarvis, a fast, highly capable AI executive assistant running on the user's computer.

Respond concisely in 1-2 sentences. Be direct, helpful, and natural.
Use saved facts and conversation history when relevant.
Do not claim to remember information that is not available in your memory.
"""


def _get_api_key():
    if os.environ.get("GROQ_API_KEY"):
        return os.environ["GROQ_API_KEY"].strip()

    if os.path.exists(KEYFILE):
        with open(KEYFILE, "r") as file:
            return file.read().strip()

    return None


def ready():
    key = _get_api_key()
    return bool(key) and time.time() >= _cooldown_until


def _is_rate_limited(error):
    status = getattr(error, "status_code", None)

    if status == 429:
        return True

    message = str(error).lower()

    return any(word in message for word in (
        "429",
        "rate limit",
        "too many requests",
        "rate_limit",
        "exceeded"
    ))


def _retry_after_seconds(error, default=60):
    message = str(error).lower()

    match = re.search(
        r"try again in\s*(\d+)m\s*([0-9]+(?:\.[0-9]+)?)s",
        message
    )

    if match:
        return int(float(match.group(1)) * 60 +
                   float(match.group(2))) + 2

    match = re.search(
        r"try again in\s*([0-9]+(?:\.[0-9]+)?)s",
        message
    )

    if match:
        return int(float(match.group(1))) + 2

    return default


def _set_cooldown(seconds):
    global _cooldown_until

    _cooldown_until = max(
        _cooldown_until,
        time.time() + float(seconds)
    )


def _save_exchange(message, reply):
    jarvis_memory.save_message("user", message)
    jarvis_memory.save_message("assistant", str(reply))


def _local_fallback(question):
    action_result = jarvis_actions.try_action(question)

    if action_result:
        return str(action_result)

    return (
        "Cloud AI is temporarily unavailable, "
        "but my local assistant is active."
    )


def think(question):
    global _client

    question = str(question).strip()

    if not question:
        return "Please enter a message."

    # Save the user's message before processing.
    jarvis_memory.save_message("user", question)

    # Check local actions first.
    local_result = jarvis_actions.try_action(question)

    if local_result:
        reply = str(local_result)
        jarvis_memory.save_message("assistant", reply)
        return reply

    # Load saved facts.
    facts = jarvis_memory.get_facts()

    facts_context = ""

    if facts:
        facts_context = "\n\nSaved user facts:\n"
        facts_context += "\n".join(
            f"- {key}: {value}"
            for key, value in facts.items()
        )

    # Load recent conversation history.
    history = jarvis_memory.get_recent_messages(limit=20)

    # Exclude the current question because it is added separately.
    if history and history[-1]["role"] == "user":
        history = history[:-1]

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + facts_context
        }
    ]

    messages.extend(history)
    messages.append({
        "role": "user",
        "content": question
    })

    key = _get_api_key()

    if not key or time.time() < _cooldown_until:
        reply = _local_fallback(question)
        jarvis_memory.save_message("assistant", reply)
        return reply

    if _client is None:
        _client = OpenAI(
            api_key=key,
            base_url="https://api.groq.com/openai/v1"
        )

    for model in MODELS:
        try:
            response = _client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=350,
                temperature=0.6
            )

            reply = response.choices[0].message.content.strip()

            if not reply:
                reply = "I couldn't generate a response. Please try again."

            jarvis_memory.save_message("assistant", reply)

            return reply

        except Exception as error:
            if _is_rate_limited(error):
                wait_seconds = _retry_after_seconds(error)
                _set_cooldown(wait_seconds)

                print(
                    f"[Rate limit: cooldown for {wait_seconds}s]"
                )

                reply = _local_fallback(question)
                jarvis_memory.save_message("assistant", reply)
                return reply

            print(f"[Model {model} failed: {error}]")

    reply = _local_fallback(question)
    jarvis_memory.save_message("assistant", reply)

    return reply


if __name__ == "__main__":
    print("Testing Jarvis Brain...")
    print(think("What time is it?"))
    print(think("How are you?"))
