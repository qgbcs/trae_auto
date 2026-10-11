#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v35 - 使用 mss + pyautogui + 精确坐标
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

def get_credits_from_storage():
    """从 storage.json 获取积分信息"""
    if not STORAGE_JSON.exists():
        return 0, False
    
    try:
        data = json.loads(STORAGE_JSON.read_text())
        
        # 尝试多种方式获取积分
        activities = data.get('commercialActivityInfo', {}).get('activities', [])
        
        for i, act in enumerate(activities):
            act_type = act.get('activityType', '')
            metadata = act.get('metadata', {})
            
            if 'checkin' in act_type.lower():
                log(f"  找到签到活动 [{i}]: type={act_type}")
                
                # 尝试各种积分字段
                credit_fields = ['totalCredits', 'credits', 'earnedCredits', 'availableCredits']
                
                for field in credit_fields:
                    if field in metadata:
                        credits = metadata[field]
                        log(f"  积分字段 {field}: {credits}")
                        return credits, True
                
                # 检查 workExtra
                work_extra = act.get('workExtra', {})
                if work_extra:
                    log(f"  workExtra: {work_extra}")
        
        # 打印所有活动数据
        log(f"  共 {len(activities)} 个活动:")
        for i, act in enumerate(activities):
            log(f"  [{i}] {act.get('activityType', 'N/A')}: {json.dumps(act, ensure_ascii=False)[:200]}")
        
        return 0, False
        
    except Exception as e:
        log(f"  读取积分失败: {e}")
        return 0, False

def find_user_icon():
    """查找用户图标位置"""
    log("\n查找用户图标...")
    
    with mss.mss() as sct:
        # 只截取顶部区域
        screenshot = sct.grab({
            'left': 0,
            'top': 0,
            'width': SCREEN['width'],
            'height': 80
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    pixels = img.load()
    w, h = img.size
    
    # 紫色图标特征
    purple_count = 0
    purple_positions = []
    
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            # 紫色: R高, G低, B高
            if r > 150 and g < 100 and b > 150:
                purple_count += 1
                if len(purple_positions) < 10:
                    purple_positions.append((x, y))
    
    log(f"  紫色像素: {purple_count}")
    
    if purple_count > 100:
        # 找到最右边的紫色区域
        rightmost_x = max(p[0] for p in purple_positions)
        # 在该x坐标范围内找中心
        in_column = [p for p in purple_positions if abs(p[0] - rightmost_x) < 20]
        if in_column:
            avg_y = sum(p[1] for p in in_column) // len(in_column)
            return rightmost_x, avg_y
    
    return None, None

def open_submenu_by_icon():
    """通过用户图标打开菜单"""
    icon_x, icon_y = find_user_icon()
    
    if icon_x is None:
        log("  未找到用户图标，使用默认坐标")
        icon_x, icon_y = 850, 15
    else:
        log(f"  找到用户图标: ({icon_x}, {icon_y})")
    
    # 点击用户图标
    log(f"  点击用户图标...")
    pyautogui.click(icon_x, icon_y)
    time.sleep(0.8)
    
    # 检查是否打开了菜单
    with mss.mss() as sct:
        screenshot = sct.grab({
            'left': 0,
            'top': 0,
            'width': SCREEN['width'],
            'height': SCREEN['height']
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(SCREENSHOTS_DIR / f'step_{int(time.time())}_icon_clicked.png')
    
    return icon_x, icon_y

def find_and_click_checkin_button():
    """在菜单中找到并点击签到按钮"""
    log("\n查找签到按钮...")
    
    # 截图整个屏幕
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    pixels = img.load()
    w, h = img.size
    
    # 搜索包含"签到"文字的按钮区域
    # 根据之前的经验，按钮在 y=380-430, x=900-1100 区域
    
    found_positions = []
    
    for y in range(380, 430):
        for x in range(900, 1100):
            r, g, b = pixels[x, y][:3]
            # 深色文字
            if r < 60 and g < 60 and b < 60:
                # 检查右侧是否有按钮背景
                if x + 20 < w:
                    br, bg, bb = pixels[x + 20, y][:3]
                    # 背景可能不同
                    found_positions.append((x, y))
    
    if found_positions:
        min_x = min(p[0] for p in found_positions)
        max_x = max(p[0] for p in found_positions)
        min_y = min(p[1] for p in found_positions)
        max_y = max(p[1] for p in found_positions)
        
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        log(f"  找到按钮区域: ({min_x}, {min_y}) - ({max_x}, {max_y})")
        log(f"  中心: ({center_x}, {center_y})")
        
        return center_x, center_y
    
    # 备用：使用已知坐标
    log("  使用备用坐标 (1013, 405)")
    return 1013, 405

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v35")
    log("=" * 60)
    
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 步骤1: 获取初始积分
    log("\n【步骤1】获取初始积分...")
    initial_credits, credits_found = get_credits_from_storage()
    log(f"  初始积分: {initial_credits} (找到: {credits_found})")
    
    # 步骤2: 打开用量管理页面
    log("\n【步骤2】打开用量管理页面...")
    subprocess.Popen([
        r'C:\Users\Administrator\AppData\Local\Trae CN\Update.exe',
        '--processStart', 'Trae CN.exe',
        '--process-start-args', '--goto=command:workbench.action.openSettings'
    ], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
    time.sleep(2)
    
    # 步骤3: 查找并点击用户图标
    log("\n【步骤3】查找并点击用户图标...")
    open_submenu_by_icon()
    time.sleep(0.5)
    
    # 步骤4: 查找并点击签到按钮
    log("\n【步骤4】查找并点击签到按钮...")
    btn_x, btn_y = find_and_click_checkin_button()
    
    log(f"  点击签到按钮: ({btn_x}, {btn_y})")
    pyautogui.click(btn_x, btn_y)
    time.sleep(1)
    
    # 截图保存证据
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        timestamp = int(time.time())
        img.save(SCREENSHOTS_DIR / f'step_{timestamp}_after_click.png')
        log(f"  已保存截图: step_{timestamp}_after_click.png")
    
    # 等待刷新
    time.sleep(2)
    
    # 步骤5: 验证积分增加
    log("\n【步骤5】验证积分变化...")
    final_credits, _ = get_credits_from_storage()
    log(f"  最终积分: {final_credits}")
    
    if final_credits > initial_credits:
        increase = final_credits - initial_credits
        log(f"  ✅ 签到成功! 积分增加: {increase}")
    else:
        log(f"  ⚠️ 积分未增加，可能需要重试")
    
    log("\n" + "=" * 60)
    log("完成!")
    log("=" * 60)

if __name__ == '__main__':
    main()
