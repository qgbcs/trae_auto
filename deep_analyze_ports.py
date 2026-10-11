#!/usr/bin/env python3
"""
深入分析端口 62900 和 51000
尝试 WebSocket 和 VSCode IPC 协议
"""

import json
import time
import socket
import struct
import hashlib
import base64
import sys

def run_cmd(cmd):
    import subprocess
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_pid_for_port(port):
    """获取监听端口的 PID"""
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

def ws_handshake(port, path='/'):
    """尝试 WebSocket 握手"""
    key = base64.b64encode(bytes(range(16))).decode()
    GUID = "258EAFA5-E914-47DA-95CA-5AB5DC10BE69"

    sock = socket.create_connection(('127.0.0.1', port), timeout=5)

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

    response = b''
    try:
        sock.settimeout(3)
        while b'\r\n\r\n' not in response:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    except socket.timeout:
        pass

    sock.close()
    return response

def test_vscode_ipc_channel(port, channel, param=None):
    """测试 VSCode IPC 通道调用"""
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=5)

        # VSCode IPC 协议格式
        # 每个消息: 4字节大端长度 + JSON消息
        # hello 消息: {"rid":0,"method":"hello","args":[...]}
        # invoke 消息: {"rid":N,"method":"vscode:xxx","args":[...]}

        # 发送 hello
        hello = json.dumps({
            "rid": 0,
            "method": "hello",
            "args": [{
                "profileName": "vscode",
                "transport": "socket",
                "ags": []
            }]
        }, separators=(',', ':')).encode('utf-8')

        header = struct.pack('>I', len(hello))
        sock.sendall(header + hello)
        time.sleep(0.5)

        # 清空响应缓冲区
        sock.settimeout(0.1)
        try:
            while True:
                sock.recv(4096)
        except:
            pass

        # 发送 invoke
        invoke_params = [param] if param else []
        invoke = json.dumps({
            "rid": 1,
            "method": channel,
            "args": invoke_params
        }, separators=(',', ':')).encode('utf-8')

        header = struct.pack('>I', len(invoke))
        sock.sendall(header + invoke)
        time.sleep(1)

        # 读取响应
        sock.settimeout(2)
        response = b''
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if len(chunk) < 4096:
                    break
        except socket.timeout:
            pass
        sock.close()

        if response:
            # 尝试解析
            try:
                # 去掉长度前缀
                if len(response) >= 4:
                    msg_len = struct.unpack('>I', response[:4])[0]
                    msg = response[4:4+msg_len]
                    return json.loads(msg.decode('utf-8', errors='replace'))
            except:
                pass
            return response.decode('utf-8', errors='replace')
        return None
    except Exception as e:
        return f"Error: {e}"

def test_socket_raw(port):
    """测试原始 socket 数据"""
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=3)
        # 发送一些试探数据
        test_msgs = [
            b'GET /json HTTP/1.1\r\nHost: localhost\r\n\r\n',
            b'{"rid":0,"method":"hello"}',
            b'\x00\x00\x00\x1a{"rid":0,"method":"hello"}',
        ]
        for i, msg in enumerate(test_msgs):
            sock.sendall(msg)
            time.sleep(0.5)
            sock.settimeout(1)
            try:
                resp = sock.recv(4096)
                if resp:
                    print(f"  测试{i+1}: 收到 {len(resp)} 字节")
                    print(f"    内容: {resp[:100]}")
            except socket.timeout:
                pass
        sock.close()
    except Exception as e:
        print(f"  原始测试失败: {e}")

def main():
    print("=" * 60)
    print("端口深度分析")
    print("=" * 60)

    # 1. 分析端口 62900
    print("\n[1] 分析端口 62900...")
    pid_62900 = get_pid_for_port(62900)
    print(f"  监听 PID: {pid_62900}")

    # WebSocket 握手测试
    print("\n  测试 WebSocket 握手...")
    for path in ['/', '/json', '/devtools/page', '/ws']:
        resp = ws_handshake(62900, path)
        if resp:
            print(f"  Path '{path}': {resp[:200]}")

    # 2. 分析端口 51000
    print("\n[2] 分析端口 51000...")
    pid_51000 = get_pid_for_port(51000)
    print(f"  监听 PID: {pid_51000}")

    # 尝试不同的协议
    print("\n  测试各种协议...")
    test_socket_raw(51000)

    # VSCode IPC 测试
    print("\n  测试 VSCode IPC...")
    channels = [
        'vscode:sandbox::main-invoke-claimCheckinCredits',
        'vscode:claimCheckinCredits',
        'hello',
    ]
    for channel in channels:
        resp = test_vscode_ipc_channel(51000, channel)
        if resp and not str(resp).startswith('Error'):
            print(f"  Channel '{channel}': {resp}")
        else:
            print(f"  Channel '{channel}': 无响应或错误")

    # 3. 分析其他端口
    print("\n[3] 分析端口 3445, 4445...")
    for port in [3445, 4445]:
        pid = get_pid_for_port(port)
        print(f"  Port {port}: PID={pid}")
        resp = ws_handshake(port, '/')
        if resp and b'101' in resp:
            print(f"    -> WebSocket 升级成功!")
        elif resp:
            print(f"    -> 响应: {resp[:100]}")

    # 4. 列出所有监听端口的 PID
    print("\n[4] 所有监听端口...")
    cmd = 'netstat -ano | findstr LISTENING | findstr 127.0.0.1'
    stdout = run_cmd(cmd)
    for line in stdout.split('\n'):
        parts = line.strip().split()
        if len(parts) >= 5:
            port = parts[1].split(':')[-1]
            pid = parts[-1]
            print(f"  Port {port}: PID {pid}")

    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
