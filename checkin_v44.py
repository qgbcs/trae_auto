#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v44 - 刷新界面后验证
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

def get_credits_from_ui():
    """从UI截图获取积分"""
    with mss.MSS() as sct:
        screenshot = sct.grab({
            'left': 1200,
            'top': 200,
            'width': 300,
            'height': 100
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    return img

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v44 - 刷新验证")
    log("=" * 60)

    # 步骤1: 截图当前状态
    log("\n【步骤1】保存当前状态截图...")
    save_screenshot('current_state')

    # 步骤2: 按F5刷新页面
    log("\n【步骤2】刷新页面...")
    pyautogui.press('f5')
    time.sleep(2)

    # 步骤3: 截图刷新后状态
    log("\n【步骤3】保存刷新后截图...")
    save_screenshot('after_refresh')

    # 步骤4: 检查storage.json
    log("\n【步骤4】检查storage.json...")
    STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'

    if STORAGE_JSON.exists():
        try:
            data = json.loads(STORAGE_JSON.read_text())
            log(f"  文件修改时间: {datetime.fromtimestamp(STORAGE_JSON.stat().st_mtime)}")

            # 打印所有顶层键
            log(f"  顶层键: {list(data.keys())}")

            # 检查是否有commercialActivityInfo
            commercial = data.get('commercialActivityInfo', {})
            log(f"  commercialActivityInfo: {json.dumps(commercial, ensure_ascii=False)[:300]}")

        except Exception as e:
            log(f"  读取失败: {e}")
    else:
        log("  storage.json 不存在")

    # 步骤5: 再次点击签到按钮（如果需要）
    log("\n【步骤5】再次尝试点击签到按钮...")
    # 点击"每日签到"按钮区域
    btn_x, btn_y = 1050, 410
    log(f"  点击: ({btn_x}, {btn_y})")
    pyautogui.click(btn_x, btn_y)
    time.sleep(2)

    # 步骤6: 最终截图
    log("\n【步骤6】保存最终截图...")
    save_screenshot('final_state')

    log("\n" + "=" * 60)
    log("完成! 请查看截图确认签到结果")
    log("=" * 60)
    log(f"\n截图目录: {SCREENSHOTS_DIR}")

if __name__ == '__main__':
    main()
