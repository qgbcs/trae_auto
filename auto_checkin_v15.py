#!/usr/bin/env python3
"""
Trae CN 自动签到 v15 - 最终方案：精确 UI 自动化
基于用户提供的信息：
- 用户图标在 (780, 20)
- 点击后弹出二级菜单，里面有签到按钮
"""

import win32gui
import win32con
import pyautogui
import time
import json
import os
import sys

pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True

# 用户提供的准确位置
USER_ICON_X = 780
USER_ICON_Y = 20


def get_credits_from_storage():
    """从 storage.json 读取积分信息"""
    storage_path = r'C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json'
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 解析 iCubeServerData
        if 'iCubeServerData://icube.cloudide' in data:
            icube_data = json.loads(data['iCubeServerData://icube.cloudide'])
            commercial = icube_data.get('commercialActivityInfo', {})
            activities = commercial.get('activities', [])

            for act in activities:
                if act.get('activityId') == 'checkin_credits':
                    work_extra = act.get('workExtra', {})
                    print(f"  checkin_credits:")
                    print(f"    granted: {work_extra.get('granted')}")
                    print(f"    grantable: {work_extra.get('grantable')}")
                    print(f"    work_credits: {work_extra.get('work_credits')}")

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 60)
    print("Trae CN 自动签到 v15 (精确 UI)")
    print("=" * 60)

    # 获取当前积分
    print("\n[1] 当前积分状态:")
    get_credits_from_storage()

    # 移动到用户图标位置并点击
    print(f"\n[2] 移动鼠标到用户图标 ({USER_ICON_X}, {USER_ICON_Y})...")
    pyautogui.moveTo(USER_ICON_X, USER_ICON_Y, duration=0.5)
    time.sleep(0.3)

    # 点击用户图标
    print("[3] 点击用户图标...")
    pyautogui.click()
    time.sleep(0.8)

    # 截图
    ss = pyautogui.screenshot()
    ss.save(r'C:\test\github\trae_auto\v15_menu.png')
    print("  Saved: v15_menu.png")

    # 查找签到按钮位置
    # 菜单通常在用户图标下方弹出
    # 假设菜单第一项是签到，位置大约在 (780, 60) 附近
    print("\n[4] 尝试点击签到按钮...")

    # 不同的候选位置
    candidates = [
        (780, 55),   # 第一菜单项
        (780, 80),   # 第二菜单项
        (750, 55),   # 左侧一点
        (800, 55),   # 右侧一点
    ]

    for i, (x, y) in enumerate(candidates):
        print(f"  尝试位置 {i+1}: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(0.3)

        # 截图
        ss = pyautogui.screenshot(region=(x-100, y-10, 200, 40))
        ss.save(rf'C:\test\github\trae_auto\v15_try_{i+1}.png')

        pyautogui.click()
        time.sleep(1)

        # 检查积分是否变化
        print(f"  点击后检查积分...")
        get_credits_from_storage()

        # 如果积分增加了，说明签到成功
        # 这里简化处理，实际应该比较前后积分

    # 最终截图
    ss_final = pyautogui.screenshot()
    ss_final.save(r'C:\test\github\trae_auto\v15_final.png')

    print("\n[5] 最终积分状态:")
    get_credits_from_storage()

    print("\n" + "=" * 60)
    print("完成！检查截图：v15_menu.png, v15_try_*.png, v15_final.png")
    print("=" * 60)


if __name__ == '__main__':
    main()
