"""
Trae CN 自动签到脚本 v46 - 优化版
使用正确的用户图标位置
"""
import sys
import time
import json
from pathlib import Path
from PIL import Image
import mss
import pyautogui

pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True

SCRIPT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = SCRIPT_DIR / 'screenshots'
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def save_screenshot(name):
    with mss.MSS() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        filepath = SCREENSHOTS_DIR / f'{name}_{int(time.time())}.png'
        img.save(filepath)
        log(f"  截图: {filepath.name}")
        return filepath

def get_credits_from_storage():
    """从storage.json获取积分"""
    STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
    if not STORAGE_JSON.exists():
        return 0

    try:
        data = json.loads(STORAGE_JSON.read_text())
        icube = data.get('iCubeServerData://icube.cloudide', {})
        if isinstance(icube, str):
            icube = json.loads(icube)
        commercial = icube.get('commercialActivityInfo', {})
        activities = commercial.get('activities', [])

        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                work_extra = act.get('workExtra', {})
                return work_extra.get('work_credits', 0)
    except:
        pass

    return 0

def find_user_icon():
    """查找用户图标位置（右上角区域）"""
    log("  查找用户图标...")

    with mss.MSS() as sct:
        # 截图顶部区域
        screenshot = sct.grab({
            'left': 1100,
            'top': 0,
            'width': 300,
            'height': 60
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    pixels = img.load()
    w, h = img.size

    # 查找紫色/蓝色图标（用户头像通常是圆形彩色图标）
    icon_pixels = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            # 紫色或蓝色图标
            if (r < 100 and g < 50 and b > 150) or (r < 50 and g < 100 and b > 150):
                icon_pixels.append((x + 1100, y))

    if icon_pixels:
        # 取中心点
        avg_x = sum(p[0] for p in icon_pixels) // len(icon_pixels)
        avg_y = sum(p[1] for p in icon_pixels) // len(icon_pixels)
        return avg_x, avg_y

    # 备用：直接返回已知位置
    return 1250, 20

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v46")
    log("=" * 60)

    # 步骤1: 读取初始积分
    log("\n【步骤1】读取初始积分...")
    initial_credits = get_credits_from_storage()
    log(f"  当前积分: {initial_credits}")

    # 步骤2: 截图当前状态
    log("\n【步骤2】保存当前状态截图...")
    save_screenshot('before')

    # 步骤3: 点击用户图标
    log("\n【步骤3】点击用户图标...")

    # 先按Escape关闭任何菜单
    pyautogui.press('esc')
    time.sleep(0.3)

    # 查找并点击用户图标
    icon_x, icon_y = find_user_icon()
    log(f"  用户图标位置: ({icon_x}, {icon_y})")
    pyautogui.click(icon_x, icon_y)
    time.sleep(0.8)

    # 步骤4: 截图菜单
    log("\n【步骤4】保存菜单截图...")
    save_screenshot('menu')

    # 步骤5: 查找并点击签到按钮
    log("\n【步骤5】查找并点击签到按钮...")

    # 截图菜单区域
    with mss.MSS() as sct:
        screenshot = sct.grab({
            'left': 1150,
            'top': 40,
            'width': 250,
            'height': 300
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    pixels = img.load()
    w, h = img.size

    # 查找"签到"文字（通常是深色）
    text_pixels = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            # 深色文字
            if r < 100 and g < 100 and b < 100 and r + g + b > 30:
                text_pixels.append((x + 1150, y + 40))

    if text_pixels:
        # 找最下面的深色文字（签到按钮通常在菜单底部）
        text_pixels.sort(key=lambda p: p[1], reverse=True)
        # 取最下面的几个点
        bottom_pixels = text_pixels[:20]
        avg_x = sum(p[0] for p in bottom_pixels) // len(bottom_pixels)
        avg_y = sum(p[1] for p in bottom_pixels) // len(bottom_pixels)
        log(f"  找到签到按钮: ({avg_x}, {avg_y})")
    else:
        # 备用坐标
        avg_x, avg_y = 1250, 150
        log(f"  使用备用坐标: ({avg_x}, {avg_y})")

    # 点击签到按钮
    pyautogui.click(avg_x, avg_y)
    time.sleep(2)

    # 步骤6: 截图点击后状态
    log("\n【步骤6】保存点击后截图...")
    save_screenshot('after_click')

    # 步骤7: 等待并重新读取积分
    log("\n【步骤7】等待刷新...")
    time.sleep(3)

    final_credits = get_credits_from_storage()
    log(f"  新积分: {final_credits}")

    # 步骤8: 最终截图
    log("\n【步骤8】保存最终截图...")
    save_screenshot('final')

    if final_credits > initial_credits:
        increase = final_credits - initial_credits
        log(f"\n✅ 签到成功! 积分增加: {increase}")
    else:
        log(f"\n⚠️ 积分未变化 ({initial_credits} -> {final_credits})")
        log("  请检查界面上的积分显示")

    log("\n" + "=" * 60)
    log(f"截图已保存到: {SCREENSHOTS_DIR}")
    log("=" * 60)

if __name__ == '__main__':
    main()
