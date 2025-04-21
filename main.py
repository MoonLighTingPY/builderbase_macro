import pydirectinput
import pyautogui
import time
import threading
import keyboard
import sys
import os
import cv2
import numpy as np
from mss import mss

sct = mss()

pyautogui.PAUSE = 0
pydirectinput.PAUSE = 0

# Get screen size
screen_width, screen_height = pyautogui.size()

# Determine if we should use high resolution images
use_2k_images = screen_width > 1920 or screen_height > 1080
image_dir = "2k/" if use_2k_images else "fullhd/"
print(f"Screen resolution: {screen_width}x{screen_height}, using {'2K' if use_2k_images else 'standard'} images")

# Define regions
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
    "start_app": f"{image_dir}start_app.png",
    "elixir_cart_really_full": f"{image_dir}/elixir_cart/elixir_cart_really_full.png",
    "elixir_cart_full": f"{image_dir}/elixir_cart/elixir_cart_full.png",
    "elixir_cart_empty": f"{image_dir}/elixir_cart/elixir_cart_empty.png",
    "elixir_cart_empty_battle": f"{image_dir}/elixir_cart/elixir_cart_empty_battle.png",
    "elixir_cart_full_battle": f"{image_dir}/elixir_cart/elixir_cart_full_battle.png",
    "elixir_cart_not_empty": f"{image_dir}/elixir_cart/elixir_cart_not_empty.png",
    "collect_full": f"{image_dir}/buttons/collect_full.png",
    "collect_empty": f"{image_dir}/buttons/collect_empty.png",
    "close_elixir": f"{image_dir}/buttons/close_elixir.png",
    "battle_open": f"{image_dir}/buttons/attack.png",
    "battle_start": f"{image_dir}/buttons/find_now.png",
    "end_battle": f"{image_dir}/buttons/end_battle.png",
    "return_home": f"{image_dir}/buttons/return_home.png",
    "surrender": f"{image_dir}/buttons/surrender.png",
    "confirm_surrender": f"{image_dir}/buttons/confirm_surrender.png",
    "battle_verify": f"{image_dir}battle_verify.png",
    "attack_cooldown": f"{image_dir}attack_cooldown.png",
    "second_village": f"{image_dir}second_battle.png",
    "troop_deployed": f"{image_dir}troop_deployed.png",
    "warplace": [os.path.join(image_dir, "warplace1", img) for img in os.listdir(os.path.join(image_dir, "warplace1")) if img.endswith(".png")]
}

elixir_check_counter = 0

first_village = True

# Track last error message time for each image
error_last_print_time = {}
ERROR_COOLDOWN = 5  # Time in seconds before printing the same error message again

# Flag to stop the script
stop_flag = False

def click_image(image_path, region=None, confidence=0.8, parsemode=False, loop=True):
    if loop:
        while not stop_flag:
            if click_image_core(image_path, region, confidence, parsemode):
                return True
    else:
        return click_image_core(image_path, region, confidence, parsemode)
        

def click_image_core(image_path, region=None, confidence=0.85, parsemode=False):
    try:
        # Load the template image
        template = cv2.imread(image_path)
        if template is None:
            print(f"Could not load image: {image_path}")
            return False
            
        # Capture screen region
        monitor = {"top": region[1], "left": region[0], "width": region[2]-region[0], "height": region[3]-region[1]} if region else {"top": 0, "left": 0, "width": screen_width, "height": screen_height}
        screenshot = np.array(sct.grab(monitor))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
        
        # Match template
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            # Calculate center position
            h, w = template.shape[:2]
            center_x = max_loc[0] + w//2 + (region[0] if region else 0)
            center_y = max_loc[1] + h//2 + (region[1] if region else 0)
            
            if not parsemode:
                pyautogui.click(center_x, center_y)
                print(f"Success clicking image {image_path}")
                return True
            else:
                return (center_x, center_y)
        else:
            current_time = time.time()
            last_time = error_last_print_time.get(image_path, 0)
            if current_time - last_time > ERROR_COOLDOWN:
                print(f"Image {image_path} not found.")
                error_last_print_time[image_path] = current_time
            return False
    except Exception as e:
        print(f"Error locating image {image_path}: {e}")
        return False

def deploy_troops(location, delay):
    pyautogui.moveTo(location)
    pyautogui.click(location)
    time.sleep(delay)
    for key in ["q", "Q", "q", "1", "2", "3", "4", "5", "6", "7", "8"]:
        time.sleep(delay)
        pydirectinput.press(key)
        time.sleep(delay)
        pyautogui.click()
    for key in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        time.sleep(delay)
        pydirectinput.press(key)

