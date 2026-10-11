#!/usr/bin/env python3
"""
通过 WebSocket 连接端口 62900 并测试 IPC 调用
"""

import json
import time
import socket
import struct
import hashlib
import base64
import sys
import os

def ws_connect(port, path='/'):
    """建立 WebSocket 连接"""
    key = base64.b64encode(os.urandom(16)).decode()
    GUID = "258EAFA5-E914-47DA-95CA-5AB5DC10BE69"

    sock = socket.create_connection(('127.0.0.1', port), timeout=10)

    # 发送 HTTP Upgrade 请求
    request = (
        f"GET {path} HTTP/1.1\r\n"
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

    if b'101 Switching Protocols' not in response:
        print(f"  WebSocket 握手失败: {response[:200]}")
        sock.close()
        return None

    # 验证 accept key
    headers = response.split(b'\r\n\r\n')[0].decode()
    accept_line = [l for l in headers.split('\n') if l.lower().startswith('sec-websocket-accept:')]
    if accept_line:
        server_key = accept_line[0].split(':', 1)[1].strip()
        expected_key = base64.b64encode(
            hashlib.sha1((key + GUID).encode()).digest()
        ).decode()
        if server_key != expected_key:
            print(f"  WebSocket accept key 不匹配")
            sock.close()
            return None

    print(f"  WebSocket 连接成功!")
    return sock

def ws_send_frame(sock, data, opcode=0x1):
    """发送 WebSocket 帧"""
    data = data.encode('utf-8') if isinstance(data, str) else data
    length = len(data)

    # FIN + opcode
    frame = bytearray([0x80 | opcode])

    # 掩码密钥（客户端必须）
    masking_key = os.urandom(4)
    frame.extend(masking_key)

    # 长度编码
    if length < 126:
        frame.append(length | 0x80)
    elif length < 65536:
        frame.append(126 | 0x80)
        frame.extend(struct.pack('>H', length))
    else:
        frame.append(127 | 0x80)
        frame.extend(struct.pack('>Q', length))

    # 掩码数据
    masked_data = bytearray(length)
    for i in range(length):
        masked_data[i] = data[i] ^ masking_key[i % 4]
    frame.extend(masked_data)

    sock.sendall(frame)

def ws_recv_frame(sock, timeout=5):
    """接收 WebSocket 帧"""
    sock.settimeout(timeout)
    result = bytearray()

    while True:
        # 读取帧头
        header = b''
        while len(header) < 2:
            chunk = sock.recv(2 - len(header))
            if not chunk:
                return None
        header += chunk

        first_byte = header[0]
        second_byte = header[1]

        opcode = first_byte & 0x0F
        length = second_byte & 0x7F
        is_masked = bool(second_byte & 0x80)

        # 读取扩展长度
        if length == 126:
            len_bytes = b''
            while len(len_bytes) < 2:
                chunk = sock.recv(2 - len(len_bytes))
                if not chunk:
                    return None
            len_bytes += chunk
            length = struct.unpack('>H', len_bytes)[0]
        elif length == 127:
            len_bytes = b''
            while len(len_bytes) < 8:
                chunk = sock.recv(8 - len(len_bytes))
                if not chunk:
                    return None
            len_bytes += chunk
            length = struct.unpack('>Q', len_bytes)[0]

        # 读取掩码密钥
        masking_key = b''
        if is_masked:
            while len(masking_key) < 4:
                chunk = sock.recv(4 - len(masking_key))
                if not chunk:
                    return None
            masking_key += chunk

        # 读取数据
        data = b''
        while len(data) < length:
            chunk = sock.recv(min(4096, length - len(data)))
            if not chunk:
                return None
            data += chunk

        # 解掩码
        if is_masked:
            data = bytes(b ^ masking_key[i % 4] for i, b in enumerate(data))

        # 处理控制帧
        if opcode == 0x8:  # Close
            return None
        if opcode == 0x9:  # Ping
            # 发送 Pong 响应
            frame = bytearray([0x8A])
            if length > 0:
                frame.extend(data)
            sock.sendall(frame)
            continue
        if opcode == 0xA:  # Pong
            continue

        # 文本或二进制帧
        try:
            text = data.decode('utf-8')
            return text
        except UnicodeDecodeError:
            return data

def test_ipc_channel(sock, channel, param=None):
    """测试 IPC 通道调用"""
    # 发送 hello
    hello = {
        "rid": 0,
        "method": "hello",
        "args": [{
            "profileName": "vscode",
            "transport": "socket",
            "ags": []
        }]
    }
    ws_send_frame(sock, json.dumps(hello, separators=(',', ':')))

    # 读取 hello 响应
    resp = ws_recv_frame(sock, timeout=3)
    if resp:
        print(f"  Hello 响应: {resp[:200]}")

    # 发送 invoke
    invoke_params = [param] if param else []
    invoke = {
        "rid": 1,
        "method": channel,
        "args": invoke_params
    }
    ws_send_frame(sock, json.dumps(invoke, separators=(',', ':')))

    # 读取响应
    resp = ws_recv_frame(sock, timeout=5)
    return resp

def main():
    print("=" * 60)
    print("WebSocket IPC 测试")
    print("=" * 60)

    port = 62900

    # 尝试连接
    print(f"\n[1] 连接 WebSocket 端口 {port}...")
    sock = ws_connect(port)
    if not sock:
        print("连接失败")
        return

    print("\n[2] 测试 VSCode IPC 通道...")

    # 测试签到通道
    channels = [
        'vscode:sandbox::main-invoke-claimCheckinCredits',
        'vscode:sandbox::main-invoke-fetchCheckinCreditsStatus',
        'claimCheckinCredits',
        'vscode:claimCheckinCredits',
    ]

    for channel in channels:
        print(f"\n  测试通道: {channel}")
        resp = test_ipc_channel(sock, channel)
        if resp:
            print(f"  响应: {resp[:300]}")
        else:
            print(f"  无响应")

    # 测试不同的方法名
    print("\n[3] 测试不同的方法调用...")
    methods = [
        'invoke',
        'handle',
        'send',
        'request',
    ]
    for method in methods:
        test_msg = json.dumps({
            "rid": 2,
            "method": method,
            "args": [{
                "channel": "vscode:sandbox::main-invoke-claimCheckinCredits",
                "params": []
            }]
        }, separators=(',', ':'))
        ws_send_frame(sock, test_msg)
        resp = ws_recv_frame(sock, timeout=2)
        if resp:
            print(f"  Method '{method}': {resp[:200]}")

    sock.close()
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
