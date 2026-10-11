#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v38 - 精确定位并点击"每日签到"按钮
"""
import sys
import time
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from PIL import Image
import mss
import pyautogui

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

# 屏幕配置
SCREEN = {
    'width': 1600,
    'height': 900
}

TRAЕ_FOLDER = Path.home() / '.trae-cn'
TRAЕ_JWT = TRAЕ_FOLDER / 'trae-jwt-token'
STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
SCRIPT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = SCRIPT_DIR / 'screenshots'

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_jwt():
    if TRAЕ_JWT.exists():
        return TRAЕ_JWT.read_text().strip()
    log("ERROR: JWT token not found")
    return None

def save_screenshot(name):
    """保存屏幕截图"""
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        filepath = SCREENSHOTS_DIR / f'{name}_{int(time.time())}.png'
        img.save(filepath)
        log(f"  截图已保存: {filepath.name}")
        return filepath

def find_checkin_button_precise():
    """精确定位签到按钮"""
    log("\n精确定位签到按钮...")
    
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    pixels = img.load()
    w, h = img.size
    
    # 根据截图分析，"每日签到"按钮在 y=380-420, x=900-1100 区域
    # 文字是深色的（接近黑色）
    
    text_pixels = []
    for y in range(380, 420):
        for x in range(900, 1100):
            r, g, b = pixels[x, y][:3]
            # 深色文字
            if r < 80 and g < 80 and b < 80:
                text_pixels.append((x, y))
    
    if text_pixels:
        min_x = min(p[0] for p in text_pixels)
        max_x = max(p[0] for p in text_pixels)
        min_y = min(p[1] for p in text_pixels)
        max_y = max(p[1] for p in text_pixels)
        
        # 按钮中心
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2 + 10  # 稍微向下偏移
        
        log(f"  找到文字区域: ({min_x}, {min_y}) - ({max_x}, {max_y})")
        log(f"  按钮中心: ({center_x}, {center_y})")
        
        return center_x, center_y
    
    # 备用：使用已知坐标
    log("  使用备用坐标 (1003, 375)")
    return 1003, 375

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v38")
    log("=" * 60)
    
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 步骤1: 读取初始积分
    log("\n【步骤1】获取当前积分...")
    if STORAGE_JSON.exists():
        try:
            data = json.loads(STORAGE_JSON.read_text())
            commercial = data.get('commercialActivityInfo', {})
            activities = commercial.get('activities', [])
            
            initial_credits = 0
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
            
            log(f"  当前积分: {initial_credits}")
        except Exception as e:
            log(f"  读取积分失败: {e}")
            initial_credits = 0
    else:
        log("  storage.json 不存在")
        initial_credits = 0
    
    # 步骤2: 截图当前状态
    log("\n【步骤2】保存初始状态截图...")
    save_screenshot('before_checkin')
    
    # 步骤3: 精确定位并点击签到按钮
    log("\n【步骤3】定位并点击每日签到按钮...")
    btn_x, btn_y = find_checkin_button_precise()
    
    log(f"  点击位置: ({btn_x}, {btn_y})")
    pyautogui.click(btn_x, btn_y)
    time.sleep(1)
    
    # 步骤4: 保存截图
    log("\n【步骤4】保存截图...")
    save_screenshot('after_click')
    
    # 步骤5: 等待并验证
    log("\n【步骤5】等待界面刷新...")
    time.sleep(3)
    
    # 重新读取积分
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
        log(f"\n⚠️ 签到可能失败，积分未变化 ({initial_credits} -> {final_credits})")
        log("  请检查界面上的积分显示")
    
    log("\n" + "=" * 60)
    log("完成! 请查看截图确认签到结果")
    log("=" * 60)
    log(f"\n截图目录: {SCREENSHOTS_DIR}")

if __name__ == '__main__':
    main()