def check_elixir():
    # Track the result of the image checks
    result = False
    for _ in range(3):
        if click_image(IMAGE_PATHS["elixir_cart_full"], loop=False, confidence=0.55, region=regions["top_half"]):
            time.sleep(0.3)
            click_image(IMAGE_PATHS["collect_full"], loop=False, confidence=0.6, region=regions["bottom_right"])
            result = True
            break

        elif click_image(IMAGE_PATHS["elixir_cart_really_full"], loop=False, confidence=0.55, region=regions["top_half"]):
            time.sleep(0.3)
            click_image(IMAGE_PATHS["collect_empty"], loop=False, confidence=0.55, region=regions["bottom_right"])
            result = True
            break

        elif click_image(IMAGE_PATHS["elixir_cart_empty"], loop=False, confidence=0.55, region=regions["top_half"]):
            time.sleep(0.3)
            click_image(IMAGE_PATHS["collect_empty"], loop=False, confidence=0.6, region=regions["bottom_right"])
            result = True
            break

        elif click_image(IMAGE_PATHS["elixir_cart_not_empty"], loop=False, confidence=0.55, region=regions["top_half"]):
            time.sleep(0.3)
            click_image(IMAGE_PATHS["collect_empty"], loop=False, confidence=0.6, region=regions["bottom_right"])
            result = True
            break

    if not result:
        return False  # Indicate that a restart is needed

    return True  # Indicate success

def find_warplace_and_deploy_troops():
    # Flag to indicate if we need to break out of the outer loop
    for path in IMAGE_PATHS["warplace"]:
        for _ in range(2):
            warplace_location = click_image(path, region=regions["whole_screen"], parsemode=True, confidence=0.8, loop=False)
            if warplace_location:
                deploy_troops(warplace_location, delay=0.1)
                print(f"Success of deploying troops!")
                return  # Exit the function immediately after success
            else:
                print(f"Could not deploy troops. Trying fallback method.")
                for _ in range(35):  # Try clicking random places up to 35 times
                    random_x = np.random.randint(regions["top_half"][0], regions["top_half"][2])
                    random_y = np.random.randint(regions["top_half"][1], regions["top_half"][3])
                    pydirectinput.press("1")
                    time.sleep(0.1)
                    pyautogui.click(random_x, random_y)
                    time.sleep(0.5)

                    if click_image(IMAGE_PATHS["troop_deployed"], region=regions["bottom_left"], loop=False, confidence=0.8):
                        print("Troops deployed successfully using fallback method!")
                        deploy_troops((random_x, random_y), delay=0.1)
                        return  # Exit the function immediately after success


def monitor_keyboard():
    global stop_flag
    while True:
        if keyboard.is_pressed('='):
            stop_flag = True
            print("Stop signal received. Exiting...")
            break
        time.sleep(0.1)

def main():
    global stop_flag, elixir_check_counter
    keyboard_thread = threading.Thread(target=monitor_keyboard, daemon=True)
    keyboard_thread.start()

    while not stop_flag:
        # Increment counter at the start of each loop
        elixir_check_counter += 1
        print(f"Counter: {elixir_check_counter}")  # Debug info
        
        # Check for elixir every 10 times
        should_check_elixir = elixir_check_counter % 10 == 0
        
        if click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], parsemode=True):
            # Check for elixir if it's time (every 10 iterations)
            if should_check_elixir:
                print("Checking for elixir this iteration")
                # Scroll to find the elixir cart
                for _ in range(10):
                    pyautogui.scroll(25000)
                    time.sleep(0.05)
                pyautogui.moveTo(200, 1070)
                for _ in range(10):
                    pyautogui.scroll(-25000)
                    time.sleep(0.05)
                time.sleep(0.4)
                check_elixir()
                click_image(IMAGE_PATHS["close_elixir"], region=regions["top_right"])
            
            # Reset counter to prevent integer overflow
            if elixir_check_counter >= 100:
                elixir_check_counter = 0

            click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"])
            time.sleep(0.3)
            while click_image(IMAGE_PATHS["attack_cooldown"], loop=False, confidence=0.8):
                print("Attack cooldown detected. Waiting for 2 seconds...")
                time.sleep(2)
            click_image(IMAGE_PATHS["battle_start"], region=regions["bottom_right"])

            start_time = time.time()
            exit_outer_loop = False
            while True:
                if click_image(IMAGE_PATHS["battle_verify"], region=regions["bottom_half"], loop=False, parsemode=True):
                    # Found battle_verify, we can proceed
                    break
                elif time.time() - start_time > 10:
                    print("battle_verify not found for more than 10 seconds. Exiting...")
                    exit_outer_loop = True  # Set flag to exit
                    break  # Break out of while loop
            
            if exit_outer_loop:  # Check if we need to restart main loop
                continue


            find_warplace_and_deploy_troops()

            while not click_image(IMAGE_PATHS["second_village"], loop=False, confidence=0.8):
                print("First village battle not finished yet. Waiting for 5 seconds...")
                time.sleep(5)
                pydirectinput.press("q")

            time.sleep(0.5)

            find_warplace_and_deploy_troops()

            while not click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.8):
                print("Second village battle not finished yet. Waiting for 5 seconds...")
                time.sleep(5)
                pydirectinput.press("q")

            click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.8)




if __name__ == "__main__":
    main()
