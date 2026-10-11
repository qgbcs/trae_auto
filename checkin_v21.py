#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v21
修正：使用正确的积分读取逻辑，从用户图标定位点击
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

def read_storage_credits():
    """从 storage.json 读取积分 - 修正版本"""
    try:
        with open(r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 解析 iCubeServerData
        icube_raw = data.get('iCubeServerData://icube.cloudide', '{}')
        icube_data = json.loads(icube_raw)
        
        # 检查各种可能的积分字段
        # 1. 直接在顶层
        for key in ['totalCredits', 'credits', 'availableCredits', 'balance']:
            if key in data:
                return data[key]
        
        # 2. 在 icubeBusinessData 中
        ibd = icube_data.get('icubeBusinessData', {})
        for key in ['totalCredits', 'credits', 'availableCredits', 'balance']:
            if key in ibd:
                return ibd[key]
        
        # 3. 检查 activities
        cai = icube_data.get('commercialActivityInfo', {})
        activities = cai.get('activities', [])
        
        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                # 签到活动
                work_extra = act.get('workExtra', {})
                # 检查各种可能的字段
                for key in ['cumulativeCheckinCredits', 'totalCredits', 'checkinCredits']:
                    if key in work_extra:
                        return work_extra[key]
                # 返回 granted 状态
                if work_extra.get('granted'):
                    return 100  # 已签到
        
        # 4. 检查 originPayStatusData
        ops = icube_data.get('originPayStatusData', {})
        for key in ['totalCredits', 'credits', 'balance']:
            if key in ops:
                return ops[key]
        
        # 5. 打印所有键帮助调试
        print(f"  顶级键: {list(data.keys())[:20]}")
        print(f"  iCubeServerData keys: {list(icube_data.keys())}")
        if 'icubeBusinessData' in icube_data:
            print(f"  icubeBusinessData keys: {list(icube_data['icubeBusinessData'].keys())}")
        
        return 0
        
    except Exception as e:
        print(f"  读取积分失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

def checkin():
    """签到"""
    print("=" * 50)
    print("Trae CN 签到 v21 - 修正积分读取")
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
    
    # 5. 使用用户图标定位点击
    # 用户图标在屏幕中间偏右位置 (850, 15)
    print("\n[5] 从用户图标定位...")
    user_icon_x, user_icon_y = 850, 15
    
    # 点击用户图标打开菜单
    click(user_icon_x, user_icon_y)
    
    # 等待菜单弹出
    time.sleep(0.8)
    
    # 6. 在菜单中点击"每日领 100 积分"
    # 菜单项在用户图标下方约 50-80 像素
    print("\n[6] 点击'每日领 100 积分'...")
    menu_item_x = user_icon_x
    menu_item_y = user_icon_y + 65
    click(menu_item_x, menu_item_y)
    
    # 等待界面更新
    time.sleep(2)
    
    # 7. 如果菜单点击没有效果，尝试在用量管理页面直接点击"每日签到"按钮
    # 用量管理页面中，"每日签到"按钮在页面上方
    print("\n[7] 尝试点击用量管理页面的'每日签到'...")
    checkin_btn_x, checkin_btn_y = 900, 320
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
