

# ... باقي الكود ...
import asyncio
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog, Toplevel, StringVar, IntVar, Radiobutton, Listbox, Scrollbar, END, SINGLE  # Added ttk, Toplevel, etc.
import sqlite3
from datetime import datetime, timedelta, date
import telegram # Make sure 'python-telegram-bot' library is installed
from telegram.constants import ParseMode # <--- IMPORT ParseMode directly
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters # Ensure Application, CommandHandler etc. are imported
from telegram import Update
import threading

import inspect
import os
import sys
print("Python Executable:", sys.executable)
print("Python Version:", sys.version)
print("Python Path (sys.path):")
for p in sys.path:
    print(p)
print("-" * 30)
try:
    from PIL import Image, ImageTk # For JPG/PNG background
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logging.error("Pillow (PIL) library not found. JPG/PNG backgrounds may not work. Install with: pip install Pillow")
# ... plus other necessary imports like sqlite3, datetime, global variables for authenticate etc.
from hashlib import sha256
import time
import pandas as pd # Make sure 'pandas' and 'openpyxl' are installed for export
import logging
import queue
from tkinter import font as tkfont
try: # Keep direct import for try-except
    from playsound import playsound # Make sure 'playsound' is installed (and potentially platform-specific backend)
except ImportError:
    playsound = None 
import math 

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # sys._MEIPASS is not set; we are likely running in a normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
def prompt_login_modal(parent_window):
    """
    Shows a modal login dialog for user switching.
    Uses grab_set() for modality. Does NOT use transient().
    Returns the authenticated username on success, None otherwise.
    """
    logging.debug("[Full Login Dialog] Attempting to create dialog.")

    # 1. Check parent_window validity BEFORE creating Toplevel
    if not parent_window:
        logging.error("[Full Login Dialog] CRITICAL: parent_window is None. Cannot create Toplevel.")
        return None
    try:
        parent_exists = parent_window.winfo_exists()
        if not parent_exists:
            logging.error("[Full Login Dialog] CRITICAL: parent_window.winfo_exists() is False. Cannot create Toplevel.")
            return None
        logging.debug(f"[Full Login Dialog] Parent window '{parent_window}' exists.")
    except tk.TclError as e_parent:
        logging.error(f"[Full Login Dialog] CRITICAL: TclError checking parent_window existence: {e_parent}. Cannot create Toplevel.")
        return None

    # 2. Create Toplevel and log its path immediately
    try:
        login_dialog = Toplevel(parent_window)
        # If Toplevel() itself fails catastrophically, this log might not even be reached,
        # or login_dialog might not be a valid widget.
        logging.info(f"[Full Login Dialog] Toplevel object created: {login_dialog}. Path name: {login_dialog._w}")
    except Exception as e_toplevel_creation:
        logging.critical(f"[Full Login Dialog] CRITICAL: Error during Toplevel(parent_window) creation: {e_toplevel_creation}", exc_info=True)
        return None # Cannot proceed if Toplevel creation fails

    # 3. Attempt to set title, with detailed error logging
    try:
        # Before setting title, explicitly check if the newly created dialog path exists
        # This is a Tk call, similar to what .title() would do.
        # login_dialog.update_idletasks() # Try forcing Tk to process creation
        current_path_exists = login_dialog.winfo_exists() # This will make a Tcl call
        logging.debug(f"[Full Login Dialog] Path '{login_dialog._w}' exists according to winfo_exists() before title: {current_path_exists}")
        if not current_path_exists:
            logging.error(f"[Full Login Dialog] Path '{login_dialog._w}' reported as non-existent immediately after creation and before setting title!")
            # Attempt to destroy if it's in a weird state
            try: login_dialog.destroy()
            except: pass
            return None 

        login_dialog.title("Switch User - Login") 
        logging.debug(f"[Full Login Dialog] Title set for '{login_dialog._w}'.")
    except tk.TclError as e_title:
        # This is where your error is likely being caught now
        logging.critical(f"[Full Login Dialog] TclError setting title for path '{login_dialog._w if hasattr(login_dialog, '_w') else 'unknown'}': {e_title}", exc_info=True)
        # If title fails, the window object is bad. Try to destroy it.
        if isinstance(login_dialog, tk.Toplevel):
            try:
                logging.warning(f"[Full Login Dialog] Attempting to destroy problematic Toplevel '{login_dialog._w if hasattr(login_dialog, '_w') else 'unknown'}'.")
                login_dialog.destroy()
            except tk.TclError as e_destroy:
                logging.warning(f"[Full Login Dialog] Further TclError destroying problematic Toplevel: {e_destroy}")
        return None # Critical failure, cannot proceed with this dialog

    # If title setting succeeded, proceed with the rest of the dialog setup
    intended_w, intended_h = 350, 350
    login_dialog.geometry(f"{intended_w}x{intended_h}") # <<<--- EXPLICITLY SET SIZE HERE
    login_dialog.update_idletasks() # 
    # login_dialog.geometry(f"{intended_w}x{intended_h}") # Size is set later by centering usually

    login_dialog.resizable(False, False)
    login_dialog.grab_set()
    logging.info(f"[Full Login Dialog] grab_set() called for '{login_dialog._w}'.")

    result = {"username": None}
    dialog_fully_built = False

    # --- Centering Logic (keep the improved version) ---
    # ... (centering logic as before) ...
    try:
        login_dialog.update_idletasks() 
        # ... (rest of your centering logic)
        # Make sure this block also uses login_dialog._w if logging paths for consistency
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_w = parent_window.winfo_width()
        parent_h = parent_window.winfo_height()
        dialog_w = login_dialog.winfo_width()
        dialog_h = login_dialog.winfo_height()
        if not (dialog_w > 1 and dialog_h > 1 and parent_w > 1 and parent_h > 1):
            # If dialog_w/h are invalid here, it means initial geometry wasn't set or isn't effective yet.
            # We use intended_w/h for calculation but will apply the actual available dialog_w/h if possible.
            logging.debug(f"[Full Login Dialog] Using intended dimensions for parent centering calculation due to invalid initial dialog/parent dims. D:{dialog_w}x{dialog_h} P:{parent_w}x{parent_h}")
            calc_dialog_w, calc_dialog_h = intended_w, intended_h
        else:
            calc_dialog_w, calc_dialog_h = dialog_w, dialog_h

        x = parent_x + (parent_w // 2) - (calc_dialog_w // 2)
        y = parent_y + (parent_h // 2) - (calc_dialog_h // 2)
        
        # Re-fetch dialog_w/h if they were 0/1, now they might have values from packing widgets later
        # Or better, set geometry based on intended_w, intended_h as a base
        final_geom_w = dialog_w if dialog_w > 1 else intended_w
        final_geom_h = dialog_h if dialog_h > 1 else intended_h
        login_dialog.geometry(f"{final_geom_w}x{final_geom_h}+{x}+{y}")
        logging.debug(f"[Full Login Dialog] Centered on PARENT at +{x}+{y} with size {final_geom_w}x{final_geom_h}")

    except Exception as e_center_parent:
        logging.warning(f"[Full Login Dialog] Could not center on parent ({e_center_parent}). Attempting screen center.")
        try:
            login_dialog.update_idletasks()
            screen_w = login_dialog.winfo_screenwidth()
            screen_h = login_dialog.winfo_screenheight()
            current_dialog_w = login_dialog.winfo_width()
            current_dialog_h = login_dialog.winfo_height()
            final_dialog_w = current_dialog_w if current_dialog_w > 1 else intended_w
            final_dialog_h = current_dialog_h if current_dialog_h > 1 else intended_h
            if not (current_dialog_w > 1 and current_dialog_h > 1):
                 logging.info(f"[Full Login Dialog] Using intended dimensions ({intended_w}x{intended_h}) for screen centering.")
            x = (screen_w // 2) - (final_dialog_w // 2)
            y = (screen_h // 2) - (final_dialog_h // 2)
            login_dialog.geometry(f"{final_dialog_w}x{final_dialog_h}+{x}+{y}")
            logging.debug(f"[Full Login Dialog] Centered on SCREEN at +{x}+{y} with size {final_dialog_w}x{final_dialog_h}")
        except Exception as e_center_screen:
            logging.error(f"[Full Login Dialog] Error during final screen centering: {e_center_screen}")


    # --- Styling (same as your full dialog) ---
    # ... (styling code as before) ...
    style = ttk.Style(login_dialog) # Ensure style is configured for login_dialog
    style.theme_use('clam')
    dialog_bg = "#4a4a4a"
    # ... (rest of style definitions and configurations) ...
    text_fg = "#000000"
    entry_font = ('Segoe UI', 10)
    label_font = ('Segoe UI', 10)
    header_font = ('Segoe UI', 12, 'bold')
    button_font = ('Segoe UI', 10, 'bold')

    login_dialog.configure(background=dialog_bg)
    style.configure("DialogSwitch.TFrame", background=dialog_bg)
    style.configure("DialogSwitch.TLabel", background=dialog_bg, foreground=text_fg, font=label_font)
    style.configure("DialogSwitch.Header.TLabel", font=header_font, background=dialog_bg, foreground=text_fg)
    style.configure("DialogSwitch.TEntry", font=entry_font, fieldbackground="white")
    style.configure("DialogSwitch.TButton", font=button_font, padding=5)
    style.map("DialogSwitch.TButton",
              foreground=[('active', 'white'), ('!disabled', 'white')],
              background=[('active', '#005a9e'), ('!disabled', '#0078D7')])
    style.configure("Error.DialogSwitch.TLabel", background=dialog_bg, foreground="tomato", font=label_font)


    # --- Widgets (from your full dialog, wrapped in try-except) ---
    # ... (rest of the widget creation, event handlers, lift, wait_window, etc. as before) ...
    try:
        main_frame = ttk.Frame(login_dialog, padding="20 20 20 20", style="DialogSwitch.TFrame")
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="Enter New User Credentials", style="DialogSwitch.Header.TLabel").pack(pady=(0, 20))
        # ... (rest of your widgets and their .pack() calls)
        user_frame = ttk.Frame(main_frame, style="DialogSwitch.TFrame")
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Username:", width=10, anchor="w", style="DialogSwitch.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        username_entry_dialog = ttk.Entry(user_frame, width=25, style="DialogSwitch.TEntry")
        username_entry_dialog.pack(side=tk.LEFT, expand=True, fill=tk.X)

        pass_frame = ttk.Frame(main_frame, style="DialogSwitch.TFrame")
        pass_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pass_frame, text="Password:", width=10, anchor="w", style="DialogSwitch.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        password_entry_dialog = ttk.Entry(pass_frame, show="*", width=25, style="DialogSwitch.TEntry")
        password_entry_dialog.pack(side=tk.LEFT, expand=True, fill=tk.X)

        error_label_dialog = ttk.Label(main_frame, text="", style="Error.DialogSwitch.TLabel")
        error_label_dialog.pack(pady=(10,0))
        
        def attempt_switch_login_action():
            # ... (same as before)
            username = username_entry_dialog.get().strip()
            password = password_entry_dialog.get()
            authenticated_user = authenticate(username, password) 
            if authenticated_user:
                if ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP and \
                   authenticated_user == ADMIN_USERNAME:
                    pass 
                result["username"] = authenticated_user
                if login_dialog.grab_status(): login_dialog.grab_release()
                login_dialog.destroy()
            else:
                error_label_dialog.config(text="Invalid username or password.")
                password_entry_dialog.delete(0, tk.END)
                password_entry_dialog.focus_set()


        def on_cancel_switch_action():
            # ... (same as before)
            result["username"] = None
            if login_dialog.grab_status(): login_dialog.grab_release()
            login_dialog.destroy()


        password_entry_dialog.bind('<Return>', lambda event=None: attempt_switch_login_action())
        username_entry_dialog.bind('<Return>', lambda event=None: password_entry_dialog.focus())

        button_frame_dialog = ttk.Frame(main_frame, style="DialogSwitch.TFrame")
        button_frame_dialog.pack(pady=(20,0))

        login_button_dialog = ttk.Button(button_frame_dialog, text="Login", command=attempt_switch_login_action, style="DialogSwitch.TButton")
        login_button_dialog.pack(side=tk.LEFT, padx=10, ipadx=10)

        cancel_button_dialog = ttk.Button(button_frame_dialog, text="Cancel", command=on_cancel_switch_action, style="DialogSwitch.TButton")
        cancel_button_dialog.pack(side=tk.LEFT, padx=10, ipadx=10)

        login_dialog.protocol("WM_DELETE_WINDOW", on_cancel_switch_action)
        username_entry_dialog.focus_set()
        dialog_fully_built = True

    except Exception as e_widget_creation:
        logging.critical(f"[Full Login Dialog] CRITICAL ERROR creating widgets: {e_widget_creation}", exc_info=True)
        if login_dialog.grab_status(): login_dialog.grab_release() # Check grab before release
        try: login_dialog.destroy()
        except tk.TclError: pass
        return None 

    logging.debug(f"[Full Login Dialog] Configured. Attempting lift, topmost, focus. Fully built: {dialog_fully_built}")
    # ... (lift, topmost, focus_force, wait_window, cleanup as before)
    try:
        login_dialog.lift()
        login_dialog.attributes('-topmost', True) 
        login_dialog.focus_force()
        logging.debug("[Full Login Dialog] Called lift(), attributes(-topmost, True), and focus_force().")
    except tk.TclError as e_lift:
        logging.error(f"[Full Login Dialog] Error trying to lift/focus: {e_lift}")
    
    logging.info(f"[Full Login Dialog] About to call parent_window.wait_window() for: {login_dialog.title()}") # title() might fail if error occurred earlier
    # Check parent_window again before wait_window, just in case
    if not parent_window or not parent_window.winfo_exists():
        logging.error("[Full Login Dialog] Parent window became invalid before wait_window!")
        if login_dialog.grab_status(): login_dialog.grab_release()
        try: login_dialog.destroy()
        except tk.TclError: pass
        return None

    parent_window.wait_window(login_dialog) 
    logging.info(f"[Full Login Dialog] Returned from parent_window.wait_window() for path '{login_dialog._w if hasattr(login_dialog, '_w') else 'destroyed_dialog'}'")

    try:
        if login_dialog.winfo_exists(): # Should generally not exist if closed properly
             login_dialog.attributes('-topmost', False)
    except tk.TclError:
        pass 
    
    return result["username"]

# ... (Ensure CyberCafeApp.switch_user calls this prompt_login_modal)
# ... (rest of your CyberCafeApp class and other code)

# ... (rest of your CyberCafeApp class and other code, including the updated switch_user method)
# --- Logging Setup ---
# Improved format to include function name and make level DEBUG for more info during fixes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s')

# --- Activation Configuration ---
ACTIVATION_CODE = "hassancypersystem7777555"
ACTIVATION_FLAG_FILE = ".activated_cybercafe"

# --- Configuration & Constants ---
ADMIN_USERNAME = "admin"
ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP = "adminpass" # CHANGE THIS FOR PRODUCTION!

# Default item prices (Consider loading from config file/DB in future)
ITEM_PRICES = {
    "": 0, # Empty option should not be selectable, handle in UI
    "اندومي": 20,
    "شاي": 10,
    "قهوه": 20,
    "بيبسي": 20,
    # Add more items as needed
}
# Filter out the empty option for dropdowns
SELECTABLE_ITEMS = {k: v for k, v in ITEM_PRICES.items() if k}

# Devices (Consider loading from config file/DB in future)
# Ensure names match checks exactly (e.g., "PS 1" including space)
DEVICES = [f"PS {i}" for i in range(1, 7)]

# --- Device and Session Configuration ---
# This could be defined globally, in a config file, or when your app starts
# At the top of your x.py file (or in a dedicated config section)

# --- RATE DEFINITIONS ---
# (Keep your rate constants as they were in the corrected version)
# Rates (EGP per hour) - Updated as per request
RATE_PS_SINGLE_PER_HOUR = 20.0
RATE_PS_MULTI_PER_HOUR = 40.0
RATE_PINGPONG_STANDARD_PER_HOUR = 50.0
RATE_PINGPONG_MULTI_PER_HOUR = 80.0
RATE_BILLIARDS_STANDARD_PER_HOUR = 50.0
RATE_BILLIARDS_MULTI_PER_HOUR = 80.0
RATE_BABYFOOT_STANDARD_PER_HOUR = 20.0
PRICE_VR_SESSION = 15.0

DEVICE_CONFIG = {
    "PlayStation": {
        "name_template": "PS{}",  # For names like PS1, PS2
        "category": "Gaming Console",
        "session_options": {
            # Option Name: {type, rate_per_hour/price}
            "Single Player": {"type": "time_based", "rate_per_hour": 20.0},
            "Multiplayer": {"type": "time_based", "rate_per_hour": 40.0}
        }
    },
    "PingPong": {
        "name_template": "PingPong{}",
        "category": "Table Game",
        "session_options": {
            "Standard": {"type": "time_based", "rate_per_hour": 50.0},
            "Multiplayer": {"type": "time_based", "rate_per_hour": 80.0}
        }
    },
    "Billiards": {
        "name_template": "Billiards{}",
        "category": "Table Game",
        "session_options": { # Same as Ping Pong
            "Standard": {"type": "time_based", "rate_per_hour": 50.0},
            "Multiplayer": {"type": "time_based", "rate_per_hour": 80.0}
        }
    },
    "BabyFoot": { # "Baby Hat" likely means Baby Foot (Foosball)
        "name_template": "BabyFoot{}",
        "category": "Table Game",
        "session_options": {
            # User mentioned "20 PER HOUR SINGLE OT MULTI" - one rate for standard play
            "Standard": {"type": "time_based", "rate_per_hour": 20.0}
        }
    },
    "VR": {
        "name_template": "VR{}",
        "category": "Virtual Reality",
        "session_options": {
            # User mentioned "THE SESSION = 15 LE WHAT EVER TIME" - fixed price
            "Fixed Session": {"type": "fixed_fee", "price": 15.0}
        }
    }
}

# Defines which devices appear on which page and how many
DEVICES_PAGES_SETUP = {
    "Page 1 (Gaming & Tables)": [ # Tab title
        # (Device Type from DEVICE_CONFIG, count)
        ("PlayStation", 3),
        ("PingPong", 1),
        ("Billiards", 1)
    ],
    "Page 2 (Fun Zone)": [
        ("BabyFoot", 2),
        ("VR", 2)
    ]
}
# (Your DEVICE_CONFIG and DEVICES_PAGES_SETUP are assumed to be defined above this)

# This is a hypothetical dictionary to store the full data for each device instance
# Your application will have something similar to hold the state and properties of each device.
ALL_ACTIVE_DEVICES = {}

def initialize_device_instances():
    """
    Populates ALL_ACTIVE_DEVICES with data for each device instance,
    crucially including 'device_category'.
    """
    global ALL_ACTIVE_DEVICES
    ALL_ACTIVE_DEVICES = {} # Reset if re-initializing

    print("Attempting to initialize all device instances...")
    for _page_name, devices_on_page in DEVICES_PAGES_SETUP.items():
        for device_type_key, count in devices_on_page:
            # device_type_key would be "PlayStation", "BabyFoot", etc.
            
            if device_type_key not in DEVICE_CONFIG:
                print(f"  [WARNING] Device type '{device_type_key}' from PAGES_SETUP not in DEVICE_CONFIG. Skipping.")
                continue

            config_for_this_type = DEVICE_CONFIG[device_type_key]
            name_template = config_for_this_type.get("name_template")
            
            # --- THIS IS THE CRITICAL STEP for 'device_category' ---
            device_category_value = config_for_this_type.get("device_category")
            # --- --- --- --- --- --- --- --- --- --- --- --- --- ---

            if not name_template:
                print(f"  [WARNING] 'name_template' missing for '{device_type_key}' in DEVICE_CONFIG. Skipping instances.")
                continue
            
            # Check if device_category was actually found in DEVICE_CONFIG for this type
            if device_category_value is None:
                print(f"  [ERROR_IN_CONFIG] 'device_category' is missing or None for device type '{device_type_key}' in DEVICE_CONFIG. Check your DEVICE_CONFIG.")
                # Based on your provided DEVICE_CONFIG, this should not happen, as 'device_category' is present.
                # This check is mostly for robustness if DEVICE_CONFIG were malformed.
                continue

            for i in range(1, count + 1):
                instance_name = name_template.format(i) # e.g., "PS1", "BabyFoot1"
                
                # Store all relevant data for this specific instance
                ALL_ACTIVE_DEVICES[instance_name] = {
                    "device_name": instance_name,
                    "device_type": device_type_key, # e.g., "PlayStation"
                    
                    # ---- ENSURE 'device_category' IS STORED FOR THE INSTANCE ----
                    "device_category": device_category_value, 
                    # -------------------------------------------------------------
                    
                    "status": "available", # Default status
                    "session_options": config_for_this_type.get("session_options", {}),
                    # Add any other properties the instance might need from config_for_this_type
                }
                print(f"  Initialized: {instance_name} (Type: {device_type_key}) -> Category: '{device_category_value}'")
    
    print(f"Initialization complete. Total devices loaded: {len(ALL_ACTIVE_DEVICES)}")
    if "PS1" in ALL_ACTIVE_DEVICES:
        print(f"  Data for PS1 after init: {ALL_ACTIVE_DEVICES['PS1']}")
    if "BabyFoot1" in ALL_ACTIVE_DEVICES:
        print(f"  Data for BabyFoot1 after init: {ALL_ACTIVE_DEVICES['BabyFoot1']}")


# --- Somewhere in your application startup ---
# initialize_device_instances()


# --- Then, your start_session function would look something like this (simplified) ---
# def start_session(device_name, session_details_from_ui):
#     # This function is where your error log originates
#     print(f"Attempting start_session for device: {device_name}")

#     if device_name not in ALL_ACTIVE_DEVICES:
#         # Log error: device not found
#         print(f"  [ERROR] Device '{device_name}' not found in ALL_ACTIVE_DEVICES.")
#         return

#     device_instance_data = ALL_ACTIVE_DEVICES[device_name]
    
#     # ---- DEBUGGING STEP: Print the data for the specific device here ----
#     print(f"  Data retrieved for '{device_name}': {device_instance_data}") # VERY IMPORTANT DEBUG STEP
#     # --------------------------------------------------------------------

#     # The code then tries to access 'device_category'
#     # If it's missing from device_instance_data, you get the error.
#     if "device_category" not in device_instance_data:
#         actual_error_details = {
#             # ... reconstruct details similar to your log ...
#         }
#         print(f"  [ERROR_RUNTIME] - [start_session] - START_SESSION_ERROR: 'device_category' missing for {device_name}. Details: {actual_error_details}")
#         return False # Session start failed
    
#     category = device_instance_data["device_category"]
#     print(f"  Successfully found device_category: '{category}' for {device_name}")
#     # ... proceed with starting the session ...
#     return True
# ... (rest of your x.py file)
# Database
DB_NAME = "cyber_cafe.db"
# Database
DB_NAME = "cyber_cafe.db"

# --- Sound Configuration ---
END_SOUND_FILE = "end_session_sound.wav" # Make sure this file exists in the same directory
SOUND_ENABLED = False
sound_thread = None # To manage the sound playing thread
# VVentinganV IMPORTANT: DEFINE REDEEM_OPTIONS HERE VVentinganV
REDEEM_OPTIONS = {
    "30 دقيقة هدية (وقت مجاني)": (30, 120),  # 30 minutes free time for 120 points
    # You can add more options here if you like:
    # "ساعة هدية (60 دقيقة)": (60, 240), # Example: 1 hour for 240 points (maintaining 120pts/30min rate)
    # "15 دقيقة هدية": (15, 60),         # Example: 15 minutes for 60 points
}
# --- Telegram Configuration (Use Environment Variables or Secure Config!) ---
# ---> BEST PRACTICE: Set these as environment variables on your system <---
# Example: export CYBERCAFE_BOT_TOKEN="1234567890:ABCdE..."
#          export CYBERCAFE_CHAT_ID="-1001234567890"
#          export TELEGRAM_PARSE_MODE="MarkdownV2" # Or "HTML", or leave unset for plain text

BOT_TOKEN = os.environ.get('CYBERCAFE_BOT_TOKEN', '7732883043:AAEwoLAUQBrbx-yFlBF8L0PhliKjb_7OgaU') # <--- REPLACE if not using Env Var
CHAT_ID = os.environ.get('CYBERCAFE_CHAT_ID', '6325158235') # <--- REPLACE if not using Env Var (Remember '-' for groups/channels)
TELEGRAM_PARSE_MODE = os.environ.get('TELEGRAM_PARSE_MODE', None) # Options: "MarkdownV2", "HTML", or None

# Validate and Log Configuration
_telegram_enabled = True
if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE' or not BOT_TOKEN:
    logging.warning("Telegram BOT_TOKEN is using the default placeholder or is missing. Set Environment Variable or Replace in code. Telegram Disabled.")
    BOT_TOKEN = None
    _telegram_enabled = False
if CHAT_ID == 'YOUR_CHAT_ID_HERE' or not CHAT_ID:
     logging.warning("Telegram CHAT_ID is using the default placeholder or is missing. Set Environment Variable or Replace in code. Telegram Disabled.")
     CHAT_ID = None
     _telegram_enabled = False
if _telegram_enabled: # Only validate parse mode if bot is potentially enabled
    if TELEGRAM_PARSE_MODE and TELEGRAM_PARSE_MODE not in ["MarkdownV2", "HTML"]:
        logging.warning(f"Invalid TELEGRAM_PARSE_MODE '{TELEGRAM_PARSE_MODE}'. Should be 'MarkdownV2', 'HTML', or None. Disabling parse_mode.")
        TELEGRAM_PARSE_MODE = None
    elif TELEGRAM_PARSE_MODE:
         logging.info(f"Telegram parse_mode enabled: {TELEGRAM_PARSE_MODE}")
         # IMPORTANT: If using MarkdownV2 or HTML, ensure messages sent via
         # send_telegram_message() are correctly formatted and escaped in the
         # main application code where those messages are constructed!

# --- Global Runtime Variables (Minimize usage where possible) ---
bot = None # Telegram bot instance
telegram_loop = None # Asyncio event loop for Telegram
telegram_thread = None # Thread running the Telegram loop
app_instance = None # Global reference to the main app instance
current_user = None # Stores the logged-in username ("admin" or employee username)
TELEGRAM_ACTION_QUEUE = queue.Queue() # <--- ADD THIS SHARED QUEUE
# --- Telegram Bot Initialization and Sending (Updated) ---
# --- Define Constants (preferably at the top of your script or in a config section) ---
ACTION_REMOTE_NEW_SESSION = "REMOTE_NEW_SESSION"
# Add other action types if you have them:
# ACTION_REMOTE_END_SESSION = "REMOTE_END_SESSION"

TIME_OPTION_OPEN = "Open Session"
TIME_OPTION_30_MIN = "30 Minutes"
TIME_OPTION_1_HOUR = "1 Hour"
TIME_OPTION_2_HOURS = "2 Hours"
TIME_OPTION_MANUAL = "Manual Time" # For when minutes are specified
async def _send_message_via_app_bot(app_bot_instance, message_text_to_send, target_chat_id_param=None):
    """Internal async function to send messages using the PTB Application's bot."""
    final_chat_id = target_chat_id_param if target_chat_id_param else CHAT_ID # Use global CHAT_ID if no target

    if app_bot_instance and final_chat_id and _telegram_enabled:
        try:
            message_str = str(message_text_to_send)
            if len(message_str) > 4096: # Telegram message length limit
                logging.warning("Truncating long message for Telegram.")
                message_str = message_str[:4090] + "..."
            
            send_args = {
                'chat_id': final_chat_id,
                'text': message_str,
                'read_timeout': 20, # seconds
                'write_timeout': 20 # seconds
            }
            current_tg_parse_mode = None
            if TELEGRAM_PARSE_MODE == "MarkdownV2":
                current_tg_parse_mode = ParseMode.MARKDOWN_V2
            elif TELEGRAM_PARSE_MODE == "HTML":
                current_tg_parse_mode = ParseMode.HTML
            if current_tg_parse_mode:
                send_args['parse_mode'] = current_tg_parse_mode

            await app_bot_instance.send_message(**send_args)
            logging.debug(f"Telegram message sent successfully to {final_chat_id}: {message_str[:50]}...")
        except Exception as e:
            logging.error(f"Error sending Telegram message to {final_chat_id} via PTB App: {e}", exc_info=True)
    elif not _telegram_enabled:
        logging.debug(f"Telegram sending skipped to {final_chat_id}: Telegram is disabled.")
    else:
        logging.warning(f"Telegram sending skipped to {final_chat_id}: Bot not ready or chat ID missing.")


def send_telegram_message(message_to_send, target_chat_id=None): # Added target_chat_id
    """Public function to send a message using the PTB Application's event loop."""
    global bot, ptb_event_loop, _telegram_enabled
    
    final_chat_id_for_check = target_chat_id if target_chat_id else CHAT_ID
    is_loop_running = ptb_event_loop.is_running() if ptb_event_loop else False

    logging.debug(
            f"Attempting to send Telegram message to {final_chat_id_for_check}. "
            f"_telegram_enabled: {_telegram_enabled}, bot: {bool(bot)}, loop_running: {is_loop_running}"
    )

    if bot and ptb_event_loop and is_loop_running and final_chat_id_for_check and _telegram_enabled:
        import asyncio 
        asyncio.run_coroutine_threadsafe(
            _send_message_via_app_bot(bot, message_to_send, target_chat_id), # Pass target_chat_id here
            ptb_event_loop
        )
    else:
        if not _telegram_enabled:
            logging.info(f"Telegram is disabled (_telegram_enabled is False), not sending message to {final_chat_id_for_check}.")
        else:
            logging.warning(
                f"Telegram bot/loop not ready for sending message to {final_chat_id_for_check}. Conditions: "
                f"bot_instance_exists={bool(bot)}, loop_running={is_loop_running}, "
                f"CHAT_ID_present={bool(final_chat_id_for_check)}, _telegram_enabled={_telegram_enabled}"
            )
# LOCATED IN: Global scope, near other Telegram command handlers

# Ensure these global variables are accessible here if needed for validation/queueing
# global TELEGRAM_ACTION_QUEUE, app_instance, DEVICES, current_user 
# (current_user is from the Tkinter app's perspective)

async def remote_new_session_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    logging.info(f"!!!!!! /newsession command handler ENTERED by user {update.effective_user.id} !!!!!!")
    logging.info(f"!!!!!! Received args: {context.args}")
    logging.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    # These globals are needed within this function
    global TELEGRAM_ACTION_QUEUE, app_instance, DEVICES, current_user 

    chat_id_telegram = update.effective_chat.id 
    telegram_user_id = update.effective_user.id
    logging.info(f"/newsession command received from Telegram User ID: {telegram_user_id}, Chat ID: {chat_id_telegram}")

    # --- BASIC AUTHORIZATION (EXAMPLE) ---
    # Replace with your actual list of trusted Telegram user IDs
    # TRUSTED_TELEGRAM_USER_IDS = [123456789, 987654321] 
    # if telegram_user_id not in TRUSTED_TELEGRAM_USER_IDS:
    #     logging.warning(f"Unauthorized attempt to use /newsession by Telegram User ID: {telegram_user_id}")
    #     await update.message.reply_text("⚠️ You are not authorized to use this command.", quote=True)
    #     return
    # --- END BASIC AUTHORIZATION ---

    if not (app_instance and hasattr(app_instance, 'root') and app_instance.root.winfo_exists()):
        await update.message.reply_text("⚠️ CyberCafe system (GUI) is not active. Please try again later.", quote=True)
        return
        
    if not TELEGRAM_ACTION_QUEUE:
        logging.error("TELEGRAM_ACTION_QUEUE is not initialized.")
        await update.message.reply_text("⚠️ System error: Action queue not available.", quote=True)
        return

    if not current_user: 
        await update.message.reply_text("⚠️ No employee is currently logged into the CyberCafe system's main application. Cannot start session remotely.", quote=True)
        return

    args = context.args
    if len(args) < 3:
        valid_devices_str = ", ".join(DEVICES) if DEVICES else "None configured"
        reply_text = (
            "Insufficient arguments. Usage:\n"
            "`/newsession <Device> <Type> <Time> [Customer] [BonusCode]`\n\n"
            "*Device*: e.g., `PS1`\n"
            "*Type*: `Single` or `Multiplayer`\n"
            "*Time*: `Open`, `30Min`, `1Hour`, `2Hours`, or minutes (e.g., `60`)\n"
            "*Customer* (Optional): e.g., `Hassan`\n"
            "*BonusCode* (Optional): e.g., `CODE123`\n\n"
            "Example:\n`/newsession PS1 Single 60 Hassan CODE123`\n\n"
            f"Valid devices: {valid_devices_str}"
        )
        await update.message.reply_text(reply_text, parse_mode='MarkdownV2', quote=True)
        return

    device_name_arg = args[0].upper()
    if not " " in device_name_arg and "PS" in device_name_arg and len(device_name_arg) > 2: # e.g. PS1 -> PS 1
        device_name_arg = device_name_arg.replace("PS", "PS ")
        
    session_type_arg = args[1].capitalize() 
    time_input_arg = args[2] 

    # Basic parsing for customer and bonus code (can be improved for names with spaces)
    customer_name_str = args[3] if len(args) > 3 else None
    bonus_code_str = args[4].upper() if len(args) > 4 else None
    if len(args) > 5: # Crude attempt to capture multi-word customer name if bonus is last
        customer_name_str = " ".join(args[3:-1])
        bonus_code_str = args[-1].upper()


    # --- Parameter Validation ---
    actual_device_name = None
    for dev_in_list in DEVICES: # DEVICES should be your global list
        if dev_in_list.upper() == device_name_arg:
            actual_device_name = dev_in_list
            break
    if not actual_device_name:
        await update.message.reply_text(f"⚠️ Invalid device: `{args[0]}`. Valid: {', '.join(DEVICES)}", parse_mode='MarkdownV2', quote=True)
        return

    if session_type_arg not in ["Single", "Multiplayer"]:
        await update.message.reply_text("⚠️ Invalid session type. Use 'Single' or 'Multiplayer'.", quote=True)
        return

    time_option_for_payload = "Open Session"
    manual_minutes_for_payload = None

    if time_input_arg.lower() == "open":
        time_option_for_payload = "Open Session"
    elif time_input_arg.lower() == "30min":
        time_option_for_payload = "30 Minutes"
    elif time_input_arg.lower() == "1hour":
        time_option_for_payload = "1 Hour"
    elif time_input_arg.lower() == "2hours":
        time_option_for_payload = "2 Hours"
    else:
        try:
            manual_minutes_val = int(time_input_arg)
            if manual_minutes_val <= 0:
                await update.message.reply_text("⚠️ Manual time (minutes) must be > 0.", quote=True)
                return
            time_option_for_payload = "Manual Time"
            manual_minutes_for_payload = manual_minutes_val
        except ValueError:
            await update.message.reply_text("⚠️ Invalid time option. Use Open, 30Min, 1Hour, 2Hours, or minutes.", quote=True)
            return

    session_action_payload = {
        "action_type": "REMOTE_NEW_SESSION",
        "device_name": actual_device_name,
        "session_type": session_type_arg,
        "time_option_str": time_option_for_payload,
        "manual_minutes_val": manual_minutes_for_payload,
        "customer_name_str": customer_name_str,
        "bonus_code_str": bonus_code_str,
        "reply_chat_id": chat_id_telegram
    }

    TELEGRAM_ACTION_QUEUE.put(session_action_payload)
    logging.info(f"REMOTE_NEW_SESSION request queued: {session_action_payload}")
    await update.message.reply_text(f"✅ Request to start session on `{actual_device_name}` for `{time_option_for_payload}` received. Processing...", parse_mode='MarkdownV2', quote=True)
def initialize_telegram_bot():
    global bot, telegram_thread, _telegram_enabled, ptb_application, ptb_event_loop
    if 'remote_new_session_command_handler' in globals() and callable(globals()['remote_new_session_command_handler']):
        ptb_application.add_handler(CommandHandler("newsession", remote_new_session_command_handler))
        logging.info("Added /newsession command handler to Telegram bot.")
    else:
        logging.warning("Global function 'remote_new_session_command_handler' not found. /newsession command will not work.")
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logging.warning("Telegram BOT_TOKEN is missing or default. Telegram Bot functions disabled.")
        _telegram_enabled = False
        bot = None
        ptb_application = None
        return

    try:
        # Build the PTB Application for command handling and more
        ptb_application = Application.builder().token(BOT_TOKEN).build()
        ptb_event_loop = ptb_application.loop # Store the asyncio event loop PTB uses
        
        # Assign the bot instance from the application for sending messages
        bot = ptb_application.bot 
        logging.info("python-telegram-bot Application and bot instance created.")

        # Add command handlers
        ptb_application.add_handler(CommandHandler("start", start_command_handler))
        ptb_application.add_handler(CommandHandler("checkout", checkout_command_handler))
        # ... add other command handlers here if needed ...

        # Add an error handler
        ptb_application.add_error_handler(telegram_error_handler)

        # Start the bot polling in a new thread
        if telegram_thread is None or not telegram_thread.is_alive():
            telegram_thread = threading.Thread(target=ptb_application.run_polling, name="TelegramBotPollingThread", daemon=True)
            telegram_thread.start()
            logging.info("Telegram bot application started polling in a new thread.")
            
            # Send a startup message (uses the new send_telegram_message)
            if CHAT_ID:
                 send_telegram_message("🟢 CyberCafe system connected. Bot is ready for commands.")
        else:
            logging.info("Telegram bot application polling thread already running.")
        _telegram_enabled = True # Explicitly set if setup is successful

    except telegram.error.InvalidToken as e:
        logging.error(f"Invalid Telegram BOT_TOKEN provided: {e}. Telegram disabled.")
        bot = None
        ptb_application = None
        _telegram_enabled = False
    except Exception as e:
        logging.error(f"Failed to initialize Telegram bot application: {e}", exc_info=True)
        # bot might still be None or an old instance if only ptb_application failed
        ptb_application = None
        _telegram_enabled = False


# --- Sound Check ---
if playsound: # Check if playsound was imported successfully
    try:
        # Check if file exists *before* attempting to use playsound fully
        if os.path.exists(END_SOUND_FILE):
            SOUND_ENABLED = false
            logging.info(f"Sound notifications enabled. Using: {END_SOUND_FILE}")
        else:
            logging.warning(f"Warning: Sound file '{END_SOUND_FILE}' not found. Sound notifications will be disabled.")
            SOUND_ENABLED = False # Explicitly disable if file not found
    except Exception as e:
        logging.error(f"Error checking sound setup: {e}", exc_info=True)
        SOUND_ENABLED = False
else:
    logging.warning("Warning: 'playsound' library not found or failed to import. Sound notifications will be disabled.")
    logging.warning("Install using: pip install playsound")
    SOUND_ENABLED = False

# --- Activation Check Logic ---
def check_activation_status():
    """Checks if the activation flag file exists."""
    return os.path.exists(ACTIVATION_FLAG_FILE)

def perform_activation_prompt():
    """Prompts for activation code if needed. Returns True if activated/successful."""
    if check_activation_status():
        logging.info("Application previously activated.")
        return True

    temp_root = tk.Tk()
    temp_root.withdraw()

    logging.info("Activation required.")
    messagebox.showinfo("Activation Required",
                        "This application requires one-time activation.",
                        parent=temp_root)

    entered_code = simpledialog.askstring("Activation",
                                          "Please enter the activation code:",
                                          show='*', # Hide input
                                          parent=temp_root)

    activation_successful = False
    if entered_code == ACTIVATION_CODE:
        try:
            with open(ACTIVATION_FLAG_FILE, 'w') as f:
                pass # Create the file
            logging.info(f"Activation successful. Flag file '{ACTIVATION_FLAG_FILE}' created.")
            messagebox.showinfo("Activation Success",
                                "Application activated successfully!",
                                parent=temp_root)
            activation_successful = True
        except IOError as e:
            logging.error(f"Failed to create activation flag file: {e}", exc_info=True)
            messagebox.showerror("Activation Error",
                                 f"Could not create activation file '{ACTIVATION_FLAG_FILE}'.\nCheck permissions.\nError: {e}",
                                 parent=temp_root)
        except Exception as e:
            logging.error(f"Unexpected error during activation file creation: {e}", exc_info=True)
            messagebox.showerror("Activation Error", f"An unexpected error occurred: {e}", parent=temp_root)

    elif entered_code is None: # User cancelled
        logging.warning("Activation cancelled by user.")
        messagebox.showwarning("Activation Cancelled", "Activation was cancelled. Exiting.", parent=temp_root)
    else: # Invalid code
        logging.warning("Invalid activation code entered.")
        messagebox.showerror("Activation Failed", "Invalid activation code.", parent=temp_root)

    temp_root.destroy()
    return activation_successful

# --- Hashing Utility ---
def hash_password(password):
    """Hashes the given password using SHA256."""
    if not password: return None
    return sha256(password.encode('utf-8')).hexdigest()

def verify_password(stored_hash, provided_password):
    """Verifies a provided password against a stored hash."""
    if not stored_hash or not provided_password: return False
    return stored_hash == hash_password(provided_password)

# --- Telegram Async Helper ---
def start_telegram_event_loop():
    global telegram_loop
    try:
        telegram_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(telegram_loop)
        logging.info("Telegram event loop starting.")
        telegram_loop.run_forever()
    except Exception as e:
        logging.error(f"Critical Error in Telegram event loop: {e}", exc_info=True)
    finally:
        logging.info("Telegram event loop run_forever finished.")
        if telegram_loop and telegram_loop.is_running():
            logging.warning("Event loop finished run_forever but is still running? Attempting shutdown.")
            try:
                telegram_loop.run_until_complete(telegram_loop.shutdown_asyncgens())
            except Exception as e_shutdown:
                logging.error(f"Error during telegram loop asyncgen shutdown: {e_shutdown}", exc_info=True)

        if telegram_loop:
            try:
                tasks = asyncio.all_tasks(loop=telegram_loop)
                if tasks:
                    logging.info(f"Cancelling {len(tasks)} outstanding Telegram tasks...")
                    for task in tasks:
                        task.cancel()
                    telegram_loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
                    logging.info("Outstanding Telegram tasks cancelled.")
            except Exception as e_cancel:
                logging.error(f"Error cancelling Telegram tasks: {e_cancel}", exc_info=True)

            if not telegram_loop.is_closed():
                telegram_loop.close()
                logging.info("Telegram event loop closed.")
        telegram_loop = None # Ensure it's reset

def stop_telegram_event_loop():
    """Thread-safe request to stop the Telegram event loop."""
    if telegram_loop and telegram_loop.is_running():
        logging.info("Requesting Telegram event loop stop...")
        telegram_loop.call_soon_threadsafe(telegram_loop.stop)
    elif telegram_loop:
        logging.info("Telegram event loop exists but is not running.")
    else:
        logging.info("No Telegram event loop to stop.")

def run_async_from_thread(coro):
    """Schedules a coroutine to run on the Telegram event loop thread."""
    future = None
    if telegram_loop and telegram_loop.is_running():
        try:
            future = asyncio.run_coroutine_threadsafe(coro, telegram_loop)
            def handle_future_exception(f):
                try:
                    if f.cancelled(): return
                    exc = f.exception()
                    if exc:
                        logging.error(f"Async Telegram task failed: {exc}", exc_info=True) # Log full traceback
                except Exception as cb_exc:
                    logging.error(f"Error in Telegram future callback: {cb_exc}", exc_info=True)
            future.add_done_callback(handle_future_exception)
        except Exception as e:
             logging.error(f"Error scheduling async task: {e}", exc_info=True)
    else:
        logging.warning("Telegram event loop not running. Cannot schedule async task.")
    return future

# --- Telegram Bot Initialization and Sending ---
def initialize_telegram_bot():
    global bot, telegram_thread, _telegram_enabled # Ensure flag is global if modified here
    if not _telegram_enabled: # Use the flag set during config validation
        logging.warning("Telegram notifications disabled due to missing/invalid configuration.")
        bot = None
        return

    try:
        if not BOT_TOKEN or ':' not in BOT_TOKEN:
             raise telegram.error.InvalidToken("Token format appears invalid (missing ':' or token is empty).")

        bot = telegram.Bot(token=BOT_TOKEN)
        logging.info("Telegram bot object created.")

        if telegram_thread is None or not telegram_thread.is_alive():
            telegram_thread = threading.Thread(target=start_telegram_event_loop, name="TelegramLoopThread", daemon=True)
            telegram_thread.start()
            logging.info("Telegram event loop thread started.")
            time.sleep(0.5) # Give the loop a moment to potentially start running

            future = run_async_from_thread(_send_message_async("🟢 CyberCafe system connected."))
            if future:
                try:
                    future.result(timeout=15)
                    logging.info("Telegram test message sent successfully.")
                except asyncio.TimeoutError:
                    logging.warning("Timeout waiting for Telegram test message result. Check network/token/chat_id.")
                except Exception as test_e:
                    logging.error(f"Error occurred during Telegram test message sending: {test_e}", exc_info=False)
        else:
            logging.info("Telegram event loop thread already running.")

    except telegram.error.InvalidToken as e:
        logging.error(f"Invalid Telegram BOT_TOKEN provided: {e}. Please check your token. Telegram disabled.")
        bot = None
        _telegram_enabled = False
    except Exception as e:
        logging.error(f"Failed to initialize Telegram bot: {e}", exc_info=True)
        bot = None
        _telegram_enabled = False


async def _send_message_async(message):
    """Internal async function to send messages with timeouts and error handling."""
    if bot and CHAT_ID and _telegram_enabled:
        try:
            message_str = str(message)
            if len(message_str) > 4096:
                logging.warning("Truncating long message for Telegram.")
                message_str = message_str[:4090] + "..."

            send_args = {
                'chat_id': CHAT_ID,
                'text': message_str,
                'read_timeout': 20,
                'write_timeout': 20
            }
            current_parse_mode = None
            if TELEGRAM_PARSE_MODE == "MarkdownV2":
                current_parse_mode = ParseMode.MARKDOWN_V2
            elif TELEGRAM_PARSE_MODE == "HTML":
                current_parse_mode = ParseMode.HTML

            if current_parse_mode:
                send_args['parse_mode'] = current_parse_mode

            await asyncio.wait_for(
                bot.send_message(**send_args),
                timeout=30.0
            )
            logging.debug(f"Telegram message sent successfully: {message_str[:50]}...")
        except asyncio.TimeoutError:
            logging.error("Error sending Telegram message: Timeout.")
        except telegram.error.NetworkError as e:
            logging.error(f"Telegram Network error sending message: {e}")
        except telegram.error.BadRequest as e:
             logging.error(f"Telegram Bad Request error (check CHAT_ID, message format, or parse_mode issues): {e}")
        except telegram.error.ChatMigrated as e:
             logging.error(f"Telegram Chat ID migrated. New ID: {e.new_chat_id}. Please update CHAT_ID.")
        except telegram.error.Forbidden as e:
             logging.error(f"Telegram Forbidden error (Bot blocked or kicked from chat?): {e}")
        except telegram.error.TelegramError as e:
            logging.error(f"Generic Telegram API error sending message: {e}")
        except Exception as e:
            logging.error(f"Unexpected error sending Telegram message via async task: {e}", exc_info=True)
    else:
        if _telegram_enabled:
            logging.debug("Skipping Telegram send: Bot not initialized or CHAT_ID missing.")

def send_telegram_message(message):
    """Public function to send a message using the running Telegram event loop."""
    if bot and telegram_loop and telegram_loop.is_running() and CHAT_ID and _telegram_enabled:
        run_async_from_thread(_send_message_async(message))


# --- Database Setup & Admin Creation ---
# -*- coding: utf-8 -*-
# ... (جميع الـ imports التي لديك بالأعلى، تأكد من وجود import sqlite3, logging, datetime)
# from datetime import datetime
# import logging
# import sqlite3

# ... (الثوابت مثل DB_NAME, ADMIN_USERNAME, ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP يجب أن تكون مُعرفة)
# ... (الدالة hash_password يجب أن تكون مُعرفة)

# --- Database Setup & Admin Creation (Modified for Bonus Points & Expenses) ---
def setup_database():
    """Initializes the database schema and ensures the admin user exists."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME) # DB_NAME should be globally defined
        cursor = conn.cursor()

        # جدول الجلسات - مع إضافة حقول جديدة
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                device TEXT NOT NULL, 
                customer TEXT,
                start_time TEXT NOT NULL, 
                end_time TEXT, 
                duration REAL, 
                cost REAL,
                session_type TEXT, 
                shift_employee TEXT NOT NULL, 
                item_cost REAL DEFAULT 0.0, 
                drinks TEXT DEFAULT '', 
                time_option TEXT,
                bonus_code_used TEXT,                 -- NEW
                points_earned_this_session INTEGER DEFAULT 0, -- NEW
                is_free_session BOOLEAN DEFAULT 0,    -- NEW
                redeemed_points_for_session INTEGER DEFAULT 0 -- NEW
            )""")

        # جدول الموظفين - كما هو
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT UNIQUE NOT NULL, 
                password TEXT NOT NULL
            )""")

        # --- NEW TABLES ---
        # جدول أكواد النقاط
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bonus_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT 0, -- 0: غير مباع/غير نشط, 1: مباع/نشط جاهز للاستخدام
                purchase_price REAL DEFAULT 5.0, 
                sold_by_employee TEXT,
                sold_at TEXT,
                linked_customer_name TEXT,
                session_id_earned_on INTEGER, -- معرّف الجلسة التي تم كسب نقاط بها بهذا الكود (إذا كان الكود يستخدم مرة واحدة لكسب النقاط)
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")

        # جدول نقاط العملاء
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT UNIQUE NOT NULL, -- يجب أن يكون اسم العميل مميزًا
                points INTEGER DEFAULT 0
            )""")
            
        # جدول مصروفات الوردية
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shift_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                employee_username TEXT NOT NULL,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
        
        conn.commit()

        # --- محاولة إضافة الأعمدة الجديدة إلى جدول sessions إذا لم تكن موجودة ---
        existing_session_columns = [col_info[1] for col_info in cursor.execute("PRAGMA table_info(sessions)").fetchall()]
        new_session_columns_to_add = {
            'bonus_code_used': 'TEXT',
            'points_earned_this_session': 'INTEGER DEFAULT 0',
            'is_free_session': 'BOOLEAN DEFAULT 0',
            'redeemed_points_for_session': 'INTEGER DEFAULT 0'
        }
        for col_name, col_type in new_session_columns_to_add.items():
            if col_name not in existing_session_columns:
                try:
                    cursor.execute(f"ALTER TABLE sessions ADD COLUMN {col_name} {col_type}")
                    logging.info(f"Added column '{col_name}' to 'sessions' table.")
                except sqlite3.OperationalError as e_alter:
                    logging.warning(f"Could not add column '{col_name}' to 'sessions' (likely exists or DB locked): {e_alter}")
        
        conn.commit()
        # --- نهاية إضافة الأعمدة ---

        # التحقق من وجود الأدمن وإنشائه إذا لم يكن موجودًا (كما كان في الكود الأصلي)
        cursor.execute("SELECT password FROM employees WHERE username = ?", (ADMIN_USERNAME,))
        admin_record = cursor.fetchone()
        if not admin_record:
            if not ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP:
                logging.critical("CRITICAL SETUP ERROR: ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP is not set in constants.")
                # لا يمكن إظهار messagebox هنا بأمان إذا لم يتم تهيئة Tkinter بعد
                print("CRITICAL SETUP ERROR: ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP is not set.")
                return False # فشل الإعداد
            admin_hash = hash_password(ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP) # تأكد أن دالة hash_password مُعرفة
            if admin_hash:
                cursor.execute("INSERT INTO employees (username, password) VALUES (?, ?)", (ADMIN_USERNAME, admin_hash))
                conn.commit()
                logging.info(f"Initial admin user '{ADMIN_USERNAME}' created.")
                logging.warning("IMPORTANT: Change the default admin password via 'Manage Employees' in the app.")
            else:
                logging.error("Failed to hash initial admin password during setup.")
                print("SETUP ERROR: Failed to hash initial admin password.")
                return False # فشل الإعداد
        
        logging.info("Database setup/check complete with new tables and columns for bonus points and expenses.")
        return True

    except sqlite3.Error as e_db:
        logging.error(f"Database Error during setup: {e_db}", exc_info=True)
        # تجنب messagebox هنا إذا كان setup_database يُستدعى قبل تهيئة Tkinter بشكل كامل
        print(f"DATABASE ERROR: Error setting up/updating database: {e_db}")
        # يمكنك محاولة إظهار messagebox إذا كان Tkinter قد تم تهيئته
        # if tk._default_root: 
        # messagebox.showerror("Database Error", f"Error setting up/updating database: {e_db}")
        return False # فشل الإعداد
    finally:
        if conn:
            conn.close()
