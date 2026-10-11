"""
尝试通过端口51000发送IPC签到消息
Electron管理端口协议分析
"""
import socket
import json
import struct
import sys
sys.stdout.reconfigure(encoding='utf-8')

PORT = 51000

def send_message(sock, method, params=None, msg_id=1):
    """发送JSON-RPC消息到端口51000"""
    msg = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": method,
        "params": params or {}
    }
    data = json.dumps(msg).encode('utf-8')
    # 发送长度前缀 + 数据
    length = len(data)
    sock.sendall(struct.pack('>I', length) + data)
    print(f"[+] 发送消息: {method}")
    print(f"[+] 数据长度: {length}")

def test_protocol():
    """测试端口51000的协议"""
    try:
        sock = socket.create_connection(('127.0.0.1', PORT), timeout=5)
        sock.settimeout(3)
        print(f"[+] 连接到端口 {PORT}")

        # 尝试发送不同的消息格式

        # 1. 简单的ping测试
        print("\n=== 测试1: 简单ping ===")
        send_message(sock, "ping")
        try:
            resp = sock.recv(4096)
            print(f"[-] 响应: {resp[:200]}")
        except socket.timeout:
            print("[-] 无响应或超时")

        # 2. 尝试获取积分信息
        print("\n=== 测试2: 查询积分状态 ===")
        send_message(sock, "vscode:getCreditsStatus")
        try:
            resp = sock.recv(4096)
            print(f"[-] 响应: {resp[:500]}")
        except socket.timeout:
            print("[-] 无响应或超时")

        # 3. 尝试发送签到请求
        print("\n=== 测试3: 发送签到请求 ===")
        send_message(sock, "vscode:sandbox::main-invoke-claimCheckinCredits")
        try:
            resp = sock.recv(4096)
            print(f"[-] 响应: {resp[:500]}")
        except socket.timeout:
            print("[-] 无响应或超时")

        # 4. 尝试IPC格式
        print("\n=== 测试4: IPC格式签到 ===")
        msg = json.dumps({
            "id": 1,
            "method": "vscode:sandbox::main-invoke-claimCheckinCredits",
            "args": []
        }).encode()
        sock.sendall(struct.pack('>I', len(msg)) + msg)
        try:
            resp = sock.recv(4096)
            print(f"[-] 响应: {resp[:500]}")
        except socket.timeout:
            print("[-] 无响应或超时")

        sock.close()

    except ConnectionRefusedError:
        print(f"[-] 端口 {PORT} 未被监听")
    except Exception as e:
        print(f"[-] 错误: {e}")

if __name__ == '__main__':
    test_protocol()
