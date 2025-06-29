import os
import sys
import pyautogui

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Determine if we should use high resolution images
use_2k_images = screen_width > 1920 or screen_height > 1080
image_dir = "2k/" if use_2k_images else "fullhd/"

# Define screen regions
regions = {
    "top_right": (screen_width // 2, 0, screen_width, screen_height // 2),
    "bottom_left": (0, screen_height // 2, screen_width // 2, screen_height),
    "bottom_right": (screen_width // 2, screen_height // 2, screen_width, screen_height),
    "whole_screen": (0, 0, screen_width, screen_height),
    "top_half": (0, 0, screen_width, screen_height // 2),
    "bottom_half": (0, screen_height // 2, screen_width, screen_height)
}

# Paths to image assets
IMAGE_PATHS = {
    # Elixir Cart Images
    "elixir_cart_0": resource_path(f"{image_dir}elixir_cart/elixir_cart_0.png"),
    "elixir_cart_1": resource_path(f"{image_dir}elixir_cart/elixir_cart_1.png"),
    "elixir_cart_2": resource_path(f"{image_dir}elixir_cart/elixir_cart_2.png"),
    "elixir_cart_3": resource_path(f"{image_dir}elixir_cart/elixir_cart_3.png"),
    "elixir_cart_4": resource_path(f"{image_dir}elixir_cart/elixir_cart_4.png"),
    "elixir_cart_6": resource_path(f"{image_dir}elixir_cart/elixir_cart_6.png"),
    "elixir_cart_7": resource_path(f"{image_dir}elixir_cart/elixir_cart_7.png"),
    # Button Images
    "collect_full": resource_path(f"{image_dir}buttons/collect_full.png"),
    "collect_empty": resource_path(f"{image_dir}buttons/collect_empty.png"),
    "close_elixir": resource_path(f"{image_dir}buttons/close_elixir.png"),
    "battle_open": resource_path(f"{image_dir}buttons/attack.png"),
    "battle_start": resource_path(f"{image_dir}buttons/find_now.png"),
    "end_battle": resource_path(f"{image_dir}buttons/end_battle.png"),
    "return_home": resource_path(f"{image_dir}buttons/return_home.png"),
    "surrender": resource_path(f"{image_dir}buttons/surrender.png"),
    "confirm_surrender": resource_path(f"{image_dir}buttons/confirm_surrender.png"),
    "okay_starbonus": resource_path(f"{image_dir}buttons/okay_starbonus.png"),
    # Other Images
    "start_app": resource_path(f"{image_dir}start_app.png"),
    "battle_verify": resource_path(f"{image_dir}battle_verify.png"),
    "attack_cooldown": resource_path(f"{image_dir}attack_cooldown.png"),
    "ends_in": resource_path(f"{image_dir}ends_in.png"),
    # Places to deploy troops
    "warplace": [
        resource_path(os.path.join(image_dir, "warplace", img))
        for img in os.listdir(resource_path(os.path.join(image_dir, "warplace")))
        if img.endswith(".png")
    ]
}