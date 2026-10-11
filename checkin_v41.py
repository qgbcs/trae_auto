#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v41 - 通过端口51000发送签到请求
"""
import sys
import time
import json
import socket
import struct
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = SCRIPT_DIR / 'screenshots'
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def send_message(sock, channel, params=None):
    """发送消息到Electron进程"""
    try:
        # 构造消息
        message = {
            "jsonrpc": "2.0",
            "method": channel,
            "params": params or [],
            "id": int(time.time() * 1000)
        }

        msg_bytes = json.dumps(message).encode('utf-8')

        # 发送长度前缀
        length = struct.pack('>I', len(msg_bytes))
        sock.sendall(length + msg_bytes)
        log(f"  发送消息: {channel}")

        # 设置超时
        sock.settimeout(5)

        # 接收响应
        # 先接收长度
        length_data = b''
        while len(length_data) < 4:
            chunk = sock.recv(4 - len(length_data))
            if not chunk:
                break
            length_data += chunk

        if len(length_data) == 4:
            msg_len = struct.unpack('>I', length_data)[0]
            log(f"  响应长度: {msg_len}")

            # 接收消息体
            msg_data = b''
            while len(msg_data) < msg_len:
                chunk = sock.recv(msg_len - len(msg_data))
                if not chunk:
                    break
                msg_data += chunk

            if msg_data:
                resp = json.loads(msg_data.decode('utf-8'))
                log(f"  收到响应: {json.dumps(resp, ensure_ascii=False)[:200]}")
                return resp

        return None
    except Exception as e:
        log(f"  发送错误: {e}")
        return None

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v41 - 端口51000")
    log("=" * 60)

    # 连接到端口51000
    log("\n连接端口51000...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(('127.0.0.1', 51000))
        log("  连接成功")

        # 尝试发送签到请求
        log("\n发送签到请求...")

        # 方式1: 直接调用IPC channel
        result = send_message(sock, 'vscode:sandbox::main-invoke-claimCheckinCredits', [])

        if result:
            log(f"\n✅ 签到请求已发送")
            log(f"  结果: {result}")
        else:
            log(f"\n⚠️ 未收到响应")

        # 方式2: 尝试获取签到状态
        log("\n获取签到状态...")
        status = send_message(sock, 'vscode:sandbox::main-invoke-fetchCheckinCreditsStatus', [])

        if status:
            log(f"  状态: {status}")

    except Exception as e:
        log(f"  连接错误: {e}")
    finally:
        sock.close()

    log("\n" + "=" * 60)

if __name__ == '__main__':
    main()
