# Clash of Clans Builder Base Resources Farming Script

An automated script on python for Clash of Clans to farm gold and elixir in Builder Base. Fully automated.

```Works only with Night Witches(The most effective and used troop for farming anyway)```

## Features

- **No force-closing** - No need to wait till "troops finish the battle"
- **Even farms Elixir!** - Detects and collects elixir from elixir carts
- **Resolution Support** - Works with both standard (1920x1080) and QuadHD displays
- **Fully Automated** - Start the script, open Clash of Clans, and enjoy!



## Installation

1. Clone this repository
   ```bash
   git clone https://github.com/MoonLighTingPY/builderbase_macro.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure Clash of Clans is open in fullscreen you are in the builder base.
2. Alt + tab to the terminal
3. Run the script:
   ```bash
   python main.py
   ```
4. Alt + tab to Clash of clans

## How It Works

The script uses computer vision to:
1. Detect elixir cart status and collect when available (every 10 iterations)
2. Find and click the attack button
3. Wait for battle to be ready (handles cooldowns)
4. Deploy troops automatically in both villages
5. Return home after battle is complete
6. Repeat the process

## Structure

- **main.py** - Main automation script
- **2k/** - Image assets for high-resolution displays
- **fullhd/** - Image assets for standard displays
  - **/buttons** - UI button images
  - **/elixir_cart** - Elixir collector images
  - **/warplace** - Battle deployment location images

## Disclaimer

- This tool is for educational purposes only.
- Using automation scripts may violate Supercell's Terms of Service.
- Use at your own risk
