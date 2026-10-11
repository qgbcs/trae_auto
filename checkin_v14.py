# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v14 - 颜色定位 + 精确点击
通过颜色识别找到用户头像图标（紫色），然后点击
"""
import pyautogui
import win32gui
import win32con
import time
from datetime import datetime
import sys
from PIL import Image, ImageStat

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

def find_color_region(img, target_r, target_g, target_b, tolerance=60):
    """在图像中查找特定颜色区域"""
    pixels = img.load()
    w, h = img.size
    positions = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            if abs(r - target_r) <= tolerance and abs(g - target_g) <= tolerance and abs(b - target_b) <= tolerance:
                positions.append((x, y))
    return positions

def find_avg_position(positions, group_size=15):
    """找到颜色区域的中心位置"""
    if not positions:
        return None
    # 按 x 坐标分组
    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    return (sum(xs) // len(xs), sum(ys) // len(ys))

now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
print(f"=== Trae CN 签到脚本 v14 ===\n")

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

# 截取 Trae 窗口区域（全屏，因为窗口可能超出屏幕）
print("\n截取屏幕...")
screenshot = pyautogui.screenshot()
w, h = screenshot.size
print(f"屏幕分辨率: {w}x{h}")

# 保存截图供分析
shot_before = f"C:\\test\\github\\trae_auto\\v14_before_{now_str}.png"
screenshot.save(shot_before)
print(f"截图1: {shot_before}")

# 查找用户头像图标（紫色/蓝色圆形）
# 从截图中可以看到头像大约是紫色 (#7C3AED 或类似的蓝紫色)
print("\n正在查找用户头像（紫色区域）...")

# 在窗口顶部栏区域搜索紫色
# 窗口客户区: left=36, top=0, width=1330, height=768
# 顶部栏大约在 y=0 到 y=50 之间
TARGET_R, TARGET_G, TARGET_B = 124, 58, 237  # 紫色
TOLERANCE = 80

# 裁剪顶部栏区域进行搜索
top_bar_region = screenshot.crop((left, top, right, top + 60))
top_bar_pixels = list(top_bar_region.getdata())

# 查找紫色像素
purple_pixels = []
for i, pixel in enumerate(top_bar_pixels):
    r, g, b = pixel[:3]
    # 检测紫色：R 和 B 较高，G 较低
    if r > 100 and b > 100 and g < 120 and abs(r - b) < 80:
        x = i % top_bar_region.width
        y = i // top_bar_region.width
        purple_pixels.append((left + x, top + y))

print(f"  找到 {len(purple_pixels)} 个紫色像素")

if len(purple_pixels) >= 10:
    # 找到紫色区域的中心
    avg_x = sum(p[0] for p in purple_pixels) // len(purple_pixels)
    avg_y = sum(p[1] for p in purple_pixels) // len(purple_pixels)
    print(f"  头像中心: ({avg_x}, {avg_y})")

    # 高亮显示找到的位置
    highlight_img = screenshot.copy()
    from PIL import ImageDraw
    draw = ImageDraw.Draw(highlight_img)
    draw.ellipse([avg_x-10, avg_y-10, avg_x+10, avg_y+10], outline='red', width=2)
    highlight_shot = f"C:\\test\\github\\trae_auto\\v14_highlight_{now_str}.png"
    highlight_img.save(highlight_shot)
    print(f"  高亮图: {highlight_shot}")

    # 点击头像
    print(f"\n点击用户头像 ({avg_x}, {avg_y})...")
    time.sleep(0.5)
    pyautogui.click(avg_x, avg_y)
    time.sleep(1.5)

    # 截图查看菜单
    shot_menu = f"C:\\test\\github\\trae_auto\\v14_menu_{now_str}.png"
    pyautogui.screenshot(shot_menu)
    print(f"截图2（菜单）: {shot_menu}")

    # 在菜单中查找签到按钮
    # 头像被点击后，菜单应该出现在头像下方
    # 尝试在头像下方区域查找"签到"文字或按钮
    print("\n扫描菜单项...")
    MENU_START_Y = avg_y + 35
    FOUND_CHECKIN = False

    for i in range(10):
        item_y = MENU_START_Y + i * 30
        item_x = avg_x  # 对齐头像

        # 移动鼠标到菜单项
        pyautogui.moveTo(item_x, item_y, duration=0.05)
        time.sleep(0.1)

        # 检查该位置是否有文字（截图局部区域）
        region = screenshot.crop((item_x - 60, item_y - 10, item_x + 60, item_y + 20))
        region_shot = f"C:\\test\\github\\trae_auto\\v14_region{i}_{now_str}.png"
        region.save(region_shot)

        # 点击
        pyautogui.click()
        time.sleep(0.4)

        # 截图检查
        shot = f"C:\\test\\github\\trae_auto\\v14_scan{i}_{now_str}.png"
        pyautogui.screenshot(shot)
        print(f"  扫描{i}: ({item_x}, {item_y})")

        time.sleep(0.2)

    # 最终截图
    shot_final = f"C:\\test\\github\\trae_auto\\v14_final_{now_str}.png"
    pyautogui.screenshot(shot_final)
    print(f"\n最终截图: {shot_final}")
else:
    print("  未找到紫色区域，尝试其他颜色...")
    # 尝试查找其他颜色（蓝色、灰色等）
    for r, g, b in [(100, 150, 255), (150, 150, 150), (200, 200, 200)]:
        pixels = []
        for y in range(max(0, top), min(h, top + 60)):
            for x in range(left, right):
                px = screenshot.getpixel((x, y))
                if abs(px[0] - r) <= 40 and abs(px[1] - g) <= 40 and abs(px[2] - b) <= 40:
                    pixels.append((x, y))
        if len(pixels) > 20:
            avg_x = sum(p[0] for p in pixels) // len(pixels)
            avg_y = sum(p[1] for p in pixels) // len(pixels)
            print(f"  找到颜色 (R{r},G{g},B{b}) 区域中心: ({avg_x}, {avg_y})")
            print(f"  点击该位置...")
            pyautogui.click(avg_x, avg_y)
            time.sleep(1.5)
            break

win32gui.SetForegroundWindow(hwnd)
print("\n完成！请检查截图确认签到结果")
