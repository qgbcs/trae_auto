"""
直接调用Trae签到API
通过分析Electron内部IPC通道实现
"""
import json
import time
import sys
import socket
import struct
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# JWT Token
JWT_PATH = Path.home() / '.trae-cn' / 'trae-jwt-token'
token = JWT_PATH.read_text().strip() if JWT_PATH.exists() else ''
USER_ID = "3273694480187068"  # 从JWT解析

def try_vscode_channel(channel_name, args=[]):
    """尝试通过VS Code extension host IPC调用"""
    # VS Code使用named pipe或socket进行IPC
    # 在Windows上，Trae使用命名管道

    # 尝试连接到VS Code的extension host
    # 端口范围：5xxxx - 6xxxx
    for port in range(50000, 51100):
        try:
            sock = socket.create_connection(('127.0.0.1', port), timeout=1)
            sock.settimeout(2)

            # 发送VS Code IPC握手消息
            msg = json.dumps({
                "type": 1,
                "id": 0,
                "port": port,
                "value": []
            }).encode('utf-8')

            # VS Code IPC协议：先发送长度，再发送数据
            # 格式: [4字节长度][JSON消息]
            sock.sendall(struct.pack('>I', len(msg)) + msg)

            # 读取响应
            try:
                resp = sock.recv(4096)
                if resp:
                    print(f"[+] 找到IPC端口: {port}")
                    print(f"    响应: {resp[:100]}")

                    # 尝试发送IPC调用
                    ipc_msg = json.dumps({
                        "id": 1,
                        "method": channel_name,
                        "params": args
                    }).encode('utf-8')
                    sock.sendall(struct.pack('>I', len(ipc_msg)) + ipc_msg)

                    try:
                        resp = sock.recv(4096)
                        print(f"    IPC响应: {resp[:200]}")
                    except socket.timeout:
                        print("    IPC无响应")

                    sock.close()
                    return True
            except socket.timeout:
                pass
            finally:
                sock.close()
        except (ConnectionRefusedError, OSError):
            continue

    return False

def try_management_port():
    """尝试通过管理端口51000发送请求"""
    try:
        sock = socket.create_connection(('127.0.0.1', 51000), timeout=3)
        sock.settimeout(2)

        # 管理端口响应的是自定义二进制协议
        # 尝试不同的消息格式

        # 格式1: JSON-RPC
        msgs = [
            # JSON-RPC 2.0
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}).encode(),
            # VS Code IPC
            json.dumps({"type": 1, "id": 0, "port": 51000, "value": []}).encode(),
            # 简单的ping
            b"ping",
        ]

        for i, msg in enumerate(msgs):
            try:
                sock.sendall(struct.pack('>I', len(msg)) + msg)
                resp = sock.recv(1024)
                print(f"[+] 消息{i+1}响应: {resp[:50].hex()}")
            except Exception as e:
                print(f"[-] 消息{i+1}错误: {e}")
                break

        sock.close()
        return True
    except Exception as e:
        print(f"[-] 管理端口错误: {e}")
        return False

def main():
    print("="*60)
    print("尝试直接调用Trae签到API")
    print("="*60)

    print(f"\n[+] JWT: {token[:30]}...")
    print(f"[+] User ID: {USER_ID}")

    # 尝试1: 管理端口
    print("\n[步骤1] 测试管理端口51000...")
    try_management_port()

    # 尝试2: VS Code IPC通道
    print("\n[步骤2] 扫描VS Code IPC端口...")
    channels = [
        "vscode:sandbox::main-invoke-claimCheckinCredits",
        "vscode:claimCheckinCredits",
    ]

    for channel in channels:
        print(f"\n[>] 尝试通道: {channel}")
        try_vscode_channel(channel, [{"activityId": "checkin_credits"}])
        time.sleep(0.5)

    print("\n" + "="*60)
    print("结论: 端口51000是Electron管理端口，不是HTTP服务")
    print("直接调用IPC需要更深入的协议分析")
    print("="*60)

if __name__ == '__main__':
    main()
