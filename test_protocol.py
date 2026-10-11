# -*- coding: utf-8 -*-
"""
方案探索：测试端口51000的协议类型
尝试识别是CDP、WebSocket还是自定义协议
"""
import socket
import time
import struct

print("=== 测试端口51000协议 ===\n")

def send_and_receive(sock, data, timeout=2):
    """发送数据并接收响应"""
    sock.send(data)
    sock.settimeout(timeout)
    try:
        response = sock.recv(4096)
        return response
    except socket.timeout:
        return b''

# 1. 测试HTTP GET
print("1. 测试HTTP GET /json")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 51000))
sock.send(b"GET /json HTTP/1.1\r\nHost: 127.0.0.1:51000\r\n\r\n")
time.sleep(0.5)
resp = send_and_receive(sock, b"", timeout=1)
if resp:
    print(f"   响应: {resp[:500].decode('utf-8', errors='ignore')}")
else:
    print("   无响应")
sock.close()

# 2. 测试WebSocket握手
print("\n2. 测试WebSocket握手 /json")
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
resp = sock.recv(4096)
if resp:
    print(f"   响应: {resp[:500].decode('utf-8', errors='ignore')}")
else:
    print("   无响应")
sock.close()

# 3. 测试VS Code IPC协议（魔术字节 'IC'）
print("\n3. 测试VS Code IPC协议")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 51000))

# VS Code IPC header: 魔术字节 'IC' + 版本 + 长度 + 消息
magic = b'IC'
version = struct.pack('<H', 1)  # 版本1
message = b'{"id":1,"method":"test"}'
length = struct.pack('<I', len(message))
header = magic + version + length
full_message = header + message

sock.send(full_message)
time.sleep(1)
resp = sock.recv(4096)
if resp:
    print(f"   响应: {resp[:100].hex()}")
    try:
        print(f"   响应文本: {resp[:100].decode('utf-8', errors='ignore')}")
    except:
        pass
else:
    print("   无响应")
sock.close()

# 4. 测试Electron DevTools Protocol
print("\n4. 测试Electron DevTools Protocol")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 51000))

# 尝试发送简单的测试帧
test_frame = struct.pack('<I', 4) + b'test'  # 4字节长度 + 'test'
sock.send(test_frame)
time.sleep(1)
resp = sock.recv(4096)
if resp:
    print(f"   响应: {resp[:100].hex()}")
else:
    print("   无响应")
sock.close()

# 5. 尝试CDP JSON接口（不同路径）
print("\n5. 测试不同HTTP路径")
paths = ['/json', '/json/list', '/json/version', '/devtools/page', '/']
for path in paths:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        sock.connect(('127.0.0.1', 51000))
        request = f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:51000\r\nConnection: close\r\n\r\n"
        sock.send(request.encode())
        response = b''
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            except socket.timeout:
                break
        if response:
            print(f"   {path}: {response[:200].decode('utf-8', errors='ignore')}")
        else:
            print(f"   {path}: 无响应")
    except Exception as e:
        print(f"   {path}: 错误 - {e}")
    finally:
        sock.close()
        time.sleep(0.5)

print("\n=== 结论 ===")
print("需要根据实际响应判断协议类型")