# --- Authentication ---
def authenticate(username, password):
    """Authenticates user against the database. Returns username on success, None otherwise."""
    global current_user
    conn = None
    username = username.strip()

    if not username or not password:
         logging.warning("Authentication attempt with empty username or password.")
         return None

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM employees WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result:
            stored_username, stored_hash = result
            if verify_password(stored_hash, password):
                logging.info(f"Authentication successful for user '{stored_username}'.")
                if ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP and \
                   stored_username == ADMIN_USERNAME and \
                   verify_password(stored_hash, ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP):
                    logging.warning(f"Admin '{stored_username}' authenticated using the default setup password.")
                return stored_username
            else:
                logging.warning(f"Authentication failed for user '{username}': Password mismatch.")
                return None
        else:
            logging.warning(f"Authentication failed: User '{username}' not found.")
            return None

    except sqlite3.Error as e:
        logging.error(f"Database error during authentication for '{username}': {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

# --- Primary Login Screen (Uses ttk) ---
def show_login_screen(on_login_success_callback):
    """Displays the themed login screen and handles login attempts."""
    
    login_window = tk.Tk()
    login_window.title("MIX GAME Cafe Login - Football Edition")
    login_window.geometry("500x650") # Adjust as needed
    login_window.resizable(False, False)
    
    login_window.background_image_tk = None # Initialize to prevent GC issues

    # --- Background Image Setup ---
    bg_image_filename = "football_background.jpg" # <<<=== IMPORTANT: USE YOUR ACTUAL JPG FILENAME HERE
                                                 # e.g., "image_06afbe.jpg" or "ronaldo_background.jpg"
    try:
        if not PILLOW_AVAILABLE:
            logging.error("Pillow (PIL) is not available, cannot load JPG background.")
            raise ImportError("Pillow not found.")
            
        actual_image_path = resource_path(bg_image_filename)
        logging.info(f"Attempting to load background image from: {actual_image_path}")

        if not os.path.exists(actual_image_path):
            logging.error(f"Background image file NOT FOUND at: {actual_image_path}")
            raise FileNotFoundError(f"Image not found: {actual_image_path}")

        img = Image.open(actual_image_path)
        img_resized = img.resize((500, 650), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
        login_window.background_image_tk = ImageTk.PhotoImage(img_resized)
        
        background_label = tk.Label(login_window, image=login_window.background_image_tk)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        logging.info(f"Successfully loaded and placed background image: {bg_image_filename}")

    except Exception as e_bg:
        logging.error(f"Could not load background image '{bg_image_filename}': {e_bg}", exc_info=True)
        login_window.configure(bg="#2E7D32") # Fallback green color

    # --- Styling for Login Elements ---
    style = ttk.Style(login_window)
    # You might want to use a specific theme if you have ttkthemes
    # style.theme_use('clam') # or 'alt', 'default', etc.

    login_frame_bg_color = "#222222" # Dark background for the login fields area
    title_text_color = "#000000"    # Gold/Yellow for title
    label_text_color = "#000000"    # White for labels on dark background
    button_bg_color = "#008000"     # Green for login button
    button_fg_color = "#FFFFFF"     # White text on button
    button_active_bg_color = "#006400" # Darker green for active button

    style.configure("LoginCenter.TFrame", background=login_frame_bg_color)
    
    title_font_family = "Impact" if "Impact" in tkfont.families() else "Arial Black"
    default_font_family = "Segoe UI" if "Segoe UI" in tkfont.families() else "Arial"

    title_font = tkfont.Font(family=title_font_family, size=32, weight="bold") # Adjusted size slightly
    label_font = tkfont.Font(family=default_font_family, size=11)
    entry_font = tkfont.Font(family=default_font_family, size=11)
    button_font = tkfont.Font(family=default_font_family, size=12, weight="bold")

    style.configure("LoginTitle.TLabel", foreground=title_text_color, background=login_frame_bg_color, font=title_font)
    style.configure("Login.TLabel", foreground=label_text_color, background=login_frame_bg_color, font=label_font)
    style.configure("Login.TEntry", fieldbackground="#000000", foreground="#000000", font=entry_font, padding=5)
    style.configure("Login.TButton", foreground=button_fg_color, background=button_bg_color, font=button_font, padding=8)
    style.map("Login.TButton", background=[('active', button_active_bg_color)])
    
    # --- Center Frame for Login Inputs ---
    center_frame = ttk.Frame(login_window, style="LoginCenter.TFrame", padding="30 30 30 30") # Adjusted padding
    center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # --- Login Processing Function (Nested) ---
    def attempt_login_football():
        nonlocal username_entry, password_entry # Ensure access to these specific entry widgets
        logging.info("Login button clicked. Attempting login...")
        
        try:
            username = username_entry.get().strip()
            password = password_entry.get()
        except tk.TclError as e: # Should not happen if widgets are managed by this window
            logging.error(f"Error getting username/password from entry fields: {e}")
            messagebox.showerror("Error", "Login fields are not accessible.", parent=login_window)
            return
        
        logging.info(f"Username entered: '{username}', Password entered (length): {len(password)}")

        if not username or not password:
            logging.warning("Username or password field is empty.")
            messagebox.showerror("Login Failed", "Username and password cannot be empty.", parent=login_window)
            return

        # 'authenticate' must be a globally defined function
        authenticated_user = authenticate(username, password) 
        logging.info(f"Authentication result for '{username}': {authenticated_user}")

        if authenticated_user:
            global current_user # To set the global current_user variable
            current_user = authenticated_user # Set the logged-in user globally
            logging.info(f"Login successful for user: {current_user}")
            
            # 'ADMIN_USERNAME' should be a global constant
            login_type = "🛡️ Admin" if current_user == ADMIN_USERNAME else "👤 Employee" 

            # Telegram notification (ensure _telegram_enabled and send_telegram_message are global)
            if '_telegram_enabled' in globals() and _telegram_enabled and \
               'send_telegram_message' in globals() and callable(send_telegram_message):
                send_telegram_message(f"{login_type} '{current_user}' logged into MIX GAME Cafe.")
                logging.info("Login Telegram message sent.")
            else:
                logging.warning("Telegram not configured/enabled or send_telegram_message not available. Skipping login notification.")

            # Default admin password warning (ensure relevant globals are defined)
            if 'ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP' in globals() and ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP and \
               current_user == ADMIN_USERNAME and \
               password == ADMIN_PLAINTEXT_PASSWORD_FOR_SETUP:
                logging.warning(f"Admin '{current_user}' logged in with the default setup password.")
                messagebox.showwarning("Security Alert",
                                       "You are logged in as admin with the default password. "
                                       "Please change it immediately via 'Manage Employees'.",
                                       parent=login_window)
            
            if login_window.winfo_exists():
                login_window.destroy()
                logging.info("Login window destroyed.")
            
            if callable(on_login_success_callback):
                logging.info("Calling on_login_success_callback (e.g., start_main_gui).")
                on_login_success_callback()
            else:
                logging.error("on_login_success_callback is not callable!")
        else:
            logging.warning(f"Login failed for username: '{username}'. Showing error message.")
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=login_window)
            if password_entry.winfo_exists():
                password_entry.delete(0, tk.END)
                password_entry.focus_set()

    # --- Login Widgets inside center_frame ---
    title_label = ttk.Label(center_frame, text="MIX GAME CAFE", style="LoginTitle.TLabel") # Or "VIEANNA"
    title_label.pack(pady=(0, 15))

    # Optional CR7 label (if not part of background image)
    cr7_font = tkfont.Font(family=title_font_family, size=24, weight="bold")
    cr7_label = ttk.Label(center_frame, text="CR7", foreground="magenta", background=login_frame_bg_color, font=cr7_font)
    cr7_label.pack(pady=(0, 25))

    user_frame = ttk.Frame(center_frame, style="LoginCenter.TFrame")
    user_frame.pack(fill=tk.X, pady=8)
    ttk.Label(user_frame, text="Username:", style="Login.TLabel", width=10, anchor="w").pack(side=tk.LEFT, padx=(0,5))
    username_entry = ttk.Entry(user_frame, style="Login.TEntry", width=28, font=entry_font) # Use configured font
    username_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    pass_frame = ttk.Frame(center_frame, style="LoginCenter.TFrame")
    pass_frame.pack(fill=tk.X, pady=8)
    ttk.Label(pass_frame, text="Password:", style="Login.TLabel", width=10, anchor="w").pack(side=tk.LEFT, padx=(0,5))
    password_entry = ttk.Entry(pass_frame, show="*", style="Login.TEntry", width=28, font=entry_font) # Use configured font
    password_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    login_button = ttk.Button(center_frame, text="LOGIN", command=attempt_login_football, style="Login.TButton", width=15)
    login_button.pack(pady=(25, 0), ipady=4) # Adjusted padding

    # Bindings and focus
    password_entry.bind('<Return>', lambda event=None: attempt_login_football())
    username_entry.bind('<Return>', lambda event=None: password_entry.focus())
    username_entry.focus_set()

    login_window.mainloop()


# --- Helper Functions ---
def format_timedelta(delta):
    """Formats a timedelta object into HH:MM:SS."""
    if delta is None: return "00:00:00"
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0: return "00:00:00" # Handle negative durations gracefully
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def play_end_sound():
    """Plays the end session sound in a separate thread."""
    global sound_thread
    if SOUND_ENABLED and playsound:
        if sound_thread and sound_thread.is_alive():
             logging.debug("Sound play skipped: another sound is already playing.")
             return
        try:
            sound_thread = threading.Thread(target=playsound, args=(END_SOUND_FILE,), daemon=True, name="SoundPlayerThread")
            sound_thread.start()
            logging.debug(f"Started sound thread for {END_SOUND_FILE}")
        except Exception as e:
            logging.error(f"Error starting sound thread for {END_SOUND_FILE}: {e}", exc_info=True)

# --- Start Session Dialog (Uses ttk) ---
# -*- coding: utf-8 -*-
# ... (الـ imports والثوابت التي لديك)
# from tkinter import messagebox, simpledialog, ttk, Toplevel, StringVar, IntVar, Radiobutton # إلخ.
# from datetime import datetime, timedelta # إلخ.

# ... (باقي الكود الخاص بك، مثل تعريف ITEM_PRICES, DEVICES, RATES, DB_NAME, إلخ.)

# At the top of your cyper.py, ensure these are imported for StartSessionDialog:
# import tkinter as tk
# from tkinter import ttk, Toplevel, StringVar, messagebox (if used)
# from datetime import datetime, timedelta (if used for default values)

class StartSessionDialog(Toplevel):
    def __init__(self, parent, device_name):
        super().__init__(parent)
        self.parent = parent
        self.device_name = device_name
        self.result = None 

        self.title(f"بدء جلسة جديدة: {device_name}")
        self.geometry("400x420") 
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # --- Styling specific to this dialog ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # Or your app's main theme if known

        dialog_bg = "#4a4a4a" # Or use self.parent.color_dark_panel if passed from CyberCafeApp
        text_fg_dialog = "#E0E0E0"
        header_font_dialog = ('Segoe UI', 11, 'bold')
        label_font_dialog = ('Segoe UI', 10)
        entry_font_dialog = ('Segoe UI', 10) # Font for entry text
        button_font_dialog = ('Segoe UI', 10, 'bold')

        self.configure(background=dialog_bg)
        self.style.configure("DialogStart.TFrame", background=dialog_bg)
        self.style.configure("DialogStart.TLabel", background=dialog_bg, foreground=text_fg_dialog, font=label_font_dialog)
        self.style.configure("DialogStart.Header.TLabel", font=header_font_dialog, background=dialog_bg, foreground=text_fg_dialog)
        self.style.configure("DialogStart.TRadiobutton", background=dialog_bg, foreground="#AEEEEE", font=label_font_dialog)
        self.style.map("DialogStart.TRadiobutton", background=[('active', '#5a5a5a')])
        
        # VVentinganV Style for Entry fields in THIS dialog VVentinganV
        self.style.configure("DialogStart.TEntry", 
                             foreground="#000000",       # Black text
                             fieldbackground="#FFFFFF", # White field background
                             insertcolor="#000000",     # Black cursor
                             font=entry_font_dialog     # Use the font defined for entries here
                            )
        self.style.map("DialogStart.TEntry", 
                       fieldbackground=[('focus', '#F0F0F0')]) # Optional: different bg on focus
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        self.style.configure("DialogStart.Ok.TButton", font=button_font_dialog, foreground="white", background="#4CAF50")
        self.style.map("DialogStart.Ok.TButton", background=[('active', '#45a049')])
        self.style.configure("DialogStart.Cancel.TButton", font=button_font_dialog, foreground="white", background="#FF5733")
        self.style.map("DialogStart.Cancel.TButton", background=[('active', '#e64a2e')])

        # --- Variables ---
        self.session_type = StringVar(value="Single")
        self.time_option = StringVar(value="Open Session")
        self.customer_name = StringVar()
        self.manual_minutes = StringVar()
        self.bonus_code_var = StringVar()

        main_frame = ttk.Frame(self, padding=15, style="DialogStart.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Session Type ---
        ttk.Label(main_frame, text="نوع الجلسة:", style="DialogStart.Header.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        ttk.Radiobutton(main_frame, text="لاعب واحد (Single)", variable=self.session_type, value="Single", style="DialogStart.TRadiobutton").grid(row=1, column=0, sticky="w", padx=5)
        ttk.Radiobutton(main_frame, text="متعدد اللاعبين (Multiplayer)", variable=self.session_type, value="Multiplayer", style="DialogStart.TRadiobutton").grid(row=1, column=1, sticky="w", padx=5)

        # --- Time Options ---
        ttk.Label(main_frame, text="مدة الجلسة:", style="DialogStart.Header.TLabel").grid(row=2, column=0, columnspan=2, sticky="w", pady=(15, 5))
        time_options = ["Open Session", "30 Minutes", "1 Hour", "2 Hours", "Manual Time"]
        time_rb_frame = ttk.Frame(main_frame, style="DialogStart.TFrame")
        time_rb_frame.grid(row=3, column=0, columnspan=2, sticky="w")
        for i, option_text in enumerate(time_options):
            rb = ttk.Radiobutton(time_rb_frame, text=option_text, variable=self.time_option, value=option_text, command=self._toggle_manual_entry, style="DialogStart.TRadiobutton")
            rb.grid(row=i // 2, column=i % 2, sticky="w", padx=5, pady=2)

        # --- Manual Time Entry ---
        self.manual_frame = ttk.Frame(main_frame, style="DialogStart.TFrame")
        self.manual_frame.grid(row=4, column=0, columnspan=2, sticky="w", pady=5, padx=5)
        ttk.Label(self.manual_frame, text="أدخل المدة (دقائق):", style="DialogStart.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        vcmd_int = (self.register(self._validate_int_positive), '%P')
        self.manual_entry = ttk.Entry(self.manual_frame, textvariable=self.manual_minutes, 
                                      width=7, state=tk.DISABLED, validate='key', 
                                      validatecommand=vcmd_int, 
                                      style="DialogStart.TEntry") # Apply the style
        self.manual_entry.pack(side=tk.LEFT)

        # --- Customer Name ---
        ttk.Label(main_frame, text="اسم العميل (اختياري):", style="DialogStart.Header.TLabel").grid(row=5, column=0, columnspan=2, sticky="w", pady=(15, 5))
        cust_entry = ttk.Entry(main_frame, textvariable=self.customer_name, 
                               width=35, 
                               style="DialogStart.TEntry") # Apply the style
        cust_entry.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # --- Bonus Code ---
        ttk.Label(main_frame, text="كود النقاط (اختياري):", style="DialogStart.Header.TLabel").grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 5))
        bonus_code_entry = ttk.Entry(main_frame, textvariable=self.bonus_code_var, 
                                     width=35, 
                                     style="DialogStart.TEntry") # Apply the style
        bonus_code_entry.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # --- Buttons ---
        button_frame = ttk.Frame(main_frame, style="DialogStart.TFrame")
        button_frame.grid(row=9, column=0, columnspan=2, pady=(10, 0)) 
        ttk.Button(button_frame, text="بدء الجلسة", command=self._on_ok, style="DialogStart.Ok.TButton", width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="إلغاء", command=self._on_cancel, style="DialogStart.Cancel.TButton", width=15).pack(side=tk.LEFT, padx=10)

        self._toggle_manual_entry() 
        cust_entry.focus_set() 
        
        self.wait_window()

    # ... (rest of your StartSessionDialog methods: _validate_int_positive, _toggle_manual_entry, _on_ok, _on_cancel)

    def _validate_int_positive(self, value_if_allowed): # تم تغيير اسم الدالة للوضوح
        """يتحقق من أن القيمة المدخلة هي رقم صحيح موجب أو صفر."""
        if value_if_allowed == "": # السماح بالحقل الفارغ أثناء الكتابة
            return True
        try:
            val = int(value_if_allowed)
            return val >= 0 # السماح بالصفر (على الرغم من أننا نتحقق من >0 في _on_ok)
        except ValueError:
            return False # ليس رقمًا صحيحًا

    def _toggle_manual_entry(self):
        """يُفعّل أو يُعطّل حقل إدخال الوقت اليدوي بناءً على اختيار المستخدم."""
        if self.time_option.get() == "Manual Time":
            self.manual_entry.config(state=tk.NORMAL)
            self.manual_entry.focus_set() # نقل التركيز إلى حقل الدقائق
        else:
            self.manual_entry.config(state=tk.DISABLED)
            self.manual_minutes.set("") # مسح القيمة إذا تم اختيار خيار آخر

    def _on_ok(self):
        """يُجمع بيانات الجلسة عند الضغط على "بدء الجلسة"."""
        time_opt_selected = self.time_option.get() # تم تغيير اسم المتغير
        manual_mins_val = 0
        intended_end_time = None # وقت الانتهاء المتوقع (إذا كانت الجلسة محددة المدة)
        start_time_dt = datetime.now() # تم تغيير اسم المتغير للوضوح

        if time_opt_selected == "Manual Time":
            try:
                manual_mins_val = int(self.manual_minutes.get())
                if manual_mins_val <= 0: # المدة يجب أن تكون أكبر من صفر
                    messagebox.showerror("إدخال غير صحيح", "المدة المحددة يدويًا يجب أن تكون أكبر من صفر دقيقة.", parent=self)
                    return
                intended_end_time = start_time_dt + timedelta(minutes=manual_mins_val)
            except ValueError: # إذا لم يتمكن من تحويل القيمة إلى رقم صحيح
                messagebox.showerror("إدخال غير صحيح", "الرجاء إدخال عدد صحيح من الدقائق للوقت اليدوي.", parent=self)
                return
        elif time_opt_selected == "30 Minutes": 
            intended_end_time = start_time_dt + timedelta(minutes=30)
        elif time_opt_selected == "1 Hour": 
            intended_end_time = start_time_dt + timedelta(hours=1)
        elif time_opt_selected == "2 Hours": 
            intended_end_time = start_time_dt + timedelta(hours=2)
        # إذا كان "Open Session"، فإن intended_end_time يبقى None

        cust_name_val = self.customer_name.get().strip() # تم تغيير اسم المتغير
        bonus_code_val = self.bonus_code_var.get().strip().upper() # --- جديد: الحصول على كود النقاط وتحويله لحروف كبيرة ---

        # تجميع نتيجة الحوار
        self.result = {
            "session_type": self.session_type.get(),
            "time_option": time_opt_selected,
            "customer_name": cust_name_val if cust_name_val else None, # None إذا كان فارغًا
            "start_time": start_time_dt,
            "intended_end_time": intended_end_time,
            "bonus_code": bonus_code_val if bonus_code_val else None # --- جديد: إضافة الكود للنتيجة ---
        }
        self.destroy() # إغلاق نافذة الحوار

    def _on_cancel(self):
        """يُغلق الحوار عند الضغط على "إلغاء" أو 'X'."""
        self.result = None # لا توجد نتيجة
        self.destroy()
# -*- coding: utf-8 -*-
# ... (جميع الـ imports الضرورية في بداية ملفك)
# import tkinter as tk
# from tkinter import ttk, messagebox, simpledialog, filedialog, Toplevel, StringVar, Listbox, Scrollbar, END, SINGLE
# from tkinter import font as tkfont
# import sqlite3
# from datetime import datetime, timedelta, date
# import os
# import logging
# import random # For bonus code generation
# import string # For bonus code generation
# import queue  # For Telegram queue

# ... (جميع الثوابت والمتغيرات العامة والدوال المساعدة العالمية)
# global current_user, ADMIN_USERNAME, DB_NAME, DEVICES, RATES, ITEM_PRICES
# global TELEGRAM_ACTION_QUEUE, _telegram_enabled, CHAT_ID, send_telegram_message
# global hash_password, verify_password, format_timedelta, play_end_sound, SOUND_ENABLED
# global prompt_login_modal # The one we fixed
# هذا الكود سيتم تنفيذه مرة واحدة فقط عند بدء تشغيل الملف
_CYBERCAFEAPP_DEFINITIONS_FOUND = 0


class CyberCafeApp:
    def __init__(self, root_window):
        self.root = root_window
        self.device_widgets = {}
        self.sessions = {}
        self.device_to_type_map = {} # Maps device names like "PS1" to "PlayStation"
        self.current_runtime_revenue = 0.0
        self.current_shift_expenses_total = 0.0
        self._timer_update_job = None
        self.check_telegram_queue_job = None

        username_display = "N/A" # Default
        if 'current_user' in globals() and current_user:
            username_display = current_user
        elif hasattr(self, 'current_user_attribute') and self.current_user_attribute: # if passed differently
            username_display = self.current_user_attribute

        logging.debug("CyberCafeApp __init__ with Champions League Theme - Tabbed Interface")

        # --- Champions League Theme Color Palette ---
        self.cl_deep_blue = "#0D1B2A"          # Main background, deep and rich
        self.cl_midnight_blue = "#1B263B"      # Slightly lighter blue for panels
        self.cl_star_silver = "#E0E0E0"        # For text, borders, highlights (like stars)
        self.cl_trophy_gold = "#FFC107"        # Accent for important elements, selections
        self.cl_pitch_black = "#1A1A1A"        # For very dark text or accents if needed
        
        self.cl_text_on_blue = self.cl_star_silver
        self.cl_text_on_silver = self.cl_pitch_black
        self.cl_text_on_gold = self.cl_pitch_black

        self.cl_action_blue = "#4A90E2"        # A brighter blue for primary actions (Start)
        self.cl_action_blue_active = "#357ABD" # Active state for action blue

        self.cl_warning_yellow = "#F5A623"     # For warnings, item additions
        self.cl_warning_yellow_active = "#F39C12"

        self.cl_stop_red = "#D32F2F"           # For stop, exit, critical alerts
        self.cl_stop_red_active = "#B71C1C"

        self.cl_timer_default = self.cl_action_blue
        self.cl_timer_warning = self.cl_warning_yellow
        self.cl_timer_critical = self.cl_stop_red
        self.cl_disabled_grey = "#777777"
        self.cl_disabled_text_grey = "#aaaaaa"

        # --- Font Configuration (can be kept similar, or adjusted for a more "premium" feel if desired) ---
        try:
            self.font_family_header = "Impact" if "Impact" in tkfont.families() else "Arial Black"
            # For a more "premium" feel, consider fonts like "Roboto Condensed", "Lato", or "Open Sans" if available
            # For now, keeping current flexible choices
            self.font_family_body = "Segoe UI" if "Segoe UI" in tkfont.families() else "Arial"
            self.font_family_mono = "Consolas" if "Consolas" in tkfont.families() else "Courier New"

            self.font_app_header = tkfont.Font(family=self.font_family_header, size=17, weight="bold")
            self.font_device_name = tkfont.Font(family=self.font_family_header, size=14, weight="bold")
            self.font_timer = tkfont.Font(family=self.font_family_mono, size=22, weight="bold")
            self.font_button = tkfont.Font(family=self.font_family_body, size=9, weight="bold")
            self.font_button_large = tkfont.Font(family=self.font_family_body, size=11, weight="bold")
            self.font_label = tkfont.Font(family=self.font_family_body, size=10)
            self.font_info = tkfont.Font(family=self.font_family_body, size=9)
            self.font_cost = tkfont.Font(family=self.font_family_body, size=11, weight="bold")
            self.font_points = tkfont.Font(family=self.font_family_body, size=10, weight="bold")
        except Exception as e_font:
            logging.error(f"Font loading error: {e_font}. Using default Arial.")
            self.font_app_header = ("Arial", 17, "bold"); self.font_device_name = ("Arial", 14, "bold")
            self.font_timer = ("Courier New", 22, "bold"); self.font_button = ("Arial", 9, "bold")
            self.font_button_large = ("Arial", 11, "bold"); self.font_label = ("Arial", 10)
            self.font_info = ("Arial", 9); self.font_cost = ("Arial", 11, "bold")
            self.font_points = ("Arial", 10, "bold")

        # --- Load Icons (ensure these icons fit the CL theme visually) ---
        icon_folder = "icons/" # Consider CL-themed icons
        self.icons = {}
        icon_files = {
            "start": "play_icon_cl.png", "end": "stop_icon_cl.png", "add_item": "item_icon_cl.png", # Example new names
            "redeem": "star_icon_cl.png", "manage_users": "users_icon_cl.png", "report": "report_icon_cl.png",
            "bonus_codes": "ticket_icon_cl.png", "export": "excel_icon_cl.png", "checkout": "cash_icon_cl.png",
            "expense": "expense_icon_cl.png", "switch_user": "switch_user_icon_cl.png", "exit": "exit_icon_cl.png"
        }
        for name, filename in icon_files.items():
            try:
                image_path = os.path.join(icon_folder, filename)
                if os.path.exists(image_path):
                    self.icons[name] = tk.PhotoImage(file=image_path)
                else:
                    logging.warning(f"Icon file not found: {image_path}")
                    self.icons[name] = None
            except tk.TclError as e_icon:
                logging.error(f"Error loading icon {filename}: {e_icon}")
                self.icons[name] = None
        logging.info("Icons loading attempt complete.")

        # --- Root Window Configuration ---
        self.root.title(f"MIX GAME SYSTEM BY ENG.HASSAN 01126313329 - Staff: {username_display}") # Thematic title
        self.root.geometry("1280x780") # Slightly larger for a more "grand" feel
        self.root.minsize(1150, 720)
        self.root.configure(bg=self.cl_deep_blue)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- TTK Styling (Champions League Edition) ---
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic' are good starting points

        self.style.configure('.', background=self.cl_deep_blue, foreground=self.cl_text_on_blue, font=self.font_label)
        self.style.configure("TFrame", background=self.cl_deep_blue)
        self.style.configure("Top.TLabel", background=self.cl_deep_blue, foreground=self.cl_star_silver, font=self.font_app_header)
        self.style.configure("DarkPanel.TFrame", background=self.cl_midnight_blue) # For content areas

        # Labelframe for device groups and other sections
        self.style.configure("ChampionsLeague.TLabelframe",
                             background=self.cl_midnight_blue,
                             borderwidth=1, relief=tk.SOLID, # Subtle border
                             bordercolor=self.cl_star_silver)
        self.style.configure("ChampionsLeague.TLabelframe.Label",
                             background=self.cl_midnight_blue,
                             foreground=self.cl_trophy_gold, # Gold for titles
                             font=self.font_device_name, padding=(5, 3))

        # Labels within device UI
        self.style.configure("Device.TLabel", background=self.cl_midnight_blue, foreground=self.cl_text_on_blue, font=self.font_info)
        self.style.configure("Timer.TLabel", background=self.cl_midnight_blue, font=self.font_timer, foreground=self.cl_timer_default)
        self.style.configure("Cost.Device.TLabel", background=self.cl_midnight_blue, foreground=self.cl_trophy_gold, font=self.font_cost)
        self.style.configure("Points.Device.TLabel", background=self.cl_midnight_blue, foreground=self.cl_star_silver, font=self.font_points)

        button_padding_with_icon = (8, 5, 8, 5) # Slightly more padding
        button_relief = tk.FLAT # Modern flat buttons
        button_borderwidth = 2 # Will only show effectively with some themes or specific border color if relief is not flat

        # Start Button
        self.style.configure("Start.ChampionsLeague.TButton",
                             background=self.cl_action_blue, foreground=self.cl_text_on_silver, # Assuming cl_text_on_silver is dark
                             font=self.font_button, padding=button_padding_with_icon, relief=button_relief, borderwidth=0)
        self.style.map("Start.ChampionsLeague.TButton",
                       background=[('active', self.cl_action_blue_active), ('disabled', self.cl_disabled_grey)],
                       foreground=[('disabled', self.cl_disabled_text_grey)])

        # End Button
        self.style.configure("End.ChampionsLeague.TButton",
                             background=self.cl_stop_red, foreground=self.cl_star_silver,
                             font=self.font_button, padding=button_padding_with_icon, relief=button_relief, borderwidth=0)
        self.style.map("End.ChampionsLeague.TButton",
                       background=[('active', self.cl_stop_red_active), ('disabled', self.cl_disabled_grey)],
                       foreground=[('disabled', self.cl_disabled_text_grey)])

        # Add Item Button
        self.style.configure("AddItem.ChampionsLeague.TButton",
                             background=self.cl_warning_yellow, foreground=self.cl_text_on_gold,
                             font=self.font_button, padding=button_padding_with_icon, relief=button_relief, borderwidth=0)
        self.style.map("AddItem.ChampionsLeague.TButton",
                       background=[('active', self.cl_warning_yellow_active), ('disabled', self.cl_disabled_grey)],
                       foreground=[('disabled', self.cl_disabled_text_grey)])
        
        # Redeem Button (could be Gold)
        self.style.configure("Redeem.ChampionsLeague.TButton",
                             background=self.cl_trophy_gold, foreground=self.cl_text_on_gold,
                             font=self.font_button, padding=button_padding_with_icon, relief=button_relief, borderwidth=0)
        self.style.map("Redeem.ChampionsLeague.TButton",
                       background=[('active', self.cl_warning_yellow_active), ('disabled', self.cl_disabled_grey)], # Using warning active as placeholder
                       foreground=[('disabled', self.cl_disabled_text_grey)])

        # Large Action Buttons (e.g., Switch User, Admin section buttons)
        large_button_padding = (10, 6, 10, 6)
        self.style.configure("Action.Large.ChampionsLeague.TButton",
                             background=self.cl_action_blue, foreground=self.cl_star_silver,
                             font=self.font_button_large, padding=large_button_padding, relief=button_relief, borderwidth=0)
        self.style.map("Action.Large.ChampionsLeague.TButton", background=[('active', self.cl_action_blue_active)])
        
        # Admin Buttons (could be distinct, e.g. Silver with Blue text)
        self.style.configure("Admin.Large.ChampionsLeague.TButton",
                             background=self.cl_star_silver, foreground=self.cl_deep_blue, # Silver button, dark blue text
                             font=self.font_button_large, padding=large_button_padding, relief=button_relief,
                             bordercolor=self.cl_trophy_gold, borderwidth=0) # Subtle gold border on hover?
        self.style.map("Admin.Large.ChampionsLeague.TButton",
                       background=[('active', self.cl_trophy_gold)], foreground=[('active', self.cl_pitch_black)])

        # Exit Button
        self.style.configure("Exit.Large.ChampionsLeague.TButton",
                             background=self.cl_stop_red, foreground=self.cl_star_silver,
                             font=self.font_button_large, padding=large_button_padding, relief=button_relief, borderwidth=0)
        self.style.map("Exit.Large.ChampionsLeague.TButton", background=[('active', self.cl_stop_red_active)])

        # Treeview Styling
        self.style.configure("Treeview",
                             background=self.cl_midnight_blue, foreground=self.cl_text_on_blue,
                             fieldbackground=self.cl_midnight_blue, font=self.font_label, rowheight=25)
        self.style.map('Treeview',
                       background=[('selected', self.cl_trophy_gold)],
                       foreground=[('selected', self.cl_text_on_gold)])
        self.style.configure("Treeview.Heading",
                             background=self.cl_deep_blue, foreground=self.cl_star_silver, # Header of tree
                             font=self.font_button_large, relief=tk.FLAT, padding=5) # Make headings more prominent

        # Notebook (Tabs) Styling
        self.style.configure("TNotebook", tabposition='nw', background=self.cl_deep_blue)
        self.style.configure("TNotebook.Tab",
                             font=self.font_button_large, # Larger font for tabs
                             padding=[12, 6],           # More padding for tabs
                             background=self.cl_midnight_blue,    # Non-selected tab background
                             foreground=self.cl_star_silver)      # Non-selected tab text
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.cl_trophy_gold)], # Selected tab gold
                       foreground=[("selected", self.cl_text_on_gold)]) # Selected tab text

        # --- UI Structure ---
        self.top_frame = ttk.Frame(self.root, style="TFrame", padding=(10,5,10,5))
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        self.user_label = ttk.Label(self.top_frame, text=f"STAFF: {username_display}", style="Top.TLabel")
        self.user_label.pack(side=tk.LEFT, padx=10)
        
        switch_user_button = ttk.Button(self.top_frame, text="Switch Staff", command=self.switch_user,
                                        style="Action.Large.ChampionsLeague.TButton",
                                        image=self.icons.get("switch_user"),
                                        compound=tk.LEFT if self.icons.get("switch_user") else tk.NONE)
        switch_user_button.pack(side=tk.RIGHT, padx=10)

        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))
        
        self.devices_outer_frame = ttk.Frame(self.paned_window, style="TFrame")
        self.paned_window.add(self.devices_outer_frame, weight=3)

        self.notebook = ttk.Notebook(self.devices_outer_frame, style="TNotebook")
        self.notebook.pack(expand=True, fill='both', padx=0, pady=0)

        self.right_pane = ttk.Frame(self.paned_window, style="TFrame", width=350) # Slightly wider right pane
        self.right_pane.pack_propagate(False)
        self.paned_window.add(self.right_pane, weight=1)
        
        self.controls_frame = ttk.Frame(self.right_pane, style="DarkPanel.TFrame", padding=5) # Use DarkPanel
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, pady=(0,5), padx=5)
        
        self.expenses_frame_ui = ttk.LabelFrame(self.right_pane, text="Shift Expenses", style="ChampionsLeague.TLabelframe")
        self.expenses_frame_ui.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # --- Populate Devices in Notebook Pages ---
        num_cols_per_page = 3 

        if 'DEVICES_PAGES_SETUP' in globals() and 'DEVICE_CONFIG' in globals():
            for page_title, device_configs_on_page in DEVICES_PAGES_SETUP.items():
                page_content_frame = ttk.Frame(self.notebook, style="DarkPanel.TFrame", padding=10) # DarkPanel for tab content
                self.notebook.add(page_content_frame, text=page_title)

                current_device_idx_on_page = 0
                for device_type_key, count in device_configs_on_page:
                    config = DEVICE_CONFIG.get(device_type_key)
                    if not config:
                        logging.error(f"Configuration for device type '{device_type_key}' not found in DEVICE_CONFIG.")
                        continue

                    for i in range(1, count + 1):
                        device_name = config["name_template"].format(i)
                        self.device_to_type_map[device_name] = device_type_key

                        row = current_device_idx_on_page // num_cols_per_page
                        col = current_device_idx_on_page % num_cols_per_page
                        
                        # Ensure create_device_ui is defined in your class
                        if hasattr(self, 'create_device_ui'):
                             self.create_device_ui(page_content_frame, device_name, row, col)
                        else:
                            # Fallback: display a label if create_device_ui is missing for now
                            temp_label = ttk.Label(page_content_frame, text=f"{device_name}\n(UI Undefined)", style="Device.TLabel")
                            temp_label.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")


                        page_content_frame.grid_columnconfigure(col, weight=1, uniform=f"device_col_{page_title.replace(' ','_')}")
                        page_content_frame.grid_rowconfigure(row, weight=1, uniform=f"device_row_{page_title.replace(' ','_')}")
                        current_device_idx_on_page += 1
        else:
            logging.error("DEVICES_PAGES_SETUP or DEVICE_CONFIG not found. Cannot populate device tabs.")
            error_label_devices = ttk.Label(self.notebook, text="Error: Device configurations not loaded.", style="Device.TLabel")
            error_label_devices.pack(padx=10, pady=10)

        exit_button = ttk.Button(self.right_pane, text="EXIT ARENA", command=self.on_closing,
                                 style="Exit.Large.ChampionsLeague.TButton",
                                 image=self.icons.get("exit"),
                                 compound=tk.LEFT if self.icons.get("exit") else tk.NONE)
        exit_button.pack(side=tk.BOTTOM, pady=10, padx=5, fill=tk.X, ipady=5) # Increased ipady

        # --- Initialize other parts of the app ---
        if hasattr(self, 'load_current_shift_expenses'): self.load_current_shift_expenses()
        if hasattr(self, '_rebuild_control_panel'): self._rebuild_control_panel()
        if hasattr(self, 'restore_active_sessions'): self.restore_active_sessions()
        if hasattr(self, 'schedule_timer_updates'): self.schedule_timer_updates()
        if hasattr(self, 'schedule_telegram_queue_check'): self.schedule_telegram_queue_check()

        logging.info("CyberCafeApp __init__ Champions League Theme with Tabbed UI setup complete.")

    # Placeholder for methods assumed to exist, ensure they are defined in your class
    # def create_device_ui(self, parent_frame, device_name, row, col):
    #    # ... Your implementation for creating each device's UI ...
    #    # This should use the new "ChampionsLeague" styles for its internal widgets
    #    device_frame = ttk.LabelFrame(parent_frame, text=device_name, style="ChampionsLeague.TLabelframe")
    #    device_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
    #    # Add timer label, cost label, buttons etc. inside this device_frame
    #    # For example:
    #    # timer_label = ttk.Label(device_frame, text="00:00:00", style="Timer.TLabel")
    #    # timer_label.pack(pady=5)
    #    # start_button = ttk.Button(device_frame, text="Start", style="Start.ChampionsLeague.TButton")
    #    # start_button.pack(side=tk.LEFT, padx=2)
    #    # stop_button = ttk.Button(device_frame, text="End", style="End.ChampionsLeague.TButton")
    #    # stop_button.pack(side=tk.LEFT, padx=2)
    #    # self.device_widgets[device_name] = {'frame': device_frame, 'timer_label': timer_label, ...}
    #    pass


    def on_closing(self):
        logging.info("on_closing called. Application will attempt to close.")
        if messagebox.askokcancel("Exit Arena", "Are you sure you want to exit MIX GAME Cafe Arena?", parent=self.root): # Updated title
            if self._timer_update_job:
                self.root.after_cancel(self._timer_update_job)
            if self.check_telegram_queue_job:
                self.root.after_cancel(self.check_telegram_queue_job)
            # Add other cleanup if necessary
            self.root.destroy()
            logging.info("Application closed by user.")
        else:
            logging.info("User cancelled exit.")


    def switch_user(self):
        logging.info("Switch user button clicked. Implement switch user logic.")
        messagebox.showinfo("Switch User", "Switch user functionality not yet implemented.", parent=self.root)
        # Typically, this would involve:
        # 1. Ending current staff session (checkout if applicable)
        # 2. Displaying a login screen
        # 3. Re-initializing parts of the app for the new user

