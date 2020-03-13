from xdg import BaseDirectory
import os

DESKTOP_ENTRY_FILE="quikey-daemon.desktop"

DESKTOP_ENTRY_CONTENTS="""
[Desktop Entry]
Version=1.0
Name=Quikey
GenericName=Keyboard Macro Tool
Comment=A keyboard macro tool.
Exec=quikey-daemon start
Terminal=false
Type=Application
Categories=Office;Utility;
"""

def enableAutostart():
    autostartDir = os.path.join(BaseDirectory.xdg_config_home, "autostart")
    os.makedirs(autostartDir, exist_ok=True)
    with open(os.path.join(autostartDir, DESKTOP_ENTRY_FILE), 'w') as f:
        f.write(DESKTOP_ENTRY_CONTENTS)

def disableAutostart():
    autostartDir = os.path.join(BaseDirectory.xdg_config_home, "autostart")
    os.makedirs(autostartDir, exist_ok=True)
    os.remove(os.path.join(autostartDir, DESKTOP_ENTRY_FILE))