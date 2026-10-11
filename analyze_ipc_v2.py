#!/usr/bin/env python3
"""
分析 Trae CN 的 IPC 通信机制
1. 尝试不同的端口和协议
2. 探索 VSCode IPC over socket
3. 寻找 CDP/调试端口
"""

import json
import time
import socket
import struct
import sys
import win32gui
import win32process
import subprocess
import os

TRAJE_APP_PATH = r"D:\Trae CN\resources\app"

def run_cmd(cmd):
    """运行命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def find_trae_process():
    """查找 Trae 进程"""
    stdout, _, _ = run_cmd('powershell -Command "Get-Process -Name \\\"Trae CN\\\" | Select-Object Id, StartTime | ConvertTo-Json"')
    print("Trae 进程:")
    try:
        data = json.loads(stdout)
        if isinstance(data, list):
            for p in data:
                print(f"  PID={p['Id']}, Started={p['StartTime']}")
        else:
            print(f"  PID={data['Id']}, Started={data['StartTime']}")
    except:
        print(stdout[:500])

def get_process_cmdline(pid):
    """获取进程命令行"""
    cmd = f'powershell -Command "(Get-CimInstance -ClassName Win32_Process -Filter \\\"ProcessId={pid}\\\" -ErrorAction SilentlyContinue).CommandLine" 2>$null'
    stdout, _, _ = run_cmd(cmd)
    return stdout

def test_port(port, timeout=2):
    """测试端口连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            print(f"  Port {port}: OPEN")
            return sock
        sock.close()
    except:
        pass
    return None

def test_cdp_http(port, path):
    """测试 CDP HTTP 端点"""
    try:
        url = f"http://127.0.0.1:{port}{path}"
        sock = socket.create_connection(('127.0.0.1', port), timeout=3)
        sock.sendall(f"GET {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode())
        data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        sock.close()
        return data.decode('utf-8', errors='replace')
    except Exception as e:
        return None

def test_vscode_ipc_hello(port):
    """测试 VSCode IPC Hello 消息"""
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=3)

        # VSCode IPC hello 消息
        hello = {
            "rid": 0,
            "method": "hello",
            "args": [{
                "profileName": "vscode",
                "transport": "socket",
                "ags": []
            }]
        }
        msg = json.dumps(hello, separators=(',', ':')).encode('utf-8')
        # VSCode IPC 格式: 4字节大端长度前缀 + 消息
        header = struct.pack('>I', len(msg))
        sock.sendall(header + msg)

        time.sleep(1)
        response = sock.recv(4096)
        sock.close()
        return response
    except Exception as e:
        return f"Error: {e}"

def test_vscode_ipc_call(port, method, params=None):
    """测试 VSCode IPC 调用"""
    try:
        sock = socket.create_connection(('127.0.0.1', port), timeout=5)

        # 先发送 hello
        hello = {
            "rid": 0,
            "method": "hello",
            "args": [{"profileName": "vscode", "transport": "socket", "ags": []}]
        }
        msg = json.dumps(hello, separators=(',', ':')).encode('utf-8')
        header = struct.pack('>I', len(msg))
        sock.sendall(header + msg)
        time.sleep(0.5)

        # 读取 hello 响应
        resp_data = b''
        try:
            sock.settimeout(1)
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp_data += chunk
                if len(chunk) < 4096:
                    break
        except socket.timeout:
            pass

        # 发送 invoke 消息
        if params is None:
            params = {}

        invoke = {
            "rid": 1,
            "method": method,
            "args": [params]
        }
        msg = json.dumps(invoke, separators=(',', ':')).encode('utf-8')
        header = struct.pack('>I', len(msg))
        sock.sendall(header + msg)

        time.sleep(1)
        response = b''
        try:
            sock.settimeout(2)
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
        return response
    except Exception as e:
        return f"Error: {e}"

def list_named_pipes():
    """列出命名管道"""
    cmd = r'''powershell -Command "Get-ChildItem '\\.\pipe\' -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'vscode|ipc|trae|electron' } | Select-Object -ExpandProperty Name"'''
    stdout, _, _ = run_cmd(cmd)
    print("命名管道:")
    for line in stdout.split('\n'):
        line = line.strip()
        if line:
            print(f"  {line}")
    return stdout

def analyze_storage_json():
    """分析 storage.json 中的签到信息"""
    storage_path = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
    try:
        with open(storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        icube_raw = data.get('iCubeServerData://icube.cloudide', '{}')
        icube_data = json.loads(icube_raw)

        activities = icube_data.get('commercialActivityInfo', {}).get('activities', [])
        for act in activities:
            if act.get('activityId') == 'checkin_credits':
                extra = act.get('workExtra', {})
                print(f"\n[签到活动] activityId: checkin_credits")
                print(f"  grantable: {extra.get('grantable')}")
                print(f"  granted: {extra.get('granted')}")
                print(f"  work_credits: {extra.get('work_credits')}")
                return extra
    except Exception as e:
        print(f"读取 storage.json 失败: {e}")
    return None

def main():
    print("=" * 60)
    print("Trae CN IPC 分析 v2")
    print("=" * 60)

    # 1. 分析 storage.json
    print("\n[1] 分析 storage.json...")
    extra = analyze_storage_json()

    # 2. 查找进程
    print("\n[2] 查找 Trae 进程...")
    find_trae_process()

    # 3. 列出命名管道
    print("\n[3] 列出命名管道...")
    list_named_pipes()

    # 4. 检查端口
    print("\n[4] 检查监听端口...")
    ports_to_check = [51000, 62900, 3445, 4445, 11845, 8384]
    for port in ports_to_check:
        sock = test_port(port)
        if sock:
            print(f"  Port {port} 已连接")
            # 测试是否是 CDP
            cdp_resp = test_cdp_http(port, '/json')
            if cdp_resp and 'devtoolsFrontendUrl' in cdp_resp:
                print(f"    -> 这是 CDP 端口!")
                print(f"    -> 响应: {cdp_resp[:200]}...")
            else:
                print(f"    -> CDP 测试失败，可能是 VSCode IPC 端口")
                # 测试 VSCode IPC
                ipc_resp = test_vscode_ipc_hello(port)
                print(f"    -> VSCode IPC 响应: {ipc_resp[:200] if ipc_resp else 'None'}")
            sock.close()

    # 5. 尝试扫描更多端口
    print("\n[5] 扫描 9222-9231 (CDP 默认端口)...")
    cdp_found = False
    for port in range(9222, 9232):
        cdp_resp = test_cdp_http(port, '/json')
        if cdp_resp and 'devtoolsFrontendUrl' in cdp_resp:
            print(f"  找到 CDP 端口: {port}")
            print(f"  响应: {cdp_resp[:500]}...")
            cdp_found = True
            break

    if not cdp_found:
        print("  未在 9222-9231 范围内找到 CDP 端口")

    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
