#!/usr/bin/env python3
"""
深入调试端口62900的WebSocket协议
"""

import socket
import time
import json
import struct
import hashlib
import base64
import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout.strip()

def get_pid_for_port(port):
    cmd = f'netstat -ano | findstr :{port}'
    stdout = run_cmd(cmd)
    for line in stdout.split('\n'):
        if 'LISTENING' in line:
            parts = line.strip().split()
            if len(parts) >= 5:
                try:
                    return int(parts[-1])
                except:
                    pass
    return None

def ws_handshake(sock, key, path='/'):
    """发送WebSocket握手请求"""
    GUID = "258EAFA5-E914-47DA-95CA-5AB5DC10BE69"

    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: 127.0.0.1:62900\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    sock.sendall(request.encode())

    response = b''
    sock.settimeout(3)
    while b'\r\n\r\n' not in response:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    return response

def ws_send(sock, data, opcode=0x1):
    """发送WebSocket帧"""
    data = data.encode('utf-8') if isinstance(data, str) else data
    length = len(data)

    frame = bytearray([0x80 | opcode])
    masking_key = bytes([0x12, 0x34, 0x56, 0x78])
    frame.extend(masking_key)

    if length < 126:
        frame.append(length | 0x80)
    elif length < 65536:
        frame.append(126 | 0x80)
        frame.extend(struct.pack('>H', length))
    else:
        frame.append(127 | 0x80)
        frame.extend(struct.pack('>Q', length))

    masked_data = bytearray(length)
    for i in range(length):
        masked_data[i] = data[i] ^ masking_key[i % 4]
    frame.extend(masked_data)

    sock.sendall(frame)

def ws_recv(sock, timeout=3):
    """接收WebSocket帧"""
    sock.settimeout(timeout)
    result = bytearray()

    while True:
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

        masking_key = b''
        if is_masked:
            while len(masking_key) < 4:
                chunk = sock.recv(4 - len(masking_key))
                if not chunk:
                    return None
            masking_key += chunk

        data = b''
        while len(data) < length:
            chunk = sock.recv(min(4096, length - len(data)))
            if not chunk:
                return None
            data += chunk

        if is_masked:
            data = bytes(b ^ masking_key[i % 4] for i, b in enumerate(data))

        if opcode == 0x8:
            return None
        if opcode == 0x9:
            frame = bytearray([0x8A])
            if length > 0:
                frame.extend(data)
            sock.sendall(frame)
            continue
        if opcode == 0xA:
            continue

        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data

def main():
    print("=" * 70)
    print("端口62900 WebSocket深度调试")
    print("=" * 70)

    port = 62900
    pid = get_pid_for_port(port)
    print(f"\n[1] 端口 {port} 监听 PID: {pid}")

    # 获取进程命令行
    if pid:
        cmd_line = run_cmd(f'powershell -Command "(Get-CimInstance -ClassName Win32_Process -Filter \'ProcessId={pid}\').CommandLine" 2>$null')
        print(f"    命令行: {cmd_line[:200]}...")

    # 测试不同的WebSocket路径
    print("\n[2] 测试不同的WebSocket路径:")
    paths = ['/', '/json', '/devtools/page', '/ws', '/websocket', '/inspector', '/devtools']

    for path in paths:
        try:
            sock = socket.create_connection(('127.0.0.1', port), timeout=3)
            key = base64.b64encode(bytes(range(16))).decode()
            response = ws_handshake(sock, key, path)
            sock.close()

            if b'101 Switching Protocols' in response:
                print(f"  Path '{path}': WebSocket握手成功!")
            elif b'400' in response:
                print(f"  Path '{path}': 400 Bad Request")
                print(f"    响应: {response[:200]}")
            else:
                print(f"  Path '{path}': {response[:100]}")
        except Exception as e:
            print(f"  Path '{path}': 错误 - {e}")

    # 尝试不标准的路径格式
    print("\n[3] 测试自定义WebSocket路径:")
    custom_paths = [
        '/vscode/ipc',
        '/vscode-ipc',
        '/electron-ipc',
        '/trace',
        '/json.list',
        '/json/version',
    ]

    for path in custom_paths:
        try:
            sock = socket.create_connection(('127.0.0.1', port), timeout=2)
            # 先发送HTTP请求看响应
            sock.sendall(f"GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n\r\n".encode())
            time.sleep(0.5)
            sock.settimeout(1)
            resp = sock.recv(1024)
            print(f"  Path '{path}': {resp[:150]}")
            sock.close()
        except Exception as e:
            print(f"  Path '{path}': {e}")

    # 尝试连接并发送原始数据（非WebSocket）
    print("\n[4] 测试原始TCP连接:")
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=3)
        sock.settimeout(2)

        # 发送各种试探数据
        test_data = [
            b'ping',
            b'hello',
            b'{"method":"ping"}',
            b'\x00\x00\x00\x0a{"ping":1}',
        ]

        for i, data in enumerate(test_data):
            sock.sendall(data)
            time.sleep(0.5)
            try:
                resp = sock.recv(4096)
                print(f"  测试{i+1}: 收到 {len(resp)} 字节: {resp[:100]}")
            except socket.timeout:
                print(f"  测试{i+1}: 无响应")

        sock.close()
    except Exception as e:
        print(f"  原始TCP错误: {e}")

    # 尝试获取进程详细信息
    print("\n[5] 进程详细信息:")
    if pid:
        cmd = f'wmic process where "ProcessId={pid}" get CommandLine,Name,ExecutablePath /format:list'
        stdout = run_cmd(cmd)
        print(stdout[:500])

    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
