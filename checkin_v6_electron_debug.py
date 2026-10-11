# -*- coding: utf-8 -*-
"""
Trae CN 签到脚本 v6 - 通过 Electron DevTools Protocol 调用
Electron 应用开了 51000 端口用于调试，可以发送 protocol 命令
"""
import socket
import json
import struct
import sys
import time
import subprocess

# Electron DevTools Protocol 配置
HOST = "127.0.0.1"
PORT = 51000

def try_electron_debug():
    """尝试通过 Electron 调试端口执行 JS 代码"""
    print(f"=== 尝试连接 Electron 调试端口 {PORT} ===")
    try:
        sock = socket.create_connection((HOST, PORT), timeout=3)
        print(f"  成功连接到 {HOST}:{PORT}")

        # 发送一个简单的 protocol 请求
        # Electron 使用 Chrome DevTools Protocol
        msg = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": "globalThis.vscode ? 'found vscode' : 'no vscode'"
            }
        }
        data = json.dumps(msg).encode('utf-8')

        # CDP 使用帧格式: length + data
        frame = struct.pack('>I', len(data)) + data
        sock.sendall(frame)

        # 读取响应
        sock.settimeout(3)
        response = sock.recv(4096)
        print(f"  响应长度: {len(response)}")
        print(f"  响应内容: {response[:500]}")
        sock.close()
        return True
    except ConnectionRefusedError:
        print(f"  端口 {PORT} 被拒绝，可能不是调试端口")
        return False
    except Exception as e:
        print(f"  错误: {e}")
        return False

def try_ipc_channels():
    """尝试找到可用的 IPC 通道"""
    print("\n=== 查找 Trae 进程 ===")
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq trae.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        print(result.stdout)
    except:
        pass

    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq tra*.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        print(result.stdout)
    except:
        pass

    # 查找 Electron 相关进程
    try:
        result = subprocess.run(
            ["wmic", "process", "where", "name like '%trae%'", "get", "name,pid,commandline"],
            capture_output=True, text=True, timeout=5
        )
        print(result.stdout[:2000])
    except Exception as e:
        print(f"  wmic 错误: {e}")

if __name__ == "__main__":
    try_electron_debug()
    try_ipc_channels()
