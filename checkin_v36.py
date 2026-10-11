#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v36 - 简化版
"""
import sys
import time
import os
import json
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
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        filepath = SCREENSHOTS_DIR / f'{name}_{int(time.time())}.png'
        img.save(filepath)
        log(f"  截图已保存: {filepath.name}")
        return filepath

def find_user_icon():
    """查找紫色用户图标"""
    log("\n查找用户图标...")
    
    with mss.mss() as sct:
        screenshot = sct.grab({
            'left': 0,
            'top': 0,
            'width': SCREEN['width'],
            'height': 80
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    pixels = img.load()
    w, h = img.size
    
    # 查找紫色像素（用户图标）
    purple_pixels = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            # 紫色: R高, G低, B高
            if r > 150 and g < 100 and b > 150:
                purple_pixels.append((x, y))
    
    log(f"  找到 {len(purple_pixels)} 个紫色像素")
    
    if len(purple_pixels) > 50:
        # 找到最右边的紫色区域
        rightmost_x = max(p[0] for p in purple_pixels)
        # 在该x坐标附近找中心
        nearby = [p for p in purple_pixels if abs(p[0] - rightmost_x) < 30]
        if nearby:
            avg_y = sum(p[1] for p in nearby) // len(nearby)
            return rightmost_x, avg_y
    
    # 备用：使用已知坐标
    log("  使用默认坐标 (850, 15)")
    return 850, 15

def open_submenu():
    """点击用户图标打开菜单"""
    icon_x, icon_y = find_user_icon()
    log(f"  点击用户图标: ({icon_x}, {icon_y})")
    
    pyautogui.click(icon_x, icon_y)
    time.sleep(0.8)
    
    save_screenshot('menu_opened')
    return icon_x, icon_y

def find_checkin_button():
    """查找签到按钮"""
    log("\n查找签到按钮...")
    
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    pixels = img.load()
    w, h = img.size
    
    # 搜索 y=380-430, x=900-1100 区域
    dark_pixels = []
    for y in range(380, 430):
        for x in range(900, 1100):
            r, g, b = pixels[x, y][:3]
            # 深色文字
            if r < 60 and g < 60 and b < 60:
                dark_pixels.append((x, y))
    
    if dark_pixels:
        min_x = min(p[0] for p in dark_pixels)
        max_x = max(p[0] for p in dark_pixels)
        min_y = min(p[1] for p in dark_pixels)
        max_y = max(p[1] for p in dark_pixels)
        
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        log(f"  找到按钮: ({min_x}, {min_y}) - ({max_x}, {max_y})")
        log(f"  中心: ({center_x}, {center_y})")
        
        return center_x, center_y
    
    # 备用坐标
    log("  使用备用坐标 (1013, 405)")
    return 1013, 405

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v36")
    log("=" * 60)
    
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 步骤1: 打开用户菜单
    log("\n【步骤1】打开用户菜单...")
    open_submenu()
    
    # 步骤2: 查找并点击签到按钮
    log("\n【步骤2】查找并点击签到按钮...")
    btn_x, btn_y = find_checkin_button()
    
    log(f"  点击签到按钮: ({btn_x}, {btn_y})")
    pyautogui.click(btn_x, btn_y)
    time.sleep(1)
    
    # 步骤3: 保存证据截图
    log("\n【步骤3】保存截图...")
    save_screenshot('after_checkin')
    
    # 等待刷新
    time.sleep(2)
    
    # 步骤4: 验证
    log("\n【步骤4】验证...")
    log("  请检查界面上的积分是否已增加")
    
    log("\n" + "=" * 60)
    log("完成! 请查看截图确认签到结果")
    log("=" * 60)
    log(f"\n截图目录: {SCREENSHOTS_DIR}")

if __name__ == '__main__':
    main()