# --- Example of how to run this (ensure this part is outside the class definition) ---
# if __name__ == '__main__':
#     # Basic logging setup
#     logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

#     # Define dummy global configurations if not available elsewhere
#     # These should be defined BEFORE CyberCafeApp is instantiated
#     current_user = "CLKnight007" 
#     DEVICE_CONFIG = {
#         "PS5": {"name_template": "PS5 - Station {}"},
#         "VIP_PC": {"name_template": "VIP PC {}"}
#     }
#     DEVICES_PAGES_SETUP = {
#         "PlayStation Arena": [("PS5", 4)], # 4 PS5s on this tab
#         "VIP Zone": [("VIP_PC", 2)]      # 2 VIP PCs on this tab
#     }

#     root = tk.Tk()
#     app = CyberCafeApp(root)
#     root.mainloop()
    def create_device_ui(self, parent_frame, device_name, row, col):
        # Main frame for the device, using the football theme style
        frame = ttk.LabelFrame(parent_frame, text=device_name, style="Football.TLabelframe")
        frame.grid(row=row, column=col, padx=7, pady=7, sticky="nsew")

        frame.grid_columnconfigure(0, weight=1) # Content will be in a single column
        # Define row weights for responsive vertical sizing of elements
        frame.grid_rowconfigure(0, weight=0)  # Timer
        frame.grid_rowconfigure(1, weight=0)  # Cost
        frame.grid_rowconfigure(2, weight=0)  # Points
        frame.grid_rowconfigure(3, weight=1)  # Info Frame (this will expand vertically if space allows)
        frame.grid_rowconfigure(4, weight=0)  # Button Frame Row 1
        frame.grid_rowconfigure(5, weight=0)  # Button Frame Row 2

        # Timer Label
        # Initial foreground color; _update_all_device_timers will change it based on state
        timer_label = ttk.Label(frame, text="00:00:00", style="Timer.TLabel", anchor=tk.CENTER, 
                                foreground=self.color_green_start if hasattr(self, 'color_green_start') else "green")
        timer_label.grid(row=0, column=0, pady=(5, 2), sticky="ew")

        # Cost Label
        cost_label = ttk.Label(frame, text="Cost: 0.00 EGP", style="Cost.Device.TLabel", anchor=tk.CENTER)
        cost_label.grid(row=1, column=0, pady=(0, 2), sticky="ew")

        # Points Label
        points_label = ttk.Label(frame, text="Points: -", style="Points.Device.TLabel", anchor=tk.CENTER)
        points_label.grid(row=2, column=0, pady=(0, 5), sticky="ew")

        # Info Frame: Use the "DarkContent.TFrame" style
        info_frame = ttk.Frame(frame, style="DarkContent.TFrame") 
        info_frame.grid(row=3, column=0, sticky="nsew", pady=(0,5), padx=2)
        info_frame.grid_columnconfigure(0, weight=1) # Allow labels inside to expand/fill

        # Labels inside info_frame: Use "Device.TLabel" style (configured with dark background)
        customer_label = ttk.Label(info_frame, text="Customer: -", style="Device.TLabel", anchor="w", wraplength=150)
        customer_label.pack(fill=tk.X, pady=1, padx=2)
        type_label = ttk.Label(info_frame, text="Type: -", style="Device.TLabel", anchor="w")
        type_label.pack(fill=tk.X, pady=1, padx=2)
        start_lbl_text = ttk.Label(info_frame, text="Start: -", style="Device.TLabel", anchor="w") # Renamed to avoid potential conflicts
        start_lbl_text.pack(fill=tk.X, pady=1, padx=2)
        end_label = ttk.Label(info_frame, text="Ends: -", style="Device.TLabel", anchor="w")
        end_label.pack(fill=tk.X, pady=1, padx=2)
        drinks_label = ttk.Label(info_frame, text="Items: -", style="Device.TLabel", anchor="w", wraplength=150)
        drinks_label.pack(fill=tk.X, pady=1, padx=2)
        bonus_code_display_label = ttk.Label(info_frame, text="Bonus Code: -", style="Device.TLabel", anchor="w")
        bonus_code_display_label.pack(fill=tk.X, pady=1, padx=2)

        # Button Frame - Row 1: Use the "DarkContent.TFrame" style
        button_frame_row1 = ttk.Frame(frame, style="DarkContent.TFrame")
        button_frame_row1.grid(row=4, column=0, sticky="ew", pady=(5,2))
        button_frame_row1.grid_columnconfigure((0,1,2), weight=1) # Distribute buttons evenly

        start_button = ttk.Button(button_frame_row1, text="Start", 
                                  command=lambda d=device_name: self.show_start_session_dialog(d), 
                                  style="Start.Football.TButton",
                                  image=self.icon_start if hasattr(self, 'icon_start') and self.icon_start else None, 
                                  compound=tk.LEFT if hasattr(self, 'icon_start') and self.icon_start else tk.NONE)
        start_button.grid(row=0, column=0, padx=3, pady=2, sticky="ew")

        end_button = ttk.Button(button_frame_row1, text="End", 
                                command=lambda d=device_name: self.end_session(d), 
                                style="End.Football.TButton", state=tk.DISABLED,
                                image=self.icon_end if hasattr(self, 'icon_end') and self.icon_end else None, 
                                compound=tk.LEFT if hasattr(self, 'icon_end') and self.icon_end else tk.NONE)
        end_button.grid(row=0, column=1, padx=3, pady=2, sticky="ew")

        redeem_button = ttk.Button(button_frame_row1, text="Redeem", 
                                   command=lambda d=device_name: self.show_redeem_points_dialog(d), 
                                   style="Redeem.Football.TButton", 
                                   state=tk.NORMAL, # Enable by default, logic in update_device_ui can disable if session active
                                   image=self.icon_redeem if hasattr(self, 'icon_redeem') and self.icon_redeem else None, 
                                   compound=tk.LEFT if hasattr(self, 'icon_redeem') and self.icon_redeem else tk.NONE)
        redeem_button.grid(row=0, column=2, padx=3, pady=2, sticky="ew")
        
        # Button Frame - Row 2: Use the "DarkContent.TFrame" style
        button_frame_row2 = ttk.Frame(frame, style="DarkContent.TFrame")
        button_frame_row2.grid(row=5, column=0, sticky="ew", pady=(2,5))
        button_frame_row2.grid_columnconfigure(0, weight=1) # Single button, takes full width

        drink_button = ttk.Button(button_frame_row2, text="Add Item", 
                                  command=lambda d=device_name: self.show_add_item_dialog(d), 
                                  style="AddItem.Football.TButton", state=tk.DISABLED,
                                  image=self.icon_add_item if hasattr(self, 'icon_add_item') and self.icon_add_item else None, 
                                  compound=tk.LEFT if hasattr(self, 'icon_add_item') and self.icon_add_item else tk.NONE)
        drink_button.grid(row=0, column=0, padx=3, pady=2, sticky="ew")

        self.device_widgets[device_name] = {
            'frame': frame, 'timer_label': timer_label, 'cost_label': cost_label,
            'points_label': points_label, 'customer_label': customer_label, 
            'type_label': type_label, 'start_label': start_lbl_text, 'end_label': end_label,
            'drinks_label': drinks_label, 'bonus_code_display_label': bonus_code_display_label,
            'start_button': start_button, 'end_button': end_button, 
            'drink_button': drink_button, 'redeem_button': redeem_button
        }
        logging.debug(f"Created UI for device: {device_name} with football theme.")

    # ... (rest of your CyberCafeApp methods) ...

    def _rebuild_control_panel(self):
        logging.debug("Rebuilding control panel with Football Theme.")
        for widget in self.controls_frame.winfo_children():
            widget.destroy()
        
        # Ensure expenses_frame_ui children are cleared if it's repopulated by setup_expenses_ui...
        if hasattr(self, 'expenses_frame_ui') and self.expenses_frame_ui.winfo_exists():
             for widget in self.expenses_frame_ui.winfo_children():
                 widget.destroy()
        else:
            # Recreate if necessary (should be created in __init__)
            self.expenses_frame_ui = ttk.LabelFrame(self.right_pane, text="Shift Expenses", style="Football.TLabelframe")
            self.expenses_frame_ui.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)


        pady_controls = 7
        # Use new themed button styles
        admin_style = "Admin.Large.Football.TButton"
        action_style = "Action.Large.Football.TButton"
        expense_style = "AddItem.Football.TButton" # Using AddItem style for expenses for now (Yellowish)

        if current_user == ADMIN_USERNAME: # current_user should be global
            ttk.Button(self.controls_frame, text="Daily Report", command=self.show_daily_report, style=action_style, image=self.icon_report if hasattr(self, 'icon_report') else None, compound=tk.LEFT).pack(pady=pady_controls, padx=5, fill=tk.X, ipady=3)
            ttk.Button(self.controls_frame, text="Export Data", command=self.export_data_to_excel, style=action_style, image=self.icon_export if hasattr(self, 'icon_export') else None, compound=tk.LEFT).pack(pady=pady_controls, padx=5, fill=tk.X, ipady=3)
        else: # Employee View
            # Employee-specific label font if needed, or use a general one.
            emp_label_font = tkfont.Font(family=self.font_family_body, size=12, weight="bold")
            ttk.Label(self.controls_frame, text=f"STAFF: {current_user}", font=emp_label_font, style="Top.TLabel", anchor=tk.CENTER).pack(pady=pady_controls, padx=5, fill=tk.X) # Re-use Top.TLabel for consistency

        ttk.Button(self.controls_frame, text="Shift Checkout", command=self.show_checkout_summary, style=action_style, image=self.icon_checkout if hasattr(self, 'icon_checkout') else None, compound=tk.LEFT).pack(pady=pady_controls, padx=5, fill=tk.X, ipady=3)
        
        # Re-populate the expenses UI part
        self.setup_expenses_ui_in_control_panel() # This method will also need to use themed styles
        # Example for button inside setup_expenses_ui_in_control_panel:
        # add_expense_button = ttk.Button(self.expenses_frame_ui, text="Log Expense", ..., style="AddItem.Football.TButton", image=self.icon_expense)
        # Ensure labels/entries in expenses UI also use appropriate styles (e.g., "Device.TLabel" for labels on dark panel)

        logging.info("Control panel rebuilt with Football Theme styles.")
