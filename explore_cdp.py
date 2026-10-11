# -*- coding: utf-8 -*-
"""
方案探索：检查Trae的CDP/DevTools端口是否可用
端口51000是Electron的调试端口
"""
import socket
import json
import requests
import time

print("=== 检查端口51000 ===")

# 1. 测试端口是否监听
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
result = sock.connect_ex(('127.0.0.1', 51000))
if result == 0:
    print("✓ 端口51000正在监听")
else:
    print(f"✗ 端口51000未监听 (错误码: {result})")
sock.close()

# 2. 尝试HTTP连接（Electron CDP通常使用HTTP）
print("\n=== 尝试HTTP连接 ===")
try:
    resp = requests.get("http://127.0.0.1:51000/json", timeout=3)
    print(f"响应状态: {resp.status_code}")
    print(f"响应内容: {resp.text[:500]}")
except Exception as e:
    print(f"HTTP连接失败: {e}")

# 3. 尝试WebSocket（CDP使用WebSocket）
print("\n=== 尝试WebSocket连接 ===")
try:
    import websockets
    async def test_ws():
        ws = await websockets.connect("ws://127.0.0.1:51000/devtools/page/1", timeout=3)
        print(f"WebSocket连接成功!")
        await ws.close()
    
    import asyncio
    asyncio.run(test_ws())
except ImportError:
    print("websockets库未安装，尝试手动发送WebSocket握手...")
    # 手动发送WebSocket握手
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 51000))
    handshake = (
        "GET /json HTTP/1.1\r\n"
        "Host: 127.0.0.1:51000\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    sock.send(handshake.encode())
    time.sleep(1)
    try:
        resp = sock.recv(4096)
        print(f"响应: {resp[:500].decode('utf-8', errors='ignore')}")
    except:
        print("无响应或响应为空")
    sock.close()
except Exception as e:
    print(f"WebSocket连接失败: {e}")

# 4. 检查其他可能的端口
print("\n=== 检查其他端口 ===")
for port in [9222, 51001, 51002]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        print(f"✓ 端口{port}正在监听")
    else:
        print(f"✗ 端口{port}未监听")
    sock.close()

print("\n=== 检查Trae进程列表 ===")
import subprocess
result = subprocess.run(
    ['wmic', 'process', 'where', 'name="Trae CN.exe"', 'get', 'ProcessId,CommandLine', '/format:list'],
    capture_output=True, text=True, timeout=10
)
print(result.stdout[:2000] if result.stdout else "无输出")
