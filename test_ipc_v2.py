"""
通过端口51000发送正确的IPC签到消息
Electron使用自定义二进制协议
"""
import socket
import json
import struct
import sys
sys.stdout.reconfigure(encoding='utf-8')

PORT = 51000

def send_ipc_message(sock, method, params=None):
    """发送IPC消息 - 使用vscode IPC格式"""
    # vscode IPC消息格式: [长度][JSON数据]
    msg = {
        "id": 1,
        "method": method,
        "params": params or {}
    }
    data = json.dumps(msg).encode('utf-8')
    # 发送4字节长度前缀 + 数据
    sock.sendall(struct.pack('>I', len(data)) + data)
    print(f"[+] 发送: {method}")
    print(f"[+] 数据: {msg}")

def main():
    try:
        sock = socket.create_connection(('127.0.0.1', PORT), timeout=5)
        sock.settimeout(3)
        print(f"[+] 连接到端口 {PORT}\n")

        # 测试1: 先发送ping保持连接
        print("=== 测试1: Ping ===")
        ping_msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}).encode()
        sock.sendall(struct.pack('>I', len(ping_msg)) + ping_msg)
        try:
            resp = sock.recv(1024)
            print(f"[-] 响应: {resp[:100]}")
        except socket.timeout:
            print("[-] 无响应")

        # 测试2: 尝试调用签到方法
        print("\n=== 测试2: 发送签到请求 ===")
        send_ipc_message(sock, "vscode:sandbox::main-invoke-claimCheckinCredits", {})

        # 尝试读取响应
        try:
            resp = sock.recv(4096)
            print(f"[-] 响应: {resp[:500]}")
        except socket.timeout:
            print("[-] 无响应或超时")

        # 测试3: 尝试获取积分状态
        print("\n=== 测试3: 获取积分状态 ===")
        send_ipc_message(sock, "vscode:sandbox::main-getCreditsInfo", {})
        try:
            resp = sock.recv(4096)
            print(f"[-] 响应: {resp[:500]}")
        except socket.timeout:
            print("[-] 无响应或超时")

        sock.close()
        print("\n[!] 测试完成")

    except ConnectionRefusedError:
        print(f"[-] 端口 {PORT} 未被监听")
    except Exception as e:
        print(f"[-] 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