# Inside CyberCafeApp class:
    # Inside the CyberCafeApp class:

    # ... (your __init__ and other methods like start_session, end_session, etc.)

    # Inside the CyberCafeApp class:

    # Ensure 'import math' is at the top of your cyper.py file
    
# Inside CyberCafeApp class:

    # Ensure 'import math' and 'import logging' are at the top of your cyper.py file
    
# Inside the CyberCafeApp class:

    # Ensure 'import math' and 'import logging' are at the top of your cyper.py file
    
    def calculate_points_for_duration(self, duration_minutes):
        """
        Calculates potential bonus points based on session duration.
        Rule: 1 point for every completed minute of play.
        The decision to award these points is made in end_session based on total duration.
        """
        if not isinstance(duration_minutes, (int, float)) or duration_minutes <= 0:
            # This logging is for when the method is called with invalid input
            # logging.debug(f"calculate_points_for_duration: Invalid duration ({duration_minutes}), returning 0 potential points.")
            return 0
        
        # Calculate potential points: 1 point per full minute played
        potential_points = math.floor(duration_minutes) 
        
        logging.debug(
            f"calculate_points_for_duration: Potential points = {potential_points} for duration {duration_minutes:.2f} mins (1 point/min)."
        )
        return potential_points
    def setup_expenses_ui_in_control_panel(self):
        # self.expenses_frame_ui is a ttk.LabelFrame created in __init__
        # This function populates it.
        logging.debug(f"SETUP_EXPENSES: Populating expenses UI. Parent frame: {self.expenses_frame_ui}")
        if not (hasattr(self, 'expenses_frame_ui') and self.expenses_frame_ui.winfo_exists()):
            logging.error("SETUP_EXPENSES: self.expenses_frame_ui is not defined or not a valid widget here!")
            # As a fallback, try to recreate it if it was somehow destroyed by _rebuild_control_panel clearing
            # This shouldn't be necessary if _rebuild_control_panel only clears its own direct children (controls_frame).
            try:
                self.expenses_frame_ui = ttk.LabelFrame(self.right_pane, text="Shift Expenses", style="Football.TLabelframe")
                self.expenses_frame_ui.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
                logging.info("SETUP_EXPENSES: Recreated expenses_frame_ui as it was missing.")
            except Exception as e_recreate:
                logging.error(f"SETUP_EXPENSES: Failed to recreate expenses_frame_ui: {e_recreate}")
                return

        # Ensure labels inside expenses_frame_ui use styles consistent with the dark panel theme
        # For example, "Device.TLabel" which is configured with background=self.color_dark_panel
        # Or create a specific style like "Expense.TLabel"
        # For now, assuming "Device.TLabel" is appropriate for dark background.
        label_style_for_expense_frame = "Device.TLabel" 
        entry_font_for_expense_frame = self.font_label # Or a specific entry font if defined

        expense_form_frame = ttk.Frame(self.expenses_frame_ui, padding=(10,5), style="DarkContent.TFrame") # Use DarkContent style
        expense_form_frame.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(expense_form_frame, text="Expense Description:", style=label_style_for_expense_frame, 
                  font=self.font_label).grid(row=0, column=0, padx=(0,5), pady=3, sticky="w") # CORRECTED: self.font_label
        self.expense_desc_var = StringVar()
        self.expense_desc_entry = ttk.Entry(expense_form_frame, textvariable=self.expense_desc_var, 
                                            width=20, font=entry_font_for_expense_frame, style="Login.TEntry") # Re-use Login.TEntry style for white bg or define new
        self.expense_desc_entry.grid(row=0, column=1, padx=5, pady=3, sticky="ew")

        ttk.Label(expense_form_frame, text="Amount (EGP):", style=label_style_for_expense_frame, 
                  font=self.font_label).grid(row=1, column=0, padx=(0,5), pady=3, sticky="w") # CORRECTED: self.font_label
        self.expense_amount_var = StringVar()
        vcmd_float = (self.root.register(self.validate_float_positive), '%P') # Assuming validate_float_positive exists
        expense_amount_entry = ttk.Entry(expense_form_frame, textvariable=self.expense_amount_var, 
                                         width=12, font=entry_font_for_expense_frame, validate="key", 
                                         validatecommand=vcmd_float, style="Login.TEntry") # Re-use Login.TEntry style
        expense_amount_entry.grid(row=1, column=1, padx=5, pady=3, sticky="w")
        
        expense_form_frame.grid_columnconfigure(1, weight=1) 

        # Use a themed button style, e.g., AddItem.Football.TButton or a specific Expense.Football.TButton
        add_expense_button = ttk.Button(self.expenses_frame_ui, text="Log Expense", 
                                        command=self.add_shift_expense, # Assuming add_shift_expense exists
                                        style="AddItem.Football.TButton", # Example themed style
                                        image=self.icons.get("expense") if hasattr(self, 'icons') else None,
                                        compound=tk.LEFT if hasattr(self, 'icons') and self.icons.get("expense") else tk.NONE)
        add_expense_button.pack(pady=(5,10), padx=10, fill=tk.X, ipady=3) 
        
        logging.debug("Shift expenses UI populated in its dedicated frame with football theme.")
    def validate_float_positive(self, value_if_allowed):
        if not value_if_allowed: return True
        try:
            val = float(value_if_allowed)
            return val >= 0.0
        except ValueError: return False
    def show_add_item_dialog(self, device_name):
        """
        يعرض نافذة لإضافة عنصر (مشروب، إلخ) إلى جلسة نشطة على جهاز معين.
        """
        if device_name not in self.sessions:
            messagebox.showerror("خطأ", f"لا توجد جلسة نشطة على الجهاز {device_name} لإضافة عنصر إليها.", parent=self.root)
            return
        
        # SELECTABLE_ITEMS يجب أن يكون قاموسًا عالميًا يحتوي على العناصر وأسعارها (بدون الخيار الفارغ)
        if 'SELECTABLE_ITEMS' not in globals() or not SELECTABLE_ITEMS:
            messagebox.showerror("خطأ في الإعداد", "لم يتم تعريف أي عناصر قابلة للبيع في النظام.", parent=self.root)
            logging.error("show_add_item_dialog: SELECTABLE_ITEMS is not defined or empty.")
            return

        item_dialog = Toplevel(self.root)
        item_dialog.title(f"إضافة عنصر - {device_name}")
        item_dialog.geometry("350x200") # حجم النافذة يمكن تعديله
        item_dialog.resizable(False, False)
        # استخدام لون الخلفية المعرف في self، مع لون افتراضي إذا لم يكن موجودًا
        item_dialog.configure(bg=getattr(self, 'frame_bg_color', "#4a4a4a")) # استخدام لون خلفية الإطارات
        item_dialog.transient(self.root)
        item_dialog.grab_set()
        item_dialog.protocol("WM_DELETE_WINDOW", item_dialog.destroy)

        # يمكنك إنشاء نمط خاص لهذه النافذة أو استخدام الأنماط العامة
        # dialog_style = ttk.Style(item_dialog)
        # dialog_style.theme_use('clam')
        # ... (تعريف أنماط TFrame, TLabel, TCombobox, TButton لهذه النافذة إذا أردت)

        frame = ttk.Frame(item_dialog, padding=15, style="TFrame") # استخدام نمط TFrame المعرف
        frame.pack(expand=True, fill=tk.BOTH)

        # استخدام Top.TLabel إذا كانت الخلفية هي bg_color، أو TLabel إذا كانت frame_bg_color
        ttk.Label(frame, text="اختر العنصر للإضافة:", style="Top.TLabel" if getattr(self, 'bg_color', '') == getattr(self, 'frame_bg_color', '') else "TLabel", 
                  font=getattr(self, 'dialog_label_font', ('Segoe UI', 10))).pack(pady=(0, 10))

        selected_item_var = StringVar()
        # جلب أسماء العناصر من القاموس العالمي SELECTABLE_ITEMS
        item_names_list = list(SELECTABLE_ITEMS.keys())

        item_combo_font = getattr(self, 'dialog_label_font', ('Segoe UI', 10))
        item_combo = ttk.Combobox(frame, textvariable=selected_item_var, values=item_names_list,
                                  state="readonly", font=item_combo_font, width=28)
        item_combo.pack(pady=5)
        if item_names_list: # اختيار أول عنصر كافتراضي إذا كانت القائمة غير فارغة
            item_combo.current(0)

        def on_add_item_action(): # تم تغيير الاسم
            item_name = selected_item_var.get()
            if not item_name: # لم يتم اختيار عنصر
                messagebox.showwarning("لم يتم الاختيار", "الرجاء اختيار عنصر من القائمة.", parent=item_dialog)
                return
            
            # ITEM_PRICES يجب أن يكون قاموسًا عالميًا يحتوي على أسعار العناصر
            if 'ITEM_PRICES' in globals() and item_name in ITEM_PRICES:
                item_price = ITEM_PRICES[item_name]
                session_data = self.sessions[device_name] # الوصول لبيانات الجلسة الحالية
                
                # إضافة العنصر إلى قائمة العناصر في الجلسة
                session_data.setdefault('drinks', []).append(item_name) # setdefault لضمان وجود المفتاح
                # تحديث تكلفة العناصر في الجلسة
                session_data['item_cost'] = session_data.get('item_cost', 0.0) + item_price
                
                logging.debug(f"Updated item_cost for session on {device_name} to {session_data['item_cost']:.2f}")
                
                # تحديث واجهة المستخدم للجهاز لتعكس العنصر المضاف والتكلفة الجديدة
                # update_device_ui يجب أن تكون مُعرفة في الفئة
                if hasattr(self, 'update_device_ui') and callable(self.update_device_ui):
                    self.update_device_ui(device_name) 
                
                logging.info(f"Added item '{item_name}' (Price: {item_price:.2f} EGP) to session on device {device_name}.")
                
                # إرسال إشعار تيليجرام
                # send_telegram_message يجب أن تكون مُعرفة عالميًا وتعمل
                if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                    send_telegram_message(f"🥤 تم إضافة عنصر '{item_name}' (السعر: {item_price:.2f} جنيه) للجلسة على الجهاز {device_name}.")
                
                item_dialog.destroy() # إغلاق نافذة إضافة العنصر
            else:
                messagebox.showerror("خطأ", f"العنصر المختار '{item_name}' غير صالح أو سعره غير معروف.", parent=item_dialog)
                logging.error(f"Attempted to add invalid or unknown priced item: {item_name}")

        # إطار لأزرار الإضافة والإلغاء
        dialog_buttons_frame = ttk.Frame(frame, style="TFrame") # تم تغيير الاسم
        dialog_buttons_frame.pack(pady=15)
        
        # استخدام الأنماط الجديدة للأزرار
        ttk.Button(dialog_buttons_frame, text="إضافة", command=on_add_item_action, style="Pink.TButton").pack(side=tk.LEFT, padx=10, ipadx=5) # نمط وردي
        ttk.Button(dialog_buttons_frame, text="إلغاء", command=item_dialog.destroy, style="Red.TButton").pack(side=tk.LEFT, padx=10, ipadx=5) # نمط أحمر

        item_dialog.wait_window() # لجعل النافذة مودال

    # ... (باقي دوال الفئة CyberCafeApp) ...
    def load_current_shift_expenses(self):
        self.current_shift_expenses_total = 0.0 
        if not current_user:
            logging.warning("LOAD_EXPENSES: No current user.")
            return
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME) 
            cursor = conn.cursor()
            today_date_str = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT SUM(amount) FROM shift_expenses WHERE employee_username = ? AND date(logged_at) = date(?)", (current_user, today_date_str))
            result = cursor.fetchone()
            if result and result[0] is not None: self.current_shift_expenses_total = result[0]
            logging.info(f"LOAD_EXPENSES: For user '{current_user}' today: {self.current_shift_expenses_total:.2f} EGP")
        except sqlite3.Error as e: logging.error(f"LOAD_EXPENSES: Error for user '{current_user}': {e}", exc_info=True)
        finally:
            if conn: conn.close()

    def add_shift_expense(self):
        description = self.expense_desc_var.get().strip()
        amount_str = self.expense_amount_var.get().strip()
        if not description or not amount_str:
            messagebox.showwarning("إدخال ناقص", "الرجاء إدخال وصف المصروف والمبلغ.", parent=self.root)
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("مبلغ غير صحيح", "يجب أن يكون مبلغ المصروف أكبر من صفر.", parent=self.root)
                return
        except ValueError:
            messagebox.showerror("خطأ في الإدخال", "الرجاء إدخال مبلغ صحيح.", parent=self.root)
            return
        if not current_user:
            messagebox.showerror("خطأ", "لا يوجد مستخدم مسجل لإضافة المصروف باسمه.", parent=self.root)
            return
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            current_time_iso = datetime.now().isoformat() 
            cursor.execute("INSERT INTO shift_expenses (description, amount, employee_username, logged_at) VALUES (?, ?, ?, ?)", 
                           (description, amount, current_user, current_time_iso))
            conn.commit()
            self.current_shift_expenses_total += amount
            messagebox.showinfo("نجاح", f"تم تسجيل المصروف:\n{description}\nبمبلغ: {amount:.2f} جنيه.", parent=self.root)
            logging.info(f"Expense added: '{description}', Amount: {amount:.2f} by {current_user}. Total expenses: {self.current_shift_expenses_total:.2f}")
            if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                send_telegram_message(f"💸 مصروف جديد: {current_user}\nوصف: {description}\nمبلغ: {amount:.2f} ج\nإجمالي مصروفات الوردية: {self.current_shift_expenses_total:.2f} ج")
            self.expense_desc_var.set("")
            self.expense_amount_var.set("")
            if hasattr(self, 'expense_desc_entry'): self.expense_desc_entry.focus_set()
        except sqlite3.Error as e: logging.error(f"DB error adding expense: {e}", exc_info=True); messagebox.showerror("خطأ قاعدة بيانات", f"فشل تسجيل المصروف: {e}", parent=self.root)
        finally:
            if conn: conn.close()

    def generate_random_code(self, length=8):
        import random
        import string
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
# داخل فئة CyberCafeApp

    def manual_refill_points_dialog(self):
        """
        يعرض نافذة للأدمن لإضافة أو تعديل نقاط العملاء بشكل يدوي.
        """
        if current_user != ADMIN_USERNAME:
            messagebox.showerror("Permission Denied", "This function is for administrators only.", parent=self.root)
            return

        dialog = Toplevel(self.root)
        dialog.title("شحن/تعديل نقاط العملاء يدويًا")
        dialog.geometry("500x350") # حجم مبدئي للنافذة
        dialog.configure(bg=getattr(self, 'bg_color', "#3a3a3a"))
        dialog.transient(self.root)
        dialog.grab_set()

        main_dialog_frame = ttk.Frame(dialog, padding=15, style="TFrame")
        main_dialog_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. اختيار/إدخال العميل ---
        customer_frame = ttk.Frame(main_dialog_frame, style="TFrame")
        customer_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(customer_frame, text="اسم العميل:", style="Top.TLabel", font=getattr(self, 'label_font', None)).pack(side=tk.LEFT, padx=(0,5))
        
        customer_name_var = StringVar()
        # استخدام Combobox لعرض العملاء الموجودين
        # جلب أسماء العملاء من قاعدة البيانات
        conn = None
        customer_names = []
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT customer_name FROM customer_points ORDER BY customer_name")
            fetched_customers = cursor.fetchall()
            if fetched_customers:
                customer_names = [name[0] for name in fetched_customers if name[0] and name[0] != "N/A"]
        except sqlite3.Error as e_fetch_c:
            logging.error(f"Error fetching customer names for refill dialog: {e_fetch_c}")
        finally:
            if conn: conn.close()

        customer_combo = ttk.Combobox(customer_frame, textvariable=customer_name_var, values=customer_names, 
                                      font=getattr(self, 'dialog_label_font', None), width=25)
        customer_combo.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        # يمكنك أيضًا السماح بإدخال اسم عميل جديد إذا لم يكن في القائمة
        # customer_combo.bind('<KeyRelease>', lambda e: filter_customer_list(e, customer_combo, customer_names))

        current_points_var = StringVar(value="نقاط العميل الحالية: -")
        current_points_label = ttk.Label(main_dialog_frame, textvariable=current_points_var, style="Top.TLabel", font=getattr(self, 'info_label_font', None))
        current_points_label.pack(pady=(0,10))

        def on_customer_select(event=None): # يتم استدعاؤها عند اختيار عميل من الكومبوبوكس
            selected_customer = customer_name_var.get()
            if selected_customer:
                points = self.get_customer_total_points(selected_customer) # استخدام دالتك الحالية
                current_points_var.set(f"نقاط '{selected_customer}' الحالية: {points}")
            else:
                current_points_var.set("نقاط العميل الحالية: -")
        
        customer_combo.bind("<<ComboboxSelected>>", on_customer_select)
        customer_combo.bind("<Return>", on_customer_select) # لتحديث النقاط عند الضغط على Enter بعد الكتابة

        # --- 2. إدخال عدد النقاط للإضافة أو التعيين ---
        points_frame = ttk.Frame(main_dialog_frame, style="TFrame")
        points_frame.pack(fill=tk.X, pady=(0,10))

        ttk.Label(points_frame, text="النقاط المراد إضافتها:", style="Top.TLabel", font=getattr(self, 'label_font', None)).pack(side=tk.LEFT, padx=(0,5))
        points_to_add_var = StringVar()
        vcmd_int_refill = (self.root.register(self._validate_int_allow_negative), '%P') # نسمح بالسالب للخصم إذا أردنا
        points_entry = ttk.Entry(points_frame, textvariable=points_to_add_var, 
                                 font=getattr(self, 'dialog_label_font', None), width=10,
                                 validate="key", validatecommand=vcmd_int_refill)
        points_entry.pack(side=tk.LEFT, padx=(0,5))
        
        # --- (اختياري) حقل للسبب/الملاحظة ---
        reason_frame = ttk.Frame(main_dialog_frame, style="TFrame")
        reason_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Label(reason_frame, text="السبب/ملاحظة (اختياري):", style="Top.TLabel", font=getattr(self, 'label_font', None)).pack(side=tk.LEFT, padx=(0,5))
        reason_var = StringVar()
        reason_entry = ttk.Entry(reason_frame, textvariable=reason_var, font=getattr(self, 'dialog_label_font', None), width=30)
        reason_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)


        # --- 3. زر التأكيد ---
        def confirm_refill_points():
            customer_name = customer_name_var.get().strip()
            points_str = points_to_add_var.get().strip()
            reason = reason_var.get().strip()

            if not customer_name:
                messagebox.showerror("خطأ", "الرجاء اختيار أو إدخال اسم العميل.", parent=dialog)
                return
            if not points_str:
                messagebox.showerror("خطأ", "الرجاء إدخال عدد النقاط.", parent=dialog)
                return
            
            try:
                points_change = int(points_str)
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال عدد صحيح للنقاط.", parent=dialog)
                return

            # استدعاء دالة تحديث النقاط (التي أنشأناها سابقًا)
            # هذه الدالة تُنشئ العميل إذا لم يكن موجودًا وتضيف النقاط
            new_total_points = self.update_customer_points(customer_name, points_change)

            if new_total_points is not None:
                action_taken = "إضافة" if points_change >= 0 else "خصم"
                messagebox.showinfo("نجاح", 
                                    f"تمت {action_taken} {abs(points_change)} نقطة للعميل '{customer_name}'.\n"
                                    f"الرصيد الجديد: {new_total_points} نقطة.", 
                                    parent=dialog)
                logging.info(f"Manual points adjustment for '{customer_name}' by admin '{current_user}': {points_change} points. New total: {new_total_points}. Reason: {reason if reason else 'N/A'}")
                
                if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                    send_telegram_message(
                        f"⚙️ تعديل يدوي للنقاط:\n"
                        f"العميل: {customer_name}\n"
                        f"التغيير: {points_change:+} نقطة\n" # :+ لإظهار علامة + أو -
                        f"الرصيد الجديد: {new_total_points} نقطة\n"
                        f"بواسطة الأدمن: {current_user}\n"
                        f"السبب: {reason if reason else 'غير محدد'}"
                    )
                
                # تحديث عرض النقاط إذا كان العميل المختار هو نفسه في جلسة نشطة (إذا أردنا ذلك)
                # for dev_name, sess_data in self.sessions.items():
                #     if sess_data.get('customer') == customer_name:
                #         self.update_device_ui(dev_name) # سيستدعي get_customer_total_points
                
                # مسح الحقول وتحديث عرض النقاط الحالية في النافذة
                points_to_add_var.set("")
                reason_var.set("")
                on_customer_select() # لتحديث ليبل النقاط الحالية
            else:
                messagebox.showerror("فشل التحديث", f"فشل تحديث نقاط العميل '{customer_name}'. راجع السجلات.", parent=dialog)
            
        ttk.Button(main_dialog_frame, text="تأكيد تعديل النقاط", command=confirm_refill_points, style="Green.TButton").pack(pady=10, ipady=3)
        ttk.Button(main_dialog_frame, text="إغلاق", command=dialog.destroy, style="Red.TButton").pack(pady=5, ipady=3)
        
        dialog.wait_window()

    def _validate_int_allow_negative(self, value_if_allowed):
        """يتحقق من أن القيمة المدخلة هي رقم صحيح (يسمح بالسالب)."""
        if value_if_allowed == "" or value_if_allowed == "-": # السماح بالحقل الفارغ أو علامة السالب فقط
            return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False

    # ... (باقي دوال الفئة) ...
    def manage_bonus_codes_dialog(self):
        if current_user != ADMIN_USERNAME:
            messagebox.showerror("Permission Denied", "Access restricted to administrators.", parent=self.root)
            return
        dialog = Toplevel(self.root)
        dialog.title("إدارة أكواد النقاط (Admin)")
        dialog.geometry("750x550") 
        dialog.configure(bg=self.bg_color if hasattr(self, 'bg_color') else "#3a3a3a")
        dialog.transient(self.root) 
        dialog.grab_set() 

        add_frame = ttk.Frame(dialog, padding=10, style="TFrame") 
        add_frame.pack(pady=10, padx=10, fill=tk.X)
        ttk.Label(add_frame, text="إنشاء كود نقاط جديد:", style="Top.TLabel", font=self.frame_font if hasattr(self, 'frame_font') else None).pack(side=tk.LEFT, padx=(0,10))
        code_var = StringVar() 
        code_entry_font = self.dialog_label_font if hasattr(self, 'dialog_label_font') else None
        code_entry = ttk.Entry(add_frame, textvariable=code_var, font=code_entry_font, width=18)
        code_entry.pack(side=tk.LEFT, padx=(0,10))
        def generate_and_fill_code_action(): code_var.set(self.generate_random_code()) 
        ttk.Button(add_frame, text="إنشاء كود عشوائي", command=generate_and_fill_code_action, style="Blue.TButton").pack(side=tk.LEFT, padx=(0,10))
        def add_new_code_action():
            code_to_add = code_var.get().strip().upper() 
            if not code_to_add: messagebox.showwarning("إدخال ناقص", "الرجاء إدخال كود أو إنشاؤه.", parent=dialog); return
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME) 
                cursor = conn.cursor()
                cursor.execute("INSERT INTO bonus_codes (code, purchase_price) VALUES (?, ?)", (code_to_add, 5.0))
                conn.commit()
                messagebox.showinfo("نجاح الإضافة", f"تم إضافة الكود '{code_to_add}'.\nالحالة: غير نشط\nالسعر: 5.00 جنيه", parent=dialog)
                code_var.set("") 
                refresh_codes_list_action() 
                if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                    send_telegram_message(f"🔑 كود نقاط جديد '{code_to_add}' تم إنشاؤه بواسطة '{current_user}'.")
            except sqlite3.IntegrityError: messagebox.showerror("خطأ", f"الكود '{code_to_add}' موجود بالفعل.", parent=dialog)
            except sqlite3.Error as e: logging.error(f"DB error adding bonus code '{code_to_add}': {e}", exc_info=True); messagebox.showerror("خطأ قاعدة بيانات", f"لم يتم إضافة الكود: {e}", parent=dialog)
            finally:
                if conn: conn.close()
        ttk.Button(add_frame, text="إضافة الكود للنظام", command=add_new_code_action, style="Green.TButton").pack(side=tk.LEFT, padx=5)

        list_frame = ttk.Frame(dialog, padding=10, style="TFrame")
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        cols = ("ID", "الكود", "نشط/مُباع؟", "السعر", "بيع بواسطة", "تاريخ البيع", "العميل المرتبط")
        
        # Bonus Treeview Style (ensure defined or use default)
        tree_style_name = "Bonus.Treeview"
        if tree_style_name not in self.style.layout(tree_style_name): # A way to check if style exists
            self.style.configure(tree_style_name, rowheight=25, font=self.label_font if hasattr(self, 'label_font') else None, 
                                 background=self.frame_bg_color if hasattr(self, 'frame_bg_color') else "#4a4a4a", 
                                 foreground=self.text_color if hasattr(self, 'text_color') else "white",
                                 fieldbackground=self.frame_bg_color if hasattr(self, 'frame_bg_color') else "#4a4a4a")
            self.style.configure(f"{tree_style_name}.Heading", font=self.report_tab_font if hasattr(self, 'report_tab_font') else None, 
                                 background="#334", foreground=self.accent_color if hasattr(self, 'accent_color') else "yellow")
            self.style.map(tree_style_name, background=[('selected', self.button_blue if hasattr(self, 'button_blue') else "blue")])
            
        bonus_codes_tree_view = ttk.Treeview(list_frame, columns=cols, show='headings', style=tree_style_name)
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=bonus_codes_tree_view.yview); vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=bonus_codes_tree_view.xview); hsb.pack(side='bottom', fill='x')
        bonus_codes_tree_view.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        bonus_codes_tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        col_widths = {"ID": 40, "الكود": 120, "نشط/مُباع؟": 90, "السعر": 70, "بيع بواسطة":110, "تاريخ البيع":120, "العميل المرتبط":110}
        for col in cols: bonus_codes_tree_view.heading(col, text=col, anchor=tk.CENTER); bonus_codes_tree_view.column(col, width=col_widths.get(col, 90), anchor=tk.CENTER, stretch=tk.YES)
        def refresh_codes_list_action():
            for item in bonus_codes_tree_view.get_children(): bonus_codes_tree_view.delete(item)
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT id, code, is_active, purchase_price, sold_by_employee, sold_at, linked_customer_name FROM bonus_codes ORDER BY created_at DESC")
                for idx, row in enumerate(cursor.fetchall()):
                    (id_v, code_v, active_v, price_v, sold_by_v, sold_at_v, customer_v) = row
                    active_txt = "نعم (مُباع)" if active_v else "لا (غير مُباع)"
                    tag = 'activerow' if active_v else ('evenrow' if idx % 2 == 0 else 'oddrow')
                    bonus_codes_tree_view.insert("", tk.END, values=(id_v, code_v, active_txt, f"{price_v:.2f}" if price_v else "-", sold_by_v or "-", sold_at_v or "-", customer_v or "-"), tags=(tag,))
                bonus_codes_tree_view.tag_configure('oddrow', background=self.frame_bg_color if hasattr(self,'frame_bg_color') else '#5a5a5a', foreground=self.text_color if hasattr(self,'text_color') else 'white') # Adjusted oddrow
                bonus_codes_tree_view.tag_configure('evenrow', background=self.frame_bg_color if hasattr(self,'frame_bg_color') else '#4a4a4a', foreground=self.text_color if hasattr(self,'text_color') else 'white') # Even if frame_bg is dark, ensure contrast
                bonus_codes_tree_view.tag_configure('activerow', background=self.button_green if hasattr(self,'button_green') else 'green', foreground='white')
            except sqlite3.Error as e: logging.error(f"DB error fetching bonus codes: {e}", exc_info=True); messagebox.showerror("خطأ جلب بيانات", f"لا يمكن جلب أكواد النقاط: {e}", parent=dialog)
            finally:
                if conn: conn.close()
        refresh_codes_list_action()
        bottom_button_frame = ttk.Frame(dialog, padding=(10,5), style="TFrame"); bottom_button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(bottom_button_frame, text="إغلاق النافذة", command=dialog.destroy, style="Red.TButton").pack(side=tk.RIGHT, padx=10, pady=5)
        dialog.wait_window()
    def fetch_sessions_for_day(self, target_date=None):
        """
        تجلب كل الجلسات المنتهية لتاريخ معين من قاعدة البيانات.
        إذا لم يتم تحديد تاريخ، تستخدم تاريخ اليوم.
        """
        if target_date is None:
            target_date = date.today() # تاريخ اليوم
        
        conn = None
        results = []
        try:
            conn = sqlite3.connect(DB_NAME) # DB_NAME يجب أن يكون مُعرفًا عالميًا
            conn.text_factory = str # لضمان أن النصوص تُقرأ كنصوص
            cursor = conn.cursor()
            # جلب الجلسات التي لها وقت انتهاء (أي أنها مكتملة) لتاريخ محدد
            cursor.execute("""
                SELECT device, customer, start_time, end_time, duration, cost, session_type,
                       shift_employee, item_cost, drinks, time_option
                FROM sessions 
                WHERE date(start_time) = date(?) AND end_time IS NOT NULL 
                ORDER BY start_time
            """, (target_date.isoformat(),)) # استخدام .isoformat() للتاريخ
            results = cursor.fetchall()
        except sqlite3.Error as e_fetch_sessions: # تم تغيير اسم متغير الخطأ
            logging.error(f"Error fetching sessions for date {target_date.isoformat()}: {e_fetch_sessions}", exc_info=True)
            # لا تظهر messagebox من هنا مباشرة إذا كان يمكن استدعاء هذه الدالة من أماكن لا تحتوي على root
            # بدلاً من ذلك، يمكن للدالة المستدعية (show_daily_report) التعامل مع عرض الخطأ.
            # لكن بما أن show_daily_report تستدعيها، يمكن إبقاء الـ messagebox هناك.
            if self.root and self.root.winfo_exists(): # تحقق من وجود النافذة الجذرية
                 messagebox.showerror("Database Error", f"Error fetching report data for {target_date.isoformat()}:\n{e_fetch_sessions}", parent=self.root)
        finally:
            if conn:
                conn.close()
        return results
