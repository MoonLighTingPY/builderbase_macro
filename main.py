import pydirectinput
import pyautogui
import time
import cv2
import numpy as np
from mss import mss
import random
from resources import (
    screen_width,
    screen_height,
    regions,
    IMAGE_PATHS,
)

def send_overlay_status(msg_type, text=None, color=None):
    if overlay_queue is None:
        return
    if msg_type == "show":
        overlay_queue.put(("show", text, color))
    elif msg_type == "hide":
        overlay_queue.put(("hide",))
    elif msg_type == "destroy":
        overlay_queue.put(("destroy",))

# Initialize mss for screen capture
sct = mss()

# Set the delay for pyautogui and pydirectinput to 0 for faster execution
pyautogui.PAUSE = 0
pydirectinput.PAUSE = 0
# Get screen size

error_last_print_time = {} # Track last error message time for each image
ERROR_COOLDOWN = 1  # Time in seconds before printing the same error message again

elixir_check_counter = 0 # Counter for elixir check so we don't сheck elixir after every battle so we can save time
elixir_check_frequency = 2 # Check elixir every N battles
last_ability_time = 0  # Track when we last used the hero ability

# Bot timing settings
troop_deploy_delay = 0.3  # Delay between troop deployment actions
ability_cooldown = 2.5   # Seconds between hero ability casts
warplace_attempts = 8  # Number of attempts to find the warplace before giving up

trophy_dumping_mode = False  # Set to True if you want to dump trophies instead of farming

# Function to click on an image on the screen
# This function will keep trying to find the image until it is found or the loop is broken
# It will return True if the image is found and clicked, otherwise it will return False
# The function will also print an error message if the image is not found, but it will only print the message once every ERROR_COOLDOWN seconds
# Parameters:
# region, tuple of (x1, y1, x2, y2) that defines the region of the screen to search for the image
# confidence, float, between 0 and 1 that defines the confidence level for the image matching
# parsemode, boolean, defines whether to return the coordinates of the image instead of clicking it
# loop, boolean, defines whether to keep trying to find the image until it is found or no
def click_image(image_path, region=None, confidence=0.85, parsemode=False, loop=True, scales=[1.0]):
    while True:
        result = click_image_core(image_path, region, confidence, parsemode, scales)
        if result:
            return result
        if not loop:
            return result
        
