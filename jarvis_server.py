
from flask import Flask, jsonify, send_file, request
import psutil
import time
import os
import datetime
import jarvis_brain
import jarvis_memory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
start_time = time.time()
assistant_state = "idle"
command_count = 0

# Restore previous conversations from SQLite.
saved_messages = jarvis_memory.get_recent_messages(limit=100)

chat_history = [
    {
        "i": index + 1,
        "k": "you" if message["role"] == "user" else "jarvis",
        "x": message["content"],
        "t": ""
    }
    for index, message in enumerate(saved_messages)
]


@app.route("/")
def workplace():
    return send_file(os.path.join(BASE_DIR, "jarvis_workplace.html"))


@app.route("/api/state")
def get_state():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(BASE_DIR)
    battery = psutil.sensors_battery()

    system_info = {
        "cpu": psutil.cpu_percent(),
        "ram": memory.percent,
        "disk": disk.percent,
        "free": round(disk.free / (1024 ** 3), 2),
        "up": int(time.time() - start_time),
    }

    if battery:
        system_info["bat"] = battery.percent
        system_info["plug"] = battery.power_plugged

    return jsonify({
        "state": assistant_state,
        "note": "Jarvis backend connected",
        "mode": "HYBRID",
        "model": "Groq / Local",
        "t_rec": 0,
        "t_think": 0,
        "last_tool": "Text Chat",
        "tools": str(command_count),
        "facts": str(len(jarvis_memory.get_facts())),
        "mail_age": None,
        "last_you": next(
            (item["x"] for item in reversed(chat_history)
             if item["k"] == "you"),
            ""
        ),
        "tool_active": False,
        "chat": chat_history,
        "cards": [{
            "i": "welcome",
            "title": "SYSTEM STATUS",
            "t": "NOW",
            "body": "Jarvis backend connected. Memory restored."
        }],
        "stocks": [],
        "sys": system_info,
        "mic": {"n": 0, "a": []}
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    global assistant_state, command_count

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    if len(message) > 2000:
        return jsonify({"error": "Message is too long"}), 400

    assistant_state = "thinking"
    command_count += 1

    try:
        reply = jarvis_brain.think(message)

        if not reply:
            reply = "I couldn't generate a response. Please try again."

        chat_history.append({
            "i": len(chat_history) + 1,
            "k": "you",
            "x": message,
            "t": datetime.datetime.now().strftime("%H:%M")
        })

        chat_history.append({
            "i": len(chat_history) + 1,
            "k": "jarvis",
            "x": str(reply),
            "t": datetime.datetime.now().strftime("%H:%M")
        })

        return jsonify({"reply": str(reply)})

    except Exception:
        app.logger.exception("Chat processing failed")
        return jsonify({
            "error": "Jarvis encountered an internal error."
        }), 500

    finally:
        assistant_state = "idle"


if __name__ == "__main__":
    print("\nJARVIS SERVER STARTING...")
    print("Dashboard: http://127.0.0.1:5000")
    print("Persistent memory: ENABLED")
    app.run(host="127.0.0.1", port=5000, debug=False)
