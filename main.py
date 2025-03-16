import pydirectinput
import pyautogui
import time
import threading
import keyboard
import sys
import os

pyautogui.PAUSE = 0
pydirectinput.PAUSE = 0

# Get screen size
screen_width, screen_height = pyautogui.size()

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
    "start_app": "start_app.png",
    "battle_open": "attack.png",
    "elixir_cart_really_full": "elixir_cart_really_full.png",
    "elixir_cart_full": "elixir_cart_full.png",
    "elixir_cart_empty": "elixir_cart_empty.png",
    "elixir_cart_empty_battle": "elixir_cart_empty_battle.png",
    "elixir_cart_full_battle": "elixir_cart_full_battle.png",
    "elixir_cart_not_empty": "elixir_cart_not_empty.bmp",
    "collect_full": "collect_full.png",
    "collect_empty": "collect_empty.png",
    "close_elixir": "close_elixir.png",
    "battle_start": "find_now.png",
    "close_notif": "close_notif.png",
    "in_search": "in_search.bmp",
    "warplace": ["pad0.png", "pad1.png", "pad2.png", "grass0.png", "stones0.png"]
}

# Define counters
elixir_attempts = 0
elixir_failures = 0
fatal_errors = 0
all_exceptions = []

warplace_attempts = {path: 0 for path in IMAGE_PATHS["warplace"]}
warplace_failures = {path: 0 for path in IMAGE_PATHS["warplace"]}

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
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
        if location:
            center_coords = pyautogui.center(location)
            if not parsemode:
                pyautogui.click(center_coords)
                print(f"Success clicking image {image_path}")
                return True
            else:
                return center_coords
        else:
            current_time = time.time()
            last_time = error_last_print_time.get(image_path, 0)
            if current_time - last_time > ERROR_COOLDOWN:
                print(f"Image {image_path} not found.")
                error_last_print_time[image_path] = current_time
    except Exception as e:
        #all_exceptions.append(f"Error locating image {image_path}: {e}")
        print(f"Error locating image {image_path}: {e}")
        pass

def deploy_troops(location, delay=1):
    pyautogui.moveTo(location)
    pyautogui.click(location)
    time.sleep(delay)
    for key in ["q", "Q", "q", "1", "2", "3", "4", "5", "6"]:
        time.sleep(delay)
        pydirectinput.press(key)
        pyautogui.click()
    for key in ["q", "Q", "q", "1", "2", "3", "4", "5", "6"]:
        time.sleep(delay)
        pydirectinput.press(key)
        pyautogui.click()

def check_elixir():
    global elixir_attempts, elixir_failures
    elixir_attempts += 1

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
        elixir_failures += 1
        return False  # Indicate that a restart is needed

    return True  # Indicate success

def monitor_keyboard():
    global stop_flag
    while True:
        if keyboard.is_pressed('='):
            stop_flag = True
            print("Stop signal received. Exiting...")
            break
        time.sleep(0.1)

def main():
    global stop_flag, fatal_errors
    keyboard_thread = threading.Thread(target=monitor_keyboard, daemon=True)
    keyboard_thread.start()

    while not stop_flag:
        try:
           if click_image(IMAGE_PATHS["start_app"], region=regions["top_right"], confidence=0.9):
                if click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], parsemode=True):
                    # Scroll to refresh the area
                    for _ in range(10):
                        pyautogui.scroll(25000)
                        time.sleep(0.05)
                    pyautogui.moveTo(200, 1070)
                    for _ in range(10):
                        pyautogui.scroll(-25000)
                        time.sleep(0.05)
                    time.sleep(0.4)

                    if not check_elixir():
                        pyautogui.hotkey('alt', 'f4')
                        time.sleep(0.8)
                        continue  # Restart the main loop

                    click_image(IMAGE_PATHS["close_elixir"], region=regions["top_right"])
                    click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"])
                    click_image(IMAGE_PATHS["battle_start"], region=regions["bottom_right"])
                    time.sleep(2)

                    start_time = time.time()
                    exit_outer_loop = False  # Moved flag initialization here
                    while click_image(IMAGE_PATHS["in_search"], region=regions["bottom_half"], loop=False):
                        if time.time() - start_time > 10:
                            print("in_search detected for more than 10 seconds. Exiting...")
                            time.sleep(0.8)
                            exit_outer_loop = True  # Set flag to exit
                            break  # Break out of while loop
                        time.sleep(0.5)
                    
                    if exit_outer_loop:  # Check if we need to restart main loop
                        continue

                    time.sleep(1)
                    # Flag to indicate if we need to break out of the outer loop
                    exit_outer_loop = False
                    time.sleep(1)
                    for path in IMAGE_PATHS["warplace"]:
                        if exit_outer_loop:
                            break

                        warplace_attempts[path] += 1
                        
                        for _ in range(3):
                            warplace_location = click_image(path, region=regions["whole_screen"], parsemode=True, confidence=0.8, loop=False)
                            
                            if warplace_location:
                                deploy_troops(warplace_location, delay=0.1)
                                exit_outer_loop = True  # Set the flag to exit the outer loop
                                print(f"Success clicking image: {path}")
                                break
                            else:
                                warplace_failures[path] += 1
                                print(f"Could not find or click image: {path}")

                    time.sleep(0.6)
                    pyautogui.hotkey('alt', 'f4')
                    time.sleep(1.2)

                    # Display failure rates and attempts
                    print("\n[STATS] Failure Rates and Attempts:")
                    if elixir_attempts > 0:
                        elixir_fail_rate = (elixir_failures / elixir_attempts) * 100
                        print(f"[STATS] Elixir carts - {elixir_fail_rate:.2f}% fail rate")
                    else:
                        print("[STATS] No attempts made for elixir carts.")

                    for path in IMAGE_PATHS["warplace"]:
                        if warplace_attempts[path] > 0:
                            warplace_fail_rate = (warplace_failures[path] / warplace_attempts[path]) * 100
                            print(f"[STATS] Warplace - {path} - {warplace_attempts[path]} attempts - {warplace_fail_rate:.2f}% fail rate")
                        else:
                            print(f"[STATS] Warplace - {path} - No attempts made.")

                    # Print fatal errors and all exceptions
                    if fatal_errors > 0:
                        print(f"\n[STATS] Total fatal errors encountered: {fatal_errors}")
                    if all_exceptions:
                        print("\n[STATS] Logged Exceptions:")
                        for exception in all_exceptions:
                            print(exception)
                    print("============================================================================")


        except Exception as e:
            fatal_errors += 1
            all_exceptions.append(f"FATAL ERROR: {e}")
            print(f"FATAL ERROR: {e}")
            pyautogui.hotkey('alt', 'f4')
            time.sleep(1)
            continue  # Restart the main loop



if __name__ == "__main__":
    main()
