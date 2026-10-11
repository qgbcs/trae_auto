#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v22
修正：使用 mss 截图，简化积分读取逻辑
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
            if 'Trae' in title:
                results.append((hwnd, title))
    results = []
    win32gui.EnumWindows(enum_callback, results)
    return results[0] if results else None

def click(x, y):
    """安全点击"""
    pyautogui.click(x, y)
    print(f"✓ 点击 ({x}, {y})")
    time.sleep(0.5)

def read_credits():
    """读取积分 - 修正版本"""
    try:
        with open(r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 解析 iCubeServerData
        icube_raw = data.get('iCubeServerData://icube.cloudide', '{}')
        icube_data = json.loads(icube_raw)
        
        # 检查 activities
        cai = icube_data.get('commercialActivityInfo', {})
        activities = cai.get('activities', [])
        
        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                work_extra = act.get('workExtra', {})
                # granted: true 表示已签到
                if work_extra.get('granted'):
                    return "已签到"
                else:
                    return "未签到"
        
        return "未知"
        
    except Exception as e:
        print(f"  读取积分状态失败: {e}")
        return "错误"

def save_screenshot(path, region=None):
    """保存截图"""
    try:
        with mss.mss() as sct:
            if region:
                screenshot = sct.grab(region)
            else:
                monitor = sct.monitors[1]  # 主显示器
                screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.save(path, "PNG")
        print(f"  截图已保存: {path}")
    except Exception as e:
        print(f"  截图失败: {e}")

def checkin():
    """签到"""
    print("=" * 50)
    print("Trae CN 签到 v22")
    print("=" * 50)
    
    # 1. 获取初始状态
    initial_status = read_credits()
    print(f"\n[1] 当前签到状态: {initial_status}")
    
    if initial_status == "已签到":
        print("  今天已签到，无需重复签到")
        return True
    
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
    
    # 4. 打开用量管理页面
    print("\n[4] 打开用量管理页面 (Ctrl+Shift+M)...")
    pyautogui.hotkey('ctrl', 'shift', 'm')
    time.sleep(2)
    
    # 5. 截图保存当前状态
    print("\n[5] 截图保存当前状态...")
    save_screenshot(r'C:\test\github\trae_auto\screenshot_before.png')
    
    # 6. 从用户图标定位点击
    # 用户图标在屏幕中间偏右，坐标 (850, 15)
    print("\n[6] 点击用户图标打开菜单...")
    user_icon_x, user_icon_y = 850, 15
    click(user_icon_x, user_icon_y)
    
    # 7. 在菜单中点击"每日领 100 积分"
    # 菜单项在用户图标下方约 60-70 像素
    print("\n[7] 点击'每日领 100 积分'...")
    menu_item_x = user_icon_x
    menu_item_y = user_icon_y + 65
    click(menu_item_x, menu_item_y)
    
    # 等待界面更新
    time.sleep(2)
    
    # 8. 如果菜单没打开，尝试直接在用量管理页面点击"每日签到"
    print("\n[8] 尝试直接点击'每日签到'按钮...")
    checkin_btn_x, checkin_btn_y = 900, 350
    click(checkin_btn_x, checkin_btn_y)
    
    # 等待签到完成
    time.sleep(2)
    
    # 9. 截图
    print("\n[9] 保存签到后截图...")
    save_screenshot(r'C:\test\github\trae_auto\screenshot_after.png')
    
    # 10. 验证状态
    print("\n[10] 验证签到状态...")
    time.sleep(2)
    final_status = read_credits()
    print(f"  最终状态: {final_status}")
    
    if final_status == "已签到":
        print(f"\n✓ 签到成功！")
        return True
    else:
        print(f"\n✗ 签到失败，状态仍为: {final_status}")
        return False

if __name__ == '__main__':
    checkin()
