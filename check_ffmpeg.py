import os

if os.path.exists("ffmpeg.exe"):
    print("✅ GREAT! I found ffmpeg.exe.")
    print("Restart your bot and it will work.")
else:
    print("❌ ERROR: ffmpeg.exe is MISSING.")
    print(f"Please paste ffmpeg.exe into this folder:\n{os.getcwd()}")