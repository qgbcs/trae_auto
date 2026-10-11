#!/usr/bin/env python3
"""
Trae CN 自动签到 v16 - 重新定位用户图标
用户说：中间紫色用户图标，点击才有签到
之前点击 (780, 20) 弹出的是账户菜单，不是签到菜单
需要找到正确的图标位置
"""

import pyautogui
import time

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True


def main():
    print("重新定位用户图标...")

    # 先截图整个顶部区域
    width, height = pyautogui.size()
    print(f"屏幕: {width}x{height}")

    # 截取顶部区域 (0,0 到 width, 80)
    ss = pyautogui.screenshot(region=(0, 0, width, 80))
    ss.save(r'C:\test\github\trae_auto\v16_topbar.png')
    print("Saved: v16_topbar.png")

    # 根据用户描述，紫色用户图标在"中间"
    # 让我尝试点击顶部工具栏不同位置
    # 假设屏幕宽度 1920，中间大约是 960

    test_positions = [
        # 从中间向两侧测试
        (900, 20),
        (950, 20),
        (1000, 20),
        (1050, 20),
        (1100, 20),
        # 右侧（积分左边）
        (1750, 20),
        (1780, 20),
        (1800, 20),
        (1820, 20),
        # 更右侧
        (1850, 20),
        (1870, 20),
        (1880, 20),
        (1890, 20),
    ]

    print("\n测试点击位置...")
    for i, (x, y) in enumerate(test_positions):
        print(f"[{i+1}] 点击 ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(0.8)

        # 截图
        ss = pyautogui.screenshot()
        fname = f'C:\\test\\github\\trae_auto\\v16_click_{i+1}.png'
        ss.save(fname)
        print(f"    Saved: {fname}")

    print("\n请检查截图，找到弹出签到菜单的位置")


if __name__ == '__main__':
    main()
