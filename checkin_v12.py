# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v12 - 键盘快捷键方案
使用 SendInput API 发送组合键，尝试 Ctrl+Shift+P 打开命令面板搜索 checkin
"""
import pyautogui
import win32gui
import win32api
import win32con
import time
from datetime import datetime
import sys
from ctypes import windll, byref, Structure, c_ulong, sizeof

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False

class KEYBDINPUT(Structure):
    _fields_ = [
        ("wVk", c_ulong),
        ("wScan", c_ulong),
        ("dwFlags", c_ulong),
        ("time", c_ulong),
        ("dwExtraInfo", c_ulong),
    ]

class INPUT(Structure):
    _fields_ = [("type", c_ulong), ("ki", KEYBDINPUT)]

VK_MAP = {
    'Shift': 0x10, 'Ctrl': 0x11, 'Alt': 0x12,
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
    'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
    'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44,
    'E': 0x45, 'F': 0x46, 'G': 0x47, 'H': 0x48,
    'I': 0x49, 'J': 0x4A, 'K': 0x4B, 'L': 0x4C,
    'M': 0x4D, 'N': 0x4E, 'O': 0x4F, 'P': 0x50,
    'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
    'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58,
    'Y': 0x59, 'Z': 0x5A,
    'SPACE': 0x20, 'TAB': 0x09, 'ENTER': 0x0D,
    'ESCAPE': 0x1B, 'DOWN': 0x28, 'UP': 0x26,
    'LEFT': 0x25, 'RIGHT': 0x27, 'HOME': 0x24,
    'END': 0x23, 'PAGEUP': 0x21, 'PAGEDOWN': 0x22,
}

def send_key_combo(keys):
    """发送键盘组合键"""
    for k in keys:
        vk = VK_MAP.get(k, 0)
        if vk:
            windll.user32.SendInput(1, byref(INPUT(c_ulong(0), KEYBDINPUT(vk, 0, 0, 0, 0))), c_ulong(sizeof(INPUT)))
    time.sleep(0.1)
    for k in reversed(keys):
        vk = VK_MAP.get(k, 0)
        if vk:
            windll.user32.SendInput(1, byref(INPUT(c_ulong(0), KEYBDINPUT(vk, 0, 0x2, 0, 0))), c_ulong(sizeof(INPUT)))
    time.sleep(0.1)

def send_key(vk_code):
    """发送单个按键"""
    windll.user32.SendInput(1, byref(INPUT(c_ulong(0), KEYBDINPUT(vk_code, 0, 0, 0, 0))), c_ulong(sizeof(INPUT)))
    time.sleep(0.05)
    windll.user32.SendInput(1, byref(INPUT(c_ulong(0), KEYBDINPUT(vk_code, 0, 0x2, 0, 0))), c_ulong(sizeof(INPUT)))

def find_trae_window():
    windows = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title.upper():
                rect = win32gui.GetWindowRect(hwnd)
                w, h = rect[2]-rect[0], rect[3]-rect[1]
                if w > 600 and h > 300:
                    results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, windows)
    if not windows:
        return None
    return max(windows, key=lambda x: (x[2][2]-x[2][0]) * (x[2][3]-x[2][1]))

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v12 ===\n")

# 找窗口
print("查找 Trae 窗口...")
result = find_trae_window()
if not result:
    print("ERROR: 找不到 Trae 窗口!")
    sys.exit(1)

hwnd, title, rect = result
left, top, right, bottom = rect
width = right - left
height = bottom - top
print(f"窗口: {title}")
print(f"位置: ({left}, {top}), 大小: {width}x{height}")

# 激活窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.3)

# 用户图标位置
USER_REL_X = int(width * 0.55)
USER_REL_Y = 20
screen_offset_y = max(0, -top)
screen_x = left + USER_REL_X
screen_y = top + USER_REL_Y + screen_offset_y
print(f"用户图标: 窗口内({USER_REL_X}, {USER_REL_Y}), 屏幕({screen_x}, {screen_y})")

# 方法1: 尝试 Ctrl+Shift+P 打开命令面板搜索 checkin
print("\n--- 方法1: Ctrl+Shift+P 命令面板 ---")
send_key_combo(['Ctrl', 'Shift', 'P'])
time.sleep(0.8)

shot1 = f"C:\\test\\github\\trae_auto\\v12_cmd_{now_str}.png"
pyautogui.screenshot(shot1)
print(f"截图1: {shot1}")

# 输入 checkin
print("输入 'checkin'...")
pyautogui.typewrite('checkin', interval=0.05)
time.sleep(0.5)

shot2 = f"C:\\test\\github\\trae_auto\\v12_cmd2_{now_str}.png"
pyautogui.screenshot(shot2)
print(f"截图2: {shot2}")

# 按回车
print("按回车...")
send_key(win32con.VK_RETURN)
time.sleep(1)

shot3 = f"C:\\test\\github\\trae_auto\\v12_cmd3_{now_str}.png"
pyautogui.screenshot(shot3)
print(f"截图3: {shot3}")

# 关闭面板
send_key(win32con.VK_ESCAPE)
time.sleep(0.3)

# 方法2: 直接点击用户图标
print(f"\n--- 方法2: 点击用户图标 ({screen_x}, {screen_y}) ---")
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.2)

pyautogui.moveTo(screen_x, screen_y, duration=0.3)
time.sleep(0.3)
print("点击用户图标...")
pyautogui.click()
time.sleep(1.5)

shot4 = f"C:\\test\\github\\trae_auto\\v12_menu_{now_str}.png"
pyautogui.screenshot(shot4)
print(f"截图4（菜单）: {shot4}")

# 在菜单中扫描签到按钮
MENU_START_Y = USER_REL_Y + 40
for i in range(8):
    item_y = MENU_START_Y + i * 28
    item_screen_y = top + item_y + screen_offset_y

    pyautogui.moveTo(screen_x, item_screen_y, duration=0.05)
    time.sleep(0.15)

    pyautogui.click()
    time.sleep(0.5)

    shot = f"C:\\test\\github\\trae_auto\\v12_scan{i}_{now_str}.png"
    pyautogui.screenshot(shot)
    print(f"  扫描{i}: ({screen_x}, {item_screen_y})")

    time.sleep(0.3)

# 最终截图
shot_final = f"C:\\test\\github\\trae_auto\\v12_final_{now_str}.png"
pyautogui.screenshot(shot_final)
print(f"\n最终截图: {shot_final}")

win32gui.SetForegroundWindow(hwnd)
print("\n完成！请检查截图确认签到结果")
