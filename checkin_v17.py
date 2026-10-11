# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v17 - 使用Computer Use技能
根据用户反馈：
- 不要点击屏幕右上角（那是关闭按钮）
- 用户图标在中间偏右，坐标约(780, 20)
- 点击后弹出二级菜单，里面有签到按钮
"""
import pyautogui
import win32gui
import win32con
import time
import sys

pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = False

def find_trae_main_window():
    """查找Trae主窗口"""
    windows = []
    def enum(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title.upper():
                rect = win32gui.GetWindowRect(hwnd)
                w, h = rect[2]-rect[0], rect[3]-rect[1]
                if w > 800 and h > 400:
                    results.append((hwnd, title, rect))
    win32gui.EnumWindows(enum, windows)
    if not windows:
        return None
    # 选择最大的可见窗口
    return max(windows, key=lambda x: (x[2][2]-x[2][0]) * (x[2][3]-x[2][1]))

def checkin():
    print("=== Trae CN 签到脚本 v17 - Computer Use版本 ===\n")

    # 步骤1: 查找Trae主窗口
    print("步骤1: 查找Trae主窗口...")
    result = find_trae_main_window()
    if not result:
        print("ERROR: 找不到Trae主窗口!")
        sys.exit(1)

    hwnd, title, rect = result
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    print(f"  窗口: {title}")
    print(f"  位置: ({left}, {top})")
    print(f"  大小: {width}x{height}")

    # 步骤2: 激活窗口
    print("\n步骤2: 激活Trae窗口...")
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    # 步骤3: 点击用户图标（用户说在约780, 20位置）
    print("\n步骤3: 点击用户图标...")
    # 用户说点击(780, 20)弹出二级菜单
    # 这是屏幕坐标，不是窗口坐标
    user_icon_x = 780
    user_icon_y = 20

    print(f"  点击用户图标: ({user_icon_x}, {user_icon_y})")
    pyautogui.click(user_icon_x, user_icon_y)
    time.sleep(1.5)

    # 截图确认菜单已弹出
    shot_menu = f"C:\\test\\github\\trae_auto\\v17_menu_{int(time.time())}.png"
    pyautogui.screenshot(shot_menu)
    print(f"  菜单截图: {shot_menu}")

    # 步骤4: 在菜单中找到并点击签到按钮
    print("\n步骤4: 寻找并点击签到按钮...")
    # 截图搜索签到按钮区域
    # 菜单应该在用户图标下方弹出
    menu_region = f"C:\\test\\github\\trae_auto\\v17_menu_region_{int(time.time())}.png"
    screenshot = pyautogui.screenshot()
    # 截取用户图标下方区域（菜单应该在这里）
    menu_area = screenshot.crop((user_icon_x - 100, user_icon_y + 30, user_icon_x + 300, user_icon_y + 300))
    menu_area.save(menu_region)
    print(f"  菜单区域截图: {menu_region}")

    # 尝试点击签到按钮（通常在菜单的第一项或第二项）
    # 用户图标在(780, 20)，菜单大约在 y=60-150 之间
    checkin_candidates = [
        (780, 60),   # 候选1：菜单第一项
        (780, 90),   # 候选2：菜单第二项
        (780, 120),  # 候选3：菜单第三项
    ]

    for i, (x, y) in enumerate(checkin_candidates, 1):
        print(f"  尝试点击签到候选 {i}: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(1)

        # 检查是否有变化
        shot = f"C:\\test\\github\\trae_auto\\v17_try{i}_{int(time.time())}.png"
        pyautogui.screenshot(shot)
        print(f"    截图: {shot}")

        # 如果积分变化了，说明签到成功
        if check_credit_change():
            print(f"  ✓ 签到成功！积分已增加")
            return True

    # 步骤5: 如果上面的方法都不行，尝试打开用量管理页面
    print("\n步骤5: 尝试通过用量管理页面签到...")
    # 使用键盘快捷键打开用量管理
    # 先点击用户图标打开菜单
    pyautogui.click(user_icon_x, user_icon_y)
    time.sleep(1)

    # 按向下箭头选择"用量管理"
    pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(1.5)

    # 截图确认
    shot_usage = f"C:\\test\\github\\trae_auto\\v17_usage_{int(time.time())}.png"
    pyautogui.screenshot(shot_usage)
    print(f"  用量管理截图: {shot_usage}")

    # 在用量管理页面查找签到按钮
    # 从之前的数据看，用量管理页面有"每日签到"链接
    checkin_btn_x = 920
    checkin_btn_y = 425
    print(f"  点击每日签到按钮: ({checkin_btn_x}, {checkin_btn_y})")
    pyautogui.click(checkin_btn_x, checkin_btn_y)
    time.sleep(2)

    # 最终截图
    shot_final = f"C:\\test\\github\\trae_auto\\v17_final_{int(time.time())}.png"
    pyautogui.screenshot(shot_final)
    print(f"\n最终截图: {shot_final}")

    # 验证积分
    if check_credit_change():
        print("\n✓ 签到成功！积分已增加100")
        return True
    else:
        print("\n✗ 签到可能失败，请检查截图")
        return False

def check_credit_change():
    """检查积分是否变化（通过读取本地存储）"""
    try:
        import json
        storage_path = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'iCubeServerData://icube.cloudide' in data:
            server_data = json.loads(data['iCubeServerData://icube.cloudide'])
            credits = server_data.get('totalCredits', 0)
            print(f"  当前积分: {credits}")
            return credits > 400  # 如果积分超过400，说明签到成功
    except Exception as e:
        print(f"  检查积分失败: {e}")
    return False

if __name__ == "__main__":
    checkin()
