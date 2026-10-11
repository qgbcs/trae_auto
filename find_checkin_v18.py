#!/usr/bin/env python3
"""
Trae CN 自动签到 v18 - 基于实际截图的精确定位
积分 384 在右上角，紫色图标在其左侧
"""

import pyautogui
import time
import win32gui
import win32con
import json

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True


def get_credits_from_storage():
    """从 storage.json 读取积分"""
    storage_path = r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json'
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'iCubeServerData://icube.cloudide' in data:
            icube_data = json.loads(data['iCubeServerData://icube.cloudide'])
            commercial = icube_data.get('commercialActivityInfo', {})
            activities = commercial.get('activities', [])

            for act in activities:
                if act.get('activityId') == 'checkin_credits':
                    work_extra = act.get('workExtra', {})
                    return {
                        'granted': work_extra.get('granted'),
                        'grantable': work_extra.get('grantable'),
                        'work_credits': work_extra.get('work_credits'),
                    }
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def main():
    print("=" * 60)
    print("Trae CN 自动签到 v18 (精确定位)")
    print("=" * 60)

    # 获取当前积分状态
    print("\n[1] 当前积分状态:")
    credits = get_credits_from_storage()
    if credits:
        print(f"  granted: {credits['granted']}")
        print(f"  grantable: {credits['grantable']}")
        print(f"  work_credits: {credits['work_credits']}")

    # 获取屏幕尺寸
    width, height = pyautogui.size()
    print(f"\n[2] 屏幕尺寸: {width}x{height}")

    # 截取顶部区域 (0, 0 到 width, 60)
    print("\n[3] 截取顶部区域...")
    top_bar = pyautogui.screenshot(region=(0, 0, width, 60))
    top_bar.save(r'C:\test\github\trae_auto\v18_topbar.png')
    print("  Saved: v18_topbar.png")

    # 方法：从右向左扫描，找到积分数字左边的紫色图标
    # 积分通常在右上角，大约在 x=width-100 到 x=width-20 之间
    # 紫色图标在积分左边，大约 x=width-200 到 x=width-100 之间

    print("\n[4] 扫描紫色图标位置...")

    # 从右向左，每次移动 20px
    candidates = []
    for x in range(width - 150, width - 50, 20):
        y = 20
        candidates.append((x, y))

    # 测试每个位置
    for i, (x, y) in enumerate(candidates):
        print(f"  [{i+1}] 尝试 ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.2)
        pyautogui.click()
        time.sleep(0.8)

        # 截图
        ss = pyautogui.screenshot()
        fname = f'C:\\test\\github\\trae_auto\\v18_scan_{i+1}.png'
        ss.save(fname)

        # 检查是否弹出了包含"签到"的菜单
        # 这里简化处理，手动检查截图

    print("\n请检查 v18_scan_*.png 截图，找到弹出签到菜单的位置")
    print("然后告诉我坐标，我会创建最终的签到脚本")


if __name__ == '__main__':
    main()