# داخل فئة CyberCafeApp

    def show_bonus_code_usage_dialog(self):
        """
        يعرض نافذة تحتوي على تفاصيل استخدام أكواد النقاط.
        """
        dialog = Toplevel(self.root)
        dialog.title("تقرير استخدام أكواد النقاط")
        dialog.geometry("850x500") # نافذة أوسع قليلاً
        dialog.configure(bg=getattr(self, 'bg_color', "#3a3a3a"))
        dialog.transient(self.root)
        dialog.grab_set()

        main_dialog_frame = ttk.Frame(dialog, padding=15, style="TFrame")
        main_dialog_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_dialog_frame, text="تفاصيل الأكواد المباعة والمستخدمة", 
                  font=getattr(self, 'frame_font', ('Segoe UI', 14, 'bold')), 
                  style="Top.TLabel").pack(pady=(0,15))

        tree_container_frame = ttk.Frame(main_dialog_frame, style="TFrame")
        tree_container_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("الكود", "مُباع؟", "العميل المرتبط", "بيع بواسطة", "تاريخ البيع", "استُخدم في جلسة ID", "النقاط المكتسبة بالجلسة")
        
        code_usage_tree = ttk.Treeview(tree_container_frame, columns=cols, show='headings', style="Treeview")
        
        vsb = ttk.Scrollbar(tree_container_frame, orient="vertical", command=code_usage_tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(tree_container_frame, orient="horizontal", command=code_usage_tree.xview)
        hsb.pack(side='bottom', fill='x')
        code_usage_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        code_usage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        col_widths = {"الكود": 100, "مُباع؟": 60, "العميل المرتبط": 120, "بيع بواسطة": 100, 
                      "تاريخ البيع": 120, "استُخدم في جلسة ID": 100, "النقاط المكتسبة بالجلسة": 120}
        for col_name_iter in cols:
            anchor_val = tk.W if col_name_iter in ["الكود", "العميل المرتبط", "بيع بواسطة"] else tk.CENTER
            code_usage_tree.heading(col_name_iter, text=col_name_iter, anchor=anchor_val)
            code_usage_tree.column(col_name_iter, width=col_widths.get(col_name_iter, 90), anchor=anchor_val, stretch=tk.YES)

        def refresh_code_usage_list():
            for item in code_usage_tree.get_children():
                code_usage_tree.delete(item)
            
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                # استعلام يربط بين bonus_codes و sessions
                cursor.execute("""
                    SELECT 
                        bc.code, bc.is_active, bc.linked_customer_name, bc.sold_by_employee, bc.sold_at,
                        bc.session_id_earned_on, s.points_earned_this_session
                    FROM bonus_codes bc
                    LEFT JOIN sessions s ON bc.session_id_earned_on = s.id
                    ORDER BY bc.created_at DESC
                """)
                all_code_data = cursor.fetchall()
                
                if not all_code_data:
                    code_usage_tree.insert("", tk.END, values=("لا توجد أكواد في النظام.", "", "", "", "", "", ""))
                else:
                    for row_idx, data_row in enumerate(all_code_data):
                        (code, is_act, linked_cust, sold_by, sold_time, session_id_used, points_in_session) = data_row
                        active_disp = "نعم" if is_act else "لا"
                        tag = 'evenrow_report' if row_idx % 2 == 0 else 'oddrow_report'
                        
                        points_display = points_in_session if points_in_session is not None else "-"
                        if is_act and session_id_used is None and points_in_session is None: # كود مُباع ولم يُستخدم بعد
                            points_display = "لم يُستخدم بعد"

                        code_usage_tree.insert("", tk.END, values=(
                            code, active_disp, linked_cust or "-", sold_by or "-", sold_time or "-",
                            session_id_used or "-", points_display
                        ), tags=(tag,))
                
                # (configure tags as in show_all_customer_points_dialog)
            except sqlite3.Error as e_fetch_code_usage:
                messagebox.showerror("خطأ قاعدة بيانات", f"لا يمكن جلب بيانات استخدام الأكواد: {e_fetch_code_usage}", parent=dialog)
                logging.error(f"DB error fetching code usage: {e_fetch_code_usage}", exc_info=True)
            finally:
                if conn: conn.close()

        refresh_code_usage_list()

        bottom_buttons_frame_cu = ttk.Frame(main_dialog_frame, padding=(0,10,0,0), style="TFrame")
        bottom_buttons_frame_cu.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(bottom_buttons_frame_cu, text="تحديث", command=refresh_code_usage_list, style="Blue.TButton").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(bottom_buttons_frame_cu, text="إغلاق", command=dialog.destroy, style="Red.TButton").pack(side=tk.RIGHT, padx=10, pady=5)
        
        dialog.wait_window()
# داخل فئة CyberCafeApp
# LOCATED IN: CyberCafeApp class, process_telegram_actions(self) method

    def process_telegram_actions(self):
        global current_user, CHAT_ID # Ensure CHAT_ID is accessible for comparing reply target
        try:
            while not TELEGRAM_ACTION_QUEUE.empty():
                action_data = TELEGRAM_ACTION_QUEUE.get_nowait()
                logging.info(f"Dequeued Telegram action: {action_data}")

                action_type = action_data.get("action_type")

                if action_type == "SHOW_CHECKOUT_SUMMARY":
                    # Your existing logic for checkout summary
                    logging.info("Processing SHOW_CHECKOUT_SUMMARY action from Telegram queue.")
                    if current_user: # Ensure someone is logged in to the app
                        self.show_checkout_summary(triggered_by_telegram=True)
                        # Bring window to front if possible
                        if self.root and self.root.winfo_exists():
                            try:
                                if self.root.state() == 'withdrawn': self.root.deiconify()
                                self.root.lift()
                                self.root.focus_force()
                            except tk.TclError: pass 
                    else:
                        logging.warning("Cannot show checkout summary via Telegram: No user logged into app.")
                        # Feedback to Telegram user (using target_chat_id if available)
                        reply_to = action_data.get("reply_chat_id", CHAT_ID)
                        send_telegram_message("⚠️ Cannot process checkout: No user logged into the main application.", target_chat_id=reply_to)

                elif action_type == "REMOTE_NEW_SESSION":
                    logging.info(f"Processing REMOTE_NEW_SESSION request: {action_data}")
                    device_name = action_data.get("device_name")
                    telegram_reply_chat_id = action_data.get("reply_chat_id")
                    feedback_message = ""

                    try:
                        if not device_name: # Should be validated by handler, but check again
                            raise ValueError("Device name missing in request.")
                        if device_name in self.sessions:
                            raise ValueError(f"Device {device_name} is already busy.")
                        if not current_user: # Global current_user from Tkinter app login
                            raise ValueError("No employee is logged into the CyberCafe system to own this session.")

                        start_time = datetime.now()
                        intended_end_time = None
                        time_option_str = action_data.get("time_option_str")
                        manual_minutes = action_data.get("manual_minutes_val")

                        if time_option_str == "30 Minutes":
                            intended_end_time = start_time + timedelta(minutes=30)
                        elif time_option_str == "1 Hour":
                            intended_end_time = start_time + timedelta(hours=1)
                        elif time_option_str == "2 Hours":
                            intended_end_time = start_time + timedelta(hours=2)
                        elif time_option_str == "Manual Time" and isinstance(manual_minutes, int) and manual_minutes > 0:
                            intended_end_time = start_time + timedelta(minutes=manual_minutes)
                        elif time_option_str != "Open Session": # If not open and not any other valid timed option
                            raise ValueError(f"Invalid time option processed: {time_option_str}")
                        
                        session_details_for_app = {
                            'start_time': start_time,
                            'customer_name': action_data.get("customer_name_str"), # Can be None
                            'session_type': action_data.get("session_type"),
                            'time_option': time_option_str, # The descriptive string
                            'intended_end_time': intended_end_time,
                            'bonus_code': action_data.get("bonus_code_str"), # Can be None
                            'is_free_session': False, 
                            'redeemed_points': 0,
                            # item_cost and drinks will default if not provided to start_session
                        }
                        
                        self.start_session(device_name, session_details_for_app)
                        # self.start_session already sends a Telegram notification to the main CHAT_ID.
                        # Send a specific confirmation to the user who issued the command IF their chat is different.
                        feedback_message = f"✅ Session successfully started on {device_name} for {time_option_str}."
                        if telegram_reply_chat_id and str(telegram_reply_chat_id) != str(CHAT_ID):
                            send_telegram_message(feedback_message, target_chat_id=telegram_reply_chat_id)
                        # If it's the same chat, the main notification from start_session might be enough,
                        # or you might want to suppress the general one if a targeted one is sent.

                    except ValueError as ve:
                        error_message = f"⚠️ Failed to start session on {device_name}: {ve}"
                        logging.warning(error_message)
                        feedback_message = error_message # Send this error back
                        if telegram_reply_chat_id: # Always send error feedback to the command issuer
                             send_telegram_message(feedback_message, target_chat_id=telegram_reply_chat_id)
                        elif callable(send_telegram_message): # Fallback to main chat if no reply_chat_id (should not happen)
                             send_telegram_message(feedback_message)


                    except Exception as e_proc_remote_sess:
                        error_message = f"⚠️ Internal error starting session on {device_name}."
                        logging.error(f"Error processing REMOTE_NEW_SESSION for {device_name}: {e_proc_remote_sess}", exc_info=True)
                        feedback_message = error_message
                        if telegram_reply_chat_id:
                             send_telegram_message(feedback_message, target_chat_id=telegram_reply_chat_id)
                        elif callable(send_telegram_message):
                             send_telegram_message(feedback_message)


                # ... (any other action types you might have) ...
                TELEGRAM_ACTION_QUEUE.task_done()
        except queue.Empty:
            pass # No actions in queue, which is normal
        except Exception as e_process_q_loop:
            logging.error(f"Error in Telegram action processing loop: {e_process_q_loop}", exc_info=True)
        
        # Re-schedule this method to run again
        if hasattr(self, 'root') and self.root and self.root.winfo_exists():
             self.check_telegram_queue_job = self.root.after(200, self.schedule_telegram_queue_check) # Make sure this re-scheduling is happening correctly
        else:
            logging.info("Process Telegram Actions: Root window closed, stopping queue check.")
            self.check_telegram_queue_job = None
    def show_all_customer_points_dialog(self):
        """
        يعرض نافذة تحتوي على قائمة بجميع العملاء المسجلين وإجمالي نقاطهم.
        يمكن للأدمن والموظف (إذا سمحت بذلك في _rebuild_control_panel) الوصول إليها.
        """
        # يمكنك إضافة تحقق من الصلاحيات هنا إذا أردت، على سبيل المثال:
        # if not current_user: # current_user يجب أن يكون مُعرفًا عالميًا
        #     messagebox.showerror("Error", "No user logged in.", parent=self.root)
        #     return
        # أو إذا كانت للأدمن فقط:
        # if current_user != ADMIN_USERNAME:
        #     messagebox.showerror("Permission Denied", "Access restricted to administrators.", parent=self.root)
        #     return

        dialog = Toplevel(self.root)
        dialog.title("أرصدة نقاط العملاء")
        dialog.geometry("550x480") # يمكن تعديل الحجم حسب الحاجة
        dialog.configure(bg=getattr(self, 'bg_color', "#3a3a3a")) # استخدام لون الخلفية المعرف
        dialog.transient(self.root)
        dialog.grab_set()

        # إطار رئيسي داخل النافذة المنبثقة
        main_dialog_frame = ttk.Frame(dialog, padding=10, style="TFrame")
        main_dialog_frame.pack(fill=tk.BOTH, expand=True)

        # عنوان أعلى الجدول
        ttk.Label(main_dialog_frame, text="قائمة العملاء ونقاطهم", 
                  font=getattr(self, 'frame_font', ('Segoe UI', 12, 'bold')), 
                  style="Top.TLabel").pack(pady=(0,10))


        # إطار للجدول (Treeview) وأشرطة التمرير
        tree_container_frame = ttk.Frame(main_dialog_frame, style="TFrame") # تم تغيير الاسم
        tree_container_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("اسم العميل", "إجمالي النقاط")
        
        # استخدام النمط العام "Treeview" الذي يفترض أنه مُعرّف بشكل جيد في __init__
        # مع الخطوط والألوان المناسبة.
        customer_points_tree = ttk.Treeview(tree_container_frame, columns=cols, show='headings', style="Treeview")
        
        vsb = ttk.Scrollbar(tree_container_frame, orient="vertical", command=customer_points_tree.yview)
        vsb.pack(side=tk.RIGHT, fill='y')
        hsb = ttk.Scrollbar(tree_container_frame, orient="horizontal", command=customer_points_tree.xview)
        hsb.pack(side=tk.BOTTOM, fill='x')
        customer_points_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        customer_points_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # تحديد عرض الأعمدة ومحاذاة النص
        col_widths = {"اسم العميل": 300, "إجمالي النقاط": 100}
        customer_points_tree.heading("اسم العميل", text="اسم العميل", anchor=tk.W) # W for west (left align)
        customer_points_tree.column("اسم العميل", width=col_widths["اسم العميل"], anchor=tk.W, stretch=tk.YES)
        
        customer_points_tree.heading("إجمالي النقاط", text="إجمالي النقاط", anchor=tk.CENTER)
        customer_points_tree.column("إجمالي النقاط", width=col_widths["إجمالي النقاط"], anchor=tk.CENTER, stretch=tk.YES)

        def refresh_customer_points_list_action(): # تم تغيير الاسم للوضوح
            # مسح البيانات القديمة من الجدول
            for item in customer_points_tree.get_children():
                customer_points_tree.delete(item)
            
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME) # DB_NAME يجب أن يكون مُعرفًا عالميًا
                cursor = conn.cursor()
                # جلب العملاء ونقاطهم، مع ترتيب تنازلي بالنقاط ثم أبجدي بالاسم
                cursor.execute("SELECT customer_name, points FROM customer_points ORDER BY points DESC, customer_name ASC")
                all_customer_points_data = cursor.fetchall() # تم تغيير الاسم
                
                if not all_customer_points_data:
                    customer_points_tree.insert("", tk.END, values=("لا يوجد عملاء لديهم نقاط مسجلة حاليًا.", ""))
                else:
                    for row_idx, (name, pts) in enumerate(all_customer_points_data):
                        # استخدام tags لتلوين الأسطر بالتناوب (يفترض أن هذه tags مُعرفة في نمط Treeview)
                        tag_name = 'evenrow' if row_idx % 2 == 0 else 'oddrow' 
                        customer_points_tree.insert("", tk.END, values=(name, pts), tags=(tag_name,))
                
                # إذا كنت لم تُعرف tags 'evenrow' و 'oddrow' للنمط "Treeview" العام في __init__,
                # يمكنك تعريفها هنا بشكل خاص لهذا الـ Treeview:
                # customer_points_tree.tag_configure('oddrow', background=getattr(self, 'frame_bg_color_odd', '#5a5a5a'), foreground=getattr(self, 'text_color', 'white'))
                # customer_points_tree.tag_configure('evenrow', background=getattr(self, 'frame_bg_color_even', '#4a4a4a'), foreground=getattr(self, 'text_color', 'white'))
                # أو تأكد من أن نمط "Treeview" في __init__ يتضمن هذه tags.

            except sqlite3.Error as e_fetch_cust_pts:
                messagebox.showerror("خطأ في قاعدة البيانات", f"لا يمكن جلب قائمة نقاط العملاء:\n{e_fetch_cust_pts}", parent=dialog)
                logging.error(f"DB error fetching customer points list: {e_fetch_cust_pts}", exc_info=True)
            finally:
                if conn: conn.close()

        refresh_customer_points_list_action() # تحميل البيانات عند فتح النافذة

        # إطار الأزرار السفلية
        bottom_buttons_frame = ttk.Frame(main_dialog_frame, padding=(0,10,0,0), style="TFrame") # تم تغيير الاسم
        bottom_buttons_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # زر تحديث القائمة
        ttk.Button(bottom_buttons_frame, text="تحديث القائمة", command=refresh_customer_points_list_action, style="Blue.TButton").pack(side=tk.LEFT, padx=10, pady=5)
        
        # زر الإغلاق
        ttk.Button(bottom_buttons_frame, text="إغلاق", command=dialog.destroy, style="Red.TButton").pack(side=tk.RIGHT, padx=10, pady=5)
        
        dialog.wait_window()


        def refresh_customer_points_list():
            for item in customer_points_tree.get_children():
                customer_points_tree.delete(item)
            
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT customer_name, points FROM customer_points ORDER BY points DESC, customer_name ASC")
                all_customer_points = cursor.fetchall()
                
                for row_idx, (name, pts) in enumerate(all_customer_points):
                    tag = 'evenrow_report' if row_idx % 2 == 0 else 'oddrow_report' # استخدام نفس tags التقرير
                    customer_points_tree.insert("", tk.END, values=(name, pts), tags=(tag,))
                
                # تأكد أن tags التقرير مُعرفة (عادةً في show_daily_report أو يمكنك نسخها هنا)
                # customer_points_tree.tag_configure('oddrow_report', ...)
                # customer_points_tree.tag_configure('evenrow_report', ...)
            except sqlite3.Error as e_fetch_cust_pts:
                messagebox.showerror("خطأ قاعدة بيانات", f"لا يمكن جلب نقاط العملاء: {e_fetch_cust_pts}", parent=dialog)
                logging.error(f"DB error fetching customer points: {e_fetch_cust_pts}", exc_info=True)
            finally:
                if conn: conn.close()

        refresh_customer_points_list()

        bottom_button_frame = ttk.Frame(dialog, padding=(10,5), style="TFrame")
        bottom_button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(bottom_button_frame, text="إغلاق", command=dialog.destroy, style="Red.TButton").pack(side=tk.RIGHT, padx=10, pady=5)
        
        dialog.wait_window()
    def show_daily_report(self):
        """
        يعرض نافذة تحتوي على تقرير بالجلسات اليومية والإجماليات.
        هذه الوظيفة متاحة للأدمن فقط.
        """
        if current_user != ADMIN_USERNAME: # current_user و ADMIN_USERNAME يجب أن يكونا مُعرفين عالميًا
            messagebox.showerror("Permission Denied", "Only administrators can view the daily report.", parent=self.root)
            return

        target_date = date.today() # تقرير اليوم الحالي
        report_data = self.fetch_sessions_for_day(target_date) # استدعاء الدالة لجلب البيانات

        report_window = Toplevel(self.root)
        report_window.title(f"Daily Report - {target_date.strftime('%Y-%m-%d')}")
        report_window.geometry("1000x600") # حجم نافذة التقرير
        report_window.configure(bg=self.bg_color if hasattr(self, 'bg_color') else "#3a3a3a")
        report_window.transient(self.root)
        report_window.grab_set()

        # إطار يحتوي على الـ Treeview وأشرطة التمرير
        tree_frame = ttk.Frame(report_window, padding=10, style="TFrame") # استخدام نمط TFrame
        tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # نمط الـ Treeview (يفترض أن يكون معرفًا في __init__ أو هنا)
        # إذا لم يكن "Report.Treeview" معرفًا، يمكنك استخدام "Treeview" الافتراضي أو تعريف نمط جديد.
        # لقد قمنا بتعريف "Treeview" و "Treeview.Heading" في __init__
        tree_report_style_name = "Report.Treeview" # يمكنك استخدام هذا أو "Treeview" مباشرة
        # يمكنك إضافة هذا النمط إذا أردت تخصيصًا إضافيًا للتقرير
        # self.style.configure(tree_report_style_name, ...)
        # self.style.configure(f"{tree_report_style_name}.Heading", ...)
        
        cols = ("Device", "Customer", "Start", "End", "Duration (m)", "Type", "Items", "Item Cost", "Total Cost", "Employee", "Time Opt")
        report_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', style="Treeview") # استخدام النمط العام "Treeview"

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=report_tree.yview)
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=report_tree.xview)
        hsb.pack(side='bottom', fill='x')
        report_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # تحديد عرض الأعمدة وعناوينها
        col_widths = {
            "Device": 70, "Customer": 120, "Start": 80, "End": 80, 
            "Duration (m)": 80, "Type": 90, "Items": 150, 
            "Item Cost": 80, "Total Cost": 90, "Employee": 100, "Time Opt": 100
        }
        for col_name_iter in cols: # تم تغيير اسم المتغير لتجنب التعارض
            report_tree.heading(col_name_iter, text=col_name_iter, anchor=tk.CENTER)
            report_tree.column(col_name_iter, width=col_widths.get(col_name_iter, 80), anchor=tk.CENTER, stretch=tk.YES)

        total_revenue_report = 0.0
        total_item_revenue_report = 0.0
        total_duration_minutes_report = 0.0

        # إضافة البيانات إلى الـ Treeview
        for i, db_row in enumerate(report_data): # تم تغيير اسم المتغير row إلى db_row
            # (device, customer, start_iso, end_iso, duration_min, cost, s_type, employee, item_cost, drinks, time_opt)
            # تأكد أن ترتيب الأعمدة هنا يطابق ترتيبها في استعلام SELECT
            
            # تحويل التواريخ من ISO format إلى H:M:S للعرض
            try: start_str_display = datetime.fromisoformat(db_row[2]).strftime('%H:%M:%S') if db_row[2] else "-"
            except (ValueError, TypeError): start_str_display = str(db_row[2])[:19] if db_row[2] else "-"; logging.warning(f"Could not parse start_time ISO: {db_row[2]}")
            try: end_str_display = datetime.fromisoformat(db_row[3]).strftime('%H:%M:%S') if db_row[3] else "-"
            except (ValueError, TypeError): end_str_display = str(db_row[3])[:19] if db_row[3] else "-"; logging.warning(f"Could not parse end_time ISO: {db_row[3]}")

            duration_display = f"{db_row[4]:.0f}" if db_row[4] is not None else "0"
            customer_display_report = db_row[1] if db_row[1] else "-"
            drinks_display_report = db_row[9] if db_row[9] else "-"
            item_cost_val_report = db_row[8] if db_row[8] is not None else 0.0
            cost_val_report = db_row[5] if db_row[5] is not None else 0.0
            
            # تحديد tag للسطر (لتلوين الأسطر الفردية/الزوجية إذا أردت)
            tag = 'evenrow_report' if i % 2 == 0 else 'oddrow_report'
            report_tree.insert("", END, values=(
                db_row[0], customer_display_report, start_str_display, end_str_display, duration_display,
                db_row[6], drinks_display_report, f"{item_cost_val_report:.2f}", f"{cost_val_report:.2f}",
                db_row[7] if db_row[7] else "-", db_row[10] if db_row[10] else "-"
            ), tags=(tag,))
            
            total_revenue_report += cost_val_report
            total_item_revenue_report += item_cost_val_report
            if db_row[4] is not None: total_duration_minutes_report += db_row[4]

        # تلوين الأسطر (تأكد أن لديك هذه الأنماط أو قم بتعريفها)
        report_tree.tag_configure('oddrow_report', background='#5a5a5a', foreground=getattr(self, 'text_color', 'white'))
        report_tree.tag_configure('evenrow_report', background=getattr(self, 'frame_bg_color', '#000000'), foreground=getattr(self, 'text_color', 'white'))

        # إطار لعرض الإجماليات أسفل التقرير
        totals_frame_report = ttk.Frame(report_window, padding=(10, 5), style="TFrame") # تم تغيير الاسم
        totals_frame_report.pack(side=tk.BOTTOM, fill=tk.X)

        total_time_revenue_report = total_revenue_report - total_item_revenue_report
        total_hours_report = total_duration_minutes_report / 60.0
        
        # استخدام Top.TLabel للإجماليات ليكون لون الخلفية متناسقًا مع خلفية النافذة
        font_for_totals = self.report_total_font if hasattr(self, 'report_total_font') else ('Segoe UI', 11, 'bold')
        ttk.Label(totals_frame_report, text=f"Total Sessions: {len(report_data)}", style="Top.TLabel", font=font_for_totals).pack(side=tk.LEFT, padx=10)
        ttk.Label(totals_frame_report, text=f"Total Time: {total_hours_report:.1f} hrs", style="Top.TLabel", font=font_for_totals).pack(side=tk.LEFT, padx=10)
        ttk.Label(totals_frame_report, text=f"Time Revenue: {total_time_revenue_report:.2f} EGP", style="Top.TLabel", foreground=getattr(self, 'timer_yellow', 'yellow'), font=font_for_totals).pack(side=tk.LEFT, padx=10)
        ttk.Label(totals_frame_report, text=f"Item Revenue: {total_item_revenue_report:.2f} EGP", style="Top.TLabel", foreground=getattr(self, 'timer_yellow', 'yellow'), font=font_for_totals).pack(side=tk.LEFT, padx=10)
        ttk.Label(totals_frame_report, text=f"TOTAL REVENUE: {total_revenue_report:.2f} EGP", style="Top.TLabel", foreground=getattr(self, 'accent_color', 'gold'), font=font_for_totals).pack(side=tk.RIGHT, padx=10)
        
        report_window.wait_window() # لجعل النافذة مودال

    # ... (باقي دوال الفئة CyberCafeApp) ...
    def export_data_to_excel(self):
        """
        يُصدِّر بيانات الجلسات والموظفين إلى ملف Excel.
        هذه الوظيفة متاحة للأدمن فقط.
        """
        if current_user != ADMIN_USERNAME: # التحقق من أن المستخدم الحالي هو الأدمن
            messagebox.showerror("Permission Denied", "Only administrators can export data.", parent=self.root)
            return

        # اسم الملف الافتراضي المقترح
        default_filename = f"MIX GAME_cafe_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # فتح حوار حفظ الملف
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Exported Data As",
            initialfile=default_filename,
            parent=self.root
        )

        if not filename: # إذا ألغى المستخدم الحوار
            logging.info("Excel data export cancelled by user.")
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_NAME) # DB_NAME يجب أن يكون مُعرفًا عالميًا
            logging.info(f"Starting data export to Excel file: {filename}...")

            # قراءة جدول الجلسات وجدول الموظفين (بدون كلمة المرور) إلى pandas DataFrames
            sessions_df = pd.read_sql_query("SELECT * FROM sessions ORDER BY start_time", conn)
            # جلب فقط الأعمدة التي لا تحتوي على معلومات حساسة مثل كلمة المرور
            employees_df = pd.read_sql_query("SELECT id, username FROM employees", conn) 
            # يمكنك إضافة جدول أكواد النقاط وجدول نقاط العملاء وجدول المصروفات إذا أردت
            bonus_codes_df = pd.read_sql_query("SELECT * FROM bonus_codes", conn)
            customer_points_df = pd.read_sql_query("SELECT * FROM customer_points", conn)
            shift_expenses_df = pd.read_sql_query("SELECT * FROM shift_expenses ORDER BY logged_at", conn)


            # كتابة الـ DataFrames إلى صفحات مختلفة في ملف Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                sessions_df.to_excel(writer, sheet_name='Sessions', index=False)
                employees_df.to_excel(writer, sheet_name='Employees', index=False)
                bonus_codes_df.to_excel(writer, sheet_name='BonusCodes', index=False)
                customer_points_df.to_excel(writer, sheet_name='CustomerPoints', index=False)
                shift_expenses_df.to_excel(writer, sheet_name='ShiftExpenses', index=False)
            
            num_sessions = len(sessions_df) if not sessions_df.empty else 0
            num_employees = len(employees_df) if not employees_df.empty else 0
            logging.info(f"Data successfully exported to {filename} ({num_sessions} sessions, {num_employees} employees, and other tables).")
            messagebox.showinfo("Export Successful", f"Data has been successfully exported to:\n{filename}", parent=self.root)
            
            if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                send_telegram_message(f"📊 تم تصدير بيانات النظام إلى ملف Excel بواسطة الأدمن '{current_user}'.")

        except ImportError: # إذا لم يتم تثبيت pandas أو openpyxl
            logging.error("Export to Excel failed: 'pandas' or 'openpyxl' library not found.")
            messagebox.showerror("Export Error", 
                                 "Exporting data to Excel requires 'pandas' and 'openpyxl' libraries.\n"
                                 "Please install them using:\n"
                                 "pip install pandas openpyxl", 
                                 parent=self.root)
        except sqlite3.Error as e_sql_export: # لأخطاء قاعدة البيانات أثناء القراءة
            logging.error(f"Database error during Excel export: {e_sql_export}", exc_info=True)
            messagebox.showerror("Export Error", f"Database error during export: {e_sql_export}", parent=self.root)
        except Exception as e_export: # لأي أخطاء أخرى غير متوقعة
            logging.error(f"An unexpected error occurred during Excel export: {e_export}", exc_info=True)
            messagebox.showerror("Export Error", f"An unexpected error occurred during export:\n{e_export}", parent=self.root)
        finally:
            if conn:
                conn.close()

    # ... (باقي دوال الفئة CyberCafeApp) ...
    def manage_employees(self):
        """
        يعرض نافذة لإدارة حسابات الموظفين (إضافة، حذف، تغيير كلمة المرور).
        هذه الوظيفة متاحة للأدمن فقط.
        """
        if current_user != ADMIN_USERNAME: # التحقق من أن المستخدم الحالي هو الأدمن
            messagebox.showerror("Permission Denied", "Access restricted to administrators.", parent=self.root)
            return

        manage_window = Toplevel(self.root)
        manage_window.title("Manage Employees (Admin)")
        manage_window.geometry("550x450") # يمكن تعديل الحجم
        # تأكد أن self.bg_color, self.text_color, self.frame_font, self.button_font, self.dialog_label_font, self.button_blue
        # مُعرفة في self.__init__
        manage_window.configure(bg=getattr(self, 'bg_color', "#3a3a3a"))
        manage_window.transient(self.root)
        manage_window.grab_set()
        manage_window.protocol("WM_DELETE_WINDOW", manage_window.destroy)

        m_style = ttk.Style(manage_window)
        m_style.theme_use('clam') 
        m_style.configure("Manage.TFrame", background=getattr(self, 'bg_color', "#000000"))
        m_style.configure("Manage.TLabel", background=getattr(self, 'bg_color', "#3a3a3a"), 
                          foreground=getattr(self, 'text_color', "white"), 
                          font=getattr(self, 'frame_font', ('Segoe UI', 12, 'bold')))
        m_style.configure("Manage.TButton", font=getattr(self, 'button_font', ('Segoe UI', 10)))
        # يمكنك إضافة أنماط ألوان للأزرار هنا باستخدام الألوان المعرفة في self، مثل:
        # m_style.configure("Green.Manage.TButton", background=getattr(self, 'button_green', 'green'), foreground='white')
        # m_style.map("Green.Manage.TButton", background=[('active', getattr(self, 'button_green_active', '#45a049'))])
        # ثم استخدم style="Green.Manage.TButton" للأزرار. للتبسيط، سنستخدم "Manage.TButton" حاليًا.

        list_frame = ttk.Frame(manage_window, padding=10, style="Manage.TFrame")
        list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="Current Employees:", style="Manage.TLabel").pack(anchor="w")
        
        listbox_frame = ttk.Frame(list_frame, style="Manage.TFrame")
        listbox_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        employee_listbox = Listbox(
            listbox_frame, 
            font=getattr(self, 'dialog_label_font', ('Segoe UI', 10)), 
            width=40, height=10,
            bg="#555", fg="white", 
            selectbackground=getattr(self, 'button_blue', "#0078D7"),
            relief=tk.SUNKEN, borderwidth=1,
            yscrollcommand=listbox_scrollbar.set, 
            exportselection=False
        )
        listbox_scrollbar.config(command=employee_listbox.yview)
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        employee_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def refresh_employee_list_action():
            employee_listbox.delete(0, END)
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME) 
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM employees ORDER BY username")
                employees_data = cursor.fetchall()
                for emp_row in employees_data:
                    employee_listbox.insert(END, emp_row[0])
            except sqlite3.Error as e_fetch_emp:
                logging.error(f"Error fetching employees list: {e_fetch_emp}", exc_info=True)
                messagebox.showerror("Error", f"Could not fetch employees: {e_fetch_emp}", parent=manage_window)
            finally:
                if conn: conn.close()
        
        refresh_employee_list_action()

        def get_selected_employee():
            selected_indices = employee_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select an employee from the list first.", parent=manage_window)
                return None
            return employee_listbox.get(selected_indices[0])

        action_buttons_frame = ttk.Frame(manage_window, padding=(10, 5), style="Manage.TFrame")
        action_buttons_frame.pack(fill=tk.X)

        def add_employee_action():
            username_new = simpledialog.askstring("Add Employee", "Enter new employee username:", parent=manage_window)
            if not username_new: return
            username_new = username_new.strip().lower()
            if not username_new: messagebox.showwarning("Invalid Input", "Username cannot be empty.", parent=manage_window); return
            if username_new == ADMIN_USERNAME: messagebox.showerror("Error", f"Username '{ADMIN_USERNAME}' is reserved.", parent=manage_window); return
            
            password_new = simpledialog.askstring("Set Password", f"Enter password for '{username_new}':", show='*', parent=manage_window)
            if password_new is None: return
            if not password_new: messagebox.showwarning("Password Required", "Password cannot be empty.", parent=manage_window); return
            
            password_new_hash = hash_password(password_new) # hash_password يجب أن تكون مُعرفة عالميًا
            if not password_new_hash: messagebox.showerror("Error", "Failed to hash password.", parent=manage_window); return
            
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO employees (username, password) VALUES (?, ?)", (username_new, password_new_hash))
                conn.commit()
                logging.info(f"Employee '{username_new}' added by admin '{current_user}'.")
                messagebox.showinfo("Success", f"Employee '{username_new}' added.", parent=manage_window)
                if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                    send_telegram_message(f"➕ Employee '{username_new}' added by admin '{current_user}'.")
                refresh_employee_list_action()
            except sqlite3.IntegrityError:
                logging.warning(f"Failed to add employee '{username_new}': Username already exists.")
                messagebox.showerror("Error", f"Username '{username_new}' already exists.", parent=manage_window)
            except sqlite3.Error as e_add_emp:
                logging.error(f"Error adding employee '{username_new}': {e_add_emp}", exc_info=True)
                messagebox.showerror("Database Error", f"Failed to add employee: {e_add_emp}", parent=manage_window)
            finally:
                if conn: conn.close()

        def remove_employee_action():
            username_to_remove_val = get_selected_employee()
            if not username_to_remove_val: return
            if username_to_remove_val == ADMIN_USERNAME: 
                messagebox.showerror("Action Denied", "Cannot remove the primary admin account.", parent=manage_window); return
            
            if messagebox.askyesno("Confirm Deletion", f"Delete employee '{username_to_remove_val}'?\nThis cannot be undone.", parent=manage_window, icon='warning'):
                conn = None
                try:
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM employees WHERE username = ?", (username_to_remove_val,))
                    conn.commit()
                    if cursor.rowcount > 0:
                        logging.info(f"Employee '{username_to_remove_val}' removed by admin '{current_user}'.")
                        messagebox.showinfo("Success", f"Employee '{username_to_remove_val}' removed.", parent=manage_window)
                        if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                            send_telegram_message(f"➖ Employee '{username_to_remove_val}' removed by admin '{current_user}'.")
                        refresh_employee_list_action()
                    else:
                        messagebox.showwarning("Not Found", f"Employee '{username_to_remove_val}' not found.", parent=manage_window)
                except sqlite3.Error as e_remove_emp:
                    logging.error(f"Error removing employee '{username_to_remove_val}': {e_remove_emp}", exc_info=True)
                    messagebox.showerror("Database Error", f"Failed to remove: {e_remove_emp}", parent=manage_window)
                finally:
                    if conn: conn.close()

        def change_password_action():
            username_to_change_pass = get_selected_employee()
            if not username_to_change_pass: return
            
            new_password_val = simpledialog.askstring("Change Password", f"Enter NEW password for '{username_to_change_pass}':", show='*', parent=manage_window)
            if new_password_val is None: return
            if not new_password_val: messagebox.showwarning("Password Required", "New password cannot be empty.", parent=manage_window); return
            
            new_password_hash_val = hash_password(new_password_val)
            if not new_password_hash_val: messagebox.showerror("Error", "Failed to hash new password.", parent=manage_window); return
            
            if not messagebox.askyesno("Confirm Change", f"Change password for '{username_to_change_pass}'?", parent=manage_window):
                return

            # ... (منطق التحقق من كلمة مرور الأدمن الافتراضية يمكن إضافته هنا إذا أردت) ...

            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("UPDATE employees SET password = ? WHERE username = ?", (new_password_hash_val, username_to_change_pass))
                conn.commit()
                if cursor.rowcount > 0:
                    logging.info(f"Password changed for '{username_to_change_pass}' by admin '{current_user}'.")
                    messagebox.showinfo("Success", f"Password for '{username_to_change_pass}' changed.", parent=manage_window)
                    if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                         send_telegram_message(f"🔑 Password for '{username_to_change_pass}' changed by admin '{current_user}'.")
                else:
                    messagebox.showwarning("Not Found", f"Employee '{username_to_change_pass}' not found.", parent=manage_window)
            except sqlite3.Error as e_change_pass:
                logging.error(f"Error changing password for '{username_to_change_pass}': {e_change_pass}", exc_info=True)
                messagebox.showerror("Database Error", f"Failed to change password: {e_change_pass}", parent=manage_window)
            finally:
                if conn: conn.close()

        # استخدام أنماط الأزرار المعرفة في __init__ إذا أمكن
        ttk.Button(action_buttons_frame, text="Add Employee", command=add_employee_action, style="Green.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(action_buttons_frame, text="Remove Selected", command=remove_employee_action, style="Red.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(action_buttons_frame, text="Change Password", command=change_password_action, style="Orange.TButton").pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(action_buttons_frame, text="Close", command=manage_window.destroy, style="Blue.TButton").pack(side=tk.RIGHT, padx=5, pady=5)

    # ... (باقي دوال الفئة CyberCafeApp) ...
    def sell_activate_bonus_code_dialog(self):
        dialog = Toplevel(self.root)
        dialog.title("بيع وتفعيل كود نقاط")
        dialog.geometry("650x500")
        dialog.configure(bg=self.bg_color if hasattr(self, 'bg_color') else "#3a3a3a")
        dialog.transient(self.root)
        dialog.grab_set()

        codes_frame = ttk.LabelFrame(dialog, text="الأكواد المتاحة للبيع (غير نشطة)", style="TLabelframe", padding=10)
        codes_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        codes_listbox_frame = ttk.Frame(codes_frame, style="TFrame"); codes_listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        codes_scrollbar = ttk.Scrollbar(codes_listbox_frame, orient=tk.VERTICAL)
        dialog_listbox_font = self.dialog_label_font if hasattr(self, 'dialog_label_font') else ('Segoe UI', 10)
        self.available_codes_listbox = Listbox(codes_listbox_frame, font=dialog_listbox_font, bg="#555", fg="white", selectbackground=self.button_blue if hasattr(self, 'button_blue') else "#0078D7", selectmode=SINGLE, yscrollcommand=codes_scrollbar.set, exportselection=False)
        codes_scrollbar.config(command=self.available_codes_listbox.yview); codes_scrollbar.pack(side=tk.RIGHT, fill='y')
        self.available_codes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        def refresh_available_codes_list_action():
            self.available_codes_listbox.delete(0, END)
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT code, purchase_price FROM bonus_codes WHERE is_active = 0 ORDER BY created_at DESC")
                codes = cursor.fetchall()
                if not codes: self.available_codes_listbox.insert(END, "لا توجد أكواد متاحة للبيع."); self.available_codes_listbox.config(state=tk.DISABLED)
                else:
                    self.available_codes_listbox.config(state=tk.NORMAL)
                    for code, price in codes: self.available_codes_listbox.insert(END, f"{code} (السعر: {price:.2f} جنيه)")
            except sqlite3.Error as e: logging.error(f"Error fetching available bonus codes: {e}", exc_info=True); messagebox.showerror("خطأ", "لا يمكن تحميل الأكواد.", parent=dialog)
            finally:
                if conn: conn.close()
        refresh_available_codes_list_action()

        action_frame = ttk.Frame(dialog, padding=10, style="TFrame"); action_frame.pack(pady=10, padx=10, fill=tk.X)
        label_font_local = self.label_font if hasattr(self, 'label_font') else ('Segoe UI', 10)
        ttk.Label(action_frame, text="اسم العميل:", style="Top.TLabel", font=label_font_local).pack(side=tk.LEFT, padx=(0,5)) # Top.TLabel for consistency
        customer_name_var = StringVar()
        customer_name_entry = ttk.Entry(action_frame, textvariable=customer_name_var, font=self.dialog_label_font if hasattr(self, 'dialog_label_font') else None, width=25)
        customer_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,10))
        def sell_and_activate_selected_code_action():
            idx = self.available_codes_listbox.curselection()
            if not idx: messagebox.showwarning("لم يتم التحديد", "اختر كود من القائمة.", parent=dialog); return
            item_text = self.available_codes_listbox.get(idx[0])
            if "لا توجد أكواد" in item_text: messagebox.showinfo("لا أكواد", "لا توجد أكواد للبيع.", parent=dialog); return
            code_sell = item_text.split(" ")[0]
            customer = customer_name_var.get().strip()
            if not customer: messagebox.showwarning("مطلوب اسم العميل", "أدخل اسم العميل.", parent=dialog); customer_name_entry.focus_set(); return
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT purchase_price FROM bonus_codes WHERE code = ? AND is_active = 0", (code_sell,))
                details = cursor.fetchone()
                if not details: messagebox.showerror("خطأ", f"الكود '{code_sell}' غير متاح.", parent=dialog); refresh_available_codes_list_action(); return
                price = details[0]
                time_now_iso = datetime.now().isoformat()
                cursor.execute("UPDATE bonus_codes SET is_active = 1, sold_by_employee = ?, sold_at = ?, linked_customer_name = ? WHERE code = ? AND is_active = 0", (current_user, time_now_iso, customer, code_sell))
                if cursor.rowcount == 0: messagebox.showerror("فشل", f"الكود '{code_sell}' لم يعد متاحًا.", parent=dialog)
                else:
                    conn.commit(); self.current_runtime_revenue += price
                    logging.info(f"Code '{code_sell}' sold for {price:.2f} by '{current_user}' to '{customer}'. Revenue: {self.current_runtime_revenue:.2f}")
                    messagebox.showinfo("نجاح", f"تم بيع وتفعيل: {code_sell}\nللعميل: {customer}\nالسعر: {price:.2f} ج.", parent=dialog)
                    if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                        send_telegram_message(f"💳 كود نقاط '{code_sell}' بيع وفُعِّل:\nموظف: {current_user}\nعميل: {customer}\nسعر: {price:.2f} ج")
                    customer_name_var.set("")
                refresh_available_codes_list_action()
            except sqlite3.Error as e: logging.error(f"DB error selling code '{code_sell}': {e}", exc_info=True); messagebox.showerror("خطأ", f"فشل بيع الكود: {e}", parent=dialog)
            finally:
                if conn: conn.close()
        ttk.Button(action_frame, text="بيع وتفعيل الكود المحدد", command=sell_and_activate_selected_code_action, style="Green.TButton").pack(side=tk.RIGHT, padx=(5,0))
        bottom_frame = ttk.Frame(dialog, padding=(10,5), style="TFrame"); bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(bottom_frame, text="إغلاق", command=dialog.destroy, style="Red.TButton").pack(side=tk.RIGHT, padx=10, pady=5)
        dialog.wait_window()

    def show_start_session_dialog(self, device_name):
        if device_name in self.sessions:
            messagebox.showwarning("الجلسة نشطة", f"توجد جلسة على {device_name}.", parent=self.root)
            return
        # StartSessionDialog class should be defined elsewhere
        dialog = StartSessionDialog(self.root, device_name) 
        if dialog.result:
            self.start_session(device_name, dialog.result)

