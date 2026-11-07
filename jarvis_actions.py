
"""
jarvis_actions.py - Windows-native local automation for Jarvis.

Features:
- Windows application launching
- Website launching
- WhatsApp Web
- Google search
- YouTube search and playback
- Windows volume controls with state-aware mute/unmute
- Date and time
- Local mail briefing

Stock-market functionality is intentionally excluded.
"""

import os
import re
import json
import subprocess
import urllib.parse
import webbrowser
import datetime
from pathlib import Path


# --------------------------------------------------
# WEBSITE SHORTCUTS
# --------------------------------------------------

SITES = {
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "maps": "https://maps.google.com",
    "calendar": "https://calendar.google.com",
    "drive": "https://drive.google.com",
}


# --------------------------------------------------
# WINDOWS APPLICATION ALIASES
# --------------------------------------------------

ALIASES = {
    "vs code": "code",
    "code": "code",
    "chrome": "chrome",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "terminal": "wt",
    "command prompt": "cmd",
    "file explorer": "explorer",
}


# --------------------------------------------------
# GENERAL OPEN FUNCTION
# --------------------------------------------------

def _open(target):
    """Open a website, file or Windows application."""

    try:
        if target.startswith(("https://", "http://")):
            return bool(webbrowser.open(target))

        os.startfile(target)
        return True

    except (OSError, AttributeError):
        try:
            subprocess.Popen(target, shell=True)
            return True
        except OSError:
            return False


# --------------------------------------------------
# APPLICATION LOOKUP
# --------------------------------------------------

def find_app(name):
    """Resolve common Windows application aliases."""

    clean_name = name.lower().strip()
    return ALIASES.get(clean_name, clean_name)


# --------------------------------------------------
# WHATSAPP
# --------------------------------------------------

def send_whatsapp_message(
    contact_name,
    message="Hello from Jarvis"
):
    """
    Open WhatsApp Web with a prefilled message.

    The message is NOT sent automatically.
    The user must review and send it.
    """

    encoded_msg = urllib.parse.quote(message)

    url = (
        f"https://web.whatsapp.com/send?"
        f"text={encoded_msg}"
    )

    if _open(url):
        return (
            f"WhatsApp opened with your message "
            f"prepared for {contact_name}. "
            f"Please review and send it yourself."
        )

    return "I couldn't open WhatsApp Web."


# --------------------------------------------------
# MAIL BRIEFING
# --------------------------------------------------

def get_mail_brief():
    """
    Read a locally saved mail cache.

    Does not invent emails or unread counts.
    """

    cache_file = (
        Path.home()
        / ".openjarvis"
        / "mail_cache.txt"
    )

    if cache_file.exists():
        try:
            content = cache_file.read_text(
                encoding="utf-8"
            ).strip()

            if content:
                return (
                    "Here is your locally saved "
                    "mail briefing:\n"
                    + content[:600]
                )

        except OSError:
            pass

    return (
        "I don't have access to your Gmail inbox yet. "
        "No real email briefing is available."
    )


# --------------------------------------------------
# WINDOWS VOLUME CONTROL
# --------------------------------------------------

def _change_volume(action):
    """
    Increase or decrease Windows master volume
    using Windows media-key events.
    """

    scripts = {

        "up": """
            Add-Type -TypeDefinition @'
            using System;
            using System.Runtime.InteropServices;

            public class Audio {
                [DllImport("user32.dll")]
                public static extern void keybd_event(
                    byte bVk,
                    byte bScan,
                    int dwFlags,
                    int dwExtraInfo
                );
            }
'@

            [Audio]::keybd_event(0xAF, 0, 0, 0)
            [Audio]::keybd_event(0xAF, 0, 2, 0)
        """,

        "down": """
            Add-Type -TypeDefinition @'
            using System;
            using System.Runtime.InteropServices;

            public class Audio {
                [DllImport("user32.dll")]
                public static extern void keybd_event(
                    byte bVk,
                    byte bScan,
                    int dwFlags,
                    int dwExtraInfo
                );
            }
'@

            [Audio]::keybd_event(0xAE, 0, 0, 0)
            [Audio]::keybd_event(0xAE, 0, 2, 0)
        """
    }

    if action not in scripts:
        return False

    try:
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                scripts[action]
            ],
            check=True,
            capture_output=True,
            text=True
        )

        return True

    except (subprocess.CalledProcessError, OSError):
        return False


