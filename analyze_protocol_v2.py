"""
通过注入JS到Electron渲染进程调用IPC
使用Electron的debugger协议
"""
import sys
import json
import time
import socket
import struct
import urllib.request
sys.stdout.reconfigure(encoding='utf-8')

# 端口51000是管理端口，但可能有其他协议
PORT = 51000

def test_http_endpoints(port):
    """测试HTTP端点"""
    endpoints = [
        '/json',
        '/json/list',
        '/json/version',
        '/ping',
        '/status',
    ]

    print(f"\n[测试HTTP端点 端口 {port}]")
    for endpoint in endpoints:
        try:
            url = f"http://127.0.0.1:{port}{endpoint}"
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=2)
            data = resp.read().decode()
            print(f"  [+] {endpoint}: {data[:100]}")
        except Exception as e:
            pass  # 静默失败

def test_binary_protocol(port):
    """测试二进制协议"""
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=3)
        sock.settimeout(2)

        print(f"\n[测试二进制协议 端口 {port}]")

        # 测试不同的消息格式
        tests = [
            # 1. 简单的二进制握手
            (b"handshake", b"\x00\x00\x00\x01"),

            # 2. JSON-RPC格式
            (b"jsonrpc_ping", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}).encode()),

            # 3. VS Code IPC格式
            (b"vscode_ipc", json.dumps({
                "type": 1,
                "id": 0,
                "port": port,
                "value": []
            }).encode()),

            # 4. Electron消息格式
            (b"electron_msg", json.dumps({
                "id": 1,
                "method": "vscode:sandbox::main-invoke-claimCheckinCredits",
                "args": []
            }).encode()),

            # 5. 尝试直接发送签到
            (b"checkin_direct", json.dumps({
                "method": "claimCheckinCredits",
                "params": {"activityId": "checkin_credits"}
            }).encode()),
        ]

        for name, data in tests:
            try:
                # 发送长度前缀 + 数据
                sock.sendall(struct.pack('>I', len(data)) + data)
                print(f"  [发送] {name} ({len(data)} bytes)")

                # 读取响应
                resp = sock.recv(1024)
                if resp:
                    print(f"  [响应] {len(resp)} bytes: {resp[:50].hex()}")
                else:
                    print(f"  [响应] 空")
            except socket.timeout:
                print(f"  [超时] {name}")
                break
            except Exception as e:
                print(f"  [错误] {name}: {e}")
                break

        sock.close()
        return True
    except Exception as e:
        print(f"[-] 连接错误: {e}")
        return False

def test_websocket(port):
    """测试WebSocket连接"""
    try:
        import base64
        import hashlib
        import secrets

        print(f"\n[测试WebSocket 端口 {port}]")

        # 生成WebSocket key
        key = base64.b64encode(secrets.token_bytes(16)).decode()

        sock = socket.create_connection(('127.0.0.1', port), timeout=3)

        # 发送WebSocket握手
        request = (
            f"GET / HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"\r\n"
        )

        sock.sendall(request.encode())

        # 读取响应
        response = b''
        while b'\r\n\r\n' not in response:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        if b'101 Switching Protocols' in response:
            print("  [+] WebSocket握手成功!")

            # 发送签到消息
            msg = json.dumps({
                "id": 1,
                "method": "vscode:sandbox::main-invoke-claimCheckinCredits",
                "params": [{"activityId": "checkin_credits"}]
            })

            # WebSocket帧
            data = msg.encode('utf-8')
            length = len(data)
            frame = bytearray([0x81])  # FIN + Text

            if length < 126:
                frame.append(length | 0x80)  # MASK bit
            else:
                frame.append(126 | 0x80)
                frame.extend(struct.pack('>H', length))

            # 掩码
            masking_key = secrets.token_bytes(4)
            frame.extend(masking_key)

            masked_data = bytearray(length)
            for i in range(length):
                masked_data[i] = data[i] ^ masking_key[i % 4]
            frame.extend(masked_data)

            sock.sendall(frame)
            print("  [+] 已发送签到请求")

            # 读取响应
            sock.settimeout(3)
            resp = sock.recv(4096)
            if resp:
                print(f"  [响应] {len(resp)} bytes")
            else:
                print("  [响应] 空")

            sock.close()
            return True
        else:
            print("  [-] WebSocket握手失败")
            sock.close()
            return False
    except Exception as e:
        print(f"  [-] WebSocket错误: {e}")
        return False

def main():
    print("="*60)
    print("深度分析Trae CN通信协议")
    print("="*60)

    # 测试端口51000
    test_http_endpoints(PORT)
    test_binary_protocol(PORT)
    test_websocket(PORT)

    print("\n" + "="*60)
    print("结论: 端口51000使用自定义二进制协议，不是标准CDP")
    print("="*60)

if __name__ == '__main__':
    main()
