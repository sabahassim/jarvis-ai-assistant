# ⚡ JARVIS AI Personal Assistant

**A Python-powered personal AI assistant combining cloud intelligence, voice interaction, persistent memory, and desktop automation.**

JARVIS is a personal AI assistant designed to make everyday computer interactions easier. It combines Groq-powered conversational AI with local automation, voice commands, SQLite-based memory, and a browser-based dashboard.

The project explores how AI models, Python automation, and persistent memory can work together to create a modular personal assistant.

---

## 🚀 Features

### 🧠 AI-Powered Conversations
- Uses the Groq API through the OpenAI-compatible Python client.
- Supports multiple language models through a fallback sequence.
- Uses recent conversation history and saved facts as context.
- Handles API rate limits with an automatic cooldown mechanism.

### 💾 Persistent Memory
- SQLite database for storing conversations and facts.
- Retrieves recent conversation history.
- Saves and updates remembered information.
- Maintains memory locally using `jarvis_memory.db`.

### 🎙️ Voice Interaction
- Microphone input using SpeechRecognition.
- Speech-to-text using Google's speech recognition service.
- Text-to-speech using `pyttsx3` when available.
- Optional JARVIS wake-word handling.
- Console-input fallback when microphone access is unavailable.

### 🖥️ Desktop Automation
On supported Windows systems, JARVIS can:
- Launch applications such as VS Code, Chrome, Notepad, Calculator, Word, Excel, and PowerPoint.
- Open commonly used websites.
- Search Google and YouTube.
- Find and open YouTube videos.
- Prepare WhatsApp messages with prefilled text for manual review and sending.
- Control system volume and mute settings when the required dependencies are installed.
- Provide date and time information.

### 🌐 Browser-Based Dashboard
- Flask-powered local backend.
- Browser-based chat interface.
- Live system information, including CPU, RAM, disk, and battery status where supported.
- Displays conversation and memory information.
- Runs locally at `127.0.0.1:5000`.

### 📈 Experimental Market Analysis
The separate `jarvis_market.py` module provides experimental market-data analysis using Yahoo Finance chart data.

It includes:
- A predefined watchlist of Indian and international market tickers.
- Price-change calculations.
- Short-term and long-term moving averages.
- Basic heuristic BUY / SELL / HOLD signals.

**Note:** This is a standalone experimental module and is not currently integrated into the main voice assistant or dashboard. Its output is informational only, not financial advice.

---

## 🏗️ Project Architecture

