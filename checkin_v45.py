#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v45 - 修复F5冲突问题
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from PIL import Image
import mss
import pyautogui

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

SCRIPT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = SCRIPT_DIR / 'screenshots'
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def save_screenshot(name):
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        filepath = SCREENSHOTS_DIR / f'{name}_{int(time.time())}.png'
        img.save(filepath)
        log(f"  截图: {filepath.name}")
        return filepath

def get_credits_from_storage():
    """从storage.json获取积分"""
    STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
    if not STORAGE_JSON.exists():
        return 0

    try:
        data = json.loads(STORAGE_JSON.read_text())
        icube = data.get('iCubeServerData://icube.cloudide', {})
        commercial = icube.get('commercialActivityInfo', {})
        activities = commercial.get('activities', [])

        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                work_extra = act.get('workExtra', {})
                return work_extra.get('work_credits', 0)
    except:
        pass

    return 0

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v45")
    log("=" * 60)

    # 步骤1: 读取初始积分
    log("\n【步骤1】读取初始积分...")
    initial_credits = get_credits_from_storage()
    log(f"  当前积分: {initial_credits}")

    # 步骤2: 截图当前状态
    log("\n【步骤2】保存当前状态截图...")
    save_screenshot('before')

    # 步骤3: 查找并点击签到按钮
    log("\n【步骤3】定位并点击签到按钮...")

    # 先按Escape关闭任何打开的菜单
    pyautogui.press('esc')
    time.sleep(0.3)

    # 点击用量管理页面区域（确保焦点在那里）
    pyautogui.click(1300, 300)
    time.sleep(0.5)

    # 查找"每日签到"按钮
    with mss.MSS() as sct:
        screenshot = sct.grab({
            'left': 950,
            'top': 350,
            'width': 650,
            'height': 150
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    pixels = img.load()
    w, h = img.size

    # 搜索深色文字区域
    dark_pixels = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            if r < 80 and g < 80 and b < 80:
                dark_pixels.append((x + 950, y + 350))

    if dark_pixels:
        min_x = min(p[0] for p in dark_pixels)
        max_x = max(p[0] for p in dark_pixels)
        min_y = min(p[1] for p in dark_pixels)
        max_y = max(p[1] for p in dark_pixels)
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2 + 5
        log(f"  找到按钮: ({center_x}, {center_y})")
    else:
        center_x, center_y = 1050, 410
        log(f"  使用备用坐标: ({center_x}, {center_y})")

    # 点击签到按钮
    pyautogui.click(center_x, center_y)
    time.sleep(2)

    # 步骤4: 截图点击后状态
    log("\n【步骤4】保存点击后截图...")
    save_screenshot('after_click')

    # 步骤5: 等待并重新读取积分
    log("\n【步骤5】等待刷新...")
    time.sleep(3)

    final_credits = get_credits_from_storage()
    log(f"  新积分: {final_credits}")

    # 步骤6: 最终截图
    log("\n【步骤6】保存最终截图...")
    save_screenshot('final')

    if final_credits > initial_credits:
        increase = final_credits - initial_credits
        log(f"\n✅ 签到成功! 积分增加: {increase}")
    else:
        log(f"\n⚠️ 积分未变化 ({initial_credits} -> {final_credits})")
        log("  请检查界面上的积分显示")

    log("\n" + "=" * 60)
    log(f"截图已保存到: {SCREENSHOTS_DIR}")
    log("=" * 60)

if __name__ == '__main__':
    main()
