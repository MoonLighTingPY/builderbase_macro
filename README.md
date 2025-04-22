# 💥 Clash of Clans: Builder Base Resources Farming Script

> Fully automated resource farming using **Night Witches** in Builder Base  
> ⚠️ *Works only with English UI and Night Witches in the army camp (the most effective and used troop for farming anyway)*

---

## 🚀 Features

- ✅ **No force-closing** – No need to wait for battles to end
- 💧 **Elixir Support** – Detects and collects elixir from elixir cart 
- 🖥️ **Resolution Friendly** – Supports both **Full HD (1920x1080)** and **Quad HD** screens  
- 🤖 **Fully Automated** – Just run the script, open Clash of Clans, and chill  

---

## 🛠 Installation

```bash
git clone https://github.com/MoonLighTingPY/builderbase_macro.git
cd builderbase_macro
pip install -r requirements.txt
```

---

## ⚙️ Setup (Pre-requirements)

1. Set Clash of Clans language to: **English**
2. Ensure your army camp has **8 Night Witches**

> 🔥 **DO NOT SKIP THEESE STEPS!**  
> The script uses English UI elements and relies on Night Witches for detection.

---

## ▶️ Usage

1. Open Clash of Clans in **fullscreen** and go to the **Builder Base**
2. `Alt + Tab` to your terminal
3. Run the script:
   ```bash
   python main.py
   ```
4. `Alt + Tab` back to Clash of Clans  
5. Sit back and let it farm 😎

---

## 🧠 How It Works

1. Collect elixir every N iteration
2. Finds the match
3. Automatically deploys troops in both villages
4. Returns home when battle ends 
6. Repeats the cycle endlessly

---

## 📁 Project Structure

```
📦 builderbase_macro/
├── main.py                  # Main automation script
├── requirements.txt         # Dependencies for the script
├── 2k/                      # Assets for high-resolution displays
└── fullhd/                  # Assets for standard Full HD displays
    ├── buttons/             # UI button images
    ├── elixir_cart/         # Elixir collection images
    └── warplace/            # Battle deployment location images
```

---

## ⚠️ Disclaimer

- Automation tools may **violate Supercell's Terms of Service!**
- This script is for **educational purposes only**
- Use at your own risk
