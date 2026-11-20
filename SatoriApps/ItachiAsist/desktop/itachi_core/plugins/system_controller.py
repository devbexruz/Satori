"""
SATORI ECOSYSTEM — ItachiAssist
================================
plugins/system_controller.py

AI (Gemini) uchun Tizim, Ilovalar, Sichqoncha va Klaviatura boshqaruv asboblari.
Ixtiyoriy dasturni ochish, ekranni boshqarish va tizim buyruqlarini bajarish.
"""

import logging
import os
import shutil
import subprocess
import time
from typing import Any

logger = logging.getLogger("itachi.system_controller")

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    PYAUTOGUI_AVAILABLE = True
except Exception as e:
    logger.warning(f"[SystemController] PyAutoGUI ishga tushmadi: {e}")
    PYAUTOGUI_AVAILABLE = False


# Keng tarqalgan ilovalarning Linux komandalari bilan mosligi
APP_ALIASES = {
    "chrome": "google-chrome",
    "google chrome": "google-chrome",
    "google-chrome": "google-chrome",
    "browser": "google-chrome",
    "brave": "brave-browser",
    "firefox": "firefox",
    "code": "code",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "terminal": "x-terminal-emulator",
    "console": "x-terminal-emulator",
    "telegram": "telegram-desktop",
    "telegram-desktop": "telegram-desktop",
    "files": "xdg-open ~",
    "file manager": "xdg-open ~",
    "nautilus": "nautilus",
    "calculator": "gnome-calculator",
    "calc": "gnome-calculator",
    "text editor": "gedit",
    "gedit": "gedit",
    "notepad": "gedit",
    "settings": "gnome-control-center",
}


