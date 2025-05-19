import pydirectinput
import pyautogui
import time
import os
import sys
import cv2
import numpy as np
from mss import mss
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import signal
import atexit

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


keyboard_thread = None
stop_event = threading.Event()

# Initialize mss for screen capture
sct = mss()

# Set the delay for pyautogui and pydirectinput to 0 for faster execution
pyautogui.PAUSE = 0
pydirectinput.PAUSE = 0
# Get screen size
screen_width, screen_height = pyautogui.size()

error_last_print_time = {} # Track last error message time for each image
ERROR_COOLDOWN = 1  # Time in seconds before printing the same error message again

elixir_check_counter = 0 # Counter for elixir check so we don't сheck elixir after every battle so we can save time
elixir_check_frequency = 2 # Check elixir every N battles
last_ability_time = 0  # Track when we last used the hero ability

# Bot timing settings
troop_deploy_delay = 0.1  # Delay between troop deployment actions
ability_cooldown = 5.0    # Seconds between hero ability casts
warplace_attempts = 3  # Number of attempts to find the warplace before giving up

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
    "elixir_cart_really_full": resource_path(f"{image_dir}elixir_cart/elixir_cart_really_full.png"),
    "elixir_cart_full": resource_path(f"{image_dir}elixir_cart/elixir_cart_full.png"),
    "elixir_cart_empty": resource_path(f"{image_dir}elixir_cart/elixir_cart_empty.png"),
    "elixir_cart_empty_battle": resource_path(f"{image_dir}elixir_cart/elixir_cart_empty_battle.png"),
    "elixir_cart_full_battle": resource_path(f"{image_dir}elixir_cart/elixir_cart_full_battle.png"),
    "elixir_cart_not_empty": resource_path(f"{image_dir}elixir_cart/elixir_cart_not_empty.png"),
    
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
    "second_village": resource_path(f"{image_dir}second_battle.png"),
    "troop_deployed": resource_path(f"{image_dir}troop_deployed.png"),

    # Places to deploy troops
    "warplace": [resource_path(os.path.join(image_dir, "warplace", img)) for img in os.listdir(resource_path(os.path.join(image_dir, "warplace"))) if img.endswith(".png")]
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
def click_image(image_path, region=None, confidence=0.85, parsemode=False, loop=True, scales=[1.0]):
    if loop:
        if image_path == IMAGE_PATHS["battle_start"]:
            # When looking for battle_start button, add a timeout to check for star bonus popup
            start_time = time.time()
            while not stop_event.is_set():
                # First try to find the battle start button
                if click_image_core(image_path, region, confidence, parsemode, scales) and not stop_event.is_set():
                    return True
                
                # If we've been searching for a while, check for star bonus popup
                if time.time() - start_time > 2:
                    print("Battle start button not found, checking for star bonus popup...")
                    # Try to find and click okay_starbonus with different scales

                    if click_image_core(IMAGE_PATHS["okay_starbonus"], None, 0.7, False, [0.75, 1.0, 1.25]) and not stop_event.is_set():
                        print(f"Star bonus popup detected and dismissed")
                        time.sleep(0.3)
                        return "restart"  # Return "restart" to indicate we need to restart the battle sequence
                    
                    # If no star bonus found after checking, reset timer and continue looking for battle_start
                    start_time = time.time()
        else:
            # Normal behavior for other images
            while not stop_event.is_set():
                if click_image_core(image_path, region, confidence, parsemode, scales) and not stop_event.is_set():
                    return True
    elif not stop_event.is_set():
        return click_image_core(image_path, region, confidence, parsemode, scales)
        

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
def deploy_troops(location, delay):
    pyautogui.moveTo(location)
    pyautogui.click(location)
    time.sleep(delay)
    
    # Deploy troops and cast abilities using keys 1-8 and Q
    troop_keys = ["q", "Q", "1", "2", "3", "4", "5", "6", "7", "8"]
    for _ in range(2):  # Loop twice: first for deployment, second for abilities
        for key in troop_keys:
            if stop_event.is_set():
                return
            time.sleep(delay)
            pydirectinput.press(key)
            if _ == 0:  # Only click during the first loop (deployment phase)
                pyautogui.click()

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

    # Scroll so the elixir cart is visible in case it is not
    for _ in range(3):
        # Move mouse to the middle of the screen to zoom in
        pyautogui.moveTo(screen_width // 2, screen_height // 2)
        for _ in range(10):
            pyautogui.scroll(25000)
            time.sleep(0.05)
        # Move mouse to the bottom of the screen to zoom out and outwards (because the elixir cart is at the bottom of the base)
        pyautogui.moveTo(screen_width // 2, screen_height - 100)
        for _ in range(10):
            pyautogui.scroll(-25000)
            time.sleep(0.05)
    time.sleep(1)
    
    # Try to find and click the elixir cart and collect it
    for cart_img, collect_img, cart_conf, btn_conf in image_pairs:
        if click_image(IMAGE_PATHS[cart_img], loop=False, confidence=cart_conf):
            time.sleep(0.3)
            click_image(IMAGE_PATHS[collect_img], loop=False, confidence=btn_conf, region=regions["bottom_right"])
            time.sleep(0.3)
            click_image(IMAGE_PATHS["close_elixir"], region=regions["top_right"], confidence=0.7)
            return True  # Success
                
    return False  # Indicate that a restart is needed

# Function to find the warplace and deploy troops
# This function will try to find the warplace image and deploy troops at that location
# If the warplace image is not found, it will try to click random places on the screen until a troop is deployed
def find_warplace_and_deploy_troops():
    found_warplace = False # Flag to indicate if the warplace was found
    count = 0 # Counter for the number of attempts to find the warplace

    # Try to find the warplace image and deploy troops
    for path in IMAGE_PATHS["warplace"]:
        if count >= warplace_attempts:  # Exit if we've already deployed 3 times
            print(f"Successfully deployed troops at {count} locations")
            return
            
        warplace_location = click_image(path, region=regions["whole_screen"], parsemode=True, confidence=0.7, loop=False)
        
        if warplace_location:
            deploy_troops(warplace_location, delay=troop_deploy_delay)
            print(f"Troop deployed successfully at {warplace_location}!")
            print(f"Success deploying troops at {path}!")
            found_warplace = True
            count += 1  # Increment count after successful deployment
            
    # If we get here, we either deployed at multiple locations or couldn't find enough warplaces
    if count > 0:
        print(f"Deployed troops at {count} locations")
        return
        

    # If the warplace image is not found, try to deploy troops by clicking random places
    # This is a fallback method to ensure troops are deployed even if the warplace image is not found
    if not found_warplace and not stop_event.is_set():
        print(f"Could not deploy troops. Trying fallback method.")
        for _ in range(15):  # Try clicking N random places. Usually 10 is enough
            if stop_event.is_set():
                return
            # Click random places in the top half of the screen (to avoild the troops menu)
            random_x = np.random.randint(regions["top_half"][0], regions["top_half"][2])
            random_y = np.random.randint(regions["top_half"][1], regions["top_half"][3])
            # Try to deploy a troop by clicking the random place
            pydirectinput.press("1")
            time.sleep(0.1)
            pyautogui.click(random_x, random_y)
            time.sleep(0.35)

            # Check if the troop was deployed successfully
            if click_image(IMAGE_PATHS["troop_deployed"], region=regions["bottom_half"], loop=False, confidence=0.7):
                print("Troop deployed successfully using fallback method!")
                # If successful, deploy other troops and the hero at the discovered location
                deploy_troops((random_x, random_y), delay=troop_deploy_delay)
                return  # Exit after success

def cast_hero_ability():
    # Periodically cast the hero ability to help the troops
    global last_ability_time
    current_time = time.time()
    if current_time - last_ability_time >= ability_cooldown:
        pydirectinput.press("q")
        last_ability_time = current_time

# Function that runs in a separate thread to monitor pause bot key press 
def keyboard_listener():
    keyboard.wait('p')  # Wait for the 'p' key to be pressed
    print("P key pressed, stopping bot...")
    stop_event.set()  # Signal all threads to stop
    
    # Call stop_bot using root.after to ensure it's called from the main thread
    if 'root' in globals():
        root.after(0, stop_bot)
    else:
        stop_bot()

# Function to handle safe exit
def safe_exit():
    print("Performing safe exit...")
    global running
    running = False
    stop_event.set()
    
    # If this is called from Python exit, make sure threads are cleaned up
    if bot_thread and bot_thread.is_alive():
        try:
            bot_thread.join(timeout=1.0)
        except:
            pass


# Flag to control the bot running state
running = False
# Global thread reference
bot_thread = None

atexit.register(safe_exit)
signal.signal(signal.SIGINT, lambda sig, frame: safe_exit())
signal.signal(signal.SIGTERM, lambda sig, frame: safe_exit())

def farming_bot():
    global elixir_check_counter, elixir_check_frequency, running
    while running and not stop_event.is_set():
        try:

            # Check if the game is open in the builder base by looking for the attack button
            if click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], confidence=0.7, parsemode=True):
                print("Game is open in the builder base, starting bot...")                       
            
            elixir_check_counter += 1
            if elixir_check_counter >= elixir_check_frequency:
                elixir_check_counter = 0
                print("Checking for elixir this iteration")
                check_elixir()
           
            # Press the attack button to open the battle menu
            click_image(IMAGE_PATHS["battle_open"], region=regions["bottom_left"], confidence=0.7)
            time.sleep(0.3)

            # Check if we need to restart the battle sequence if we found a star bonus popup
            result = click_image(IMAGE_PATHS["battle_start"], region=regions["bottom_right"], confidence=0.7)
            if result == "restart":
                print("Star bonus popup handled, restarting battle sequence")
                continue  # Restart the loop from the beginning

            # Wait for troops menu to appear before deploying troops
            while running:
                if click_image(IMAGE_PATHS["battle_verify"], region=regions["bottom_half"], loop=False, parsemode=True, confidence=0.7):
                    # Found battle_verify, we can proceed
                    break
                if not running:
                    return
            
            # Deploy troops at the first village
            find_warplace_and_deploy_troops()

            # Wait for the first battle to finish. This is done by looking for new troops to appear in the menu
            # If the troops are not found, we assume the battle is still going on in the first village
            battle_finished = False # Flag to indicate if we are in the first village battle
            while running and not click_image(IMAGE_PATHS["second_village"], loop=False, confidence=0.7, parsemode=True):
                print("First village battle is not finished yet.")
                
                # Check for return home button
                if click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.7):
                    battle_finished = True
                    print("First village battle didn't advance to the second village. Returning home.")
                    break
                cast_hero_ability()
                if not running:
                    return

            # Battle is still going on
            if battle_finished == False and running:
                # The battle advanced to the second village, as the return home button is not found but new troops are found
                # Deploy troops at the second village
                print("Battle advanced to the second village.")
                time.sleep(0.5)
                find_warplace_and_deploy_troops()

                # Wait for the second battle to finish. This is done by looking for the return home button
                # If the return home button is not found, we assume the battle is still going on in the second village
                while running and not click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.7):
                    print("Second village battle not finished yet.")               
                    cast_hero_ability()
                    if not running:
                        return
                # Try to click the return home button once more just to be sure (lol)
                click_image(IMAGE_PATHS["return_home"], loop=False, confidence=0.7)
        except Exception as e:
            print(f"Error in farming bot: {e}")
            if not running:
                return
            # Wait a bit before trying again to avoid spamming errors
            time.sleep(2)

