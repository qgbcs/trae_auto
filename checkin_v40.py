#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v40 - 通过 Electron IPC 调用签到API
"""
import sys
import time
import json
import socket
import struct
from pathlib import Path
from datetime import datetime
import subprocess
import psutil

SCRIPT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = SCRIPT_DIR / 'screenshots'
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_trae_process():
    """获取 Trae CN 主进程"""
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        if 'Trae CN.exe' in proc.info['name']:
            # 找到主进程（通常pid最小）
            return proc.info['pid'], proc.info['exe']
    return None, None

def send_ipc_message(conn, channel, args):
    """发送IPC消息到Electron进程"""
    try:
        # 构造JSON-RPC消息
        message = json.dumps({
            "jsonrpc": "2.0",
            "method": channel,
            "params": args,
            "id": 1
        })

        # 发送消息长度（4字节）
        msg_bytes = message.encode('utf-8')
        length = struct.pack('>I', len(msg_bytes))
        conn.sendall(length + msg_bytes)

        # 接收响应
        response = conn.recv(4096)
        if response:
            resp_len = struct.unpack('>I', response[:4])[0]
            resp_data = response[4:4+resp_len].decode('utf-8')
            return json.loads(resp_data)
        return None
    except Exception as e:
        log(f"  IPC发送错误: {e}")
        return None

def try_electron_debug_port():
    """尝试通过Electron调试端口发送IPC消息"""
    log("\n尝试通过Electron调试端口...")

    # 查找Trae进程
    pid, exe = get_trae_process()
    if not pid:
        log("  未找到Trae进程")
        return False

    log(f"  找到Trae进程 PID: {pid}")

    # Electron调试端口通常是51000或类似
    # 尝试连接
    for port in [51000, 51001, 51002, 9222, 9223]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect(('127.0.0.1', port))

            # 尝试发送简单的测试消息
            test_msg = json.dumps({
                "method": "vscode:sandbox::main-invoke-claimCheckinCredits",
                "params": []
            }).encode('utf-8')

            sock.sendall(test_msg)
            time.sleep(0.5)

            # 接收响应
            try:
                data = sock.recv(1024)
                if data:
                    log(f"  端口 {port} 有响应")
                    # 尝试解析
                    try:
                        resp = json.loads(data.decode('utf-8'))
                        log(f"  响应: {resp}")
                        if resp.get('result', {}).get('success'):
                            return True
                    except:
                        pass
            except socket.timeout:
                pass

            sock.close()
        except (ConnectionRefusedError, socket.timeout):
            continue
        except Exception as e:
            log(f"  端口 {port} 错误: {e}")
            continue

    log("  所有端口尝试失败")
    return False

def try_vscode_ipc():
    """尝试通过VSCode IPC通道"""
    log("\n尝试VSCode IPC通道...")

    # VSCode IPC通常使用named pipe或socket
    # 在Windows上，可能使用命名管道
    pipe_path = r'\\.\pipe\vscode-channels-*-main'

    try:
        # 列出所有命名管道
        import win32pipe
        import win32file

        # 尝试常见的IPC路径
        ipc_paths = [
            r'\\.\pipe\vscode-channels-main',
            r'\\.\pipe\vscode-unified-channel-0',
        ]

        for path in ipc_paths:
            try:
                handle = win32pipe.CreateFile(
                    path,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )

                # 发送签到请求
                message = json.dumps({
                    "method": "vscode:sandbox::main-invoke-claimCheckinCredits",
                    "params": []
                }).encode('utf-8')

                win32pipe.WriteFile(handle, message)
                time.sleep(1)

                # 尝试读取响应
                try:
                    ret, data = win32file.ReadFile(handle, 4096)
                    log(f"  收到响应: {data.decode('utf-8', errors='ignore')}")
                    win32file.CloseHandle(handle)
                    return True
                except Exception as e:
                    log(f"  读取响应失败: {e}")
                    win32file.CloseHandle(handle)

            except Exception as e:
                log(f"  管道 {path} 错误: {e}")
                continue

    except ImportError:
        log("  win32pipe/win32file 模块不可用")
    except Exception as e:
        log(f"  IPC错误: {e}")

    return False

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v40 - IPC方式")
    log("=" * 60)

    # 尝试不同的IPC方式
    success = False

    # 方式1: Electron调试端口
    if not success:
        success = try_electron_debug_port()

    # 方式2: VSCode IPC
    if not success:
        success = try_vscode_ipc()

    if success:
        log("\n✅ 签到请求已发送")
    else:
        log("\n❌ 所有IPC方式都失败")
        log("  建议：手动点击'每日签到'按钮")

    log("\n" + "=" * 60)

if __name__ == '__main__':
    main()
