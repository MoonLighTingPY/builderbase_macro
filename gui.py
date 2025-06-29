import dearpygui.dearpygui as dpg
import multiprocessing
import time
import threading
import keyboard  # Global hotkey support
from main import farming_bot_main, use_2k_images, screen_width, screen_height

bot_process = None

def start_bot(elixir_freq, ability_cd, trophy_dumping):
    global bot_process
    if bot_process is None or not bot_process.is_alive():
        ctx = multiprocessing.get_context("spawn")
        bot_process = ctx.Process(
            target=farming_bot_main,
            args=(elixir_freq, ability_cd, trophy_dumping, screen_width, screen_height, use_2k_images)
        )
        bot_process.start()


def start_bot_callback(sender, app_data, user_data):
    elixir_freq = dpg.get_value("elixir_freq")
    ability_cd = dpg.get_value("ability_cd")
    trophy_dumping = dpg.get_value("trophy_dumping")
    dpg.set_value("status_text", "Running")
    dpg.set_value("log", dpg.get_value("log") + "Bot started...\n")
    start_bot(elixir_freq, ability_cd, trophy_dumping)


def stop_bot_callback(sender, app_data, user_data):
    global bot_process
    if bot_process is not None and bot_process.is_alive():
        print("Stopping bot process instantly...")
        bot_process.terminate()
        bot_process.join(timeout=2.0)
        if bot_process.is_alive():
            print("Warning: Bot process is still running after terminate()")
        bot_process = None
    dpg.set_value("status_text", "Stopped")
    dpg.set_value("log", dpg.get_value("log") + "Bot stopped.\n")

def global_hotkey_listener():
    while True:
        keyboard.wait('o')
        print("Global hotkey: O pressed (start bot)")
        dpg.set_value("log", dpg.get_value("log") + "Global hotkey: O pressed (start bot)\n")
        start_bot(
            dpg.get_value("elixir_freq"),
            dpg.get_value("ability_cd"),
            dpg.get_value("trophy_dumping")
        )
        # Debounce: wait for key release
        while keyboard.is_pressed('o'):
            time.sleep(0.1)

        keyboard.wait('p')
        print("Global hotkey: P pressed (stop bot)")
        dpg.set_value("log", dpg.get_value("log") + "Global hotkey: P pressed (stop bot)\n")
        stop_bot_callback(None, None, None)
        while keyboard.is_pressed('p'):
            time.sleep(0.1)

def main():
    dpg.create_context()
    viewport_width, viewport_height = 900, 700  # You can set your preferred default size
    dpg.create_viewport(title='CoC Builder Base Farming Bot', width=viewport_width, height=viewport_height, resizable=True)

    # Modern, neutral theme
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (24, 26, 34), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (32, 34, 44), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (44, 48, 60), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Button, (52, 120, 200), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (72, 140, 220), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (32, 100, 180), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (34, 36, 46), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (54, 58, 80), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (74, 78, 100), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 220), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, (60, 60, 80), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 2, category=dpg.mvThemeCat_Core)

    with dpg.font_registry():
        default_font = dpg.add_font("C:/Windows/Fonts/segoeui.ttf", 16)
        header_font = dpg.add_font("C:/Windows/Fonts/segoeui.ttf", 24, default_font=True)

    with dpg.window(label="Builder Base Farming Bot", pos=(0, 0), width=viewport_width, height=viewport_height, no_collapse=True, no_resize=True, no_move=True, tag="main_window"):
        dpg.add_spacer(height=18)
        dpg.add_text("Clash of Clans Builder Base Bot")
        dpg.bind_item_font(dpg.last_item(), header_font)
        dpg.add_spacer(height=10)
        dpg.add_text("Automated farming for Builder Base. Minimal, modern UI.", color=(180, 180, 190))
        dpg.add_spacer(height=8)
        dpg.add_separator()
        dpg.add_spacer(height=8)
        with dpg.group(horizontal=True):
            dpg.add_input_int(label="Elixir Check Interval", default_value=2, min_value=1, tag="elixir_freq", width=140)
            dpg.add_input_float(label="Hero Ability Cooldown (s)", default_value=2.5, min_value=0, tag="ability_cd", width=180)
            dpg.add_checkbox(label="Trophy Dumping", tag="trophy_dumping")
        dpg.add_spacer(height=8)
        dpg.add_text(f"Resolution: {screen_width}x{screen_height}   |   Assets: {'2K' if use_2k_images else 'FullHD'}", color=(120, 160, 200))
        dpg.add_spacer(height=8)
        dpg.add_separator()
        dpg.add_spacer(height=8)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Start Bot", callback=start_bot_callback, width=140)
            dpg.add_button(label="Stop Bot", callback=stop_bot_callback, width=140)
            dpg.add_spacer(width=30)
            dpg.add_text("Status:", color=(160, 160, 160))
            dpg.add_text("Stopped", tag="status_text", color=(220, 80, 80))
        dpg.add_spacer(height=8)
        dpg.add_separator()
        dpg.add_spacer(height=8)
        dpg.add_text("Bot Log", color=(160, 160, 160))
        dpg.add_input_text(multiline=True, readonly=True, height=190, width=-1, tag="log", default_value="Bot initialized and ready to start...\n")
        dpg.add_spacer(height=8)
        dpg.add_separator()
        dpg.add_spacer(height=8)
        dpg.add_text("Start the bot, then switch to Clash of Clans.", color=(160, 160, 160))
        dpg.add_spacer(height=4)
        dpg.add_text("Press 'O' to start and 'P' to stop the bot at any time (even when minimized).", color=(160, 160, 160))

    dpg.set_primary_window("main_window", True)
    dpg.bind_theme(global_theme)
    dpg.bind_font(default_font)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    # Start global hotkey listener in a daemon thread
    threading.Thread(target=global_hotkey_listener, daemon=True).start()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()