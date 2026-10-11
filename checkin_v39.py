#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v39 - 直接点击"每日签到"按钮
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

SCREENSHOTS_DIR = Path(__file__).parent / 'screenshots'
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def save_screenshot(name):
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        filepath = SCREENSHOTS_DIR / f'{name}_{int(time.time())}.png'
        img.save(filepath)
        return filepath

def find_button_by_text():
    """通过文字特征找到按钮位置"""
    log("\n查找'每日签到'按钮...")

    with mss.MSS() as sct:
        # 只截取右侧用量管理区域
        screenshot = sct.grab({
            'left': 1000,
            'top': 200,
            'width': 600,
            'height': 300
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    pixels = img.load()
    w, h = img.size

    # 搜索深色文字区域（按钮文字）
    dark_regions = []
    current_region = []

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            # 深色文字（接近黑色）
            if r < 60 and g < 60 and b < 60:
                current_region.append((x + 1000, y + 200))  # 转换为全局坐标
            else:
                if len(current_region) > 20:  # 足够大的区域
                    dark_regions.append(current_region)
                current_region = []

    if current_region and len(current_region) > 20:
        dark_regions.append(current_region)

    # 找到包含"每日签到"文字的按钮区域
    # 根据截图，按钮在 y=380-420, x=900-1100 区域
    best_match = None
    min_distance = float('inf')

    for region in dark_regions:
        if not region:
            continue

        min_x = min(p[0] for p in region)
        max_x = max(p[0] for p in region)
        min_y = min(p[1] for p in region)
        max_y = max(p[1] for p in region)

        # 检查是否在目标区域
        if 380 <= min_y <= 420 and 900 <= min_x <= 1100:
            # 计算与中心点的距离
            center_x = (min_x + max_x) // 2
            center_y = (min_y + max_y) // 2
            distance = ((center_x - 1000) ** 2 + (center_y - 400) ** 2) ** 0.5

            if distance < min_distance:
                min_distance = distance
                best_match = (center_x, center_y)
                log(f"  找到候选按钮: ({min_x}, {min_y}) - ({max_x}, {max_y}), 中心: ({center_x}, {center_y})")

    if best_match:
        return best_match

    # 备用：使用已知坐标
    log("  使用备用坐标 (1012, 415)")
    return 1012, 415

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v39")
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

    # 步骤2: 截图
    log("\n【步骤2】保存初始截图...")
    save_screenshot('before')

    # 步骤3: 查找并点击签到按钮
    log("\n【步骤3】定位并点击签到按钮...")
    btn_x, btn_y = find_button_by_text()

    log(f"  点击: ({btn_x}, {btn_y})")
    pyautogui.click(btn_x, btn_y)
    time.sleep(1.5)

    # 步骤4: 截图
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
        log(f"\n⚠️ 积分未变化，可能需要手动点击")
        log(f"  请查看截图确认签到状态")

    log("\n" + "=" * 60)
    log(f"截图已保存到: {SCREENSHOTS_DIR}")
    log("=" * 60)

if __name__ == '__main__':
    main()
