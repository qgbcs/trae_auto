"""测试Node.js Inspector协议连接到Trae CN"""
import subprocess
import asyncio
import json
import time

async def test_inspector_protocol():
    print("=== 测试Node.js Inspector协议 ===\n")

    # 获取Trae进程
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq TraeCN.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, shell=True
        )
        print("Trae CN进程:")
        for line in result.stdout.strip().split('\n')[1:]:
            if line:
                parts = line.split('","')
                pid = parts[0].replace('"', '')
                print(f"  PID: {pid}")
    except Exception as e:
        print(f"获取进程失败: {e}")
        return

    # 测试WebSocket连接到端口62900
    print("\n=== 测试WebSocket到端口62900 ===")
    try:
        import websockets
        async with websockets.connect('ws://127.0.0.1:62900') as websocket:
            print("✓ WebSocket连接成功")

            # 发送Inspector协议消息
            msg = {
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "process.version",
                    "awaitPromise": False
                }
            }
            await websocket.send(json.dumps(msg))
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"响应: {response}")

    except Exception as e:
        print(f"WebSocket连接失败: {e}")

    # 测试端口51000的自定义协议
    print("\n=== 测试端口51000 ===")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 51000))
        print("✓ TCP连接成功")

        # 尝试发送不同的消息格式
        # Electron管理端口通常使用protobuf或自定义二进制协议
        # 让我们先尝试简单的文本消息
        test_messages = [
            b'getClients',
            b'listTargets',
            json.dumps({"command": "list"}).encode(),
        ]

        for i, msg in enumerate(test_messages):
            try:
                sock.sendall(msg)
                time.sleep(0.5)
                data = sock.recv(1024)
                print(f"  消息{i+1}响应: {data[:100]}")
            except Exception as e:
                print(f"  消息{i+1}失败: {e}")

        sock.close()
    except Exception as e:
        print(f"端口51000连接失败: {e}")

    # 尝试通过CDP端口发现
    print("\n=== 发现CDP端点 ===")
    try:
        import urllib.request
        # 尝试常见的CDP发现端口
        ports = [51000, 51001, 9222, 62900]
        for port in ports:
            try:
                url = f'http://127.0.0.1:{port}/json/version'
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=2) as response:
                    data = json.loads(response.read().decode())
                    print(f"  端口{port}: {data.get('Browser', 'Unknown')}")
            except Exception as e:
                pass  # 静默忽略失败的连接
    except Exception as e:
        print(f"CDP发现失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_inspector_protocol())
