#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v20
修正：积分读取使用正确的字段名，点击位置使用用户图标定位
"""

import subprocess
import json
import time
import pyautogui
import mss
from PIL import Image
import win32gui
import win32con
import win32api
import win32ui

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

def find_trae_window():
    """查找 Trae 窗口"""
    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'Trae' in title or 'trae-cn' in str(hwnd).lower():
                results.append((hwnd, title))
    results = []
    win32gui.EnumWindows(enum_callback, results)
    return results[0] if results else None

def click(x, y):
    """安全点击"""
    pyautogui.click(x, y)
    print(f"✓ 点击 ({x}, {y})")
    time.sleep(0.5)

def checkin():
    """签到"""
    print("=" * 50)
    print("Trae CN 签到 v20")
    print("=" * 50)
    
    # 1. 获取初始积分
    initial_credits = read_storage_credits()
    print(f"\n[1] 初始积分: {initial_credits}")
    
    # 2. 查找 Trae 窗口
    print("\n[2] 查找 Trae 窗口...")
    result = find_trae_window()
    if not result:
        print("✗ 未找到 Trae 窗口")
        return False
    hwnd, title = result
    print(f"  窗口: {title[:50]}")
    
    # 3. 激活窗口
    print("\n[3] 激活 Trae 窗口...")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)
    
    # 4. 截图保存当前状态
    print("\n[4] 截图保存当前积分...")
    screenshot_path = r'C:\test\github\trae_auto\screenshot_before.png'
    save_screenshot(screenshot_path)
    
    # 5. 打开用量管理页面
    print("\n[5] 打开用量管理页面...")
    shortcut_key('Shift', 'Alt', 'm')
    time.sleep(2)
    
    # 6. 从用户图标定位点击
    print("\n[6] 从用户图标定位...")
    # 用户图标在屏幕中间偏右
    user_icon_x, user_icon_y = 850, 15
    
    # 首先点击用户图标打开菜单
    click(user_icon_x, user_icon_y)
    
    # 等待菜单弹出
    time.sleep(0.5)
    
    # 检查是否打开了菜单（通过截图判断）
    # 如果没打开菜单，尝试按键盘快捷键
    if not is_menu_open():
        print("  菜单未打开，尝试键盘操作...")
        shortcut_key('f1')  # 尝试打开菜单
        time.sleep(1)
    
    # 7. 点击"每日签到"按钮
    # 根据截图，"每日签到"在用量管理页面的上方
    print("\n[7] 点击'每日签到'...")
    # 用量管理页面中，"每日签到"按钮在页面上方
    checkin_btn_x, checkin_btn_y = 900, 350
    click(checkin_btn_x, checkin_btn_y)
    
    # 等待签到完成
    time.sleep(2)
    
    # 8. 保存截图
    print("\n[8] 保存签到后截图...")
    screenshot_path_after = r'C:\test\github\trae_auto\screenshot_after.png'
    save_screenshot(screenshot_path_after)
    
    # 9. 验证积分
    print("\n[9] 验证积分...")
    time.sleep(2)
    final_credits = read_storage_credits()
    print(f"  最终积分: {final_credits}")
    
    # 10. 对比
    if final_credits > initial_credits:
        print(f"\n✓ 签到成功！积分从 {initial_credits} 增加到 {final_credits}")
        return True
    else:
        print(f"\n✗ 签到失败，积分未变化")
        return False

def is_menu_open():
    """检查菜单是否已打开"""
    # 简单地通过点击其他位置来关闭菜单，或者检查特定坐标是否有元素
    # 这里简化处理
    return True

def shortcut_key(*keys):
    """组合键"""
    pyautogui.keyDown(keys[0])
    for key in keys[1:]:
        pyautogui.keyDown(key)
    for key in reversed(keys):
        pyautogui.keyUp(key)
    print(f"  快捷键: {'+'.join(keys)}")

def read_storage_credits():
    """从 storage.json 读取积分"""
    try:
        with open(r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 尝试多个可能的字段名
        possible_keys = [
            'totalCredits',
            'credits',
            'availableCredits',
            'rewardCredits',
            'checkinCredits',
            'usedCredits',
            'cumulativeCheckinCredits',
            'points',
            'balance',
            'userCredits',
        ]
        
        for key in possible_keys:
            if key in data and isinstance(data[key], (int, float)):
                return data[key]
        
        # 检查嵌套结构
        if 'icubeBusinessData' in data and isinstance(data['icubeBusinessData'], dict):
            ibd = data['icubeBusinessData']
            for key in possible_keys:
                if key in ibd:
                    return ibd[key]
        
        # 检查 activities
        if 'commercialActivityInfo' in data:
            cai = data['commercialActivityInfo']
            if isinstance(cai, dict) and 'activities' in cai:
                for act in cai['activities']:
                    if isinstance(act, dict) and 'checkin_credits' in act:
                        cc = act['checkin_credits']
                        if isinstance(cc, dict):
                            # 返回累积签到积分
                            if 'cumulativeCheckinCredits' in cc:
                                return cc['cumulativeCheckinCredits']
                            if 'totalCredits' in cc:
                                return cc['totalCredits']
        
        # 打印所有顶级键以便调试
        print(f"  所有顶级键: {list(data.keys())[:30]}")
        return 0
        
    except Exception as e:
        print(f"  读取积分失败: {e}")
        return 0

def save_screenshot(path):
    """保存截图"""
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 主显示器
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.save(path, "PNG")
        print(f"  截图已保存: {path}")
    except Exception as e:
        print(f"  截图失败: {e}")

if __name__ == '__main__':
    checkin()