class SystemController:
    """Tizim darajasidagi boshqaruvchi (Tools/Actions)."""

    @staticmethod
    def open_application(app_name: str, target: str = "") -> str:
        """
        Ixtiyoriy dasturni ochadi yoki URL/faylni ochadi.
        
        Args:
            app_name: Ilova nomi (masalan, "chrome", "code", "firefox", "telegram", "terminal")
            target: Qo'shimcha parametr, sayt manzili yoki fayl yo'li (masalan, "https://google.com")
        """
        clean_name = app_name.lower().strip()
        cmd_name = APP_ALIASES.get(clean_name, clean_name)

        # Agar URL berilgan bo'lsa
        if clean_name.startswith("http://") or clean_name.startswith("https://"):
            try:
                subprocess.Popen(["xdg-open", clean_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Successfully opened URL: {clean_name}"
            except Exception as e:
                return f"Failed to open URL: {e}"

        # YouTube va musiqa so'rovlarini to'g'ridan-to'g'ri brauzerda ochish
        if "youtube" in clean_name or "music" in clean_name or "youtube" in target.lower():
            import urllib.parse
            query = target if target else clean_name.replace("youtube", "").replace("music", "").strip()
            if query and query not in ("youtube", "music"):
                url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Successfully opened YouTube search for: {query}"
            else:
                subprocess.Popen(["xdg-open", "https://www.youtube.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return "Successfully opened YouTube"

        # Agar target URL yoki fayl bo'lsa
        if target:
            try:
                # Agar app mavjud bo'lsa app bilan ochish
                binary = shutil.which(cmd_name.split()[0])
                if binary:
                    subprocess.Popen([binary, target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Successfully launched {app_name} with target: {target}"
                else:
                    subprocess.Popen(["xdg-open", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Successfully opened {target}"
            except Exception as e:
                return f"Error opening with target: {e}"

        # To'g'ridan-to'g'ri dasturni ochish
        cmd_parts = cmd_name.split()
        binary = shutil.which(cmd_parts[0])

        if binary:
            try:
                subprocess.Popen(cmd_parts, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                return f"Successfully launched {app_name} ({binary})"
            except Exception as e:
                return f"Failed to launch {app_name}: {e}"

        # Brauzer orqali qidirish yoki xdg-open orqali sinash
        try:
            subprocess.Popen(["xdg-open", cmd_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Attempted to open {app_name} via system handler."
        except Exception as e:
            return f"Application '{app_name}' not found on system. Error: {e}"

    @staticmethod
    def mouse_control(action: str, x: int = None, y: int = None, button: str = "left", clicks: int = 1) -> str:
        """
        Sichqonchani boshqaradi.
        
        Args:
            action: 'move', 'click', 'double_click', 'right_click', 'scroll'
            x, y: Ekran koordinatalari (agar bo'lmasa joriy joyida bajaradi)
            button: 'left', 'right', 'middle'
            clicks: Necha marta bosish
        """
        if not PYAUTOGUI_AVAILABLE:
            return "PyAutoGUI is not available on this environment."

        try:
            screen_w, screen_h = pyautogui.size()

            if x is not None and y is not None:
                target_x = max(0, min(screen_w - 1, x))
                target_y = max(0, min(screen_h - 1, y))
            else:
                target_x, target_y = pyautogui.position()

            action_lower = action.lower()

            if action_lower == "move":
                pyautogui.moveTo(target_x, target_y, duration=0.25)
                return f"Mouse moved to ({target_x}, {target_y})"

            elif action_lower == "click":
                pyautogui.click(target_x, target_y, clicks=clicks, button=button)
                return f"Mouse clicked at ({target_x}, {target_y}) with {button} button"

            elif action_lower in ("double_click", "doubleclick"):
                pyautogui.doubleClick(target_x, target_y)
                return f"Mouse double-clicked at ({target_x}, {target_y})"

            elif action_lower in ("right_click", "rightclick"):
                pyautogui.rightClick(target_x, target_y)
                return f"Mouse right-clicked at ({target_x}, {target_y})"

            elif action_lower == "scroll":
                clicks_amount = clicks if clicks != 1 else 3
                pyautogui.scroll(clicks_amount)
                return f"Mouse scrolled by {clicks_amount}"

            return f"Unknown mouse action: {action}"
        except Exception as e:
            return f"Mouse control error: {e}"

    @staticmethod
    def keyboard_control(action: str, text: str = "", hotkey: str = "", key: str = "") -> str:
        """
        Klaviaturani boshqaradi.
        
        Args:
            action: 'type', 'hotkey', 'press'
            text: Yozilishi kerak bo'lgan matn
            hotkey: Klavishlar kombinatsiyasi vergul bilan (masalan, "ctrl,t", "alt,f4", "ctrl,c")
            key: Bitta bosiladigan klavish (masalan, "enter", "esc", "tab", "space")
        """
        if not PYAUTOGUI_AVAILABLE:
            return "PyAutoGUI is not available on this environment."

        try:
            action_lower = action.lower()

            if action_lower == "type":
                pyautogui.write(text, interval=0.03)
                return f"Typed text: '{text[:50]}...'" if len(text) > 50 else f"Typed text: '{text}'"

            elif action_lower == "hotkey":
                keys = [k.strip().lower() for k in hotkey.replace("+", ",").split(",") if k.strip()]
                if keys:
                    pyautogui.hotkey(*keys)
                    return f"Pressed hotkey: {'+'.join(keys)}"
                return "No hotkey keys provided"

            elif action_lower == "press":
                target_key = key.lower().strip() or "enter"
                pyautogui.press(target_key)
                return f"Pressed key: {target_key}"

            return f"Unknown keyboard action: {action}"
        except Exception as e:
            return f"Keyboard control error: {e}"

    @staticmethod
    def execute_bash(command: str) -> str:
        """
        Tizim darajasidagi bash komandasini bajaradi va natijani qaytaradi.
        
        Args:
            command: Bajariladigan bash komandasi
        """
        # Xavfsizlik cheklovi: tizimni butunlay o'chirib yuboradigan destruktiv komandalarni bloklash
        blocked = ["rm -rf /", ":(){ :|:& };:", "mkfs", "dd if=/dev/zero"]
        for b in blocked:
            if b in command:
                return f"Command blocked for security reasons: {b}"

        try:
            res = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            output = res.stdout.strip()
            err = res.stderr.strip()
            if res.returncode == 0:
                return output if output else "Command executed successfully (no output)."
            return f"Command exited with code {res.returncode}. Error: {err}\nOutput: {output}"
        except subprocess.TimeoutExpired:
            return "Command timed out after 15 seconds."
        except Exception as e:
            return f"Error executing command: {e}"