# داخل فئة CyberCafeApp
# داخل فئة CyberCafeApp

   
        # ... (باقي كود start_session لإرسال إشعار تيليجرام والـ logging) ...
    
    def update_customer_points(self, customer_name, points_to_add):
        if not customer_name or customer_name == "N/A": logging.warning("Cannot update points: Customer name missing."); return None
        conn = None; new_total_points = None
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM customer_points WHERE customer_name = ?", (customer_name,))
            data = cursor.fetchone()
            if data:
                new_total_points = data[0] + points_to_add
                cursor.execute("UPDATE customer_points SET points = ? WHERE customer_name = ?", (new_total_points, customer_name))
                logging.info(f"Updated points for '{customer_name}': to {new_total_points}")
            else:
                new_total_points = points_to_add
                cursor.execute("INSERT INTO customer_points (customer_name, points) VALUES (?, ?)", (customer_name, new_total_points))
                logging.info(f"Created points entry for '{customer_name}' with {new_total_points} pts.")
            conn.commit(); return new_total_points
        except sqlite3.Error as e: logging.error(f"DB error updating points for '{customer_name}': {e}", exc_info=True); conn.rollback(); return None
        finally:
            if conn: conn.close()

# داخل فئة CyberCafeApp

    def end_session(self, device_name):
        if device_name not in self.sessions:
            logging.warning(f"END_SESSION: Attempted to end session on non-active device: {device_name}")
            messagebox.showwarning("خطأ", f"لا توجد جلسة نشطة على الجهاز {device_name}.", 
                                   parent=self.root if hasattr(self, 'root') and self.root and self.root.winfo_exists() else None)
            return

        logging.info(f"END_SESSION: Ending session for device {device_name}.")
        session = self.sessions[device_name]
        end_time_dt = datetime.now()
        start_time_dt = session['start_time']

        if not isinstance(start_time_dt, datetime):
            logging.error(f"END_SESSION: Invalid start_time for device {device_name}. Aborting end_session.")
            messagebox.showerror("خطأ فادح", f"وقت بدء الجلسة للجهاز {device_name} غير صالح!",
                                 parent=self.root if hasattr(self, 'root') and self.root and self.root.winfo_exists() else None)
            # Clean up potentially broken session state
            if device_name in self.sessions: del self.sessions[device_name]
            self.reset_device_ui(device_name)
            return
            
        employee_ending_session = current_user # Global current_user (employee who clicked "End")
        session_employee_owner = session.get('shift_employee', 'N/A')

        duration_delta_obj = end_time_dt - start_time_dt
        duration_minutes_actual = max(0, duration_delta_obj.total_seconds() / 60.0)

        is_session_free = session.get('is_free_session', False)
        points_redeemed_for_this_session = session.get('redeemed_points_for_session', 0)
        
        time_cost_calculated = 0.0
        if not is_session_free:
            if session['session_type'] == 'Multiplayer':
                rate_per_hour = RATE_MULTIPLAYER
            elif device_name in ["PS 1", "PS 2"]: # Assumes DEVICES global list exists
                rate_per_hour = RATE_SINGLE_PS1_PS2
            
                
            time_cost_calculated = (duration_minutes_actual / 60.0) * rate_per_hour
        
        item_cost_val = session.get('item_cost', 0.0)
        total_session_cost = time_cost_calculated + item_cost_val
        
        drinks_list = session.get('drinks', [])
        drinks_ordered_str = ", ".join(drinks_list) if drinks_list else "None"

        # --- Points Calculation & Awarding Logic ---
        MIN_DURATION_FOR_AWARDING_POINTS = 120  # 2 hours in minutes

        potential_points_calculated = 0
        points_earned_this_session = 0  # Actual awarded points
        customer_total_points_after_session = None 

        applied_bonus_code = session.get('bonus_code_applied')
        customer_name_for_session = session.get('customer')

        if not is_session_free and applied_bonus_code and customer_name_for_session and customer_name_for_session != "N/A":
            potential_points_calculated = self.calculate_points_for_duration(duration_minutes_actual)
            logging.info(f"END_SESSION: Potential points for {device_name}: {potential_points_calculated} (duration: {duration_minutes_actual:.2f} mins).")

            if potential_points_calculated > 0:
                if duration_minutes_actual >= MIN_DURATION_FOR_AWARDING_POINTS:
                    points_earned_this_session = potential_points_calculated
                    logging.info(f"END_SESSION: Awarding {points_earned_this_session} points for {device_name} (met {MIN_DURATION_FOR_AWARDING_POINTS} min threshold).")
                    customer_total_points_after_session = self.update_customer_points(customer_name_for_session, points_earned_this_session)
                    if customer_total_points_after_session is None:
                        logging.error(f"END_SESSION: Failed to update points in DB for {customer_name_for_session}. Reverting earned points to 0.")
                        points_earned_this_session = 0 
                else:
                    logging.info(f"END_SESSION: Session for {device_name} ({duration_minutes_actual:.2f} mins) too short. Potential {potential_points_calculated} points NOT awarded.")
        
        if customer_name_for_session and customer_name_for_session != "N/A" and customer_total_points_after_session is None:
            # If no points were processed (earned/redeemed) but customer exists, get their current total for display
            customer_total_points_after_session = self.get_customer_total_points(customer_name_for_session)

        # --- Save session to database ---
        saved_session_id = None
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (device, customer, start_time, end_time, duration, cost, 
                                      session_type, shift_employee, item_cost, drinks, time_option,
                                      bonus_code_used, points_earned_this_session,
                                      is_free_session, redeemed_points_for_session)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (device_name, customer_name_for_session, start_time_dt.isoformat(), end_time_dt.isoformat(),
                  duration_minutes_actual, total_session_cost, session['session_type'], session_employee_owner,
                  item_cost_val, drinks_ordered_str, session.get('time_option', 'N/A'), # Ensure time_option has default
                  applied_bonus_code if points_earned_this_session > 0 else None, # Only store code if points were awarded
                  points_earned_this_session, # Actually awarded points
                  is_session_free, 
                  points_redeemed_for_this_session
                  ))
            saved_session_id = cursor.lastrowid
            
            # Update bonus_codes table only if points were actually awarded from this session
            if not is_session_free and applied_bonus_code and points_earned_this_session > 0 and saved_session_id:
                cursor.execute("UPDATE bonus_codes SET session_id_earned_on = ? WHERE code = ? AND is_active = 1", 
                               (saved_session_id, applied_bonus_code))
                logging.info(f"END_SESSION: Bonus code '{applied_bonus_code}' marked as used for earning {points_earned_this_session} points on session ID {saved_session_id}.")
            
            conn.commit()
            logging.info(f"END_SESSION: Session for {device_name} (ID: {saved_session_id}) saved. Cost: {total_session_cost:.2f}. Points Awarded: {points_earned_this_session}")
            
            self.current_runtime_revenue += total_session_cost
            logging.info(f"END_SESSION: Runtime revenue updated to: {self.current_runtime_revenue:.2f} EGP")

        except sqlite3.Error as e_save_session:
            logging.error(f"END_SESSION: DB error saving session for {device_name}: {e_save_session}", exc_info=True)
            messagebox.showerror("خطأ قاعدة بيانات", f"فشل حفظ الجلسة للجهاز {device_name}:\n{e_save_session}", 
                                 parent=self.root if hasattr(self, 'root') and self.root and self.root.winfo_exists() else None)
        finally:
            if conn:
                conn.close()

        # --- Display summary messagebox to GUI user ---
        gui_summary_lines = [
            f"{'** جلسة مجانية **' if is_session_free else 'انتهت الجلسة'}: {device_name}",
            f"العميل: {customer_name_for_session if customer_name_for_session else 'N/A'}",
            f"المدة: {format_timedelta(duration_delta_obj)} (~{duration_minutes_actual:.0f} دقيقة)",
            f"التكلفة الإجمالية: {total_session_cost:.2f} جنيه"
        ]
        if is_session_free:
            gui_summary_lines.append(f"✨ تم استبدال {points_redeemed_for_this_session} نقطة لهذا الوقت المجاني.")
        
        if points_earned_this_session > 0 : # Only if points were actually awarded
             gui_summary_lines.append(f"🎁 نقاط مكتسبة: {points_earned_this_session} (بالكود: {applied_bonus_code})")
        elif not is_session_free and applied_bonus_code and potential_points_calculated > 0 and points_earned_this_session == 0:
             gui_summary_lines.append(f"⚠️ لم يتم منح النقاط المحتملة ({potential_points_calculated}) لأن مدة الجلسة أقل من ساعتين.")

        if customer_total_points_after_session is not None:
            gui_summary_lines.append(f"💳 الرصيد الكلي للعميل: {customer_total_points_after_session} نقطة")
        
        messagebox.showinfo("ملخص الجلسة", "\n".join(gui_summary_lines), 
                            parent=self.root if hasattr(self, 'root') and self.root and self.root.winfo_exists() else None)

        # --- Construct and Send VERY DETAILED Telegram Message ---
        if '_telegram_enabled' in globals() and _telegram_enabled and callable(send_telegram_message):
            net_shift_revenue = self.current_runtime_revenue - self.current_shift_expenses_total
            
            start_time_str_tg = start_time_dt.strftime('%Y-%m-%d %H:%M:%S')
            end_time_str_tg = end_time_dt.strftime('%Y-%m-%d %H:%M:%S')
            duration_str_formatted_tg = format_timedelta(duration_delta_obj) 

            customer_name_display_tg = customer_name_for_session if customer_name_for_session else "N/A"
            items_display_tg = drinks_ordered_str

            session_status_display_tg = "Normal Playtime"
            if is_session_free: session_status_display_tg = f"Free Session (Redeemed {points_redeemed_for_this_session} pts)"
            elif applied_bonus_code: session_status_display_tg = "Bonus Code Applied"
            
            bonus_code_display_value_tg = applied_bonus_code if applied_bonus_code else "N/A"
            # points_earned_this_session already holds the *awarded* points
            new_total_points_display_value_tg = str(customer_total_points_after_session) if customer_total_points_after_session is not None else "N/A"
            
            points_note_tg = ""
            if not is_session_free and applied_bonus_code and potential_points_calculated > 0 and points_earned_this_session == 0:
                 points_note_tg = f"\n  (Note: Session < {MIN_DURATION_FOR_AWARDING_POINTS} mins, potential {potential_points_calculated} pts NOT awarded)"

            detailed_telegram_message = f"""
--- ⏹️ **{device_name} الوقت انتهي ل** ⏹️ ---
**الجهاز:** {device_name} 
**بدا في:** {start_time_str_tg}
**انتهي في:** {end_time_str_tg}
**المده:** {duration_str_formatted_tg} (~{duration_minutes_actual:.1f} mins)
**نوع التايم المفتوح:** {session.get('time_option', 'N/A')}
**نوع اللعب:** {session.get('session_type', 'N/A')}
**مشروبات:** {item_cost_val:.2f} EGP
  **ثمن المشروبات:** {items_display_tg}
**اجمالي المدفوع: {total_session_cost:.2f} EGP**
   


"""
            detailed_telegram_message = "\n".join([line.strip() for line in detailed_telegram_message.strip().splitlines()])
            send_telegram_message(detailed_telegram_message)
            logging.info(f"END_SESSION: Detailed Telegram notification sent for {device_name}.")

        # --- Finalize and Reset UI ---
        if device_name in self.sessions:
            del self.sessions[device_name]
        self.reset_device_ui(device_name) 
        
        if SOUND_ENABLED and not is_session_free and callable(play_end_sound):
            play_end_sound()

        logging.info(f"END_SESSION: Session processing complete for {device_name}.")
    def get_customer_total_points(self, customer_name):
        if not customer_name or customer_name == "N/A": return 0
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM customer_points WHERE customer_name = ?", (customer_name,))
            res = cursor.fetchone()
            return res[0] if res else 0
        except sqlite3.Error as e: logging.error(f"Error fetching points for '{customer_name}': {e}", exc_info=True); return 0
        finally:
            if conn: conn.close()

# داخل فئة CyberCafeApp

    def get_customer_total_points(self, customer_name):
        """
        يجلب إجمالي النقاط الحالي لعميل معين من قاعدة البيانات.
        يُرجع 0 إذا لم يكن العميل موجودًا أو حدث خطأ.
        """
        if not customer_name or customer_name == "N/A":
            return 0 
        
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME) # DB_NAME يجب أن يكون مُعرفًا عالميًا
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM customer_points WHERE customer_name = ?", (customer_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return 0 
        except sqlite3.Error as e:
            logging.error(f"Error fetching points for customer '{customer_name}': {e}", exc_info=True)
            return 0 
        finally:
            if conn: conn.close()

