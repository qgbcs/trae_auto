#!/usr/bin/env python3
"""
Trae CN 自动签到 v17 - 精确定位紫色用户图标
根据截图分析：
- 积分在右上角，显示"384"
- 积分左边有一个紫色图标
- 点击紫色图标应该弹出签到菜单
"""

import pyautogui
import time
import win32gui
import win32con

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True


def find_trae_window():
    """找到 Trae 主窗口"""
    results = []

    def enum_proc(hwnd, results):
        try:
            title = win32gui.GetWindowText(hwnd)
            if 'Trae' in title:
                rect = win32gui.GetWindowRect(hwnd)
                style = win32gui.GetWindowLong(hwnd, win32gui.GWL_STYLE)
                is_visible = bool(style & win32gui.WS_VISIBLE)
                is_minimized = bool(style & win32gui.WS_MINIMIZE)
                w = rect[2] - rect[0]
                h = rect[3] - rect[1]
                if is_visible and not is_minimized and w > 800 and h > 500:
                    results.append({'hwnd': hwnd, 'rect': rect, 'size': (w, h)})
        except:
            pass

    win32gui.EnumWindows(enum_proc, results)
    if not results:
        return None
    return max(results, key=lambda x: x['size'][0] * x['size'][1])


def main():
    print("精确定位紫色用户图标...")

    # 找到 Trae 窗口
    window = find_trae_window()
    if window:
        rect = window['rect']
        print(f"窗口位置: {rect}")
        # 激活窗口
        win32gui.SetForegroundWindow(window['hwnd'])
        time.sleep(0.3)
    else:
        rect = (36, 0, 1330, 768)
        print("使用默认窗口位置")

    # 截取顶部区域，分析像素
    print("\n截取顶部区域分析...")
    width = rect[2] - rect[0]
    top_bar = pyautogui.screenshot(region=(rect[0], 0, width, 50))
    top_bar.save(r'C:\test\github\trae_auto\v17_topbar.png')
    print("Saved: v17_topbar.png")

    # 根据用户描述，紫色用户图标在积分左边
    # 从截图看，积分在右上角，大约在 x=1200-1250, y=15-25
    # 紫色图标应该在积分左边约 50-80px

    # 测试不同的位置
    test_positions = [
        # 基于窗口位置和截图分析
        (rect[0] + 1150, 18),  # 积分左边
        (rect[0] + 1180, 18),  # 再左边一点
        (rect[0] + 1200, 18),  # 更左边
        (rect[0] + 1220, 18),  # 再左边
        # 基于屏幕坐标（假设屏幕宽度 1920）
        (1850, 18),   # 右上角附近
        (1820, 18),
        (1800, 18),
        (1780, 18),
        (1750, 18),
    ]

    print("\n测试点击位置...")
    for i, (x, y) in enumerate(test_positions):
        print(f"[{i+1}] 点击 ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.2)

        # 点击
        pyautogui.click()
        time.sleep(0.8)

        # 截图
        ss = pyautogui.screenshot()
        fname = f'C:\\test\\github\\trae_auto\\v17_click_{i+1}.png'
        ss.save(fname)
        print(f"    Saved: {fname}")

    print("\n请检查截图，找到弹出签到菜单的位置")


if __name__ == '__main__':
    main()
