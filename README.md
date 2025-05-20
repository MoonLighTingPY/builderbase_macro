# 💥 Clash of Clans: Builder Base Resources Farming Bot

> Fully automated resource farming using **Night Witches** in Builder Base  
> ⚠️ *Works only with English UI and 8 Night Witches in the army camp. *


## 🚀 Features

- 🖥️ **UI Included** – A simple and intuitive UI to control the bot.
- ✅ **No force-closing** – No need to wait for battles to end
- 💧 **Elixir Support** – Detects and collects elixir from elixir cart
- 🖥️ **Resolution Friendly** – Supports both **Full HD (1920x1080)** and **Quad HD** screens  
- 🤖 **Fully Automated** – Just run the script, open Clash of Clans, and chill  

## ⚙️ Setup (Pre-requirements)

1. Set Clash of Clans language to: **English**
2. Make sure the game is in **Fullscreen mode**
3. Choose a classic scenery **(Forest)**
4. Ensure your army camp has **8 Night Witches**

---

## 🛠️ Installation

### Option 1: Prebuilt Version ✅
1. Download the latest release from [Releases](https://github.com/MoonLighTingPY/builderbase_macro/releases)
2. Extract the archive
3. Run `main.exe`
   
> ## ⚠️ Antivirus Warning
> Your antivirus might flag this application as malicious. This is a **false positive** caused by:
> - The packaging method (PyInstaller)
> - Automation features that control mouse/keyboard
>
> If you're concerned, you can build from source using the instructions below:
### Option 2: Build from Source 🏗️

Clone the repository and install dependencies:
```bash
git clone https://github.com/MoonLighTingPY/builderbase_macro.git
cd builderbase_macro
pip install -r requirements.txt
```

Build the executable (Windows):
```bash
pyinstaller --onefile --noconsole --add-data "2k;2k" --add-data "fullhd;fullhd" main.py
```

Run the compiled `main.exe` from the `dist/` folder.

---

## ▶️ Usage Guide:

1. Start `main.exe`
2. Set how many battles to wait before collecting elixir (default: 2)
3. Press `Start Bot`  in the UI
4. Open Clash of Clans
5. Navigate to the Builder Base
7. Press `P` to pause (wait for a few second before interacting for bot to finish current operations)

---


## ⚠️ Disclaimer

- Automation tools may **violate Supercell's Terms of Service!**
- This script is for **educational purposes only**
- Use at your own risk




