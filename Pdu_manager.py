import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import paramiko
import threading
import json
import os
from datetime import datetime
import time
import base64
from io import BytesIO
from PIL import Image, ImageTk

# ----------------- Config -----------------
DEVICE_FILE = "devices.json"

# Store devices in memory
devices = {}
ssh_client = None
ssh_channel = None
current_device = None

# ----------------- Spider-Man Icon (Base64) -----------------
# Convert your spiderman.png to base64 string
# Example: with Python -> open('spiderman.png','rb').read() -> base64.b64encode(...)
# Paste the resulting string below:
SPIDERMAN_ICON_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB5klEQVRYR+2XQUvDUBCGv3uKwQx
...
(Your full base64 here)
...
"""

# Decode base64 to PhotoImage
icon_data = base64.b64decode(SPIDERMAN_ICON_BASE64)
icon_img = Image.open(BytesIO(icon_data))
icon_photo = ImageTk.PhotoImage(icon_img)

# ----------------- Helpers -----------------
def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log(message):
    console_text.config(state="normal")
    console_text.insert(tk.END, f"[{timestamp()}] {message}\n")
    console_text.see(tk.END)
    console_text.config(state="disabled")

def connect_device(name, ip, username, password):
    global ssh_client, ssh_channel, current_device
    try:
        log(f"Connecting to {name} ({ip})...")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=username, password=password, timeout=10)
        ssh_channel = ssh_client.invoke_shell()
        ssh_channel.settimeout(1)
        current_device = name
        log(f"Connected to {name}")
    except Exception as e:
        log(f"Connection failed: {e}")
        ssh_client = None
        ssh_channel = None

def disconnect_device():
    global ssh_client, ssh_channel, current_device
    if ssh_client:
        ssh_client.close()
    ssh_client = None
    ssh_channel = None
    current_device = None
    log("Disconnected")

def send_command(cmd):
    global ssh_channel
    if ssh_channel:
        ssh_channel.send(cmd + "\n")
        log(f"> {cmd}")
        time.sleep(0.5)
        try:
            output = ""
            while ssh_channel.recv_ready():
                output += ssh_channel.recv(1024).decode()
            if output.strip():
                for line in output.splitlines():
                    log(f"  {line}")
        except Exception:
            pass

def execute_load_action(load_number, action):
    if not ssh_channel:
        log("Not connected to any device!")
        return
    try:
        log(f"Executing action '{action}' on load {load_number}...")
        send_command("device")
        send_command(f"load {load_number}")
        send_command(f"{action} force")
        send_command("end")
        log(f"Action '{action}' on load {load_number} completed.")
    except Exception as e:
        log(f"Error executing action: {e}")

# ----------------- JSON Persistence -----------------
def load_devices():
    global devices
    if os.path.exists(DEVICE_FILE):
        try:
            with open(DEVICE_FILE, "r") as f:
                devices = json.load(f)
        except Exception as e:
            log(f"Error loading devices: {e}")

def save_devices():
    try:
        with open(DEVICE_FILE, "w") as f:
            json.dump(devices, f, indent=4)
    except Exception as e:
        log(f"Error saving devices: {e}")

# ----------------- Device Management -----------------
def device_popup(edit_name=None):
    popup = tk.Toplevel(root)
    popup.title("Device Settings")
    popup.geometry("300x180")
    popup.grab_set()

    if edit_name:
        d = devices[edit_name]
        name_val = edit_name
        ip_val = d["ip"]
        user_val = d["user"]
        pass_val = d["pass"]
    else:
        name_val = ip_val = user_val = pass_val = ""

    tk.Label(popup, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    name_var = tk.StringVar(value=name_val)
    tk.Entry(popup, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)

    tk.Label(popup, text="IP Address:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    ip_var = tk.StringVar(value=ip_val)
    tk.Entry(popup, textvariable=ip_var).grid(row=1, column=1, padx=5, pady=5)

    tk.Label(popup, text="Username:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    user_var = tk.StringVar(value=user_val if user_val else "localadmin")
    tk.Entry(popup, textvariable=user_var).grid(row=2, column=1, padx=5, pady=5)

    tk.Label(popup, text="Password:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    pass_var = tk.StringVar(value=pass_val)
    tk.Entry(popup, textvariable=pass_var, show="*").grid(row=3, column=1, padx=5, pady=5)

    def save_device():
        name = name_var.get()
        ip = ip_var.get()
        user = user_var.get()
        passwd = pass_var.get()
        if not name or not ip or not user or not passwd:
            messagebox.showerror("Error", "All fields are required!")
            return
        if edit_name:
            devices.pop(edit_name)
        devices[name] = {"ip": ip, "user": user, "pass": passwd}
        refresh_device_list()
        save_devices()
        popup.destroy()

    tk.Button(popup, text="Save", command=save_device).grid(row=4, column=0, pady=10)
    tk.Button(popup, text="Cancel", command=popup.destroy).grid(row=4, column=1, pady=10)

def add_device():
    device_popup()

def edit_device():
    sel = device_listbox.curselection()
    if not sel:
        return
    name = device_listbox.get(sel)
    device_popup(edit_name=name)

def remove_device():
    sel = device_listbox.curselection()
    if not sel:
        return
    name = device_listbox.get(sel)
    if messagebox.askyesno("Remove Device", f"Remove {name}?"):
        devices.pop(name)
        refresh_device_list()
        save_devices()

def refresh_device_list():
    device_listbox.delete(0, tk.END)
    for name in devices:
        device_listbox.insert(tk.END, name)

def connect_selected_device():
    sel = device_listbox.curselection()
    if not sel:
        return
    name = device_listbox.get(sel)
    d = devices[name]
    threading.Thread(target=connect_device, args=(name, d["ip"], d["user"], d["pass"]), daemon=True).start()

def disconnect_selected_device():
    disconnect_device()

def execute_action():
    load_num = load_entry.get()
    action = action_combo.get()
    if not load_num or not action:
        log("Please enter a load number and select an action.")
        return
    threading.Thread(target=execute_load_action, args=(load_num, action), daemon=True).start()

# ----------------- GUI Layout -----------------
root = tk.Tk()
root.title("PDU Manager")
root.geometry("900x500")
root.iconphoto(False, icon_photo)  # set Spider-Man icon

# Header
header_label = tk.Label(
    root, text='With great power comes great responsibility.',
    fg="red", font=("Helvetica", 14)
)
header_label.pack(pady=5)

frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Left column (devices)
left_frame = tk.Frame(frame)
left_frame.pack(side="left", fill="y")

tk.Label(left_frame, text="Devices").pack()
device_listbox = tk.Listbox(left_frame, height=12, width=25)
device_listbox.pack()

tk.Button(left_frame, text="Add", command=add_device).pack(fill="x")
tk.Button(left_frame, text="Edit", command=edit_device).pack(fill="x")
tk.Button(left_frame, text="Remove", command=remove_device).pack(fill="x")
tk.Button(left_frame, text="Connect", command=connect_selected_device).pack(fill="x")
tk.Button(left_frame, text="Disconnect", command=disconnect_selected_device).pack(fill="x")

# Right column (console + controls)
right_frame = tk.Frame(frame)
right_frame.pack(side="left", fill="both", expand=True, padx=10)

tk.Label(right_frame, text="Console Log:").pack(anchor="w")
console_text = tk.Text(right_frame, height=20, width=80, state="disabled")
console_text.pack(fill="both", expand=True)

controls_frame = tk.Frame(right_frame)
controls_frame.pack(pady=5)

tk.Label(controls_frame, text="Load #").grid(row=0, column=0, padx=5)
load_entry = tk.Entry(controls_frame, width=6)
load_entry.grid(row=0, column=1, padx=5)

tk.Label(controls_frame, text="Action").grid(row=0, column=2, padx=5)
action_combo = ttk.Combobox(controls_frame, values=["on", "off", "cycle"], state="readonly", width=10)
action_combo.grid(row=0, column=3, padx=5)

tk.Button(controls_frame, text="Execute", command=execute_action).grid(row=0, column=4, padx=10)

# Footer
footer_label = tk.Label(root, text="Ahmed Aldulaimi", anchor="e")
footer_label.pack(side="bottom", anchor="se", padx=10, pady=5)

# Load devices from JSON at start
load_devices()
refresh_device_list()

root.mainloop()