# --------------------------------------------------
# STATE-AWARE MUTE / UNMUTE
# --------------------------------------------------

def _set_mute(mute: bool):
    """
    Read the actual Windows mute state and change it
    only when necessary.

    Initialize COM on the current thread because Flask
    may execute this function in a request thread.

    mute=True  -> mute
    mute=False -> unmute
    """

    import comtypes

    com_initialized = False

    try:
        comtypes.CoInitialize()
        com_initialized = True

        from pycaw.pycaw import AudioUtilities

        volume = (
            AudioUtilities
            .GetSpeakers()
            .EndpointVolume
        )

        currently_muted = bool(volume.GetMute())

        # Already in the requested state
        if currently_muted == mute:
            return (
                "Your system is already muted."
                if mute
                else "Your system is already unmuted."
            )

        # Set the exact requested state
        volume.SetMute(1 if mute else 0, None)

        # Verify the change
        new_state = bool(volume.GetMute())

        if new_state == mute:
            return (
                "System muted successfully."
                if mute
                else "System unmuted successfully."
            )

        return "I couldn't verify the audio state change."

    except Exception as e:
        print(f"Audio mute control error: {e}")
        return "I couldn't access Windows audio controls."

    finally:
        if com_initialized:
            comtypes.CoUninitialize()


# --------------------------------------------------
# YOUTUBE SEARCH
# --------------------------------------------------

def search_youtube(query):
    """
    Search YouTube and display search results.
    Does not automatically play a video.
    """

    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )

    if _open(url):
        return f"Searching YouTube for {query}."

    return "Couldn't open YouTube."


# --------------------------------------------------
# YOUTUBE PLAYBACK
# --------------------------------------------------

def play_youtube(query):
    """
    Find the first YouTube search result using yt-dlp
    and open its watch page in the browser.

    Does not download the video.
    """

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--playlist-end",
                "1",
                "--dump-single-json",
                f"ytsearch1:{query}"
            ],
            capture_output=True,
            text=True,
            timeout=45,
            check=True
        )

        data = json.loads(result.stdout)

        entries = data.get("entries") or []
        video = entries[0] if entries else data

        video_id = video.get("id")

        if not video_id:
            return f"I couldn't find a video for {query}."

        video_url = (
            f"https://www.youtube.com/watch?v={video_id}"
        )

        if _open(video_url):
            return (
                f"Opening the first YouTube result "
                f"for {query}."
            )

        return "I found the video but couldn't open it."

    except subprocess.TimeoutExpired:
        return (
            "YouTube search took too long. "
            "Please try again."
        )

    except subprocess.CalledProcessError:
        return (
            "I couldn't retrieve YouTube results. "
            "Please check your internet connection "
            "or update yt-dlp."
        )

    except (json.JSONDecodeError, OSError, IndexError):
        return (
            f"I couldn't find a playable YouTube result "
            f"for {query}."
        )


# --------------------------------------------------
# MAIN ACTION HANDLER
# --------------------------------------------------

