"""
直接通过pyautogui点击用户图标和签到按钮
根据用户反馈优化位置
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

def main():
    log("=" * 60)
    log("Trae CN 自动签到 - 最终版")
    log("=" * 60)

    # 步骤1: 读取初始积分
    log("\n【步骤1】读取初始积分...")
    initial_credits = get_credits_from_storage()
    log(f"  当前积分: {initial_credits}")

    # 步骤2: 截图当前状态
    log("\n【步骤2】保存当前状态截图...")
    save_screenshot('before')

    # 步骤3: 关闭可能打开的菜单
    log("\n【步骤3】关闭现有菜单...")
    pyautogui.press('esc')
    time.sleep(0.3)

    # 步骤4: 点击用户图标
    # 根据用户反馈，用户图标在右上角区域
    # 用户说坐标是(780, 20)，但之前测试显示是(1250, 15)
    # 让我们扫描整个顶部区域找到图标
    log("\n【步骤4】查找并点击用户图标...")

    # 截图顶部区域
    with mss.MSS() as sct:
        screenshot = sct.grab({
            'left': 1100,
            'top': 0,
            'width': 300,
            'height': 50
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(SCREENSHOTS_DIR / 'top_area.png')

    # 查找彩色图标（用户头像通常是圆形彩色）
    pixels = img.load()
    w, h = img.size

    # 查找紫色/蓝色像素（用户图标颜色）
    icon_candidates = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            # 紫色图标: R低, G低, B高
            if r < 150 and g < 100 and b > 150:
                icon_candidates.append((x + 1100, y))

    if icon_candidates:
        # 取中心点
        avg_x = sum(p[0] for p in icon_candidates) // len(icon_candidates)
        avg_y = sum(p[1] for p in icon_candidates) // len(icon_candidates)
        log(f"  找到用户图标: ({avg_x}, {avg_y})")
        pyautogui.click(avg_x, avg_y)
    else:
        # 使用备用位置
        log(f"  使用备用位置: (1250, 15)")
        pyautogui.click(1250, 15)

    time.sleep(0.8)

    # 步骤5: 截图菜单
    log("\n【步骤5】保存菜单截图...")
    save_screenshot('menu')

    # 步骤6: 查找并点击签到按钮
    log("\n【步骤6】查找并点击签到按钮...")

    # 截图菜单区域
    with mss.MSS() as sct:
        screenshot = sct.grab({
            'left': 1100,
            'top': 30,
            'width': 300,
            'height': 200
        })
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(SCREENSHOTS_DIR / 'menu_area.png')

    pixels = img.load()
    w, h = img.size

    # 查找深色文字（"签到"）
    text_pixels = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y][:3]
            # 深色文字
            if r < 100 and g < 100 and b < 100 and r + g + b > 30:
                text_pixels.append((x + 1100, y + 30))

    if text_pixels:
        # 找最下面的深色文字（签到按钮通常在菜单底部）
        text_pixels.sort(key=lambda p: p[1], reverse=True)
        bottom_pixels = text_pixels[:15]
        avg_x = sum(p[0] for p in bottom_pixels) // len(bottom_pixels)
        avg_y = sum(p[1] for p in bottom_pixels) // len(bottom_pixels)
        log(f"  找到签到按钮: ({avg_x}, {avg_y})")
    else:
        # 备用坐标
        avg_x, avg_y = 1200, 100
        log(f"  使用备用坐标: ({avg_x}, {avg_y})")

    # 点击签到按钮
    pyautogui.click(avg_x, avg_y)
    time.sleep(2)

    # 步骤7: 截图点击后状态
    log("\n【步骤7】保存点击后截图...")
    save_screenshot('after_click')

    # 步骤8: 等待并重新读取积分
    log("\n【步骤8】等待刷新...")
    time.sleep(3)

    final_credits = get_credits_from_storage()
    log(f"  新积分: {final_credits}")

    # 步骤9: 最终截图
    log("\n【步骤9】保存最终截图...")
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