def start_bot():
    global running, bot_thread, elixir_check_frequency, keyboard_thread, stop_event, elixir_check_counter, ability_cooldown, warplace_attempts
    elixir_check_counter = 0  # Reset the elixir check counter when starting the bot
    
    # Update elixir check frequency from UI
    try:
        elixir_check_frequency = int(elixir_freq_entry.get())
        if elixir_check_frequency <= 0:
            messagebox.showerror("Error", "Elixir check frequency must be greater than 0")
            return
    except ValueError:
        messagebox.showerror("Error", "Elixir check frequency must be a number")
        return

    # Update delays and cooldown from UI
    try:
        ability_cooldown = float(ability_cd_entry.get())
        if troop_deploy_delay < 0 or ability_cooldown < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Delays and cooldown must be non-negative numbers")
        return
    
    # Update warplace attempts from UI
    try:
        warplace_attempts = int(warplace_entry.get())
        if warplace_attempts <= 0:
            messagebox.showerror("Error", "Warplace deployment attempts must be greater than 0")
            return
    except ValueError:
        messagebox.showerror("Error", "Warplace deployment attempts must be a number")
        return
    
    if not running:
        # Reset the stop_event - critical for restarting
        stop_event.clear()
        
        running = True
        start_button.config(text="Stop Bot", bg="#ff6b6b")
        status_label.config(text="Status: Running", foreground="green")
        log_text.insert(tk.END, "Bot started...\n")
        log_text.insert(tk.END, f"Elixir check frequency set to every {elixir_check_frequency} battles\n")
        log_text.insert(tk.END, "Press 'P' key to stop the bot at any time\n")
        log_text.see(tk.END)
        
        # Create and start the bot thread
        bot_thread = threading.Thread(target=farming_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Start keyboard listener in a separate thread
        keyboard_thread = threading.Thread(target=keyboard_listener)
        keyboard_thread.daemon = True
        keyboard_thread.start()
    else:
        stop_bot()

def stop_bot():
    global running, bot_thread, keyboard_thread
    
    if running:
        print("Stopping bot...")
        running = False
        stop_event.set()  # Signal all threads to stop
        
        # Update UI safely
        if 'root' in globals():
            root.after(0, lambda: start_button.config(text="Start Bot", bg="#4CAF50"))
            root.after(0, lambda: status_label.config(text="Status: Stopped", foreground="red"))
            root.after(0, lambda: log_text.insert(tk.END, "Bot stopped.\n"))
            root.after(0, lambda: log_text.see(tk.END))
        
        # Try to forcefully terminate operations that might be stuck
        try:
            # Press Escape key a few times to try to exit any in-game menus
            for _ in range(3):
                pydirectinput.press('escape')
                time.sleep(0.1)
        except Exception as e:
            print(f"Error sending escape keys: {e}")
            
        print("Stop event set, waiting for threads to terminate...")
        
        # Give threads a chance to terminate gracefully
        if bot_thread and bot_thread.is_alive():
            try:
                bot_thread.join(timeout=2.0)
                if bot_thread.is_alive():
                    print("Warning: Bot thread is still running after timeout")
            except Exception as e:
                print(f"Error joining bot thread: {e}")
                
        # Clear thread references after stopping
        bot_thread = None
        keyboard_thread = None

def on_closing():
    stop_bot()
    root.destroy()

# Create the main UI window
root = tk.Tk()
root.title("CoC Builder Base Farming Bot")
root.geometry("600x500")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Configure the grid
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(3, weight=1)

# Create a header frame
header_frame = ttk.Frame(root, padding="10")
header_frame.grid(row=0, column=0, sticky="ew")

# Add a title
title_label = ttk.Label(header_frame, text="Clash of Clans Builder Base Farming Bot", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

# Create a settings frame
settings_frame = ttk.LabelFrame(root, text="Settings", padding="10")
settings_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

# Add elixir frequency setting (row 0)
elixir_freq_label = ttk.Label(settings_frame, text="Check Elixir Every N Battles:")
elixir_freq_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

elixir_freq_entry = ttk.Entry(settings_frame, width=5)
elixir_freq_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
elixir_freq_entry.insert(0, str(elixir_check_frequency))

# Resolution info
resolution_label = ttk.Label(settings_frame, text=f"Screen Resolution: {screen_width}x{screen_height}, Using {'2K' if use_2k_images else 'FullHD'} Images")
resolution_label.grid(row=0, column=2, sticky="e", padx=5, pady=5)

# Add warplace attempts setting (row 1)
warplace_label = ttk.Label(settings_frame, text="Warplace Deployment Attempts:")
warplace_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
warplace_entry = ttk.Entry(settings_frame, width=5)
warplace_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
warplace_entry.insert(0, str(warplace_attempts))

# Add warplace description
warplace_help = ttk.Label(
    settings_frame, 
    text="(Number of times to try deploying troops at different warplaces)", 
    font=("Helvetica", 8), 
    foreground="grey"
)
warplace_help.grid(row=1, column=2, sticky="w", padx=5, pady=5)

# Add hero ability cooldown setting (row 3)
ability_cd_label = ttk.Label(settings_frame, text="Hero Ability Cooldown (s):")
ability_cd_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
ability_cd_entry = ttk.Entry(settings_frame, width=5)
ability_cd_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
ability_cd_entry.insert(0, str(ability_cooldown))

# Create a control frame
control_frame = ttk.Frame(root, padding="10")
control_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

# Add start button with custom style
start_button = tk.Button(
    control_frame, 
    text="Start Bot", 
    font=("Helvetica", 12, "bold"),
    bg="#4CAF50", 
    fg="white",
    activebackground="#45a049",
    activeforeground="white",
    width=15,
    height=2,
    command=start_bot
)
start_button.pack(side="left", padx=10)

# Add status label
status_label = ttk.Label(control_frame, text="Status: Not Running", font=("Helvetica", 10), foreground="red")
status_label.pack(side="left", padx=20)

# Create a log frame
log_frame = ttk.LabelFrame(root, text="Bot Log", padding="10")
log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

# Create a scrollable text widget for logs
log_text = tk.Text(log_frame, height=10, width=70, wrap=tk.WORD)
log_text.pack(side="left", fill="both", expand=True)

# Add a scrollbar to the log text
log_scroll = ttk.Scrollbar(log_frame, command=log_text.yview)
log_scroll.pack(side="right", fill="y")
log_text.config(yscrollcommand=log_scroll.set)


# Add some initial log messages
log_text.insert(tk.END, "Bot initialized and ready to start...\n")
log_text.insert(tk.END, "Please make sure Clash of Clans is running in fullscreen mode\n")
log_text.insert(tk.END, "and you are in the Builder Base before starting the bot.\n\n")
log_text.insert(tk.END, "⚠️ DISCLAIMER: Using automation tools may violate Supercell's Terms of Service.\n")
log_text.insert(tk.END, "This tool is for educational purposes only. Use at your own risk.\n")
log_text.see(tk.END)

# Add a footer with instructions
footer_frame = ttk.Frame(root, padding="10")
footer_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)

instructions_label = ttk.Label(
    footer_frame, 
    text="Instructions: Start the bot, then switch back to Clash of Clans within 3 seconds.",
    font=("Helvetica", 9, "italic")
)
instructions_label.pack()

# Start the UI main loop
root.mainloop()