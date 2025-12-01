import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import xml.etree.ElementTree as ET

SETTINGS_FILE = "settings.json"

# --------------------------
# Load/save settings
# --------------------------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"roku_ip": ""}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

settings = load_settings()

# --------------------------
# Roku HTTP helpers
# --------------------------
def roku_base():
    ip = ip_entry.get().strip()
    if not ip:
        raise ValueError("Roku IP is empty.")
    return f"http://{ip}:8060"

def send_key(key):
    try:
        url = f"{roku_base()}/keypress/{key}"
        resp = requests.post(url, timeout=2)
        if resp.status_code not in (200, 204):
            messagebox.showerror("Error", f"Error {resp.status_code}")
    except Exception as e:
        messagebox.showerror("Network Error", str(e))

def launch_app(app_id):
    try:
        url = f"{roku_base()}/launch/{app_id}"
        resp = requests.post(url, timeout=2)
        if resp.status_code not in (200, 204):
            messagebox.showerror("Error", f"Error {resp.status_code}")
    except Exception as e:
        messagebox.showerror("Network Error", str(e))

def send_text(text):
    """
    Roku text input uses:
    /keypress/Lit_<char>
    """
    for ch in text:
        try:
            url = f"{roku_base()}/keypress/Lit_{ch}"
            resp = requests.post(url, timeout=2)
        except:
            messagebox.showerror("Error", f"Failed at char: {ch}")
            break

# --------------------------
# Query installed apps
# --------------------------
def refresh_apps():
    try:
        url = f"{roku_base()}/query/apps"
        resp = requests.get(url, timeout=3)
        xml = ET.fromstring(resp.text)
        
        app_list = []
        for app in xml.findall("app"):
            app_id = app.get("id")
            name = app.text or "Unnamed"
            app_list.append((name, app_id))

        app_list.sort()
        apps_dropdown["values"] = [f"{name} (ID {app_id})" for name, app_id in app_list]
        global installed_apps
        installed_apps = app_list
    except Exception as e:
        messagebox.showerror("Error", f"Failed loading apps: {str(e)}")

def launch_selected_app():
    sel = apps_dropdown.get()
    if "(" not in sel:
        return
    app_id = sel.split("ID ")[1].rstrip(")")
    launch_app(app_id)

# --------------------------
# UI Setup
# --------------------------
root = tk.Tk()
root.title("Roku Remote Controller")
root.geometry("400x600")
root.resizable(False, False)

# Frame: IP entry
ip_frame = tk.Frame(root)
ip_frame.pack(pady=10)

tk.Label(ip_frame, text="Roku IP Address:").pack(side=tk.LEFT)
ip_entry = tk.Entry(ip_frame, width=20)
ip_entry.pack(side=tk.LEFT, padx=5)
ip_entry.insert(0, settings.get("roku_ip", ""))

def save_ip():
    settings["roku_ip"] = ip_entry.get().strip()
    save_settings(settings)
    messagebox.showinfo("Saved", "Roku IP saved.")

tk.Button(ip_frame, text="Save", command=save_ip).pack(side=tk.LEFT)

# --------------------------
# Navigation Buttons Grid
# --------------------------
nav_frame = tk.Frame(root)
nav_frame.pack(pady=20)

def add_btn(frame, text, key, r, c):
    tk.Button(frame, text=text, width=8, height=2,
              command=lambda: send_key(key)).grid(row=r, column=c, padx=5, pady=5)

add_btn(nav_frame, "Home", "Home", 0, 1)
add_btn(nav_frame, "Up", "Up", 1, 1)
add_btn(nav_frame, "Left", "Left", 2, 0)
add_btn(nav_frame, "Select", "Select", 2, 1)
add_btn(nav_frame, "Right", "Right", 2, 2)
add_btn(nav_frame, "Down", "Down", 3, 1)
add_btn(nav_frame, "Back", "Back", 4, 1)
add_btn(nav_frame, "Play/Pause", "Play", 5, 1)

# --------------------------
# Text input
# --------------------------
text_frame = tk.Frame(root)
text_frame.pack(pady=10)

tk.Label(text_frame, text="Send Text to Roku:").pack()

text_entry = tk.Entry(text_frame, width=30)
text_entry.pack(pady=5)

def send_text_btn():
    send_text(text_entry.get())

tk.Button(text_frame, text="Send Text", command=send_text_btn).pack()

# --------------------------
# Installed Apps
# --------------------------
app_frame = tk.Frame(root)
app_frame.pack(pady=20)

tk.Label(app_frame, text="Installed Apps:").pack()

apps_dropdown = ttk.Combobox(app_frame, width=35, state="readonly")
apps_dropdown.pack(pady=5)

tk.Button(app_frame, text="Refresh Apps", command=refresh_apps).pack(pady=5)
tk.Button(app_frame, text="Launch Selected App", command=launch_selected_app).pack()

installed_apps = []

root.mainloop()
