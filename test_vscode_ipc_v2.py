#!/usr/bin/env python3
"""
测试通过 VSCode IPC 调用签到接口
研究 vscode.ipcRenderer.invoke 的通信机制
"""

import json
import time
import socket
import struct
import win32gui
import win32process
import win32api
import subprocess
import os

def find_trae_processes():
    """查找 Trae 进程及其主窗口"""
    result = subprocess.run(
        ['powershell', '-Command',
         'Get-Process -Name "Trae CN" | Select-Object Id, ProcessName, StartTime'],
        capture_output=True, text=True
    )
    print("Trae 进程列表:")
    print(result.stdout)
    return result.stdout

def get_main_window():
    """获取 Trae 主窗口"""
    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'TRAE' in title.upper() or 'Trae' in title:
                results.append((hwnd, title))
    results = []
    win32gui.EnumWindows(enum_callback, results)
    for hwnd, title in results:
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
        print(f"  HWND={hwnd}, PID={pid}, Title='{title}'")
    return results[0] if results else None

def get_process_command_line(pid):
    """获取进程命令行参数"""
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             f'(Get-CimInstance -ClassName Win32_Process -Filter "ProcessId={pid}").CommandLine'],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except:
        return ""

def test_windows_messages(hwnd):
    """测试通过 Windows 消息发送"""
    # 尝试发送自定义消息
    WM_APP = 0x8000
    try:
        # 先测试窗口是否响应
        result = win32api.SendMessageTimeout(
            hwnd, WM_APP + 1, 0, 0,
            win32con.SMTO_ABORTIFHUNG, 1000
        )
        print(f"  SendMessageTimeout 结果: {result}")
    except Exception as e:
        print(f"  SendMessageTimeout 失败: {e}")

def test_named_pipes():
    """尝试连接命名管道"""
    pipe_name = r'\\.\pipe\vscode-shared-42-unix-ipc'
    try:
        hPipe = win32file.CreateFile(
            pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None, win32file.OPEN_EXISTING, 0, None
        )
        print(f"  成功连接到命名管道: {pipe_name}")
        win32file.CloseHandle(hPipe)
        return True
    except Exception as e:
        print(f"  命名管道连接失败: {e}")
        return False

def try_vscode_ipc_over_socket():
    """尝试通过 socket 发送 VSCode IPC 消息"""
    # VSCode 内部使用 named pipes 或 Unix sockets
    # 在 Windows 上通常是命名管道

    # 列出所有可能的命名管道
    pipe_patterns = [
        r'\\.\pipe\vscode-*',
        r'\\.\pipe\*trae*',
        r'\\.\pipe\*ipc*',
    ]

    for pattern in pipe_patterns:
        try:
            # 使用 PowerShell 列出匹配的管道
            result = subprocess.run(
                ['powershell', '-Command',
                 f'Get-ChildItem -Path \\.\pipe\\ | Where-Object {{ $_.Name -like "{pattern.replace(chr(92)*2, "*")}" }} | Select-Object Name'],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                print(f"  找到管道: {result.stdout}")
        except Exception as e:
            print(f"  列出管道失败: {e}")

def analyze_electron_ipc():
    """分析 Electron IPC 机制"""
    print("\n=== Electron IPC 分析 ===")

    # VSCode IPC 格式：
    # 每个消息有一个4字节的长度前缀
    # 消息格式: { "id": number, "method": string, "params": any }

    # 测试端口 51000 的响应模式
    print("\n[测试端口 51000 响应模式]")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('127.0.0.1', 51000))

        # 发送空的 hello 消息
        # VSCode IPC 的 hello 消息格式
        hello = {
            "rid": 0,
            "method": "hello",
            "args": [{
                "profileName": "vscode",
                "transport": "socket",
                "ags": []
            }]
        }
        msg = json.dumps(hello).encode('utf-8')
        length = struct.pack('>I', len(msg))
        sock.sendall(length + msg)

        time.sleep(0.5)
        response = sock.recv(4096)
        print(f"  响应长度: {len(response)} bytes")
        print(f"  响应内容: {response[:100]}")
        sock.close()
    except Exception as e:
        print(f"  端口 51000 通信失败: {e}")

def check_webview_port():
    """检查是否有 Webview 调试端口"""
    print("\n=== 检查 Webview 调试端口 ===")

    # 尝试常见的 CDP 端口范围
    for port in range(9222, 9232):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"  端口 {port} 打开")
                # 检查是否是 CDP
                sock.sendall(b'GET /json HTTP/1.1\r\nHost: localhost\r\n\r\n')
                response = sock.recv(4096)
                if b'"devtoolsFrontendUrl"' in response:
                    print(f"    -> CDP 端点: http://127.0.0.1:{port}/json")
            sock.close()
        except:
            pass

def main():
    print("=" * 60)
    print("VSCode IPC 签到分析 v1")
    print("=" * 60)

    # 1. 查找进程
    print("\n[1] 查找 Trae 进程...")
    find_trae_processes()

    # 2. 查找主窗口
    print("\n[2] 查找主窗口...")
    window = get_main_window()

    # 3. 分析 IPC
    print("\n[3] 分析 Electron IPC 机制...")
    analyze_electron_ipc()

    # 4. 检查 Webview 端口
    check_webview_port()

    # 5. 尝试命名管道
    print("\n[4] 尝试命名管道...")
    test_named_pipes()

    print("\n=== 分析完成 ===")

if __name__ == '__main__':
    main()
