# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v15 - 直接点击"每日签到"按钮
从用量管理页面点击"每日签到"完成签到
"""
import pyautogui
import win32gui
import win32con
import time
from datetime import datetime
import sys
from PIL import Image

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

def find_color_bounded_region(img, target_r, target_g, target_b, tolerance=60):
    """找到同色区域的包围盒"""
    pixels = img.load()
    w, h = img.size
    positions = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            if abs(r - target_r) <= tolerance and abs(g - target_g) <= tolerance and abs(b - target_b) <= tolerance:
                positions.append((x, y))
    if not positions:
        return None
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    return (min(xs), min(ys), max(xs), max(ys))

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v15 ===\n")

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

# 方法1: 先尝试点击用户头像打开用量管理
print("\n步骤1: 点击用户头像...")
# 用颜色定位紫色头像
screenshot = pyautogui.screenshot()
W, H = screenshot.size
print(f"屏幕: {W}x{H}")

# 在顶部栏区域查找紫色
TARGET_R, TARGET_G, TARGET_B = 124, 58, 237
purple_box = find_color_bounded_region(screenshot, TARGET_R, TARGET_G, TARGET_B, tolerance=60)
if purple_box:
    x1, y1, x2, y2 = purple_box
    avatar_x = (x1 + x2) // 2
    avatar_y = (y1 + y2) // 2
    print(f"  头像区域: ({x1},{y1},{x2},{y2}), 中心: ({avatar_x}, {avatar_y})")

    pyautogui.click(avatar_x, avatar_y)
    time.sleep(1.5)

    # 截图查看用量管理页面
    shot1 = f"C:\\test\\github\\trae_auto\\v15_usage_{now_str}.png"
    pyautogui.screenshot(shot1)
    print(f"  截图（用量管理）: {shot1}")
else:
    print("  未找到紫色头像，使用备用坐标")
    # 备用坐标：根据之前分析的窗口位置
    client_left = 36
    avatar_x = client_left + int(1330 * 0.58)
    avatar_y = 20
    pyautogui.click(avatar_x, avatar_y)
    time.sleep(1.5)

# 方法2: 在用量管理页面查找"每日签到"按钮
print("\n步骤2: 查找并点击'每日签到'按钮...")
screenshot2 = pyautogui.screenshot()

# 查找"每日签到"按钮 - 通常是一个带箭头的文本按钮
# 在截图中搜索包含"每日签到"文字的区域
# 由于没有 OCR，我们用颜色来定位（按钮背景通常是白色/浅灰色，文字是深色）

# 方法：在用量管理区域搜索特定布局
# 用量管理页面中，"每日签到"通常在中间偏左位置
# 从之前的截图看，它在约 (950, 400) 附近（相对于屏幕）

# 尝试在已知位置点击
# 用量管理页面的"每日签到"行大约在 y=400-450 之间
CHECKIN_Y_START = 380
CHECKIN_Y_END = 500

for y in range(CHECKIN_Y_START, CHECKIN_Y_END, 15):
    # 在 y 行搜索深色文字区域（按钮文字）
    found_text = False
    for x in range(left + 200, right - 100, 5):
        px = screenshot2.getpixel((x, y))
        # 检查是否是深色文字（R,G,B 都比较低但不全黑）
        if px[0] < 80 and px[1] < 80 and px[2] < 80 and px[0] > 20:
            # 检查右侧是否有箭头 ">"
            for dx in range(1, 30):
                right_px = screenshot2.getpixel((x + dx, y))
                # 箭头可能是灰色或紫色
                if right_px[0] < 100 and right_px[1] < 100 and right_px[2] < 100:
                    found_text = True
                    print(f"  可能找到文字区域: ({x}, {y})")
                    break
            if found_text:
                break

    if found_text:
        # 移动到文字右侧点击
        click_x = x + 20
        click_y = y
        print(f"\n  点击'每日签到'按钮: ({click_x}, {click_y})")
        pyautogui.moveTo(click_x, click_y, duration=0.2)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(1.5)
        break

# 如果上面的方法没成功，尝试直接在截图中查找特定位置
# 从之前截图看，"每日签到"文字大约在屏幕中部偏右
if not found_text:
    print("  直接用备用坐标尝试...")
    # 用量管理页面中，"每日签到"大约在屏幕中央偏右
    backup_x = left + 500
    backup_y = top + 420 + max(0, -top)
    print(f"  备用坐标: ({backup_x}, {backup_y})")
    pyautogui.moveTo(backup_x, backup_y, duration=0.2)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(1.5)

# 截图查看结果
shot_result = f"C:\\test\\github\\trae_auto\\v15_result_{now_str}.png"
pyautogui.screenshot(shot_result)
print(f"\n结果截图: {shot_result}")

# 再截取一次确认积分变化
time.sleep(0.5)
shot_confirm = f"C:\\test\\github\\trae_auto\\v15_confirm_{now_str}.png"
pyautogui.screenshot(shot_confirm)
print(f"确认截图: {shot_confirm}")

# 查找积分数字
print("\n分析积分数字...")
screenshot3 = pyautogui.screenshot()
pixels = screenshot3.load()
# 查找大数字（白色背景上的深色数字）
# 从截图中看到积分数字在用量管理卡片中，大约 (950, 280) 附近
# 直接在该区域搜索数字

# 查找可能的积分数字区域（白色背景上的深色数字）
DIGIT_REGION = [(900, 260), (1050, 310)]  # 估计的积分显示区域
for dx, dy in DIGIT_REGION:
    region = screenshot3.crop((dx-30, dy-15, dx+60, dy+20))
    region.save(f"C:\\test\\github\\trae_auto\\v15_digit_{dx}_{dy}.png")

win32gui.SetForegroundWindow(hwnd)
print("\n完成！请检查截图确认签到结果")
