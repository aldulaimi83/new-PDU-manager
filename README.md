PDU Manager – User Guide

Author: Ahmed Aldulaimi
Version: 1.0

Overview

PDU Manager is a Windows GUI application to manage multiple PDUs (Rack 1 – Rack 8 or more).
You can connect via SSH, control individual loads, and log all actions with timestamps.

Getting Started
1. Launch the Application

Double-click PDU_Manager.exe.

The main window will open with:

Device list on the left.

Console log and load controls on the right.

Your name at the bottom.

2. Add a Device

Click Add on the left panel.

Enter the following in the pop-up:

Name: Friendly name for your PDU (e.g., Rack 1).

IP Address: PDU IP (e.g., 10.228.42.005).

Username: Usually localadmin.

Password: Device password.

Click Save. The device appears in the list.

3. Edit or Remove a Device

Select a device from the list, then click Edit or Remove.

4. Connect to a Device

Select a device from the list.

Click Connect.

Console log will show:

[HH:MM:SS] Connecting to Rack1 (IP)...
[HH:MM:SS] Connected to Rack1

5. Control Loads

Enter the Load # in the text box.

Select Action from the dropdown:

on → Turn on the load

off → Turn off the load

cycle → Cycle power (off → on)

Click Execute.

Console log shows:

[HH:MM:SS] Executing action 'off' on load 12...
[HH:MM:SS] Action 'off' on load 12 completed.


No need to type device, load xx, or end — the program handles it automatically.

6. Disconnect

Click Disconnect to close the SSH connection.

Console log will show [HH:MM:SS] Disconnected.

7. Notes

Commands are logged with timestamps.

Devices are saved in devices.json automatically.

You can minimize the window; all buttons remain visible.

Works on any Windows computer — no extra files required.

8. Troubleshooting

Cannot connect: Check IP, username, and password.

No console output: Ensure the device supports SSH and commands device, load xx, and off/on/cycle force.

Application doesn’t start: Make sure PDU_Manager.exe is not blocked by Windows Defender.

Enjoy controlling your PDUs safely!

"With great power comes great responsibility." 🕷️