# داخل فئة CyberCafeApp


    def update_device_ui(self, device_name):
        if device_name not in self.device_widgets or \
           not self.device_widgets[device_name]['frame'].winfo_exists():
            logging.warning(f"UPDATE_UI: Widget for {device_name} not found/destroyed.")
            return
        
        widgets = self.device_widgets[device_name]
        try:
            if device_name in self.sessions: 
                session = self.sessions[device_name]
                
                # ... (تحديث الليبلات الأخرى: customer, type, start, end, drinks) ...
                widgets['customer_label'].config(text=f"Customer: {session.get('customer', 'N/A')}")
                # ... (إلخ)

                applied_bonus_code = session.get('bonus_code_applied')
                customer_name_for_points = session.get('customer')
                is_free = session.get('is_free_session', False)

                # --- عرض كود النقاط ---
                if applied_bonus_code and not is_free: # لا نعرض كود نقاط مستخدم لجلسة مجانية
                    widgets['bonus_code_display_label'].config(text=f"Bonus Code: {applied_bonus_code}")
                else:
                    widgets['bonus_code_display_label'].config(text="Bonus Code: -")

                # --- عرض النقاط ---
                if customer_name_for_points and customer_name_for_points != "N/A":
                    # نعرض دائمًا إجمالي نقاط العميل المخزنة عند بدء الجلسة
                    # (أو بعد الخصم في حالة الجلسة المجانية)
                    # _update_all_device_timers ستقوم بإضافة (+X session) إذا كانت جلسة كسب نقاط
                    current_total_points_display = session.get('customer_initial_total_points', 0)
                    widgets['points_label'].config(text=f"Points: {current_total_points_display}")
                    
                    # تفعيل/تعطيل زر الاستبدال (يجب أن يكون معطلاً طالما الجلسة نشطة)
                    widgets['redeem_button'].config(state=tk.DISABLED) 
                else:
                    widgets['points_label'].config(text="Points: -")
                    widgets['redeem_button'].config(state=tk.DISABLED) # لا عميل، لا استبدال
                
                widgets['start_button'].config(state=tk.DISABLED)
                widgets['end_button'].config(state=tk.NORMAL)
                widgets['drink_button'].config(state=tk.NORMAL)
                
                if hasattr(self, '_update_all_device_timers') and callable(self._update_all_device_timers):
                    self._update_all_device_timers() 
            else: 
                self.reset_device_ui(device_name) 
        except Exception as e_update_ui: 
            logging.error(f"UPDATE_UI: Unexpected error for device {device_name}: {e_update_ui}", exc_info=True)
    def on_closing(self):
        """
        يتم استدعاؤها عند محاولة إغلاق النافذة الرئيسية للتطبيق.
        تقوم بإيقاف العمليات الجارية بشكل نظيف.
        """
        # للوصول إلى المتغيرات العالمية التي قد يتم تعديلها أو فحصها
        global ptb_application, ptb_event_loop, telegram_thread, app_instance 

        logging.info("Application closing sequence initiated by user.")
        active_sessions_count = len(self.sessions)
        proceed_with_exit = True
        
        if active_sessions_count > 0:
            parent_window_for_confirm = self.root if (self.root and self.root.winfo_exists()) else None
            if not messagebox.askokcancel("تأكيد الخروج - توجد جلسات نشطة",
                                          f"يوجد {active_sessions_count} جلسة نشطة حاليًا.\n"
                                          "الخروج الآن لن يقوم بحفظ هذه الجلسات تلقائيًا.\n\n"
                                          "هل أنت متأكد أنك تريد الخروج على أي حال؟",
                                          icon='warning', parent=parent_window_for_confirm):
                logging.info("User cancelled application exit due to active sessions.")
                proceed_with_exit = False
            else:
                logging.warning(f"User confirmed exiting with {active_sessions_count} active session(s) potentially unsaved.")
                # التأكد من وجود المتغيرات والدوال العالمية قبل استدعائها
                if '_telegram_enabled' in globals() and _telegram_enabled and \
                   'CHAT_ID' in globals() and CHAT_ID and \
                   'send_telegram_message' in globals() and callable(send_telegram_message):
                    send_telegram_message(f"⚠️ تنبيه: البرنامج يغلق مع وجود {active_sessions_count} جلسة نشطة لم يتم إنهاؤها!")
        
        if not proceed_with_exit:
            return 

        logging.info("Proceeding with application shutdown...")
        
        # إيقاف مؤقت تحديث الواجهة
        if hasattr(self, '_timer_update_job') and self._timer_update_job:
            try:
                if self.root and self.root.winfo_exists():
                    self.root.after_cancel(self._timer_update_job)
                logging.info("Cancelled scheduled UI timer updates.")
            except Exception as e_cancel_timer:
                 logging.warning(f"Could not cancel UI timer job during closing: {e_cancel_timer}")
            self._timer_update_job = None
        
        # إيقاف مؤقت فحص قائمة التيليجرام
        if hasattr(self, 'check_telegram_queue_job') and self.check_telegram_queue_job: 
            try:
                if self.root and self.root.winfo_exists():
                    self.root.after_cancel(self.check_telegram_queue_job)
                logging.info("Cancelled scheduled Telegram queue check.")
            except Exception as e_cancel_queue:
                 logging.warning(f"Could not cancel Telegram queue check job during closing: {e_cancel_queue}")
            self.check_telegram_queue_job = None

        # إيقاف بوت التيليجرام
        # global ptb_application, ptb_event_loop, telegram_thread # تم تعريفها في بداية الدالة
        if ptb_application: 
            logging.info("Attempting to shutdown Telegram bot application (ptb_application)...")
            if hasattr(ptb_application, 'running') and ptb_application.running: 
                logging.debug("PTB Application is running, attempting to stop/shutdown.")
                if ptb_event_loop and ptb_event_loop.is_running(): 
                    logging.debug("Scheduling PTB application shutdown on its event loop.")
                    # التأكد من أن asyncio مُستورد
                    if 'asyncio' not in sys.modules: import asyncio

                    future = asyncio.run_coroutine_threadsafe(ptb_application.shutdown(), ptb_event_loop)
                    try:
                        future.result(timeout=5) 
                        logging.info("PTB Application shutdown successfully initiated via future.")
                    except asyncio.TimeoutError:
                        logging.warning("Timeout waiting for PTB application to complete shutdown via future.")
                        if ptb_application.running: ptb_application.stop()
                    except Exception as e_ptb_shutdown:
                        logging.error(f"Exception during PTB application shutdown via future: {e_ptb_shutdown}")
                        if ptb_application.running: ptb_application.stop() 
                else:
                    logging.warning("PTB event loop not running or not accessible, calling ptb_application.stop() directly.")
                    if ptb_application.running: ptb_application.stop() 
            else:
                logging.info("PTB Application was not marked as running or does not have 'running' attribute.")
        else:
            logging.info("No ptb_application instance to stop (it's None or not defined globally).")


        if telegram_thread and telegram_thread.is_alive(): 
            logging.info("Waiting for Telegram polling thread to join...")
            telegram_thread.join(timeout=7.0) 
            if telegram_thread.is_alive():
                logging.warning("Telegram polling thread did not stop gracefully after shutdown/stop signal.")
            else:
                logging.info("Telegram polling thread stopped successfully.")
            telegram_thread = None # تعيينه لـ None بعد الانتهاء
        
        logging.info("Destroying main Tkinter window...")
        if self.root: 
            try:
                root_to_destroy = self.root 
                self.root = None 
                root_to_destroy.destroy()
                logging.info("Main Tkinter window destroyed.")
            except tk.TclError as e_destroy_root:
                 logging.warning(f"Error destroying Tkinter root window on close: {e_destroy_root}")
        
        if 'app_instance' in globals(): # التحقق من وجوده قبل تعيينه
            app_instance = None 
        logging.info("Application resources released. Exiting now.")
        if 'sys' not in sys.modules: import sys # تأكد من استيراد sys
        sys.exit(0)
    def restore_active_sessions(self):
        """
        يمسح أي جلسات نشطة في الذاكرة عند بدء التشغيل (أو تبديل المستخدم)
        ويعيد تعيين واجهات المستخدم لجميع الأجهزة إلى الحالة الافتراضية.
        كما يقوم بإعادة تعيين إجمالي الإيرادات والمصروفات للوردية الحالية.
        """
        self.sessions.clear() # مسح قاموس الجلسات النشطة في الذاكرة
        
        # إعادة تعيين متغيرات الوردية الحالية
        # هذه المتغيرات يجب أن تكون مُعرفة كأعضاء في الفئة في __init__
        if hasattr(self, 'current_runtime_revenue'):
            self.current_runtime_revenue = 0.0
        else:
            logging.warning("restore_active_sessions: self.current_runtime_revenue not defined, cannot reset.")
            
        if hasattr(self, 'current_shift_expenses_total'):
            self.current_shift_expenses_total = 0.0
        else:
            logging.warning("restore_active_sessions: self.current_shift_expenses_total not defined, cannot reset.")
            
        logging.info("Session state, runtime revenue, and shift expenses reset (restore_active_sessions).")
        
        # إعادة تعيين واجهات المستخدم لكل جهاز
        # DEVICES يجب أن تكون قائمة عالمية بأسماء الأجهزة
        if 'DEVICES' in globals() and isinstance(DEVICES, list):
            for device_name_iter in DEVICES: # تم تغيير اسم المتغير لتجنب التعارض
                if device_name_iter in self.device_widgets: # التحقق من وجود واجهة الجهاز
                    # reset_device_ui يجب أن تكون مُعرفة كدالة في الفئة
                    if hasattr(self, 'reset_device_ui') and callable(self.reset_device_ui):
                        self.reset_device_ui(device_name_iter)
                    else:
                        logging.error(f"restore_active_sessions: Method 'reset_device_ui' not found or not callable for device {device_name_iter}.")
                # else:
                    # logging.debug(f"restore_active_sessions: No UI widget found for device {device_name_iter} to reset.")
        else:
            logging.warning("Global list 'DEVICES' not found or not a list. Cannot reset device UIs in restore_active_sessions.")
    def schedule_telegram_queue_check(self):
        """
        تقوم بجدولة الفحص الدوري لقائمة أوامر التيليجرام.
        وتستدعي نفسها بشكل متكرر باستخدام self.root.after.
        """
        # self.check_telegram_queue_job يتم تعيينه في __init__ إلى None مبدئيًا
        try:
            # التحقق من أن النافذة الجذرية لا تزال موجودة
            if self.root and self.root.winfo_exists():
                self.process_telegram_actions() # معالجة أي أوامر موجودة في القائمة
                # جدولة الاستدعاء التالي لهذه الدالة
                self.check_telegram_queue_job = self.root.after(200, self.schedule_telegram_queue_check) # تفحص كل 200 ميلي ثانية
            else:
                # النافذة تم تدميرها، أوقف الجدولة
                logging.info("TELEGRAM_QUEUE: Root window closed or doesn't exist, stopping Telegram queue check.")
                if hasattr(self, 'check_telegram_queue_job') and self.check_telegram_queue_job:
                    # لا حاجة لإلغاء .after هنا لأن الشرط أعلاه سيمنع إعادة الجدولة
                    pass
                self.check_telegram_queue_job = None
        except Exception as e_schedule_tg_q:
            logging.error(f"TELEGRAM_QUEUE: Error in scheduling loop: {e_schedule_tg_q}", exc_info=True)
            if hasattr(self, 'check_telegram_queue_job') and self.check_telegram_queue_job:
                try:
                    if self.root and self.root.winfo_exists(): # تحقق مرة أخرى قبل الإلغاء
                        self.root.after_cancel(self.check_telegram_queue_job)
                except Exception as e_cancel_tg_q:
                    logging.error(f"TELEGRAM_QUEUE: Error cancelling job after schedule error: {e_cancel_tg_q}")
            self.check_telegram_queue_job = None # إيقاف الجدولة في حالة الخطأ


    def process_telegram_actions(self):
        """
        تقوم بمعالجة الأوامر (المهام) الموجودة في TELEGRAM_ACTION_QUEUE.
        يتم استدعاؤها بشكل دوري بواسطة schedule_telegram_queue_check.
        """
        # TELEGRAM_ACTION_QUEUE يجب أن يكون مُعرفًا كـ queue.Queue() عالميًا
        if 'TELEGRAM_ACTION_QUEUE' not in globals():
            logging.error("PROCESS_TELEGRAM_ACTIONS: Global TELEGRAM_ACTION_QUEUE not found!")
            return
            
        try:
            while not TELEGRAM_ACTION_QUEUE.empty(): # تحقق إذا كانت القائمة ليست فارغة
                action = TELEGRAM_ACTION_QUEUE.get_nowait() # جلب الأمر بدون انتظار
                logging.info(f"PROCESS_TELEGRAM_ACTIONS: Dequeued action: {action}")
                
                if action == "SHOW_CHECKOUT_SUMMARY":
                    logging.info("PROCESS_TELEGRAM_ACTIONS: Processing SHOW_CHECKOUT_SUMMARY action.")
                    # current_user يجب أن يكون مُعرفًا عالميًا
                    if 'current_user' in globals() and current_user:
                        # show_checkout_summary يجب أن تكون مُعرفة كدالة في الفئة
                        if hasattr(self, 'show_checkout_summary') and callable(self.show_checkout_summary):
                            self.show_checkout_summary(triggered_by_telegram=True)
                            
                            # محاولة إظهار النافذة الرئيسية إذا كانت مخفية
                            if self.root and self.root.winfo_exists():
                                try:
                                    if self.root.state() == 'withdrawn':
                                        self.root.deiconify()
                                    self.root.lift() # رفع النافذة للأمام
                                    self.root.focus_force() # محاولة إعطائها التركيز
                                    logging.debug("PROCESS_TELEGRAM_ACTIONS: Main window lifted and focused for Telegram action.")
                                except tk.TclError as e_lift_focus_tg: # تم تغيير اسم متغير الخطأ
                                    logging.warning(f"PROCESS_TELEGRAM_ACTIONS: Could not lift/focus main window: {e_lift_focus_tg}")
                        else:
                             logging.error("PROCESS_TELEGRAM_ACTIONS: Method 'show_checkout_summary' not found or not callable.")
                    else:
                        logging.warning("PROCESS_TELEGRAM_ACTIONS: Cannot show checkout summary via Telegram: No user logged in or insufficient permissions in app.")
                        if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                            send_telegram_message("⚠️ تعذر عرض ملخص الخروج: لا يوجد مستخدم نشط في التطبيق أو الصلاحيات غير كافية.")
                
                # يمكنك إضافة معالجة لأوامر أخرى هنا باستخدام elif
                # elif action == "ANOTHER_ACTION_FROM_TELEGRAM":
                #     self.handle_another_telegram_action()

        except queue.Empty: # هذا طبيعي إذا كانت القائمة فارغة
            pass 
        except Exception as e_process_q: # تم تغيير اسم متغير الخطأ
            logging.error(f"PROCESS_TELEGRAM_ACTIONS: Error processing Telegram action queue: {e_process_q}", exc_info=True)

    # ... (باقي دوال الفئة CyberCafeApp) ...
    # ... (باقي دوال الفئة CyberCafeApp) ...        
    def show_checkout_summary(self, triggered_by_telegram=False):
        """
        يعرض ملخص الوردية الحالي، بما في ذلك الإيرادات الإجمالية، المصروفات، وصافي الإيراد.
        """
        # self.current_runtime_revenue و self.current_shift_expenses_total
        # يجب أن تكون مُعرفة كأعضاء في الفئة (عادةً في __init__) ويتم تحديثها بشكل صحيح.
        
        gross_revenue = getattr(self, 'current_runtime_revenue', 0.0)
        total_expenses = getattr(self, 'current_shift_expenses_total', 0.0)
        net_revenue = gross_revenue - total_expenses

        # current_user يجب أن يكون مُعرفًا عالميًا أو كعضو في الفئة يتم تعيينه عند تسجيل الدخول
        app_user_display = current_user if 'current_user' in globals() and current_user else 'N/A'
        trigger_source_display = "(عبر تيليجرام)" if triggered_by_telegram else f"(بواسطة {app_user_display} في البرنامج)"
        
        summary_lines = [
            f"--- ملخص الوردية الحالية {trigger_source_display} ---",
            "",
            f"إجمالي الإيرادات (جلسات، مبيعات أكواد، إلخ): {gross_revenue:.2f} جنيه",
            f"إجمالي المصروفات المسجلة: {total_expenses:.2f} جنيه",
            "-----------------------------------------", # خط أطول للفصل
            f"💰 صافي الإيراد للوردية: {net_revenue:.2f} جنيه",
            "",
            "(الإيرادات والمصروفات للوردية الحالية أو منذ آخر تشغيل/تسجيل دخول)" # نص توضيحي مُعدل
        ]
        summary_msg_for_dialog = "\n".join(summary_lines)
        
        log_message_source = "Telegram" if triggered_by_telegram else app_user_display
        logging.info(f"Checkout Summary requested by {log_message_source}: Gross Revenue={gross_revenue:.2f}, Expenses={total_expenses:.2f}, Net Revenue={net_revenue:.2f} EGP")
        
        parent_for_messagebox = self.root if self.root and self.root.winfo_exists() else None
        messagebox.showinfo("ملخص الوردية / Checkout", summary_msg_for_dialog, parent=parent_for_messagebox)
        
        # إرسال الملخص إلى تيليجرام
        # التأكد من وجود المتغيرات والدوال العالمية قبل استخدامها
        if '_telegram_enabled' in globals() and _telegram_enabled and \
           'CHAT_ID' in globals() and CHAT_ID and \
           'send_telegram_message' in globals() and callable(send_telegram_message):
            summary_for_telegram = (
                f"🧾 ملخص وردية Checkout:\n"
                f"بواسطة: {log_message_source}\n"
                f"المستخدم المسجل في البرنامج: {app_user_display}\n"
                f"إجمالي الإيرادات: {gross_revenue:.2f} ج.م\n"
                f"إجمالي المصروفات: {total_expenses:.2f} ج.م\n"
                f"صافي الإيراد: {net_revenue:.2f} ج.م"
            )
            send_telegram_message(summary_for_telegram)
        elif triggered_by_telegram: 
            logging.warning("Checkout triggered by Telegram, but could not send summary back (CHAT_ID or _telegram_enabled issue, or send_telegram_message not found).")

    # ... (باقي دوال الفئة CyberCafeApp) ...
    # ... (باقي دوال الفئة)
# داخل فئة CyberCafeApp
# (تأكد أن لديك: import sqlite3, from tkinter import messagebox, Toplevel, StringVar, ttk, END, SINGLE, Listbox, Scrollbar
# from datetime import datetime, timedelta
# global DB_NAME, current_user, send_telegram_message, _telegram_enabled)
# داخل فئة CyberCafeApp
# (تأكد أن لديك: import sqlite3, from tkinter import messagebox, Toplevel, StringVar, ttk, END, SINGLE, Listbox, Scrollbar
# from datetime import datetime, timedelta
# global DB_NAME, current_user, send_telegram_message, _telegram_enabled)

    def show_redeem_points_dialog(self, device_name):
        """
        Displays a dialog for an employee/admin to redeem a customer's points
        for free playtime on a specified device.
        """
        if device_name in self.sessions:
            messagebox.showwarning("الجهاز مشغول",
                                   f"لا يمكن استبدال النقاط على الجهاز {device_name} لأنه مشغول حاليًا.\n"
                                   "الرجاء اختيار جهاز فارغ أو إنهاء الجلسة الحالية أولاً.",
                                   parent=self.root)
            return

        dialog = Toplevel(self.root)
        dialog.title(f"استبدال النقاط للجهاز: {device_name}")
        dialog.geometry("500x500") # Adjusted height
        dialog.configure(bg=getattr(self, 'bg_color', "#3a3a3a")) # Use app's bg_color
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

        # Ensure REDEEM_OPTIONS is accessible (preferably global)
        if 'REDEEM_OPTIONS' not in globals() or not REDEEM_OPTIONS:
            logging.error("REDEEM_OPTIONS is not defined or is empty. Cannot proceed with redemption.")
            messagebox.showerror("خطأ في الإعداد", "لم يتم تعريف خيارات استبدال النقاط.", parent=dialog)
            dialog.destroy()
            return

        main_dialog_frame = ttk.Frame(dialog, padding=15, style="TFrame") # Use app's TFrame style
        main_dialog_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_dialog_frame, text="استبدال نقاط العميل بوقت مجاني",
                  font=getattr(self, 'frame_font', ('Segoe UI', 14, 'bold')),
                  style="Top.TLabel").pack(pady=(0, 15)) # Use app's Top.TLabel style

        # --- 1. Customer Selection ---
        customer_frame = ttk.Frame(main_dialog_frame, style="TFrame")
        customer_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(customer_frame, text="اسم العميل:", style="Top.TLabel", 
                  font=getattr(self, 'label_font', ('Segoe UI', 10))).pack(side=tk.LEFT, padx=(0,5))
        
        customer_name_var_redeem = StringVar()
        customer_names_list = []
        conn = None
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            # Fetch customers who have at least enough points for the cheapest redeem option
            min_points_needed = min(cost for _, cost in REDEEM_OPTIONS.values()) if REDEEM_OPTIONS else 0
            cursor.execute("SELECT DISTINCT customer_name FROM customer_points WHERE points >= ? AND customer_name IS NOT NULL AND customer_name != 'N/A' ORDER BY customer_name", (min_points_needed,))
            fetched_customers = cursor.fetchall()
            if fetched_customers:
                customer_names_list = [name[0] for name in fetched_customers]
        except sqlite3.Error as e_cust_fetch:
            logging.error(f"Error fetching customers for redeem dialog: {e_cust_fetch}", exc_info=True)
        finally:
            if conn: conn.close()

        customer_combo_redeem = ttk.Combobox(customer_frame, textvariable=customer_name_var_redeem, 
                                           values=customer_names_list,
                                           font=getattr(self, 'dialog_label_font', ('Segoe UI', 10)), 
                                           width=28, state="normal" if customer_names_list else "disabled")
        customer_combo_redeem.pack(side=tk.LEFT, expand=True, fill=tk.X)
        if customer_names_list:
            customer_combo_redeem.set("اختر عميلاً أو أدخل اسمه")


        current_points_display_var = StringVar(value="اختر أو أدخل اسم عميل لعرض نقاطه...")
        current_points_display_label = ttk.Label(main_dialog_frame, textvariable=current_points_display_var,
                                               style="Top.TLabel", 
                                               font=getattr(self, 'info_label_font', ('Segoe UI', 10, 'bold')),
                                               justify=tk.CENTER, wraplength=450)
        current_points_display_label.pack(pady=10)

        options_frame = ttk.Frame(main_dialog_frame, style="TFrame")
        options_frame.pack(pady=10, fill=tk.X, expand=True)
        
        selected_redeem_option_var = StringVar()

        def populate_redeem_options(customer_points_val, customer_name_for_display="العميل"):
            for widget in options_frame.winfo_children():
                widget.destroy()
            
            eligible_options_found = False
            if not REDEEM_OPTIONS: # Should have been checked earlier
                ttk.Label(options_frame, text="لا توجد خيارات استبدال معرفة.", style="Top.TLabel", foreground="orange").pack()
                return

            sorted_redeem_options = sorted(REDEEM_OPTIONS.items(), key=lambda item: item[1][1]) # Sort by points cost

            for option_text, (duration_mins, points_needed) in sorted_redeem_options:
                can_afford = customer_points_val >= points_needed
                rb_state = tk.NORMAL if can_afford else tk.DISABLED
                
                rb_display_text = f"{option_text} (تحتاج {points_needed} نقطة)"
                if not can_afford:
                    rb_display_text += f" - ينقص {points_needed - customer_points_val} نقطة"

                # Use a style that's defined in your app, e.g., for dialog radio buttons
                rb = ttk.Radiobutton(options_frame,
                                     text=rb_display_text,
                                     variable=selected_redeem_option_var,
                                     value=option_text,
                                     style="DialogStart.TRadiobutton", # Assuming this style exists
                                     state=rb_state)
                rb.pack(anchor=tk.W, padx=20, pady=3)
                if can_afford:
                    eligible_options_found = True
            
            if not eligible_options_found and customer_name_var_redeem.get().strip(): # Only show if a customer is actually selected/entered
                ttk.Label(options_frame, text=f"{customer_name_for_display} لا يملك نقاط كافية لأي من خيارات الاستبدال.",
                          style="Top.TLabel", foreground="orange", wraplength=400, justify=tk.CENTER).pack(pady=5)


        def on_customer_selected_or_typed(event=None):
            customer_name = customer_name_var_redeem.get().strip()
            if not customer_name or customer_name == "اختر عميلاً أو أدخل اسمه":
                current_points_display_var.set("اختر أو أدخل اسم عميل لعرض نقاطه...")
                populate_redeem_options(0)
                return

            points = self.get_customer_total_points(customer_name)
            current_points_display_var.set(f"العميل: {customer_name}\nالرصيد الحالي: {points} نقطة")
            populate_redeem_options(points, customer_name)
            selected_redeem_option_var.set("") # Reset selection when customer changes

        customer_combo_redeem.bind("<<ComboboxSelected>>", on_customer_selected_or_typed)
        customer_combo_redeem.bind("<Return>", on_customer_selected_or_typed)
        customer_combo_redeem.bind("<FocusOut>", on_customer_selected_or_typed) # Update when user types and tabs away

        # Initial population if a default customer was somehow set or for placeholder
        on_customer_selected_or_typed()


        def confirm_redemption():
            customer_name = customer_name_var_redeem.get().strip()
            selected_option_key = selected_redeem_option_var.get()

            if not customer_name or customer_name == "اختر عميلاً أو أدخل اسمه":
                messagebox.showerror("خطأ", "الرجاء اختيار أو إدخال اسم العميل.", parent=dialog)
                return
            if not selected_option_key:
                messagebox.showerror("خطأ", "الرجاء اختيار باقة لاستبدالها.", parent=dialog)
                return

            duration_to_redeem, points_cost_for_redeem = REDEEM_OPTIONS.get(selected_option_key, (None, None))

            if duration_to_redeem is None:
                messagebox.showerror("خطأ", "الخيار المختار غير صالح.", parent=dialog)
                return

            current_customer_points = self.get_customer_total_points(customer_name)
            if current_customer_points < points_cost_for_redeem:
                messagebox.showerror("نقاط غير كافية",
                                     f"العميل '{customer_name}' لا يملك نقاطًا كافية ({points_cost_for_redeem} مطلوبة).\n"
                                     f"الرصيد الحالي: {current_customer_points} نقطة.",
                                     parent=dialog)
                return

            # Deduct points
            new_total_points_after_redeem = self.update_customer_points(customer_name, -points_cost_for_redeem)

            if new_total_points_after_redeem is not None:
                start_time_val = datetime.now()
                session_details_redeemed = {
                    "session_type": "Single", # Redeemed sessions are typically single player
                    "time_option": f"Redeemed: {selected_option_key}",
                    "customer_name": customer_name,
                    "start_time": start_time_val,
                    "intended_end_time": start_time_val + timedelta(minutes=duration_to_redeem),
                    "bonus_code": None, # No bonus code for earning points on a redeemed session
                    "is_free_session": True,
                    "redeemed_points": points_cost_for_redeem,
                    "item_cost": 0.0, # Items can still be added later and will have cost
                    "drinks": []
                }
                
                self.start_session(device_name, session_details_redeemed) # This will update UI and sessions dict

                success_msg = (
                    f"تم استبدال {points_cost_for_redeem} نقطة للعميل '{customer_name}'.\n"
                    f"تم بدء جلسة مجانية لمدة {duration_to_redeem} دقيقة على الجهاز {device_name}.\n"
                    f"الرصيد المتبقي للعميل: {new_total_points_after_redeem} نقطة."
                )
                messagebox.showinfo("نجاح الاستبدال", success_msg, parent=dialog)
                logging.info(f"Points redeemed for '{customer_name}' by '{current_user}': {points_cost_for_redeem} pts for {duration_to_redeem} mins on {device_name}. New total: {new_total_points_after_redeem}")

                if '_telegram_enabled' in globals() and _telegram_enabled and callable(send_telegram_message):
                    send_telegram_message(
                        f"🔄 استبدال نقاط:\n"
                        f"العميل: {customer_name}\n"
                        f"النقاط المستخدمة: {points_cost_for_redeem} نقطة\n"
                        f"الوقت المكتسب: {selected_option_key} على {device_name}\n"
                        f"الرصيد الجديد: {new_total_points_after_redeem} نقطة\n"
                        f"بواسطة: {current_user}"
                    )
                dialog.destroy()
            else:
                messagebox.showerror("فشل تحديث النقاط", f"فشل تحديث نقاط العميل '{customer_name}' بعد محاولة الخصم. لم يتم بدء الجلسة.", parent=dialog)
        
        # --- Buttons ---
        buttons_bottom_frame = ttk.Frame(main_dialog_frame, style="TFrame") # Using app's TFrame
        buttons_bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10,0))

        # Use app's button styles if available, e.g., "Green.TButton", "Red.TButton"
        confirm_button = ttk.Button(buttons_bottom_frame, text="تأكيد الاستبدال وبدء الجلسة", 
                                   command=confirm_redemption, style="Green.TButton") 
        confirm_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)

        cancel_button = ttk.Button(buttons_bottom_frame, text="إلغاء", command=dialog.destroy, 
                                 style="Red.TButton")
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=5, expand=True, fill=tk.X)
        
        dialog.wait_window()

    # ... (rest of CyberCafeApp methods) ...
