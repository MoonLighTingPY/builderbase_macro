import requests
import webbrowser
import subprocess
import os
import sys
import json
import shutil
import time
from tkinter import messagebox
from packaging import version

# Track whether we're running from a PyInstaller bundle
def is_bundled():
    return getattr(sys, 'frozen', False)

def resource_path(relative_path):
    """Get absolute path to resource, works in development and PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_current_version():
    """Get current version from main module or use default"""
    try:
        # Try to import version from main module
        from main import APP_VERSION
        return APP_VERSION
    except ImportError:
        # Default if version cannot be imported
        return "1.0.0"

def check_for_updates(current_version=None):
    """
    Check GitHub for newer versions of the application
    Returns: (update_available, latest_version, download_url) tuple
    """
    if current_version is None:
        current_version = get_current_version()
        
    try:
        # GitHub API endpoint for releases
        api_url = "https://api.github.com/repos/MoonLighTingPY/builderbase_macro/releases/latest"
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            release_data = response.json()
            latest_version = release_data['tag_name']  # Get the tag name
            download_url = None
            
            # Find the .exe or .zip asset
            for asset in release_data['assets']:
                if asset['name'].endswith('.exe') or asset['name'].endswith('.zip'):
                    download_url = asset['browser_download_url']
                    break
            
            # Try to compare versions if they look like semantic versions
            try:
                # Remove 'v' prefix if present for comparison
                clean_latest = latest_version.lstrip('v')
                clean_current = current_version.lstrip('v')
                update_available = version.parse(clean_latest) > version.parse(clean_current)
            except Exception:
                # If version parsing fails, use release date as a fallback
                # A newer release is considered an update
                update_available = True
                print(f"Could not parse version {latest_version}, assuming update available")
            
            return update_available, latest_version, download_url
        
        return False, current_version, None
    
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, current_version, None
    


def download_and_install_update(download_url):
    """
    Download the update and prepare for installation
    """
    if not is_bundled():
        print("Auto-updates only work with compiled versions")
        return False
        
    try:
        # Create a temp directory for the download
        temp_dir = os.path.join(os.path.abspath("."), "update_temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Download file
        local_filename = os.path.join(temp_dir, "update.exe")
        response = requests.get(download_url, stream=True)
        
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Create a batch file to perform the update when the current process exits
        update_script = os.path.join(temp_dir, "update.bat")
        current_exe = sys.executable
        
        with open(update_script, 'w') as f:
            f.write(f'@echo off\n')
            f.write(f'echo Updating, please wait...\n')
            f.write(f'timeout /t 2 /nobreak > nul\n')  # Wait for the current process to exit
            f.write(f'copy /Y "{local_filename}" "{current_exe}"\n')
            f.write(f'start "" "{current_exe}"\n')
            f.write(f'rmdir /S /Q "{temp_dir}"\n')
        
        # Start the update script and exit the current application
        subprocess.Popen(['start', update_script], shell=True)
        return True
    
    except Exception as e:
        print(f"Error installing update: {e}")
        return False

def prompt_update(parent_window, latest_version, download_url):
    """
    Show dialog asking if user wants to update
    """
    result = messagebox.askyesno(
        "Update Available", 
        f"A new version ({latest_version}) is available. Would you like to update?",
        parent=parent_window
    )
    
    if result:
        # User wants to update
        if download_url.endswith('.exe'):
            # Direct executable download
            success = download_and_install_update(download_url)
            if success:
                messagebox.showinfo("Update", "Update downloading. The application will restart shortly.")
                return True
        else:
            # Open browser to download page
            webbrowser.open(download_url)
            messagebox.showinfo("Update", "Please download and install the update manually.")
    
    return False

def check_and_prompt_update(parent_window, show_latest_message=True):
    """Check for updates and prompt user if available"""
    current_version = get_current_version()
    update_available, latest_version, download_url = check_for_updates(current_version)
    
    if update_available and download_url:
        return prompt_update(parent_window, latest_version, download_url)
    elif show_latest_message:
        messagebox.showinfo("Updates", "You are using the latest version.", parent=parent_window, wait=True)
        messagebox.askyesno("Update Available", "...", parent=parent_window, wait=True)
    return False