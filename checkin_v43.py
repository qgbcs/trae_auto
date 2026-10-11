#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v43 - 精确定位并点击"每日签到"按钮
根据截图分析：
- 屏幕分辨率：1600x900
- "每日签到"按钮位置：y=395-425, x=1010-1100 区域
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

def find_checkin_button():
    """精确定位'每日签到'按钮"""
    log("\n查找'每日签到'按钮...")

    with mss.MSS() as sct:
        # 截取右侧用量管理区域
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
            # 深色文字（接近黑色）
            if r < 80 and g < 80 and b < 80:
                dark_pixels.append((x + 950, y + 350))  # 转换为全局坐标

    if dark_pixels:
        # 找到最大的文字区域（应该是"每日签到"按钮）
        min_x = min(p[0] for p in dark_pixels)
        max_x = max(p[0] for p in dark_pixels)
        min_y = min(p[1] for p in dark_pixels)
        max_y = max(p[1] for p in dark_pixels)

        # 按钮中心
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2 + 5

        log(f"  找到文字: ({min_x}, {min_y}) - ({max_x}, {max_y})")
        log(f"  按钮中心: ({center_x}, {center_y})")

        return center_x, center_y

    # 备用坐标
    log("  使用备用坐标 (1050, 410)")
    return 1050, 410

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v43")
    log("=" * 60)

    # 步骤1: 读取初始积分
    log("\n【步骤1】读取当前积分...")
    STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
    initial_credits = 0

    if STORAGE_JSON.exists():
        try:
            data = json.loads(STORAGE_JSON.read_text())
            commercial = data.get('commercialActivityInfo', {})
            activities = commercial.get('activities', [])

            for act in activities:
                if 'checkin' in act.get('activityType', '').lower():
                    metadata = act.get('metadata', {})
                    work_extra = act.get('workExtra', {})
                    for key in ['totalCredits', 'credits', 'earnedCredits', 'availableCredits']:
                        if key in metadata:
                            initial_credits = metadata[key]
                            break
                        if key in work_extra:
                            initial_credits = work_extra[key]
                            break
                    break
        except Exception as e:
            log(f"  读取失败: {e}")

    log(f"  当前积分: {initial_credits}")

    # 步骤2: 保存初始截图
    log("\n【步骤2】保存初始截图...")
    save_screenshot('before')

    # 步骤3: 查找并点击签到按钮
    log("\n【步骤3】定位并点击签到按钮...")
    btn_x, btn_y = find_checkin_button()

    log(f"  点击位置: ({btn_x}, {btn_y})")
    pyautogui.click(btn_x, btn_y)
    time.sleep(1.5)

    # 步骤4: 保存截图
    log("\n【步骤4】保存点击后截图...")
    save_screenshot('after')

    # 步骤5: 验证
    log("\n【步骤5】验证积分变化...")
    final_credits = initial_credits

    if STORAGE_JSON.exists():
        try:
            data = json.loads(STORAGE_JSON.read_text())
            commercial = data.get('commercialActivityInfo', {})
            activities = commercial.get('activities', [])

            for act in activities:
                if 'checkin' in act.get('activityType', '').lower():
                    metadata = act.get('metadata', {})
                    work_extra = act.get('workExtra', {})
                    for key in ['totalCredits', 'credits', 'earnedCredits', 'availableCredits']:
                        if key in metadata:
                            final_credits = metadata[key]
                            break
                        if key in work_extra:
                            final_credits = work_extra[key]
                            break
                    break
        except:
            pass

    log(f"  新积分: {final_credits}")

    if final_credits > initial_credits:
        increase = final_credits - initial_credits
        log(f"\n✅ 签到成功! 积分增加: {increase}")
    else:
        log(f"\n⚠️ 积分未变化 ({initial_credits} -> {final_credits})")
        log("  请检查界面上的积分显示")
        log("  可能需要手动点击'每日签到'按钮")

    log("\n" + "=" * 60)
    log(f"截图已保存到: {SCREENSHOTS_DIR}")
    log("=" * 60)

if __name__ == '__main__':
    main()