# Inside CyberCafeApp class:

    def switch_user(self):
        """Logs out current user, prompts for new login, resets shift financials."""
        global current_user 
        logging.info(f"Switch user initiated by {previous_user if 'previous_user' in locals() else 'unknown'}.") # Ensure previous_user is defined if used
        previous_user_for_log = current_user # Capture current user before changing

        # ... (your existing logic for pausing timer, self.root.withdraw()) ...
        timer_was_running = False
        if self._timer_update_job:
            try:
                if self.root and self.root.winfo_exists():
                    self.root.after_cancel(self._timer_update_job)
                self._timer_update_job = None
                timer_was_running = True
                logging.debug("Paused timer updates for user switch.")
            except Exception as e_cancel_timer:
                logging.warning(f"Could not cancel timer job before switch: {e_cancel_timer}")
        
        if self.root and self.root.winfo_exists(): # Ensure root exists before withdrawing
            self.root.withdraw()
        logging.debug("Main window hidden, prompting for new user login.")

        # prompt_login_modal should be your global function for the switch user login dialog
        new_username = prompt_login_modal(self.root if self.root and self.root.winfo_exists() else None) 

        if new_username:
            logging.info(f"User successfully switched from '{previous_user_for_log}' to '{new_username}'.")
            current_user = new_username # Update the global current_user

            # !!! NEW: Reset shift financials for the new user !!!
            self.current_runtime_revenue = 0.0
            self.current_shift_expenses_total = 0.0
            logging.info(f"Runtime revenue and shift expenses reset to 0 for new user '{current_user}'.")
            
            # Optional: If you want to load any pre-existing expenses for this new user for *today*,
            # call self.load_current_shift_expenses() AFTER resetting to 0.
            # If a switch always means a completely fresh financial slate, then just resetting to 0 is enough.
            # For now, let's assume a completely fresh slate upon switch for this session:
            # self.load_current_shift_expenses() # Uncomment if needed based on your exact requirement

            # Transfer active session ownership (your existing logic)
            transferred_sessions_count = 0
            if self.sessions:
                logging.info(f"Transferring {len(self.sessions)} active session(s) ownership to new user '{new_username}'.")
                for device, session_data in self.sessions.items():
                    session_data['shift_employee'] = new_username
                    transferred_sessions_count += 1
                if transferred_sessions_count > 0 and '_telegram_enabled' in globals() and _telegram_enabled and callable(send_telegram_message):
                    send_telegram_message(f"🔄 User switched: '{previous_user_for_log}' ➔ '{new_username}'.\n{transferred_sessions_count} active session(s) ownership transferred.")
            
            # Send login notification for new user
            login_type_msg_tg = "🛡️ Admin" if current_user == ADMIN_USERNAME else "👤 Employee"
            if '_telegram_enabled' in globals() and _telegram_enabled and callable(send_telegram_message):
                send_telegram_message(f"{login_type_msg_tg} '{current_user}' logged in (via switch).")

            # Update UI
            self.user_label.config(text=f"STAFF: {current_user}")
            self.root.title(f"MIX GAME Cafe Stadium - Staff: {current_user}")
            self._rebuild_control_panel() # This will also call setup_expenses_ui_in_control_panel
            
            if self.root: self.root.deiconify(); self.root.lift()
            try:
                if self.root: self.root.focus_force()
            except tk.TclError: pass
            logging.debug(f"Login successful for '{new_username}'. Main window restored, UI updated.")

        else: # Login failed or cancelled
            logging.info(f"Switch user login cancelled or failed. Restoring session for '{previous_user_for_log}'.")
            current_user = previous_user_for_log # Revert to previous user
            if self.root: self.root.deiconify(); self.root.lift()
        
        # Restart timer updates if it was running (your existing logic)
        if timer_was_running and not self._timer_update_job and self.sessions:
            logging.debug("Restarting timer updates after user switch attempt (timer was running).")
            self.schedule_timer_updates()
        elif not self._timer_update_job and self.sessions: # If not running but sessions exist
            logging.debug("Starting timer updates as sessions exist after user switch attempt.")
            self.schedule_timer_updates()    
    def on_closing(self):
        """يتم استدعاؤها عند محاولة إغلاق النافذة الرئيسية للتطبيق."""
        global telegram_thread, app_instance, ptb_application, ptb_event_loop 

        logging.info("Application closing sequence initiated by user.")
        active_sessions_count = len(self.sessions)
        proceed_with_exit = True
        
        if active_sessions_count > 0:
            parent_window_for_confirm = self.root if (self.root and self.root.winfo_exists()) else None
            if not messagebox.askokcancel("تأكيد الخروج - توجد جلسات نشطة",
                                          f"يوجد {active_sessions_count} جلسة نشطة حاليًا.\n"
                                          "الخروج الآن لن يقوم بحفظ هذه الجلسات تلقائيًا.\n\n"
                                          "هل أنت متأكد أنك تريد الخروج على أي حال؟",
                                          icon='warning', parent=parent_window_for_confirm):
                logging.info("User cancelled application exit due to active sessions.")
                proceed_with_exit = False
            else:
                logging.warning(f"User confirmed exiting with {active_sessions_count} active session(s) potentially unsaved.")
                if '_telegram_enabled' in globals() and _telegram_enabled and 'send_telegram_message' in globals():
                    send_telegram_message(f"⚠️ تنبيه: البرنامج يغلق مع وجود {active_sessions_count} جلسة نشطة لم يتم إنهاؤها!")
        
        if not proceed_with_exit:
            return # إيقاف عملية الإغلاق

        logging.info("Proceeding with application shutdown...")
        
        # إيقاف مؤقت تحديث الواجهة
        if self._timer_update_job:
            try:
                if self.root and self.root.winfo_exists():
                    self.root.after_cancel(self._timer_update_job)
                logging.info("Cancelled scheduled UI timer updates.")
            except Exception as e_cancel_timer:
                 logging.warning(f"Could not cancel UI timer job during closing: {e_cancel_timer}")
            self._timer_update_job = None
        
        # إيقاف مؤقت فحص قائمة التيليجرام
        if self.check_telegram_queue_job: 
            try:
                if self.root and self.root.winfo_exists():
                    self.root.after_cancel(self.check_telegram_queue_job)
                logging.info("Cancelled scheduled Telegram queue check.")
            except Exception as e_cancel_queue:
                 logging.warning(f"Could not cancel Telegram queue check job during closing: {e_cancel_queue}")
            self.check_telegram_queue_job = None

        # إيقاف بوت التيليجرام
        if ptb_application: # ptb_application يجب أن يكون مُعرفًا عالميًا
            logging.info("Attempting to shutdown Telegram bot application (ptb_application)...")
            # الطريقة المثلى لإيقاف run_polling هي عبر application.stop() أو application.shutdown()
            # run_polling هو استدعاء مُعطِّل (blocking) ويعمل في thread منفصل
            if ptb_application.running: # تحقق إذا كان يعمل
                logging.debug("PTB Application is running, attempting to stop/shutdown.")
                # ptb_application.stop() # يرسل إشارة للتوقف (غير مُعطِّل)
                # ptb_application.shutdown() # أكثر شمولاً، يجب أن يكون await ولكننا في thread رئيسي
                # الطريقة الآمنة لاستدعاء دالة async من thread متزامن هي run_coroutine_threadsafe
                if ptb_event_loop and ptb_event_loop.is_running(): # ptb_event_loop يجب أن يكون مُعرفًا عالميًا
                    logging.debug("Scheduling PTB application shutdown on its event loop.")
                    future = asyncio.run_coroutine_threadsafe(ptb_application.shutdown(), ptb_event_loop)
                    try:
                        future.result(timeout=5) # انتظر لـ 5 ثوانٍ حتى يتم الإغلاق
                        logging.info("PTB Application shutdown successfully initiated via future.")
                    except asyncio.TimeoutError:
                        logging.warning("Timeout waiting for PTB application to complete shutdown via future.")
                        # إذا حدث timeout، استدعِ stop() كإجراء احتياطي
                        if ptb_application.running: ptb_application.stop()
                    except Exception as e_ptb_shutdown:
                        logging.error(f"Exception during PTB application shutdown via future: {e_ptb_shutdown}")
                        if ptb_application.running: ptb_application.stop() # إجراء احتياطي
                else:
                    logging.warning("PTB event loop not running or not accessible, calling ptb_application.stop() directly.")
                    if ptb_application.running: ptb_application.stop() # إجراء احتياطي إذا لم يكن اللوب متاحًا
            else:
                logging.info("PTB Application was not marked as running.")
        else:
            logging.info("No ptb_application instance to stop.")


        if telegram_thread and telegram_thread.is_alive(): # telegram_thread يجب أن يكون مُعرفًا عالميًا
            logging.info("Waiting for Telegram polling thread to join...")
            telegram_thread.join(timeout=7.0) # زيادة المهلة قليلاً
            if telegram_thread.is_alive():
                logging.warning("Telegram polling thread did not stop gracefully after shutdown/stop signal.")
            else:
                logging.info("Telegram polling thread stopped successfully.")
            telegram_thread = None
        
        logging.info("Destroying main Tkinter window...")
        if self.root: # تحقق أن self.root لا يزال كائنًا صالحًا
            try:
                root_to_destroy = self.root # خزنه في متغير مؤقت قبل تعيين self.root إلى None
                self.root = None # مهم لمنع استدعاءات .after إضافية إذا كانت هناك
                root_to_destroy.destroy()
                logging.info("Main Tkinter window destroyed.")
            except tk.TclError as e_destroy_root:
                 logging.warning(f"Error destroying Tkinter root window on close: {e_destroy_root}")
        
        app_instance = None # app_instance يجب أن يكون مُعرفًا عالميًا
        logging.info("Application resources released. Exiting now.")
        sys.exit(0) # الخروج من البرنامج بشكل نظيف
    def schedule_timer_updates(self):
        """
        تقوم بجدولة التحديث الدوري لواجهات عرض الوقت والتكلفة لكل الأجهزة.
        """
        try:
            # التحقق من أن النافذة الجذرية لا تزال موجودة قبل جدولة المزيد من التحديثات
            if self.root and self.root.winfo_exists():
                self._update_all_device_timers() # استدعاء الدالة التي تقوم بالتحديث الفعلي
                # جدولة الاستدعاء التالي لنفسها بعد 1000 ميلي ثانية (1 ثانية)
                self._timer_update_job = self.root.after(1000, self.schedule_timer_updates)
            else:
                # النافذة تم تدميرها، أوقف الجدولة
                logging.info("Root window closed or doesn't exist, stopping UI timer updates.")
                self._timer_update_job = None
        except Exception as e_schedule:
            # في حالة حدوث أي خطأ غير متوقع أثناء الجدولة
            logging.error(f"Error in UI timer scheduling loop: {e_schedule}", exc_info=True)
            self._timer_update_job = None # إيقاف الجدولة في حالة الخطأ
    def schedule_timer_updates(self):
        """
        تقوم بجدولة التحديث الدوري لواجهات عرض الوقت والتكلفة لكل الأجهزة.
        """
        try:
            if self.root and self.root.winfo_exists():
                self._update_all_device_timers()
                self._timer_update_job = self.root.after(1000, self.schedule_timer_updates)
            else:
                logging.info("SCHEDULE_TIMER: Root window closed, stopping UI timer updates.")
                self._timer_update_job = None
        except Exception as e_schedule:
            logging.error(f"SCHEDULE_TIMER: Error in UI timer scheduling loop: {e_schedule}", exc_info=True)
            self._timer_update_job = None
    def _calculate_current_cost(self, device_name):
        """
        Calculates the current cost for an active session based on new rules.
        يحسب التكلفة الحالية لجلسة نشطة بناءً على القواعد الجديدة.
        """
        if device_name not in self.sessions:
            logging.warning(f"_calculate_current_cost: No session found for device {device_name}")
            return 0.0

        session = self.sessions[device_name]
        item_cost = session.get('item_cost', 0.0)  # Cost of drinks, other items

        # If the session is marked as free, only item costs apply (or 0 if no items)
        if session.get('is_free_session', False):
            return item_cost

        # Handle fixed-price sessions (like VR)
        # These sessions have their total time-related cost set at the start.
        if session.get('is_fixed_price', False):
            fixed_session_price = session.get('fixed_price_amount', 0.0)
            # logging.debug(f"_CALC_COST [{device_name}]: Fixed Price Session. Price={fixed_session_price:.2f}, Items={item_cost:.2f}")
            return fixed_session_price + item_cost

        # For time-based sessions that are not free and not fixed price
        now = datetime.now()
        start_time = session.get('start_time')

        if not isinstance(start_time, datetime):
            logging.error(f"_CALC_COST: start_time for {device_name} is not a datetime object: {type(start_time)}. Session data: {session}")
            return item_cost  # Return only item cost if start_time is invalid

        elapsed_delta = now - start_time
        elapsed_minutes = max(0, elapsed_delta.total_seconds() / 60.0)
        elapsed_hours = elapsed_minutes / 60.0

        time_cost_calculated = 0.0
        rate_per_hour = 0.0

        device_category = session.get('device_category') # e.g., 'PS', 'PingPong', 'BabyFoot'
        player_mode = session.get('player_mode')         # e.g., 'Single', 'Multiplayer'

        if device_category == 'PS':
            if player_mode == 'Single':
                rate_per_hour = self.RATE_PS_SINGLE_PER_HOUR
            elif player_mode == 'Multiplayer':
                rate_per_hour = self.RATE_PS_MULTI_PER_HOUR
            else:
                logging.warning(f"Unknown player_mode '{player_mode}' for PS on {device_name}")
        elif device_category == 'PingPong':
            if player_mode == 'Single':
                rate_per_hour = self.RATE_PINGPONG_STANDARD_PER_HOUR
            elif player_mode == 'Multiplayer':
                rate_per_hour = self.RATE_PINGPONG_MULTI_PER_HOUR
            else:
                logging.warning(f"Unknown player_mode '{player_mode}' for PingPong on {device_name}")
        elif device_category == 'Billiards':
            if player_mode == 'Single':
                rate_per_hour = self.RATE_BILLIARDS_STANDARD_PER_HOUR
            elif player_mode == 'Multiplayer':
                rate_per_hour = self.RATE_BILLIARDS_MULTI_PER_HOUR
            else:
                logging.warning(f"Unknown player_mode '{player_mode}' for Billiards on {device_name}")
        elif device_category == 'BabyFoot':
            # BabyFoot has one rate for single or multi
            rate_per_hour = self.RATE_BABYFOOT_STANDARD_PER_HOUR
        else:
            logging.error(f"Unknown or unhandled device_category '{device_category}' for timed session on {device_name}")

        if rate_per_hour > 0:
            time_cost_calculated = elapsed_hours * rate_per_hour
        elif device_category and device_category != 'VR': # VR is handled by 'is_fixed_price'
             logging.warning(f"Rate per hour is 0 for {device_category} ({player_mode}) on {device_name}. Check configuration.")


        total_current_cost = time_cost_calculated + item_cost
        # logging.debug(f"_CALC_COST [{device_name}]: Cat={device_category}, Mode={player_mode}, ElapsedH={elapsed_hours:.2f}, Rate={rate_per_hour:.2f}, TimeCost={time_cost_calculated:.2f}, Items={item_cost:.2f}, Total={total_current_cost:.2f}")
        return total_current_cost
    def start_session(self, device_name, session_details):
        """
        يبدأ جلسة جديدة على جهاز معين، مع التحقق من كود النقاط وتخزين النقاط الأولية للعميل.
        """
        if device_name in self.sessions:
            messagebox.showwarning("نشطة بالفعل", f"توجد جلسة نشطة على الجهاز {device_name}.", parent=self.root)
            return
        if not current_user: 
            messagebox.showerror("خطأ", "لا يوجد مستخدم مسجل حاليًا لبدء الجلسة.", parent=self.root)
            return

        start_time = session_details['start_time'] 
        
        # معالجة اسم العميل بشكل أفضل
        raw_customer_name_ss = session_details.get('customer_name') # اسم متغير جديد
        customer_name = "N/A" # قيمة افتراضية
        if raw_customer_name_ss is not None and isinstance(raw_customer_name_ss, str):
            customer_name_stripped = raw_customer_name_ss.strip()
            if customer_name_stripped: # إذا لم يكن فارغًا بعد strip
                customer_name = customer_name_stripped
        
        session_type = session_details['session_type']
        time_option = session_details['time_option']
        intended_end_time = session_details.get('intended_end_time')
        
        raw_bonus_code_ss = session_details.get('bonus_code') # اسم متغير جديد
        bonus_code_input = None # قيمة افتراضية
        if raw_bonus_code_ss is not None and isinstance(raw_bonus_code_ss, str):
            processed_code = raw_bonus_code_ss.strip().upper()
            if processed_code: # إذا لم يكن فارغًا بعد المعالجة
                bonus_code_input = processed_code

        is_free_session_val = session_details.get('is_free_session', False)
        redeemed_points_val = session_details.get('redeemed_points', 0)    

        valid_bonus_code_for_session = None 
        initial_customer_points = 0 

        if customer_name != "N/A":
            if hasattr(self, 'get_customer_total_points') and callable(self.get_customer_total_points):
                initial_customer_points = self.get_customer_total_points(customer_name)
            logging.debug(f"START_SESSION: Initial points for customer '{customer_name}': {initial_customer_points}")
        else:
            logging.debug("START_SESSION: Customer name is N/A, initial points set to 0 for session data.")

        if bonus_code_input and not is_free_session_val:
            conn = None
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, code FROM bonus_codes 
                    WHERE code = ? AND is_active = 1 AND session_id_earned_on IS NULL
                """, (bonus_code_input,))
                code_data = cursor.fetchone()
                if code_data:
                    valid_bonus_code_for_session = code_data[1]
                    logging.info(f"Bonus code '{valid_bonus_code_for_session}' accepted for session on {device_name}.")
                    # messagebox.showinfo("كود نقاط صالح", f"تم قبول كود النقاط: {valid_bonus_code_for_session}.\nسيتم احتساب النقاط لهذه الجلسة.", parent=self.root)
                else:
                    logging.warning(f"Bonus code '{bonus_code_input}' for device {device_name} is invalid, inactive, or already used for earning points.")
                    messagebox.showwarning("كود نقاط غير صالح", f"كود النقاط '{bonus_code_input}' غير صالح، أو لم يتم تفعيله، أو تم استخدامه من قبل.", parent=self.root)
            except sqlite3.Error as e_bonus_check_ss: # اسم متغير جديد
                logging.error(f"Database error checking bonus code '{bonus_code_input}': {e_bonus_check_ss}", exc_info=True)
                messagebox.showerror("خطأ قاعدة البيانات", "حدث خطأ أثناء التحقق من كود النقاط.", parent=self.root)
            finally:
                if conn: conn.close()
        
        self.sessions[device_name] = {
            'start_time': start_time,
            'customer': customer_name, 
            'session_type': session_type,
            'time_option': time_option,
            'intended_end_time': intended_end_time,
            'shift_employee': current_user,
            'drinks': session_details.get('drinks', []), 
            'item_cost': session_details.get('item_cost', 0.0), 
            'limit_sound_played': False,
            'bonus_code_applied': valid_bonus_code_for_session, 
            'customer_initial_total_points': initial_customer_points, 
            'is_free_session': is_free_session_val,           
            'redeemed_points_for_session': redeemed_points_val  
        }
        
        if hasattr(self, 'update_device_ui') and callable(self.update_device_ui):
            self.update_device_ui(device_name) 
        else:
            logging.error("START_SESSION: Method 'update_device_ui' not found or not callable.")

        logging.info(f"Session started on {device_name} by {current_user}. Is Free: {is_free_session_val}. Bonus Code: {valid_bonus_code_for_session}. Initial Cust Pts: {initial_customer_points}")
        
        telegram_msg_ss = ( # اسم متغير جديد
            f"▶️ {'جلسة مجانية' if is_free_session_val else 'جلسة'} بدأت على {device_name} بواسطة {current_user}.\n"
            f"النوع: {session_type}, المدة: {time_option}\n"
            f"العميل: {self.sessions[device_name]['customer']}"
        )
        if valid_bonus_code_for_session:
            telegram_msg_ss += f"\n🎁 كود نقاط مُطبّق: {valid_bonus_code_for_session}"
        if is_free_session_val:
            telegram_msg_ss += f"\n✨ تم استبدال {redeemed_points_val} نقطة."
        
        if '_telegram_enabled' in globals() and _telegram_enabled and \
           'send_telegram_message' in globals() and callable(send_telegram_message):
            send_telegram_message(telegram_msg_ss)


    def update_device_ui(self, device_name):
        if device_name not in self.device_widgets or \
           not self.device_widgets[device_name]['frame'].winfo_exists():
            logging.warning(f"UPDATE_UI_V3: Widget for {device_name} not found/destroyed.")
            return
        
        widgets = self.device_widgets[device_name]
        try:
            if device_name in self.sessions: 
                session = self.sessions[device_name]
                
                widgets['customer_label'].config(text=f"Customer: {session.get('customer', 'N/A')}")
                widgets['type_label'].config(text=f"Type: {session.get('session_type', '-')}")
                widgets['start_label'].config(text=f"Start: {session['start_time'].strftime('%H:%M:%S') if isinstance(session.get('start_time'), datetime) else '-'}")
                
                end_time_obj_upd = session.get('intended_end_time') 
                end_time_str_upd = end_time_obj_upd.strftime('%H:%M:%S') if isinstance(end_time_obj_upd, datetime) else "Open"
                widgets['end_label'].config(text=f"Ends: {end_time_str_upd}")
                
                drinks_list_upd = session.get('drinks', []) 
                drinks_str_upd = ", ".join(drinks_list_upd) if drinks_list_upd else '-'
                widgets['drinks_label'].config(text=f"Items: {drinks_str_upd}")

                applied_bonus_code_upd = session.get('bonus_code_applied')
                customer_name_for_points_upd = session.get('customer')
                is_free_upd = session.get('is_free_session', False)

                # عرض كود النقاط
                if applied_bonus_code_upd and not is_free_upd:
                    widgets['bonus_code_display_label'].config(text=f"Bonus Code: {applied_bonus_code_upd}")
                else:
                    widgets['bonus_code_display_label'].config(text="Bonus Code: -")

                # عرض النقاط - سيعرض الرصيد الأولي، و _update_all_device_timers سيضيف الجزء الحي
                if customer_name_for_points_upd and customer_name_for_points_upd != "N/A":
                    initial_total_points_upd = session.get('customer_initial_total_points', 0)
                    widgets['points_label'].config(text=f"Points: {initial_total_points_upd}")
                else:
                    widgets['points_label'].config(text="Points: -")
                
                widgets['start_button'].config(state=tk.DISABLED)
                widgets['end_button'].config(state=tk.NORMAL)
                widgets['drink_button'].config(state=tk.NORMAL)
                widgets['redeem_button'].config(state=tk.DISABLED) # الاستبدال معطل أثناء الجلسة
                
                if hasattr(self, '_update_all_device_timers') and callable(self._update_all_device_timers):
                    self._update_all_device_timers() # استدعِ لتحديث التايمر والتكلفة والجزء الحي من النقاط
                else:
                    logging.error("UPDATE_UI_V3: Method '_update_all_device_timers' not found!")
            else: 
                self.reset_device_ui(device_name) 
        except Exception as e_update_ui_v3: 
            logging.error(f"UPDATE_UI_V3: Unexpected error for device {device_name}: {e_update_ui_v3}", exc_info=True)

    def _update_all_device_timers(self):
        now = datetime.now()
        for device_name in list(self.sessions.keys()):
            if device_name not in self.device_widgets or \
               not self.device_widgets[device_name]['frame'].winfo_exists() or \
               device_name not in self.sessions:
                continue

            try:
                session = self.sessions[device_name]
                widgets = self.device_widgets[device_name]
                timer_label = widgets['timer_label']
                cost_label = widgets['cost_label']
                points_label_ui_live = widgets['points_label'] # اسم متغير جديد

                if not isinstance(session.get('start_time'), datetime):
                    logging.error(f"_UPDATE_TIMERS_V3: Session start_time for {device_name} is invalid.")
                    continue 

                elapsed_time_live = now - session['start_time'] 
                current_display_time_str_live = "Error"  
                timer_fg_color_live = getattr(self, 'timer_green', "green") 

                if session.get('intended_end_time') and isinstance(session.get('intended_end_time'), datetime):
                    remaining_time_live = session['intended_end_time'] - now 
                    if remaining_time_live.total_seconds() <= 0:
                        current_display_time_str_live = "00:00:00" 
                        timer_fg_color_live = getattr(self, 'timer_red', "red")
                        if not session.get('limit_sound_played', False):
                            session['limit_sound_played'] = True 
                            # ... (منطق تشغيل الصوت وإرسال إشعار تيليجرام كما كان) ...
                    else: 
                        current_display_time_str_live = format_timedelta(remaining_time_live)
                        if remaining_time_live.total_seconds() < 300: 
                            timer_fg_color_live = getattr(self, 'timer_yellow', "yellow")
                else: 
                    current_display_time_str_live = format_timedelta(elapsed_time_live)
                
                if timer_label.cget("text") != current_display_time_str_live or timer_label.cget("foreground") != timer_fg_color_live:
                    timer_label.config(text=current_display_time_str_live, foreground=timer_fg_color_live)

                current_cost_val_live = self._calculate_current_cost(device_name) 
                cost_text_str_live = f"Cost: {current_cost_val_live:.2f} EGP" 
                if cost_label.cget("text") != cost_text_str_live:
                    cost_label.config(text=cost_text_str_live)

                # --- تحديث ليبل النقاط بشكل "حي" ---
                if session.get('bonus_code_applied') and \
                   session.get('customer') and session['customer'] != "N/A" and \
                   not session.get('is_free_session', False):
                    
                    current_duration_minutes_live_pts = max(0, elapsed_time_live.total_seconds() / 60.0) 
                    # calculate_points_for_duration يجب أن تكون مُعرفة وتقبل duration_minutes
                    points_this_session_live_val = self.calculate_points_for_duration(current_duration_minutes_live_pts) 
                    
                    initial_points_live_val = session.get('customer_initial_total_points', 0) 
                    live_total_display_val = initial_points_live_val + points_this_session_live_val 
                    points_text_live_str = f"Points: {live_total_display_val} (+{points_this_session_live_val})" 
                    
                    if points_label_ui_live.cget("text") != points_text_live_str:
                        points_label_ui_live.config(text=points_text_live_str)
                elif session.get('is_free_session', False) and session.get('customer') and session['customer'] != "N/A":
                    # للجلسات المجانية، اعرض فقط الرصيد المتبقي (الذي لا يتغير خلال الجلسة)
                    # هذا يتم تعيينه بواسطة update_device_ui عند بدء الجلسة، فلا حاجة لتحديثه هنا كل ثانية
                    pass # points_label_ui_live.config(text=f"Points: {session.get('customer_initial_total_points',0)}")
                # else: (لا يوجد كود، لا يوجد عميل، أو جلسة مجانية بدون عميل) points_label يبقى على "-"
                #   (يتم تعيينه بواسطة reset_device_ui أو update_device_ui)

            except Exception as e_timer_update_v3: 
                logging.error(f"_UPDATE_TIMERS_V3: Unexpected error for {device_name}: {e_timer_update_v3}", exc_info=True)

    def reset_device_ui(self, device_name):
        if device_name in self.device_widgets and \
           self.device_widgets[device_name]['frame'].winfo_exists():
            widgets = self.device_widgets[device_name]
            try:
                timer_default_fg_reset_v2 = getattr(self, 'timer_green', "green") 
                
                widgets['timer_label'].config(text="00:00:00", foreground=timer_default_fg_reset_v2)
                widgets['cost_label'].config(text="Cost: 0.00 EGP")
                widgets['points_label'].config(text="Points: -") 
                widgets['customer_label'].config(text="Customer: -")
                widgets['type_label'].config(text="Type: -")
                widgets['start_label'].config(text="Start: -")
                widgets['end_label'].config(text="Ends: -")
                widgets['drinks_label'].config(text="Items: -")
                widgets['bonus_code_display_label'].config(text="Bonus Code: -")
                
                widgets['start_button'].config(state=tk.NORMAL) 
                widgets['end_button'].config(state=tk.DISABLED) 
                widgets['drink_button'].config(state=tk.DISABLED)
                widgets['redeem_button'].config(state=tk.NORMAL) 
            except Exception as e_reset_ui_v3: 
                logging.error(f"RESET_UI_V3: Unexpected error for {device_name}: {e_reset_ui_v3}", exc_info=True)
        else:
            logging.warning(f"RESET_UI_V3: Widget for {device_name} not found/destroyed.")
    def _calculate_current_cost(self, device_name):
        if device_name not in self.sessions:
            return 0.0
        
        session = self.sessions[device_name]
        now = datetime.now()
        start_time = session['start_time']
        
        if not isinstance(start_time, datetime):
            logging.error(f"_CALC_COST: start_time for {device_name} is not a datetime object.")
            return 0.0 # لا يمكن حساب التكلفة

        elapsed_delta = now - start_time
        elapsed_minutes = max(0, elapsed_delta.total_seconds() / 60.0)

        if session['session_type'] == 'Multiplayer':
            rate = RATE_MULTIPLAYER
        elif device_name in ["PS 1", "PS 2"]: # تأكد أن أسماء الأجهزة متطابقة مع ما في DEVICES
            rate = RATE_SINGLE_PS1_PS2
        
        
        current_time_cost = (elapsed_minutes / 60.0) * rate
        item_cost = session.get('item_cost', 0.0)
        total_current_cost = current_time_cost + item_cost
        # logging.debug(f"_CALC_COST [{device_name}]: ElapsedM={elapsed_minutes:.2f}, Rate={rate}, TimeCost={current_time_cost:.2f}, ItemCost={item_cost:.2f}, Total={total_current_cost:.2f}")
        return total_current_cost
def start_main_gui():
    global app_instance 
    if app_instance and app_instance.root and app_instance.root.winfo_exists():
        logging.warning("Main GUI seems to be already running. Attempting to lift.")
        try:
            app_instance.root.deiconify()
            app_instance.root.lift()
        except tk.TclError:
            logging.warning("Failed to lift existing window, it might have been closed improperly.")
            app_instance = None 
        if app_instance: 
            return

    try: 
        root = tk.Tk() 
        logging.debug(f"Root window created: {root}")

     
        app_instance = CyberCafeApp(root) 
        # ------------------------------------
        
        logging.info("CyberCafeApp instance created successfully.")
       

    except Exception as e_init_gui: 
        logging.critical(f"FATAL ERROR initializing main application GUI (CyberCafeApp): {e_init_gui}", exc_info=True)
        print(f"FATAL ERROR: Could not start the main application:\n{e_init_gui}")
        
        # محاولة إيقاف التيليجرام بشكل نظيف
        if 'ptb_application' in globals() and ptb_application and hasattr(ptb_application, 'running') and ptb_application.running:
            logging.info("Attempting to stop PTB application due to fatal error in start_main_gui...")
            if hasattr(ptb_application, 'stop'): ptb_application.stop()
        elif 'bot' in globals() and bot and 'telegram_thread' in globals() and telegram_thread and telegram_thread.is_alive():
            if 'stop_telegram_event_loop' in globals():
                logging.info("Attempting to stop old Telegram event loop due to fatal error in start_main_gui...")
                stop_telegram_event_loop() 
        
        if 'telegram_thread' in globals() and telegram_thread and telegram_thread.is_alive():
            telegram_thread.join(timeout=3.0)
            if telegram_thread.is_alive():
                 logging.warning("Telegram thread still alive after stop attempt during fatal error in start_main_gui.")
        sys.exit(1)


if __name__ == "__main__":
    # يفترض أنك قمت بتعطيل الصوت في بداية الملف بتعيين SOUND_ENABLED = False و playsound = None
    # لذا، التحذيرات الخاصة بـ playsound يجب ألا تظهر إذا تم ذلك بشكل صحيح.
    # سطر الطباعة المميز يمكن إبقاؤه أو حذفه:
    # print("!!! تم تشغيل هذا الملف cyper.py الآن !!!") 
    
    logging.info("------------------ APPLICATION START ------------------")
    logging.info("Performing activation check...")
    if not perform_activation_prompt(): 
        logging.error("Activation failed or cancelled. Exiting.")
        sys.exit(1)
    logging.info("Activation check passed.")

    logging.info("Initializing database...")
    if not setup_database(): 
        logging.critical("Database setup failed. Exiting.")
        sys.exit(1)
    logging.info("Database initialization complete.")

    logging.info("Initializing Telegram bot...")
    initialize_telegram_bot() 
    logging.info("Telegram bot initialization process finished (may run in background).")

    logging.info("Starting login process...")
    try:
        show_login_screen(start_main_gui) 
        logging.info("show_login_screen has finished.")

    except tk.TclError as e_tcl_login: 
        logging.warning(f"Tkinter TclError occurred, likely login window was closed: {e_tcl_login}")
        if not (app_instance and app_instance.root and app_instance.root.winfo_exists()):
            logging.info("Main application window not running after login screen TclError. Performing cleanup.")
            # ... (نفس منطق إيقاف التيليجرام كما في كتلة except السابقة) ...
            sys.exit(0) 
        else:
            logging.info("Login screen TclError, but main application seems to be running.")

    except Exception as e_login_fatal: 
        logging.critical(f"Unhandled exception during or after login screen: {e_login_fatal}", exc_info=True)
        print(f"FATAL ERROR during login/startup sequence: {e_login_fatal}")
        # ... (نفس منطق الإغلاق النظيف ومحاولة إيقاف التيليجرام كما في كتلة except السابقة) ...
        sys.exit(1) 

    logging.info("Application main process scope (__name__ == '__main__') finished.")
    
    # ... (محاولة أخيرة لتنظيف التيليجرام إذا كان الـ thread لا يزال يعمل) ...
    logging.info("------------------- APPLICATION END -------------------")