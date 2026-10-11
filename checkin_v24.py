#!/usr/bin/env python3
"""
Trae CN 签到脚本 - v24
修正：从截图中看到点用户图标打开的是"升级权益"页面
需要找到正确的签到入口
"""

import json
import time
import pyautogui
import mss
from PIL import Image
import win32gui
import win32con

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

def find_trae_window():
    """查找 Trae 窗口"""
    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title or 'Trae' in title:
                results.append((hwnd, title))
    results = []
    win32gui.EnumWindows(enum_callback, results)
    return results[0] if results else None

def click(x, y):
    """安全点击"""
    pyautogui.click(x, y)
    print(f"✓ 点击 ({x}, {y})")
    time.sleep(0.5)

def read_credits_status():
    """读取积分状态"""
    try:
        with open(r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        icube_raw = data.get('iCubeServerData://icube.cloudide', '{}')
        icube_data = json.loads(icube_raw)
        cai = icube_data.get('commercialActivityInfo', {})
        activities = cai.get('activities', [])
        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                work_extra = act.get('workExtra', {})
                return work_extra.get('granted', False)
        return False
    except Exception as e:
        print(f"  读取失败: {e}")
        return False

def save_screenshot(path):
    """保存截图"""
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.save(path, "PNG")
        print(f"  截图已保存: {path}")
    except Exception as e:
        print(f"  截图失败: {e}")

def checkin():
    """签到"""
    print("=" * 50)
    print("Trae CN 签到 v24 - 修正方案")
    print("=" * 50)
    
    # 1. 检查是否已签到
    if read_credits_status():
        print("\n今天已签到，无需重复签到")
        return True
    
    print("\n[1] 当前未签到，开始签到流程...")
    
    # 2. 查找 Trae 窗口
    print("\n[2] 查找 Trae 窗口...")
    result = find_trae_window()
    if not result:
        print("✗ 未找到 Trae 窗口")
        return False
    hwnd, title = result
    print(f"  窗口: {title}")
    
    # 3. 激活窗口
    print("\n[3] 激活窗口...")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(1)
    
    # 4. 关闭可能存在的弹窗
    print("\n[4] 关闭弹窗...")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 5. 截图
    print("\n[5] 截图...")
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v24_before.png')
    
    # 6. 尝试通过快捷键打开用量管理页面
    # 根据截图，顶部有积分显示，右上角有用户图标
    # 尝试使用 Ctrl+Shift+P 打开命令面板，搜索"签到"或"用量"
    print("\n[6] 打开命令面板搜索签到...")
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(1)
    
    # 7. 输入搜索词
    print("\n[7] 搜索'用量'...")
    pyautogui.typewrite('用量')
    time.sleep(1)
    
    # 8. 截图看结果
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v24_search.png')
    
    # 9. 按回车确认
    pyautogui.press('enter')
    time.sleep(2)
    
    # 10. 截图
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v24_after_search.png')
    
    # 11. 如果没找到，尝试直接点击顶部积分区域
    print("\n[8] 尝试点击顶部积分区域...")
    # 根据截图，积分 384 在顶部中间偏右位置
    click(850, 15)
    time.sleep(1)
    
    # 12. 截图
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v24_click_credits.png')
    
    # 13. 如果还是打开升级页面，尝试关闭并找其他入口
    print("\n[9] 关闭弹窗...")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 14. 尝试在命令面板中搜索"签到"
    print("\n[10] 搜索'签到'...")
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(1)
    pyautogui.typewrite('签到')
    time.sleep(1)
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v24_search_checkin.png')
    
    # 15. 按回车
    pyautogui.press('enter')
    time.sleep(2)
    save_screenshot(r'C:\test\github\trae_auto\screenshot_v24_after_checkin.png')
    
    # 16. 验证
    print("\n[11] 验证签到状态...")
    time.sleep(2)
    final_status = read_credits_status()
    print(f"  签到状态: {'已签到' if final_status else '未签到'}")
    
    if final_status:
        print(f"\n✓ 签到成功！")
        return True
    else:
        print(f"\n✗ 签到失败")
        return False

if __name__ == '__main__':
    checkin()
