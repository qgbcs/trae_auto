# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v16 - 直接点击用量管理页面的"每日签到"
"""
import pyautogui
import win32gui
import win32con
import time
from datetime import datetime
import sys

pyautogui.PAUSE = 0.05
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

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v16 ===\n")

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

# 打开用量管理页面
print("\n步骤1: 点击用户头像打开用量管理...")
# 紫色头像区域（从之前的分析）
avatar_x, avatar_y = 733, 21
print(f"  点击头像: ({avatar_x}, {avatar_y})")
pyautogui.click(avatar_x, avatar_y)
time.sleep(1.5)

# 截图确认用量管理页面
shot_usage = f"C:\\test\\github\\trae_auto\\v16_usage_{now_str}.png"
pyautogui.screenshot(shot_usage)
print(f"  截图: {shot_usage}")

# 点击"每日签到"按钮
# 从截图可以看到，"每日签到"在用量管理页面中，大约在 x=920, y=420 附近
print("\n步骤2: 点击'每日签到'按钮...")
# 用量管理页面宽度约 440px（从之前数据 chatSize.width=440），起始 x ≈ 926
# "每日签到"行大约在页面中间偏下位置
checkin_x = 920
checkin_y = 425

print(f"  点击签到按钮: ({checkin_x}, {checkin_y})")
pyautogui.moveTo(checkin_x, checkin_y, duration=0.2)
time.sleep(0.2)
pyautogui.click()
time.sleep(2)

# 截图查看结果
shot_result = f"C:\\test\\github\\trae_auto\\v16_result_{now_str}.png"
pyautogui.screenshot(shot_result)
print(f"\n结果截图: {shot_result}")

# 检查积分是否变化
print("\n步骤3: 检查积分变化...")
time.sleep(1)
shot_final = f"C:\\test\\github\\trae_auto\\v16_final_{now_str}.png"
pyautogui.screenshot(shot_final)
print(f"最终截图: {shot_final}")

# 查找积分数字区域并截图放大
# 积分数字在用量管理卡片中，大约 (950, 280) 到 (1020, 310)
pixel_region = f"C:\\test\\github\\trae_auto\\v16_pixel_{now_str}.png"
screenshot = pyautogui.screenshot()
# 放大积分数字区域
crop_region = screenshot.crop((940, 270, 1050, 320))
crop_region.save(pixel_region)
print(f"积分区域截图: {pixel_region}")

win32gui.SetForegroundWindow(hwnd)
print("\n完成！请检查截图确认签到结果")
