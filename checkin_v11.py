# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v11 - 窗口 DC 截图方式
使用 Windows GDI BitBlt 直接捕获 Trae 窗口内容
"""
import pyautogui
import win32gui
import win32ui
import win32con
import time
from datetime import datetime
import sys
from PIL import Image
import struct
import zlib

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = False

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

def capture_window_gdi(hwnd):
    """使用 GDI BitBlt 截取窗口"""
    try:
        # 获取窗口客户区
        rect = win32gui.GetWindowRect(hwnd)
        # 获取客户区（不含标题栏、边框）
        client_rect = win32gui.GetClientRect(hwnd)
        # 转换为客户区屏幕坐标
        left, top = win32gui.ClientToScreen(hwnd, (0, 0))
        width = client_rect[2]
        height = client_rect[3]

        hdc = win32gui.GetWindowDC(hwnd)
        if not hdc:
            return None, None, left, top, width, height

        mem_dc = win32gui.CreateCompatibleDC(hdc)
        bitmap = win32gui.CreateCompatibleBitmap(hdc, width, height)
        old_bitmap = win32gui.SelectObject(mem_dc, bitmap)
        win32gui.BitBlt(mem_dc, 0, 0, width, height, hdc, left, top, win32con.SRCCOPY)

        win32gui.SelectObject(mem_dc, old_bitmap)
        win32gui.DeleteDC(mem_dc)
        win32gui.ReleaseDC(hwnd, hdc)

        # 转换为 PIL Image
        bmp_info = win32gui.GetBitmapInfoStructure(bitmap)
        bmp_bits = win32gui.GetBitmapBits(bitmap)
        img = Image.frombuffer('RGB', (width, height), bmp_bits, 'RGB', 0, 1, 0)
        win32gui.DeleteObject(bitmap)

        return img, bitmap, left, top, width, height
    except Exception as e:
        print(f"  GDI截图错误: {e}")
        import traceback
        traceback.print_exc()
        return None, None, 0, 0, 0, 0

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v11 ===\n")

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

# 用户图标位置
USER_REL_X = int(width * 0.55)
USER_REL_Y = 20
screen_offset_y = max(0, -top)
screen_x = left + USER_REL_X
screen_y = top + USER_REL_Y + screen_offset_y
print(f"用户图标: 窗口内({USER_REL_X}, {USER_REL_Y}), 屏幕({screen_x}, {screen_y})")

# 截取 Trae 窗口内容
print(f"\n截取 Trae 窗口...")
img, bmp, cap_left, cap_top, cap_w, cap_h = capture_window_gdi(hwnd)
if img:
    shot1 = f"C:\\test\\github\\trae_auto\\v11_before_{now_str}.png"
    img.save(shot1)
    print(f"截图1（签到前）: {shot1}  ({cap_w}x{cap_h})")
else:
    print("  GDI截图失败，回退到 pyautogui")
    shot1 = f"C:\\test\\github\\trae_auto\\v11_before_{now_str}.png"
    pyautogui.screenshot(shot1, region=(left, top, width, height))
    print(f"截图1: {shot1}")

time.sleep(0.5)

# 激活 Trae 窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.3)

# 点击用户图标
print(f"\n点击用户图标 ({screen_x}, {screen_y})...")
pyautogui.click(screen_x, screen_y)
time.sleep(1.5)

# 截取菜单
print("截取菜单...")
img2, _, _, _, _, _ = capture_window_gdi(hwnd)
if img2:
    shot2 = f"C:\\test\\github\\trae_auto\\v11_menu_{now_str}.png"
    img2.save(shot2)
    print(f"截图2（菜单）: {shot2}")
else:
    shot2 = f"C:\\test\\github\\trae_auto\\v11_menu_{now_str}.png"
    pyautogui.screenshot(shot2, region=(left, top, width, height))
    print(f"截图2: {shot2}")

# 在菜单中扫描签到按钮
MENU_START_Y = USER_REL_Y + 40
FOUND_CHECKIN = False

for i in range(8):
    item_y = MENU_START_Y + i * 28
    item_screen_y = top + item_y + screen_offset_y

    pyautogui.moveTo(screen_x, item_screen_y, duration=0.05)
    time.sleep(0.15)

    pyautogui.click()
    time.sleep(0.5)

    img3, _, _, _, _, _ = capture_window_gdi(hwnd)
    if img3:
        shot = f"C:\\test\\github\\trae_auto\\v11_scan{i}_{now_str}.png"
        img3.save(shot)
        print(f"  扫描{i}: ({screen_x}, {item_screen_y}), 截图: {shot}")
    else:
        shot = f"C:\\test\\github\\trae_auto\\v11_scan{i}_{now_str}.png"
        pyautogui.screenshot(shot, region=(left, top, width, height))
        print(f"  扫描{i}: 截图: {shot}")

    time.sleep(0.3)

# 最终截图
img_final, _, _, _, _, _ = capture_window_gdi(hwnd)
if img_final:
    shot3 = f"C:\\test\\github\\trae_auto\\v11_final_{now_str}.png"
    img_final.save(shot3)
    print(f"\n最终截图: {shot3}")
else:
    shot3 = f"C:\\test\\github\\trae_auto\\v11_final_{now_str}.png"
    pyautogui.screenshot(shot3, region=(left, top, width, height))
    print(f"\n最终截图: {shot3}")

win32gui.SetForegroundWindow(hwnd)
print("\n完成！请检查截图确认签到结果")
