"""
AutoHotkey Installation Checker
This script helps you locate AutoHotkey on your system
"""

import os
import shutil

print("=" * 70)
print("🔍 AutoHotkey Installation Checker")
print("=" * 70)

# Check common paths
ahk_paths = [
    r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
    r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe",
    r"C:\Program Files\AutoHotkey\v2\AutoHotkey32.exe",
    r"C:\Program Files\AutoHotkey\v1.1\AutoHotkey.exe",
    r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey64.exe",
    r"C:\Program Files (x86)\AutoHotkey\v2\AutoHotkey32.exe",
    r"C:\Program Files (x86)\AutoHotkey\v1.1\AutoHotkey.exe",
    r"C:\AutoHotkey\AutoHotkey.exe",
]

# Add LocalAppData and ProgramFiles
local_app = os.getenv('LOCALAPPDATA', '')
if local_app:
    ahk_paths.append(os.path.join(local_app, 'Programs', 'AutoHotkey', 'AutoHotkey.exe'))

program_files = os.getenv('PROGRAMFILES', '')
if program_files:
    ahk_paths.append(os.path.join(program_files, 'AutoHotkey', 'AutoHotkey.exe'))

# Check PATH
print("\n1️⃣  Checking system PATH...")
path_ahk = shutil.which('AutoHotkey.exe')
if path_ahk:
    print(f"   ✅ Found in PATH: {path_ahk}")
    print(f"\n   To use this, run:")
    print(f'   set AHK_PATH={path_ahk}')
else:
    print("   ❌ Not found in PATH")

# Check common locations
print("\n2️⃣  Checking common installation locations...")
found_any = False
for path in ahk_paths:
    if os.path.exists(path):
        print(f"   ✅ FOUND: {path}")
        found_any = True
        print(f"\n   To use this, run:")
        print(f'   set AHK_PATH={path}')
        print()

if not found_any:
    print("   ❌ Not found in any common location")

# Check if any AHK directory exists
print("\n3️⃣  Checking for AutoHotkey directories...")
ahk_dirs = [
    r"C:\Program Files\AutoHotkey",
    r"C:\Program Files (x86)\AutoHotkey",
]

for dir_path in ahk_dirs:
    if os.path.exists(dir_path):
        print(f"\n   📁 Directory exists: {dir_path}")
        print("      Contents:")
        try:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path) and item.lower().endswith('.exe'):
                    print(f"         ✅ {item}")
                elif os.path.isdir(item_path):
                    print(f"         📁 {item}/")
        except Exception as e:
            print(f"         ❌ Error reading directory: {e}")

# Summary
print("\n" + "=" * 70)
if found_any or path_ahk:
    print("✅ AutoHotkey IS INSTALLED on your system!")
    print("\n📋 NEXT STEPS:")
    print("   1. Copy the 'set AHK_PATH=...' command from above")
    print("   2. Run it in your command prompt")
    print("   3. Run the Python script again")
    print("\n   OR restart your computer (if just installed)")
else:
    print("❌ AutoHotkey NOT FOUND on your system!")
    print("\n📥 INSTALLATION REQUIRED:")
    print("   1. Download AutoHotkey v1.1 from:")
    print("      https://www.autohotkey.com/download/ahk-install.exe")
    print("   2. Run the installer")
    print("   3. Choose 'Express Installation'")
    print("   4. Restart this script")

print("\n💡 MANUAL CHECK:")
print("   Search Windows Start Menu for 'AutoHotkey'")
print("   If found, note the installation path and use:")
print('   set AHK_PATH=C:\\full\\path\\to\\AutoHotkey.exe')

print("=" * 70)

input("\nPress Enter to close...")
