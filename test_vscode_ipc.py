"""
通过VS Code/ Electron IPC通道直接调用签到API
"""
import json
import sys
import time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# VS Code IPC配置
IPCHandle = "Trae CN"
IPC_PORT = 51000

def try_vscode_rpc():
    """尝试通过VS Code RPC协议调用"""
    import socket
    import struct

    # VS Code使用自定义二进制协议
    # 端口51000是Electron管理端口

    try:
        sock = socket.create_connection(('127.0.0.1', 51000), timeout=5)
        sock.settimeout(3)
        print(f"[+] 连接到管理端口 51000")

        # 尝试发送JSON-RPC消息
        # VS Code使用MessagePack或自定义二进制格式

        # 格式1: 简单的JSON-RPC ping
        msgs = [
            # JSON-RPC 2.0
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}).encode(),
            # VS Code IPC握手
            json.dumps({"type": 1, "id": 0, "port": 51000, "value": []}).encode(),
        ]

        for i, msg in enumerate(msgs):
            try:
                # 发送长度前缀 + 数据
                sock.sendall(struct.pack('>I', len(msg)) + msg)
                print(f"[+] 发送消息 {i+1}, 长度: {len(msg)}")

                # 读取响应
                resp = sock.recv(1024)
                print(f"[-] 响应: {resp[:100].hex()}")
            except socket.timeout:
                print(f"[-] 消息 {i+1} 超时")
                break
            except Exception as e:
                print(f"[-] 消息 {i+1} 错误: {e}")
                break

        sock.close()
        return True
    except Exception as e:
        print(f"[-] 连接错误: {e}")
        return False

def try_named_pipe():
    """尝试通过命名管道连接"""
    import win32pipe
    import win32file

    # VS Code在Windows上使用命名管道
    pipe_name = r'\\.\pipe\vscode-webview-main-ipc-0'

    try:
        handle = win32pipe.CreateFile(
            pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        print(f"[+] 连接到命名管道: {pipe_name}")
        win32pipe.CloseHandle(handle)
        return True
    except Exception as e:
        print(f"[-] 命名管道错误: {e}")
        return False

def try_ipc_channel():
    """尝试通过IPC通道调用签到"""
    # VS Code扩展宿主使用特定的IPC通道
    channels = [
        "vscode:sandbox::main-invoke-claimCheckinCredits",
        "vscode:claimCheckinCredits",
        "trae:claimCheckinCredits",
    ]

    for channel in channels:
        print(f"\n[>] 尝试通道: {channel}")
        # 这里需要知道如何正确调用IPC通道

if __name__ == '__main__':
    print("="*60)
    print("测试VS Code IPC通道")
    print("="*60)

    # 测试1: 管理端口
    print("\n[测试1] 管理端口51000")
    try_vscode_rpc()

    # 测试2: 命名管道
    print("\n[测试2] 命名管道")
    try_named_pipe()

    # 测试3: IPC通道
    print("\n[测试3] IPC通道")
    try_ipc_channel()

    print("\n" + "="*60)
    print("结论: 直接调用IPC需要更深入的分析")
    print("="*60)