```text
                       USER
                         |
              +----------+----------+
              |                     |
          Voice Input           Web Dashboard
              |                     |
        jarvis_voice.py        jarvis_server.py
              |                     |
              +----------+----------+
                         |
                    JARVIS Brain
                   jarvis_brain.py
                         |
              +----------+----------+
              |                     |
           Groq API             Local Actions
        Cloud AI Models        jarvis_actions.py
              |                     |
              +----------+----------+
                         |
                   SQLite Memory
                   jarvis_memory.py
                         |
                  jarvis_memory.db


             Separate Experimental Module
                    jarvis_market.py
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Groq API | Cloud-based AI responses |
| OpenAI Python SDK | API communication |
| Flask | Local web backend |
| SQLite | Persistent memory |
| SpeechRecognition | Voice input |
| Google Speech Recognition | Speech-to-text |
| pyttsx3 | Text-to-speech |
| psutil | System monitoring |
| Requests | HTTP communication |
| Yahoo Finance data | Experimental market analysis |

---

## 📂 Project Structure

```text
jarvis-ai-assistant/
│
├── jarvis_brain.py          # AI engine and model fallback
├── jarvis_actions.py        # Desktop automation and local actions
├── jarvis_voice.py          # Voice interaction
├── jarvis_memory.py         # SQLite memory management
├── jarvis_server.py         # Flask backend
├── jarvis_market.py         # Experimental market analysis
│
├── jarvis_workplace.html    # Browser-based dashboard
│
├── requirements.txt         # Python dependencies
├── install.bat              # Windows setup script
├── install.sh               # macOS/Linux setup script
│
├── README.md
├── INDEX.md
├── LICENSE
└── .gitignore
```

Runtime files such as `.venv/` and `jarvis_memory.db` are generated locally and should not be committed to the public repository.

---

## ⚙️ Installation and Setup

### Requirements

- Python 3.10 or newer.
- Internet connection for cloud AI responses and online speech recognition.
- A Groq API key for cloud-powered conversations.
- Windows is the primary supported platform for desktop automation.

### 1. Clone the Repository

```bash
git clone https://github.com/sabahassim/jarvis-ai-assistant.git
cd jarvis-ai-assistant
```

### 2. Windows Setup

Run the Windows installer:

```bat
install.bat
```

The installer:
- Checks whether Python is installed.
- Creates a virtual environment named `.venv`.
- Installs dependencies from `requirements.txt`.
- Attempts to install additional audio packages.

### 3. Configure Your Groq API Key

Get your free API key from:

https://console.groq.com/keys

In PowerShell, configure the key for the current terminal session:

```powershell
$env:GROQ_API_KEY="YOUR_GROQ_API_KEY"
```

Replace `YOUR_GROQ_API_KEY` with your actual key.

For future sessions, configure the environment variable through Windows Environment Variables.

**Security reminder:** Never publish your API key, private credentials, or secret files on GitHub.

### 4. Start the Voice Assistant

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

Run JARVIS:

```powershell
python jarvis_voice.py
```

### 5. Start the Web Dashboard

With the virtual environment activated, run:

```powershell
python jarvis_server.py
```

Open your browser and visit:

http://127.0.0.1:5000

---

## 💬 Example Voice Commands

| Command | Expected Action |
|---|---|
| "Jarvis, open VS Code" | Launches Visual Studio Code |
| "Open YouTube" | Opens YouTube |
| "Play lofi on YouTube" | Searches YouTube and opens a matching video |
| "Search Google for Python tutorials" | Opens a Google search |
| "Send WhatsApp message to Pallavi" | Prepares a WhatsApp message for review |
| "Volume up" | Increases system volume |
| "Mute" | Mutes system audio where supported |
| "What time is it?" | Provides the current time |

The exact result depends on the supported command patterns and the applications available on the system.

---

## 🔄 Hybrid AI and Local Fallback

JARVIS combines cloud-based AI responses with local automation.

When the Groq API is available:
1. JARVIS processes the request.
2. The configured language model generates a response.
3. Recent conversation history and saved facts provide context.

When the cloud service encounters a rate limit or becomes unavailable:
1. JARVIS detects the API error.
2. It applies a cooldown period when rate-limited.
3. Supported local actions can still be processed.

This allows certain automation commands to remain available even when cloud AI responses cannot be generated.

**Important:** Local fallback is based on programmed automation and deterministic actions. It is not a fully offline conversational language model.

---

## 🖥️ JARVIS Workplace Dashboard

The project includes a browser-based dashboard in:

`jarvis_workplace.html`

To use it, start the Flask backend and visit:

http://127.0.0.1:5000

The dashboard provides a chat interface and system monitoring information.

---

## ⚠️ Current Limitations

JARVIS is an evolving personal project. Some capabilities have dependencies or are still under development.

- Cloud-powered AI responses require a valid Groq API key and internet access.
- Speech recognition uses Google's online recognition service.
- Voice and dashboard interactions currently follow separate execution paths.
- WhatsApp automation prepares messages but does not send them automatically.
- The mail briefing reads from a local cache file rather than connecting directly to Gmail.
- The market-analysis module is separate from the main assistant.
- Some optional automation and audio features require additional packages and system configuration.
- macOS/Linux installation and API-key configuration may require additional setup.

---

## 🔮 Future Improvements

Potential development directions include:

- More capable local AI model integration.
- Improved voice interaction and wake-word detection.
- Expanded desktop and browser automation.
- Advanced memory retrieval and context management.
- Productivity application integrations.
- Improved dashboard functionality.
- More reliable cross-platform installation.
- Better automation error handling and dependency management.

These are planned development directions, not claims of currently implemented functionality.

---

## 🔐 Security and Privacy

- Keep API keys and credentials outside the public repository.
- Do not upload private memory databases or personal conversation data.
- Review automation actions before interacting with external services.
- The Flask backend currently binds to `127.0.0.1`.
- Treat experimental market-analysis signals as informational only.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Saba Hassim**

GitHub: [@sabahassim](https://github.com/sabahassim)

---

<p align="center">
  ⚡ <strong>JARVIS AI Assistant</strong><br>
  <em>Building a smarter way to interact with your computer.</em>
</p>

