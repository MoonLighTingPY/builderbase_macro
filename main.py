import pydirectinput
import pyautogui
import time
import os
import cv2
import numpy as np
from mss import mss

# Initialize mss for screen capture
sct = mss()

# Set the delay for pyautogui and pydirectinput to 0 for faster execution
pyautogui.PAUSE = 0
pydirectinput.PAUSE = 0
# Get screen size
screen_width, screen_height = pyautogui.size()


elixir_check_counter = 0 # Counter for elixir check so we don't after every battle so we can save time
first_village = True # Flag to indicate if we are in the first village battle


error_last_print_time = {} # Track last error message time for each image
ERROR_COOLDOWN = 5  # Time in seconds before printing the same error message again

# Flag to stop the script


# Determine if we should use high resolution images
use_2k_images = screen_width > 1920 or screen_height > 1080
image_dir = "2k/" if use_2k_images else "fullhd/"
print(f"Screen resolution: {screen_width}x{screen_height}, using {'2K' if use_2k_images else 'standard'} images")

# Define screen regions. Used so we don't have to search the whole screen for images
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
    "elixir_cart_really_full": f"{image_dir}/elixir_cart/elixir_cart_really_full.png",
    "elixir_cart_full": f"{image_dir}/elixir_cart/elixir_cart_full.png",
    "elixir_cart_empty": f"{image_dir}/elixir_cart/elixir_cart_empty.png",
    "elixir_cart_empty_battle": f"{image_dir}/elixir_cart/elixir_cart_empty_battle.png",
    "elixir_cart_full_battle": f"{image_dir}/elixir_cart/elixir_cart_full_battle.png",
    "elixir_cart_not_empty": f"{image_dir}/elixir_cart/elixir_cart_not_empty.png",
    
    # Button Images
    "collect_full": f"{image_dir}/buttons/collect_full.png",
    "collect_empty": f"{image_dir}/buttons/collect_empty.png",
    "close_elixir": f"{image_dir}/buttons/close_elixir.png",
    "battle_open": f"{image_dir}/buttons/attack.png",
    "battle_start": f"{image_dir}/buttons/find_now.png",
    "end_battle": f"{image_dir}/buttons/end_battle.png",
    "return_home": f"{image_dir}/buttons/return_home.png",
    "surrender": f"{image_dir}/buttons/surrender.png",
    "confirm_surrender": f"{image_dir}/buttons/confirm_surrender.png",

    # Other Images
    "start_app": f"{image_dir}start_app.png",
    "battle_verify": f"{image_dir}battle_verify.png",
    "attack_cooldown": f"{image_dir}attack_cooldown.png",
    "second_village": f"{image_dir}second_battle.png",
    "troop_deployed": f"{image_dir}troop_deployed.png",

    # Places to deploy troops
    "warplace": [os.path.join(image_dir, "warplace", img) for img in os.listdir(os.path.join(image_dir, "warplace")) if img.endswith(".png")]
}


# Function to click on an image on the screen
# This function will keep trying to find the image until it is found or the loop is broken
# It will return True if the image is found and clicked, otherwise it will return False
# The function will also print an error message if the image is not found, but it will only print the message once every ERROR_COOLDOWN seconds
# Parameters:
# region, tuple of (x1, y1, x2, y2) that defines the region of the screen to search for the image
# confidence, float, between 0 and 1 that defines the confidence level for the image matching
# parsemode, boolean, defines whether to return the coordinates of the image instead of clicking it
# loop, boolean, defines whether to keep trying to find the image until it is found or no
def click_image(image_path, region=None, confidence=0.8, parsemode=False, loop=True):
    if loop:
        while True:
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
        
        # Try to find the image in the screenshot
        # If the maximum value is greater than the confidence level, we found the image
        if max_val >= confidence:
            # Calculate center position
            h, w = template.shape[:2]
            center_x = max_loc[0] + w//2 + (region[0] if region else 0)
            center_y = max_loc[1] + h//2 + (region[1] if region else 0)
            
            # Click the center of the image if parsemode is False
            if not parsemode:
                pyautogui.click(center_x, center_y)
                print(f"Success clicking image {image_path}")
                return True
            # Return the coordinates of the image if parsemode is True without clicking it
            else:
                return (center_x, center_y)
            
        # If the image is not found, print an error message
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

# Function to deploy troops at a specific location
# This function will move the mouse to the location and click it, then deploy troops using the keys 1-8
def deploy_troops(location, delay):
    pyautogui.moveTo(location)
    pyautogui.click(location)
    time.sleep(delay)
    # Deploy troops using keys 1-8 for troops and Q for Hero. 
    for key in ["q", "Q", "1", "2", "3", "4", "5", "6", "7", "8"]:
        time.sleep(delay)
        pydirectinput.press(key)
        time.sleep(delay)
        pyautogui.click()
    # Cast the ability of the hero and troops
    for key in ["q", "Q", "1", "2", "3", "4", "5", "6", "7", "8"]:
        time.sleep(delay)
        pydirectinput.press(key)

