#!/usr/bin/env python3
"""
Trae CN IPC 接口深度调试
目标: 通过IPC调用完成签到
"""

import json
import time
import socket
import struct
import hashlib
import base64
import subprocess
import sys
from pathlib import Path

# 路径配置
STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'

def run_cmd(cmd):
    """运行命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def get_credits():
    """获取当前积分"""
    try:
        data = json.loads(STORAGE_JSON.read_text())
        icube = data.get('iCubeServerData://icube.cloudide', {})
        if isinstance(icube, str):
            icube = json.loads(icube)
        commercial = icube.get('commercialActivityInfo', {})
        activities = commercial.get('activities', [])
        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                work_extra = act.get('workExtra', {})
                return {
                    'credits': work_extra.get('work_credits', 0),
                    'granted': work_extra.get('granted', False),
                    'grantable': work_extra.get('grantable', False)
                }
    except Exception as e:
        print(f"读取积分失败: {e}")
    return None

def find_trae_pids():
    """查找Trae进程"""
    cmd = r'powershell -Command "Get-Process -Name Trae* -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime | ConvertTo-Json"'
    stdout, _, _ = run_cmd(cmd)
    pids = []
    try:
        data = json.loads(stdout)
        if isinstance(data, list):
            pids = [p['Id'] for p in data]
        elif isinstance(data, dict):
            pids = [data['Id']]
    except:
        pass
    return pids

def get_process_details(pid):
    """获取进程详细信息"""
    cmd = f'powershell -Command "(Get-CimInstance -ClassName Win32_Process -Filter \'ProcessId={pid}\').CommandLine" 2>$null'
    stdout, _, _ = run_cmd(cmd)
    return stdout

def get_listening_ports(pid):
    """获取进程监听的端口"""
    cmd = f'netstat -ano | findstr {pid}'
    stdout, _, _ = run_cmd(cmd)
    ports = []
    for line in stdout.split('\n'):
        if 'LISTENING' in line:
            parts = line.split()
            if len(parts) >= 5:
                addr = parts[1]
                if ':' in addr:
                    port = int(addr.split(':')[-1])
                    ports.append(port)
    return sorted(set(ports))

def test_socket_protocol(port, messages, desc=""):
    """测试socket协议"""
    print(f"\n  测试端口 {port} ({desc})...")
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=3)
        sock.settimeout(2)

        for i, msg in enumerate(messages):
            if isinstance(msg, dict):
                msg = json.dumps(msg, separators=(',', ':'))
            if isinstance(msg, str):
                msg = msg.encode('utf-8')

            # 尝试带长度前缀
            header = struct.pack('>I', len(msg))
            sock.sendall(header + msg)
            time.sleep(0.3)

            # 尝试读取响应
            try:
                response = sock.recv(4096)
                if response:
                    print(f"    消息{i+1}: 收到 {len(response)} 字节")
                    try:
                        # 尝试解析JSON
                        if len(response) >= 4:
                            msg_len = struct.unpack('>I', response[:4])[0]
                            json_data = json.loads(response[4:4+msg_len])
                            print(f"      JSON: {json.dumps(json_data, indent=2)[:200]}")
                    except:
                        print(f"      原始: {response[:100]}")
            except socket.timeout:
                pass

        sock.close()
        return True
    except Exception as e:
        print(f"    错误: {e}")
        return False

def test_websocket_connection(port, path='/'):
    """测试WebSocket连接"""
    print(f"\n  测试WebSocket端口 {port}...")
    try:
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
        sock.settimeout(3)
        while b'\r\n\r\n' not in response:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

        if b'101 Switching Protocols' in response:
            print(f"    WebSocket握手成功!")
            return sock
        else:
            print(f"    握手失败: {response[:200]}")
            sock.close()
            return None
    except Exception as e:
        print(f"    WebSocket错误: {e}")
        return None

def ws_send_frame(sock, data, opcode=0x1):
    """发送WebSocket帧"""
    data = data.encode('utf-8') if isinstance(data, str) else data
    length = len(data)

    frame = bytearray([0x80 | opcode])
    masking_key = bytes([0x00, 0x01, 0x02, 0x03])  # 固定掩码便于调试
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

def ws_recv_frame(sock, timeout=3):
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

        if opcode == 0x8:  # Close
            return None
        if opcode == 0x9:  # Ping
            frame = bytearray([0x8A])
            if length > 0:
                frame.extend(data)
            sock.sendall(frame)
            continue
        if opcode == 0xA:  # Pong
            continue

        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            return data

def try_ipc_via_websocket(port):
    """尝试通过WebSocket发送IPC消息"""
    print(f"\n[尝试WebSocket IPC - 端口 {port}]")
    sock = test_websocket_connection(port)
    if not sock:
        return False

    try:
        # 发送hello
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

        # 读取响应
        resp = ws_recv_frame(sock, timeout=2)
        if resp:
            print(f"  Hello响应: {resp[:300]}")

        # 尝试不同的channel名称
        channels = [
            'vscode:sandbox::main-invoke-claimCheckinCredits',
            'vscode:sandbox::main-invoke-fetchCheckinCreditsStatus',
            'claimCheckinCredits',
            'fetchCheckinCreditsStatus',
        ]

        for i, channel in enumerate(channels):
            invoke = {
                "rid": i + 1,
                "method": channel,
                "args": [{}]
            }
            ws_send_frame(sock, json.dumps(invoke, separators=(',', ':')))

            resp = ws_recv_frame(sock, timeout=3)
            if resp:
                print(f"  通道 '{channel}': {resp[:300]}")
            else:
                print(f"  通道 '{channel}': 无响应")

        sock.close()
        return True
    except Exception as e:
        print(f"  WebSocket IPC错误: {e}")
        try:
            sock.close()
        except:
            pass
        return False

def try_named_pipe():
    """尝试命名管道"""
    print("\n[尝试命名管道]")
    try:
        import win32file
        import win32con

        pipe_patterns = [
            'vscode-ipc-',
            'vscode-shared-',
            'trae-ipc-',
        ]

        # 列出所有管道
        cmd = r'powershell -Command "Get-ChildItem \'\\\\.\\pipe\\\' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name"'
        stdout, _, _ = run_cmd(cmd)

        pipes = []
        for line in stdout.split('\n'):
            line = line.strip()
            if line:
                pipes.append(line)

        print(f"  发现管道: {len(pipes)} 个")
        for pipe in pipes[:20]:
            print(f"    {pipe}")

        # 尝试连接可能的Trae管道
        for pattern in pipe_patterns:
            for pipe in pipes:
                if pattern in pipe.lower():
                    try:
                        hPipe = win32file.CreateFile(
                            rf'\\.\pipe\{pipe}',
                            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                            0, None, win32file.OPEN_EXISTING, 0, None
                        )
                        print(f"  成功连接管道: {pipe}")
                        win32file.CloseHandle(hPipe)
                        return True
                    except Exception as e:
                        pass
        return False
    except ImportError:
        print("  缺少 pywin32 库")
        return False

def analyze_all():
    """全面分析"""
    print("=" * 70)
    print("Trae CN IPC 接口深度调试")
    print("=" * 70)

    # 1. 获取当前积分
    print("\n[1] 当前积分状态:")
    credits = get_credits()
    if credits:
        print(f"  积分: {credits['credits']}")
        print(f"  已签到: {credits['granted']}")
        print(f"  可签到: {credits['grantable']}")
    else:
        print("  无法读取积分信息")

    # 2. 查找Trae进程
    print("\n[2] Trae 进程:")
    pids = find_trae_pids()
    if pids:
        for pid in pids:
            cmd_line = get_process_details(pid)
            print(f"  PID {pid}: {cmd_line[:100]}...")
    else:
        print("  未找到Trae进程")
        return

    # 3. 分析端口
    print("\n[3] 端口分析:")
    all_ports = set()
    for pid in pids:
        ports = get_listening_ports(pid)
        all_ports.update(ports)
        print(f"  PID {pid} 监听端口: {ports[:20]}")

    # 4. 测试关键端口
    print("\n[4] 协议测试:")

    # 4.1 测试端口51000 (Electron管理端口)
    if 51000 in all_ports:
        print("\n  测试端口 51000 (Electron管理端口):")
        test_msgs = [
            {"jsonrpc": "2.0", "id": 1, "method": "ping"},
            {"rid": 0, "method": "hello", "args": [{"profileName": "vscode"}]},
        ]
        test_socket_protocol(51000, test_msgs, "Electron管理")

    # 4.2 测试端口62900 (WebSocket端口)
    if 62900 in all_ports:
        print("\n  测试端口 62900 (WebSocket端口):")
        test_websocket_connection(62900)

    # 4.3 测试其他端口
    for port in sorted(all_ports):
        if port not in [51000, 62900, 0]:
            # 尝试简单的TCP连接测试
            try:
                sock = socket.create_connection(('127.0.0.1', port), timeout=1)
                # 发送试探数据
                test_data = [
                    b'GET /json HTTP/1.1\r\nHost: localhost\r\n\r\n',
                    b'ping',
                ]
                for data in test_data:
                    sock.sendall(data)
                    time.sleep(0.2)
                    sock.settimeout(0.5)
                    try:
                        resp = sock.recv(1024)
                        if resp:
                            print(f"  端口 {port}: 收到响应 {resp[:50]}")
                    except socket.timeout:
                        pass
                sock.close()
            except:
                pass

    # 5. 尝试WebSocket IPC
    print("\n[5] WebSocket IPC尝试:")
    if 62900 in all_ports:
        try_ipc_via_websocket(62900)

    # 6. 尝试命名管道
    print("\n[6] 命名管道尝试:")
    try_named_pipe()

    print("\n" + "=" * 70)
    print("分析完成")
    print("=" * 70)

if __name__ == '__main__':
    analyze_all()