def click_image_core(image_path, region=None, confidence=0.85, parsemode=False , scales=[1.0, 2.0, 1.75, 1.5, 1.25, 0.75, 0.5]): 
    try:
        # Create a thread-local instance of mss for thread safety
        with mss() as thread_sct:
            # Load the template image
            template = cv2.imread(image_path)
            if template is None:
                print(f"Could not load image: {image_path}")
                return False
                
            # Capture screen region
            monitor = {"top": region[1], "left": region[0], "width": region[2]-region[0], "height": region[3]-region[1]} if region else {"top": 0, "left": 0, "width": screen_width, "height": screen_height}
            screenshot = np.array(thread_sct.grab(monitor))
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            # Multi-scale template matching
            best_val = 0
            best_loc = None
            best_scale = 1.0

            # Try different scales to account for different resolutions
            for scale in scales:
                # Resize the template according to the scale
                width = int(template.shape[1] * scale)
                height = int(template.shape[0] * scale)
                
                if width <= 0 or height <= 0 or width >= screenshot.shape[1] or height >= screenshot.shape[0]:
                    continue
                    
                resized_template = cv2.resize(template, (width, height))
                
                # Match template
                result = cv2.matchTemplate(screenshot, resized_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Keep track of the best match
                if max_val > best_val:
                    best_val = max_val
                    best_loc = max_loc
                    best_scale = scale
            
            # If the best match exceeds our confidence threshold
            if best_val >= confidence:
                # Calculate center position based on the best match
                h, w = int(template.shape[0] * best_scale), int(template.shape[1] * best_scale)
                center_x = best_loc[0] + w//2 + (region[0] if region else 0)
                center_y = best_loc[1] + h//2 + (region[1] if region else 0)
                
                # Click the center of the image if parsemode is False
                if not parsemode:
                    pyautogui.click(center_x, center_y)
                    print(f"Success clicking image {image_path} (scale: {best_scale:.2f}, confidence: {best_val:.2f})")
                    return True
                # Return the coordinates of the image if parsemode is True without clicking it
                else:
                    print(f"Found image {image_path} at ({center_x}, {center_y}) with scale {best_scale:.2f} and confidence {best_val:.2f}")
                    return (center_x, center_y)
            
            # If no good match found
            else:
                current_time = time.time()
                last_time = error_last_print_time.get(image_path, 0)
                if current_time - last_time > ERROR_COOLDOWN:
                    print(f"Image {image_path} not found. Best match: {best_val:.2f}")
                    error_last_print_time[image_path] = current_time
                return False
                
    except Exception as e:
        print(f"Error locating image {image_path}: {e}")
        return False

# Function to deploy troops at a specific location
# This function will move the mouse to the location and click it, then deploy troops using the keys 1-8
def deploy_troops(location, delay, one_troop_only=False):
    pyautogui.moveTo(location)
    pyautogui.click(location)
    if not one_troop_only:
        # Deploy troops and cast abilities using keys 1-8 and Q
        troop_keys = ["q", "Q", "1", "2", "3", "4", "5", "6", "7", "8"]
        for _ in range(2):  # Loop twice: first for deployment, second for abilities
            for key in troop_keys:
                time.sleep(random.uniform(0.1, delay))             
                pydirectinput.press(key)
                if _ == 0:  # Only click during the first loop (deployment phase)
                    pyautogui.click()
                    # random delay to avoid detection (from 0.1 to specified delay)

    else:
        # Deploy only one troop (the first one)
        pydirectinput.press("1")
        time.sleep(delay)
        pyautogui.click()

# Function to check the elixir cart and collect elixir if available
# This function will check the elixir cart for different states (full, empty, not empty) and collect elixir if available
def check_elixir():
    send_overlay_status("show", "Opening elixir cart", "purple")
    # Define image pairs (cart image, collect button, cart confidence, button confidence)
    image_pairs = [
        ("elixir_cart_0", "collect_full", 0.55, 0.7),
        ("elixir_cart_1", "collect_full", 0.55, 0.7),
        ("elixir_cart_2", "collect_full", 0.55, 0.7),
        ("elixir_cart_3", "collect_full", 0.55, 0.7),
        ("elixir_cart_4", "collect_full", 0.55, 0.7),
        ("elixir_cart_6", "collect_empty", 0.55, 0.7),
        ("elixir_cart_7", "collect_empty", 0.55, 0.7)
    ]

    # Scroll so the elixir cart is visible in case it is not
    for _ in range(3):
        # Move mouse to the middle of the screen to zoom in

        pyautogui.moveTo(screen_width // 2, screen_height // 2)
        for _ in range(10):
            pyautogui.scroll(25000)
            time.sleep(0.02)
        # Move mouse to the bottom of the screen to zoom out and outwards, this will move the screen up (elixir cart is at the top of the base)
        pyautogui.moveTo(screen_width // 2, screen_height - 100)
        for _ in range(10):
            pyautogui.scroll(-25000)
            time.sleep(0.02)
    pyautogui.scroll(500)

    # Try to find and click the elixir cart and collect it
    for cart_img, collect_img, cart_conf, btn_conf in image_pairs:
        if click_image(IMAGE_PATHS[cart_img], loop=False, confidence=cart_conf):
            send_overlay_status("show", "Colleting elixir", "purple")
            time.sleep(0.3)
            if click_image(IMAGE_PATHS[collect_img], loop=False, confidence=btn_conf, region=regions["bottom_right"]):
                time.sleep(0.3)
                click_image(IMAGE_PATHS["close_elixir"], region=regions["top_right"], confidence=0.7)
                return True  # Success
            else:            
                print(f"Collect button {collect_img} not found for cart {cart_img}.")
                return False
    return False  # Indicate that a restart is needed

# Add a dedicated function to check and dismiss star bonus popup
def check_and_dismiss_star_bonus():
    send_overlay_status("show", "Checking for star bonus", "yellow")
    """Check for star bonus popup and dismiss it if found"""

    # Wait for star bonus popup to appear and dismiss it
    print("Waiting for star bonus popup...")
    time.sleep(1)
    time.sleep(1)   
    if click_image_core(IMAGE_PATHS["okay_starbonus"], confidence=0.7, region=regions["bottom_half"], parsemode=False):
        print("Star bonus popup detected and dismissed")
        time.sleep(0.3)
        return True
    return False

# Function to find the warplace and deploy troops
# This function will try to find the warplace image and deploy troops at that location
# If the warplace image is not found, it will try to click random places on the screen until a troop is deployed
def find_warplace_and_deploy_troops(one_troop_only=False, is_second_battle=False):
    send_overlay_status("show", "Trying to find a place", "orange")
    found_warplace = False # Flag to indicate if the warplace was found

    # Choose the test troop key based on whether it's the second battle
    test_troop_key = "7" if is_second_battle else "1"

    # Try to find the warplace image and deploy troops
    for path in IMAGE_PATHS["warplace"]:
        warplace_location = click_image(path, region=regions["whole_screen"], parsemode=True, confidence=0.7, loop=False)
        
        if warplace_location:
            send_overlay_status("show", "Deployting troops", "orange")
            # First, test if the location is valid by deploying one troop
            pyautogui.moveTo(warplace_location)
            pyautogui.click(warplace_location)
            pydirectinput.press(test_troop_key)
            time.sleep(0.1)
            pyautogui.click(warplace_location)
            time.sleep(0.2)  # Wait a bit for the troop to be deployed
            
            # Check if the troop was actually deployed by looking for "ends_in"
            if click_image(IMAGE_PATHS["ends_in"], region=regions["top_half"], loop=False, confidence=0.95, parsemode=True):
                print(f"Test troop deployed successfully at {warplace_location}! Deploying all troops...")
                # If successful and not one_troop_only, deploy all remaining troops
                if not one_troop_only:
                    deploy_troops(warplace_location, delay=troop_deploy_delay, one_troop_only=False)
                found_warplace = True
                return
            else:
                print(f"Test troop failed to deploy at {warplace_location}. Trying next warplace image.")

    # If warplace images failed, try the fallback method
    if not found_warplace:
        print(f"Could not deploy troops using warplace images. Trying fallback method.")
        send_overlay_status("show", "Trying random places", "orange")
        for _ in range(15):  # Try clicking N random places
            # Click random places in the top half of the screen
            random_x = np.random.randint(regions["top_half"][0], regions["top_half"][2])
            random_y = np.random.randint(regions["top_half"][1], regions["top_half"][3])
            
            # Test with one troop first
            pyautogui.moveTo(random_x, random_y)
            pyautogui.click(random_x, random_y)
            pydirectinput.press(test_troop_key)
            time.sleep(0.05)
            pyautogui.click(random_x, random_y)
            time.sleep(0.1)

            # Check if the troop was deployed successfully
            if click_image(IMAGE_PATHS["ends_in"], region=regions["top_half"], loop=False, confidence=0.95, parsemode=True):
                print("Test troop deployed successfully using fallback method!")
                # If successful and not one_troop_only, deploy all remaining troops
                if not one_troop_only:
                    deploy_troops((random_x, random_y), delay=troop_deploy_delay, one_troop_only=False)
                return  # Exit after success
                
    # If we reach here, it means we couldn't deploy troops at any location
    print("Failed to deploy troops at any location. Ending battle.")
    if click_image(IMAGE_PATHS["end_battle"], region=regions["bottom_right"], loop=False, confidence=0.7):
        time.sleep(0.3)
        click_image(IMAGE_PATHS["confirm_surrender"], region=regions["bottom_right"], loop=False, confidence=0.7)
        print("Battle ended due to failed troop deployment.")

def cast_hero_ability():
    # Periodically cast the hero ability to help the troops
    global last_ability_time
    current_time = time.time()
    if current_time - last_ability_time >= ability_cooldown:
        pydirectinput.press("q")
        last_ability_time = current_time

def farming_bot_main(elixir_check_frequency, ability_cooldown, trophy_dumping_mode, screen_width, screen_height, use_2k_images, overlay_queue_arg=None):
    global elixir_check_counter, overlay_queue
    overlay_queue = overlay_queue_arg
    print("Bot process started")
    while True:
        send_overlay_status("show", "Waiting for Builder Base...", "yellow")
        if not trophy_dumping_mode:
            # Check if the game is open in the builder base by looking for the attack button
            print("Waiting for Builder Base...")
            if click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], confidence=0.7, parsemode=True):
                print("Game is open in the builder base, starting bot...")

            # Check for star bonus popup before starting the battle
            check_and_dismiss_star_bonus()

            elixir_check_counter += 1
            if elixir_check_counter >= elixir_check_frequency:
                elixir_check_counter = 0
                print("Checking for elixir this iteration")
                check_elixir()

            # Press the attack button to open the battle menu
            send_overlay_status("show", "Starting battle...", "orange")
            click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], confidence=0.7)
            time.sleep(0.3)

            # Simple click for battle_start - no special handling needed
            click_image(IMAGE_PATHS["battle_start"], region=regions["bottom_right"], confidence=0.7)

            # Wait for troops menu to appear before deploying troops
            print("Waiting for battle")
            while True:
                if click_image(IMAGE_PATHS["battle_verify"], region=regions["top_half"], loop=False, parsemode=True, confidence=0.95):
                    print("Battle verify found, troops menu is ready.")
                    
                    time.sleep(0.5)
                    break
                else:
                    print("Waiting for troops menu to appear...")
                    time.sleep(0.2)

            print("Deploying troops for the first village...")
            find_warplace_and_deploy_troops(one_troop_only=False, is_second_battle=False)

            # Wait for the first battle to finish
            print("1st Battle in progress...")
            send_overlay_status("show", "1st Battle in progress...", "orange")
            battle_finished = False
            while not click_image(IMAGE_PATHS["battle_verify"], region=regions["top_half"], loop=False, confidence=0.95, parsemode=True):
                print("First village battle is not finished yet.")
                if click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.7):
                    battle_finished = True
                    print("First village battle didn't advance to the second village. Returning home.")
                    time.sleep(0.5)
                    check_and_dismiss_star_bonus()
                    break
                cast_hero_ability()

            if battle_finished == False:
                print("Battle advanced to the second village.")
                time.sleep(1)
                print("Deploying troops for the second village...")
                find_warplace_and_deploy_troops(one_troop_only=False, is_second_battle=True)

                print("2nd Battle in progress...")
                send_overlay_status("show", "2nd Battle in progress...", "orange")
                while not click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.7):
                    print("Second village battle not finished yet.")
                    cast_hero_ability()

                print("Battle finished, returning home...")
                send_overlay_status("show", "Returning home...", "yellow")
                time.sleep(1)

        elif trophy_dumping_mode:
            print("Trophy dump: waiting for Builder Base...")
            if click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], confidence=0.7, parsemode=True):
                print("Game is open in the builder base, starting bot...")

            elixir_check_counter += 1
            if elixir_check_counter >= elixir_check_frequency:
                elixir_check_counter = 0
                print("Checking for elixir this iteration")
                check_elixir()

            send_overlay_status("show", "Starting battle...", "orange")
            print("Trophy dump: Starting battle")
            click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], confidence=0.7)
            time.sleep(0.3)

            click_image(IMAGE_PATHS["battle_start"], region=regions["bottom_right"], confidence=0.7)

            print("Trophy dump: Waiting for battle...")
            while True:
                if click_image(IMAGE_PATHS["battle_verify"], region=regions["top_half"], loop=False, parsemode=True, confidence=0.95):
                    print("Battle verify found, troops menu is ready.")
                    break

            print("Trophy dump: deploying one troop...")
            find_warplace_and_deploy_troops(one_troop_only=True, is_second_battle=False)

            send_overlay_status("show", "Surrendering...", "red")
            print("Trophy dump: surrendering")
            if click_image(IMAGE_PATHS["surrender"], region=regions["bottom_left"], loop=True, confidence=0.8):
                print("Surrendering the first village battle to dump trophies.")
                time.sleep(0.3)
                click_image(IMAGE_PATHS["confirm_surrender"], region=regions["bottom_right"], loop=False, confidence=0.7)
                time.sleep(0.3)
                click_image(IMAGE_PATHS["return_home"], loop=True, confidence=0.7)
                time.sleep(0.3)
                click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.7)
                print("Trophy dump: returned home.")

if __name__ == "__main__":
    import gui
    gui.main()