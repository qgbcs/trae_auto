"""
验证签到结果并截图
"""
import json
import time
import subprocess
import pyautogui
from PIL import ImageGrab

STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
SCREENSHOT_DIR = r"C:\test\github\trae_auto\screenshots"


def get_current_status():
    """获取当前签到状态"""
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        server_data_key = 'iCubeServerData://icube.cloudide'
        if server_data_key not in data:
            return None

        server_data = json.loads(data[server_data_key])
        activities = server_data.get('commercialActivityInfo', {}).get('activities', [])

        for activity in activities:
            if activity.get('activityId') == 'checkin_credits':
                work_extra = activity.get('workExtra', {})
                return {
                    'activity': activity,
                    'credits': work_extra.get('work_credits', 0),
                    'granted': work_extra.get('granted', False),
                    'grantable': work_extra.get('grantable', False)
                }
    except Exception as e:
        print(f"读取状态失败: {e}")
    return None


def take_screenshot():
    """截图"""
    try:
        # 确保目录存在
        import os
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

        # 截图
        timestamp = int(time.time())
        screenshot_path = f"{SCREENSHOT_DIR}\\checkin_verified_{timestamp}.png"

        # 截取整个屏幕
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path)
        print(f"✓ 截图已保存: {screenshot_path}")

        return screenshot_path
    except Exception as e:
        print(f"截图失败: {e}")
        return None


def main():
    print("=" * 60)
    print("验证签到结果")
    print("=" * 60)

    # 获取当前状态
    status = get_current_status()
    if status:
        print(f"\n当前积分: {status['credits']}")
        print(f"已签到: {status['granted']}")
        print(f"可签到: {status['grantable']}")

        if status['granted'] and status['credits'] >= 300:
            print("\n✓ 签到验证成功！")
        else:
            print("\n✗ 签到状态异常")
    else:
        print("无法获取签到状态")

    # 截图
    print("\n正在截图...")
    screenshot_path = take_screenshot()

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
