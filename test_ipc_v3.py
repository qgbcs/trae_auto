"""
通过VS Code IPC通道直接调用签到API
使用vscode-extension host的IPC机制
"""
import json
import sys
import time
import win32gui
import win32con
import win32api
import ctypes
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# 读取JWT token
JWT_PATH = Path.home() / '.trae-cn' / 'trae-jwt-token'
token = JWT_PATH.read_text().strip() if JWT_PATH.exists() else ''

# VS Code工作区配置路径
WORKSPACE_CONFIG = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'

def get_workspace_folders():
    """获取当前打开的工作区文件夹"""
    if not WORKSPACE_CONFIG.exists():
        return []
    try:
        data = json.loads(WORKSPACE_CONFIG.read_text())
        windows = data.get('windowsState', {}).get('lastActiveWindow', {})
        folder = windows.get('folder', '')
        if folder:
            return [folder]
    except:
        pass
    return []

def send_ime_message(hwnd, chars):
    """发送IME消息（模拟中文输入）"""
    for char in chars:
        # 发送字符的Unicode
        win32gui.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
        time.sleep(0.01)

def click_at(x, y):
    """点击指定坐标"""
    # 转换为屏幕坐标
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.1)

def find_trae_window():
    """找到Trae窗口"""
    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'Trae' in title or 'trae' in title.lower():
                results.append(hwnd)
    windows = []
    win32gui.EnumWindows(enum_callback, windows)
    return windows

def main():
    print("="*60)
    print("方案: 直接调用VS Code IPC API")
    print("="*60)

    # 1. 获取JWT token信息
    print(f"\n[+] JWT token: {token[:40]}...")

    # 2. 获取工作区信息
    folders = get_workspace_folders()
    print(f"[+] 工作区: {folders}")

    # 3. 尝试通过vscode CLI命令
    print("\n[+] 尝试通过VS Code CLI调用签到...")

    # VS Code/ Trae 的IPC channel名称
    IPC_CHANNELS = [
        "vscode:sandbox::main-invoke-claimCheckinCredits",
        "vscode:claimCheckinCredits",
        "trae:claimCheckinCredits",
    ]

    for channel in IPC_CHANNELS:
        print(f"\n[>] 尝试通道: {channel}")
        # 注意：这里需要找到正确的IPC调用方式

    # 4. 尝试直接修改storage.json（不推荐，但作为最后手段）
    print("\n[+] 检查storage.json中的签到状态...")
    STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
    if STORAGE_JSON.exists():
        data = json.loads(STORAGE_JSON.read_text())
        icube = data.get('iCubeServerData://icube.cloudide', '{}')
        if isinstance(icube, str):
            icube = json.loads(icube)
        commercial = icube.get('commercialActivityInfo', {})
        activities = commercial.get('activities', [])
        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                print(f"    activityId: {act.get('activityId')}")
                print(f"    workExtra: {act.get('workExtra')}")
                print(f"    granted: {act.get('workExtra', {}).get('granted')}")

    print("\n[!] 提示: 直接调用IPC API需要深入分析Electron的内部协议")
    print("[!] 建议: 继续使用UI自动化方式，但优化点击位置")

if __name__ == '__main__':
    main()
