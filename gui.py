import dearpygui.dearpygui as dpg
import multiprocessing
import time
from main import farming_bot_main, use_2k_images, screen_width, screen_height

bot_process = None

def start_bot_callback(sender, app_data, user_data):
    global bot_process
    elixir_freq = dpg.get_value("elixir_freq")
    ability_cd = dpg.get_value("ability_cd")
    trophy_dumping = dpg.get_value("trophy_dumping")
    dpg.set_value("status_text", "🟢 Running")
    dpg.set_value("log", dpg.get_value("log") + "🚀 Bot started...\n")
    if bot_process is None or not bot_process.is_alive():
        bot_process = multiprocessing.Process(
            target=farming_bot_main,
            args=(elixir_freq, ability_cd, trophy_dumping, screen_width, screen_height, use_2k_images)
        )
        bot_process.start()

def stop_bot_callback(sender, app_data, user_data):
    global bot_process
    if bot_process is not None and bot_process.is_alive():
        bot_process.terminate()
        bot_process.join(timeout=2.0)
        bot_process = None
        dpg.set_value("status_text", "🔴 Stopped")
        dpg.set_value("log", dpg.get_value("log") + "⏹️ Bot stopped.\n")

def main():
    dpg.create_context()
    dpg.create_viewport(title='CoC Builder Base Farming Bot', width=700, height=560)

    # Custom theme
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 32, 48), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (40, 44, 60), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (60, 64, 100), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 120, 200), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 140, 220), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (40, 100, 180), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (40, 44, 60), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (60, 64, 100), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (80, 84, 120), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 230, 230), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 8, category=dpg.mvThemeCat_Core)

    with dpg.font_registry():
        default_font = dpg.add_font("C:/Windows/Fonts/segoeui.ttf", 18)
        header_font = dpg.add_font("C:/Windows/Fonts/segoeui.ttf", 28)

    with dpg.window(label="", width=680, height=540, pos=(10, 10)):
        dpg.add_spacer(height=10)
        dpg.add_text("💥 Clash of Clans: Builder Base Bot", color=(255, 215, 0), wrap=600)
        dpg.bind_item_font(dpg.last_item(), header_font)
        dpg.add_spacer(height=8)
        dpg.add_text("Fully automated farming for Builder Base. Modern UI. No more 90's look!", color=(180, 180, 180))
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_input_int(label="Elixir Check (battles)", default_value=2, min_value=1, tag="elixir_freq", width=120)
            dpg.add_input_float(label="Hero Ability CD (s)", default_value=2.5, min_value=0, tag="ability_cd", width=120)
            dpg.add_checkbox(label="Trophy Dumping", tag="trophy_dumping")
        dpg.add_spacer(height=4)
        dpg.add_text(f"🖥️ Resolution: {screen_width}x{screen_height}   |   Assets: {'2K' if use_2k_images else 'FullHD'}", color=(120, 180, 255))
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="▶️ Start Bot", callback=start_bot_callback, width=120)
            dpg.add_button(label="⏹️ Stop Bot", callback=stop_bot_callback, width=120)
            dpg.add_spacer(width=20)
            dpg.add_text("Status:", color=(180, 180, 180))
            dpg.add_text("🔴 Stopped", tag="status_text", color=(255, 80, 80))
        dpg.add_separator()
        dpg.add_text("Bot Log:", color=(180, 180, 180))
        with dpg.child_window(width=640, height=200, border=True):
            dpg.add_input_text(multiline=True, readonly=True, height=190, width=620, tag="log", default_value="Bot initialized and ready to start...\n")
        dpg.add_separator()
        dpg.add_text("ℹ️  Start the bot, then switch to Clash of Clans within 3 seconds.", color=(180, 180, 180))
        dpg.add_spacer(height=6)
        dpg.add_text("Press 'P' to pause/stop the bot at any time.", color=(180, 180, 180))

    dpg.bind_theme(global_theme)
    dpg.bind_font(default_font)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()