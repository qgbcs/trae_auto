"""
深入分析端口51000的协议
尝试找到正确的IPC调用方式
"""
import socket
import struct
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

PORT = 51000

def analyze_response(data):
    """分析响应数据"""
    print(f"  原始数据 ({len(data)} bytes): {data.hex()}")
    print(f"  ASCII: {data[:50]}")

    # 尝试解析为JSON
    try:
        # 跳过可能的长度前缀
        if len(data) >= 4:
            length = struct.unpack('>I', data[:4])[0]
            print(f"  长度前缀: {length}")
            if length < len(data):
                json_data = data[4:length+4]
                print(f"  JSON数据: {json_data}")
                try:
                    parsed = json.loads(json_data)
                    print(f"  解析结果: {parsed}")
                except:
                    pass
    except:
        pass

def send_message(sock, data):
    """发送消息"""
    print(f"\n[发送] 数据 ({len(data)} bytes):")
    sock.sendall(struct.pack('>I', len(data)) + data)
    print(f"  hex: {data.hex()}")

def main():
    print("="*60)
    print("端口51000协议分析")
    print("="*60)

    try:
        sock = socket.create_connection(('127.0.0.1', PORT), timeout=5)
        sock.settimeout(3)
        print(f"\n[+] 连接到端口 {PORT}")

        # 测试不同的消息格式
        tests = [
            # 1. JSON-RPC ping
            (b"jsonrpc_ping", json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"}).encode()),

            # 2. VS Code IPC握手
            (b"vscode_ipc_handshake", json.dumps({
                "type": 1,
                "id": 0,
                "port": PORT,
                "value": []
            }).encode()),

            # 3. 简单的二进制数据
            (b"simple_binary", b"\x01\x00\x00\x00"),

            # 4. 尝试发送签到请求
            (b"checkin_request", json.dumps({
                "id": 1,
                "method": "vscode:sandbox::main-invoke-claimCheckinCredits",
                "params": [{"activityId": "checkin_credits"}]
            }).encode()),
        ]

        for name, data in tests:
            print(f"\n--- 测试: {name} ---")
            try:
                send_message(sock, data)
                resp = sock.recv(1024)
                if resp:
                    print(f"[-] 响应 ({len(resp)} bytes):")
                    analyze_response(resp)
                else:
                    print("[-] 无响应")
            except socket.timeout:
                print("[-] 超时")
            except Exception as e:
                print(f"[-] 错误: {e}")
                break

        sock.close()

    except Exception as e:
        print(f"[-] 连接错误: {e}")

if __name__ == '__main__':
    main()