# Function to check the elixir cart and collect elixir if available
# This function will check the elixir cart for different states (full, empty, not empty) and collect elixir if available
def check_elixir():
    # Define image pairs (cart image, collect button, cart confidence, button confidence)
    image_pairs = [
        ("elixir_cart_full", "collect_full", 0.55, 0.6),
        ("elixir_cart_really_full", "collect_empty", 0.55, 0.55),
        ("elixir_cart_empty", "collect_empty", 0.55, 0.6),
        ("elixir_cart_not_empty", "collect_empty", 0.55, 0.6)
    ]
    
    # Try each image pair up to 2 times
    for _ in range(2):
        for cart_img, collect_img, cart_conf, btn_conf in image_pairs:
            if click_image(IMAGE_PATHS[cart_img], loop=False, confidence=cart_conf, region=regions["top_half"]):
                time.sleep(0.3)
                click_image(IMAGE_PATHS[collect_img], loop=False, confidence=btn_conf, region=regions["bottom_right"])
                return True  # Success
                
    return False  # Indicate that a restart is needed

# Function to find the warplace and deploy troops
# This function will try to find the warplace image and deploy troops at that location
# If the warplace image is not found, it will try to click random places on the screen until a troop is deployed
def find_warplace_and_deploy_troops():
    # Try to find the warplace image and deploy troops
    for path in IMAGE_PATHS["warplace"]:
        warplace_location = click_image(path, region=regions["whole_screen"], parsemode=True, confidence=0.8, loop=False)

        if warplace_location:  
            deploy_troops(warplace_location, delay=0.1)
            print(f"Success of deploying troops!")
            return  # Exit after success
        
        # If the warplace image is not found, try to deploy troops by clicking random places
        # This is a fallback method to ensure troops are deployed even if the warplace image is not found
        else:
            print(f"Could not deploy troops. Trying fallback method.")
            for _ in range(35):  # Try clicking N random places. Usually 10 is enough
                # Click random places in the top half of the screen (to avoild the troops menu)
                random_x = np.random.randint(regions["top_half"][0], regions["top_half"][2])
                random_y = np.random.randint(regions["top_half"][1], regions["top_half"][3])
                # Try to deploy a troop by clicking the random place
                pydirectinput.press("1")
                time.sleep(0.1)
                pyautogui.click(random_x, random_y)
                time.sleep(0.5)

                # Check if the troop was deployed successfully
                if click_image(IMAGE_PATHS["troop_deployed"], region=regions["bottom_left"], loop=False, confidence=0.8):
                    print("Troop deployed successfully using fallback method!")
                    # If successful, deploy other troops and the hero at the discovered location
                    deploy_troops((random_x, random_y), delay=0.1)
                    return  # Exit after success



def main():
    # global for elixir_check_counter to keep track of the number of times we check for elixir
    global elixir_check_counter

    while True:
        # Increment counter at the start of each loop
        elixir_check_counter += 1
        print(f"Elixir Counter: {elixir_check_counter}")  # Debug info
        
        # Check for elixir every 10 times
        should_check_elixir = elixir_check_counter % 10 == 0
        
        # Check if the game is open in the builder base by looking for the attack button
        if click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], parsemode=True):
            # Check for elixir if it's time (every 10 iterations)
            if should_check_elixir:
                print("Checking for elixir this iteration")
                # Scroll so the elixir cart is visible in case it is not
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
            
            # Press the attack button to open the battle menu
            click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"])
            time.sleep(0.3)
            # Check if attack is available. If not, wait for 2 seconds and try again
            # This is to avoid clicking the attack button when it is on cooldown
            while click_image(IMAGE_PATHS["attack_cooldown"], loop=False, confidence=0.8):
                print("Attack cooldown detected. Waiting for 2 seconds...")
                time.sleep(2)
            # If no cooldown, start the battle
            click_image(IMAGE_PATHS["battle_start"], region=regions["bottom_right"])

            # Wait for troops menu to appear before deploying troops
            while True:
                if click_image(IMAGE_PATHS["battle_verify"], region=regions["bottom_half"], loop=False, parsemode=True):
                    # Found battle_verify, we can proceed
                    break
        

            # Deploy troops at the first village
            find_warplace_and_deploy_troops()

            # Wait for the first battle to finish. This is done by looking for new troops to appear in the menu
            # If the troops are not found, we assume the battle is still going on in the first village
            while not click_image(IMAGE_PATHS["second_village"], loop=False, confidence=0.8):
                print("First village battle is not finished yet.")
                # Perodically cast the hero ability to help the troops
                time.sleep(5)
                pydirectinput.press("q")
                # If return home button appeared before the new troops - it means the battle is over and didn't advance to the second village
                if click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.8):
                    print("First village battle didn't advance to the second village. Returning home.")
                    break

                # The battle advanced to the second village, as the return home button is not found but new troops are found
                # Deplouy troops at the second village
                find_warplace_and_deploy_troops()
                print("Battle advanced to the second village.")

                # Wait for the second battle to finish. This is done by looking for the return home button
                # If the return home button is not found, we assume the battle is still going on in the second village
                while not click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.8):
                    print("Second village battle not finished yet.")
                    time.sleep(5)
                    pydirectinput.press("q")

                # Try to click the return home button once more just to be sure (lol)
                click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.8)

# After so many years, i still DON'T KNOW why this is needed, but it is
if __name__ == "__main__":
    main()