def try_action(q):
    """
    Executes deterministic local actions.

    Returns a response string if the command is handled.
    Returns None if the AI brain should handle it.
    """

    q_clean = q.lower().strip(" .,!?")

    # ----------------------------------------------
    # 1. WHATSAPP
    # ----------------------------------------------

    message_match = re.search(
        r"(?:send|reply|message)\s+"
        r"(?:on\s+whatsapp\s+to|whatsapp\s+to|to)\s+"
        r"(.+?)(?:\s+saying\s+(.+))?$",
        q_clean
    )

    if "whatsapp" in q_clean and message_match:
        contact = message_match.group(1).strip()

        message = (
            message_match.group(2).strip()
            if message_match.group(2)
            else "I received your message, will get back shortly."
        )

        return send_whatsapp_message(
            contact,
            message
        )

    if q_clean in (
        "open whatsapp",
        "check whatsapp",
        "whatsapp"
    ):
        return (
            "Opening WhatsApp."
            if _open(SITES["whatsapp"])
            else "Couldn't open WhatsApp."
        )

    # ----------------------------------------------
    # 2. MAIL BRIEFING
    # ----------------------------------------------

    if any(k in q_clean for k in (
        "mail brief",
        "check mail",
        "read emails",
        "inbox summary",
        "unread emails"
    )):
        return get_mail_brief()

    # ----------------------------------------------
    # 3. YOUTUBE SEARCH
    # ----------------------------------------------

    match = re.search(
        r"(?:search|find)\s+(.+?)\s+"
        r"(?:on|in)\s+youtube",
        q_clean
    )

    if match:
        return search_youtube(match.group(1).strip())

    # ----------------------------------------------
    # 4. YOUTUBE PLAYBACK
    # ----------------------------------------------

    match = re.search(
        r"play\s+(.+?)\s+"
        r"(?:on|in)\s+youtube",
        q_clean
    )

    if match:
        return play_youtube(match.group(1).strip())

    # ----------------------------------------------
    # 5. GOOGLE SEARCH
    # ----------------------------------------------

    match = re.match(
        r"(?:search|google)(?: for)?\s+(.+)",
        q_clean
    )

    if match:
        query = match.group(1).strip()

        url = (
            "https://www.google.com/search?q="
            + urllib.parse.quote(query)
        )

        return (
            f"Searching Google for {query}."
            if _open(url)
            else "Couldn't open Google."
        )

    # ----------------------------------------------
    # 6. APPLICATION AND WEBSITE LAUNCH
    # ----------------------------------------------

    match = re.match(
        r"(?:please\s+)?(?:open|launch|start)\s+(.+)",
        q_clean
    )

    if match:
        name = match.group(1).strip()

        if name in SITES:
            return (
                f"Opening {name}."
                if _open(SITES[name])
                else f"Couldn't open {name}."
            )

        app = find_app(name)

        try:
            subprocess.Popen(
                ["cmd", "/c", "start", "", app],
                shell=False
            )

            return f"Attempting to open {name}."

        except OSError:
            return (
                f"I couldn't launch {name}. "
                f"Check whether it is installed."
            )

    # ----------------------------------------------
    # 7. WINDOWS VOLUME CONTROLS
    # ----------------------------------------------

    if any(phrase in q_clean for phrase in (
        "volume up",
        "increase volume",
        "turn up the volume",
        "raise volume",
        "make it louder",
        "louder"
    )):
        return (
            "Volume increased."
            if _change_volume("up")
            else "Couldn't change volume."
        )

    if any(phrase in q_clean for phrase in (
        "volume down",
        "decrease volume",
        "reduce volume",
        "turn down the volume",
        "lower volume",
        "make it quieter",
        "quieter"
    )):
        return (
            "Volume decreased."
            if _change_volume("down")
            else "Couldn't change volume."
        )

    # Mute commands
    if q_clean in (
        "mute",
        "mute volume",
        "mute the volume",
        "mute sound",
        "mute the sound"
    ):
        return _set_mute(True)

    # Unmute commands
    if q_clean in (
        "unmute",
        "unmute volume",
        "unmute the volume",
        "unmute sound",
        "unmute the sound",
        "turn sound on",
        "turn the sound on"
    ):
        return _set_mute(False)

    # ----------------------------------------------
    # 8. DATE AND TIME
    # ----------------------------------------------

    if "time" in q_clean:
        return (
            "It is currently "
            + datetime.datetime.now().strftime("%I:%M %p")
        )

    if "date" in q_clean or "today" in q_clean:
        return (
            "Today is "
            + datetime.datetime.now().strftime(
                "%A, %B %d, %Y"
            )
        )

    # ----------------------------------------------
    # NO LOCAL ACTION MATCHED
    # ----------------------------------------------

    return None
