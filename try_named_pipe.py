"""
通过命名管道与Trae CN通信
Electron应用使用命名管道进行进程间通信
"""
import sys
import json
import struct
import time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

# 可能的命名管道路径
PIPE_PATHS = [
    r'\\.\pipe\vscode-channels-main',
    r'\\.\pipe\vscode-unified-channel-0',
    r'\\.\pipe\vscode-webview-main-ipc-0',
    r'\\.\pipe\vscode-ipc-0',
    r'\\.\pipe\vscode-ipc-main',
    r'\\.\pipe\vscode-shared-0',
]

def try_named_pipe(pipe_path):
    """尝试连接命名管道"""
    try:
        import win32file
        import win32pipe

        # 尝试打开管道
        handle = win32pipe.CreateFile(
            pipe_path,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )

        print(f"[+] 成功连接管道: {pipe_path}")
        return handle

    except Exception as e:
        return None

def try_socket_ipc():
    """尝试通过socket发送IPC消息"""
    import socket

    # VS Code/Trae 可能使用TCP进行IPC
    # 尝试常见的VS Code IPC端口
    for port in range(51000, 51100):
        try:
            sock = socket.create_connection(('127.0.0.1', port), timeout=2)
            sock.settimeout(1)

            # 发送VS Code IPC握手
            msg = json.dumps({
                "type": 1,
                "id": 0,
                "port": port,
                "value": []
            }).encode('utf-8')

            sock.sendall(struct.pack('>I', len(msg)) + msg)

            # 读取响应
            resp = sock.recv(1024)
            if resp:
                print(f"[+] 端口 {port} 有响应: {resp[:50].hex()}")

                # 尝试发送签到请求
                checkin_msg = json.dumps({
                    "id": 1,
                    "method": "vscode:sandbox::main-invoke-claimCheckinCredits",
                    "params": [{"activityId": "checkin_credits"}]
                }).encode('utf-8')

                sock.sendall(struct.pack('>I', len(checkin_msg)) + checkin_msg)

                try:
                    resp = sock.recv(4096)
                    print(f"    签到响应: {resp[:200].hex()}")
                    return True
                except socket.timeout:
                    print(f"    签到无响应")
                    continue

            sock.close()
        except:
            continue

    return False

def main():
    print("="*60)
    print("尝试通过命名管道/Socket IPC调用签到")
    print("="*60)

    # 1. 尝试命名管道
    print("\n[步骤1] 尝试命名管道...")
    for pipe_path in PIPE_PATHS:
        handle = try_named_pipe(pipe_path)
        if handle:
            print(f"[+] 管道 {pipe_path} 可用")
            try:
                # 尝试写入签到请求
                msg = json.dumps({
                    "channel": "vscode:sandbox::main-invoke-claimCheckinCredits",
                    "args": [{"activityId": "checkin_credits"}]
                }).encode('utf-8')
                win32file.WriteFile(handle, msg)
                print("[+] 已发送签到请求")
            except Exception as e:
                print(f"[-] 写入失败: {e}")
            finally:
                win32file.CloseHandle(handle)
        else:
            print(f"[-] 管道 {pipe_path} 不可用")

    # 2. 尝试Socket IPC
    print("\n[步骤2] 尝试Socket IPC...")
    try_socket_ipc()

    print("\n" + "="*60)

if __name__ == '__main__':
    main()
