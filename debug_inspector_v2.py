"""
Trae CN 签到 - Node.js Inspector深度调试
通过Inspector协议执行JavaScript代码来调用签到
"""
import asyncio
import json
import time
import urllib.request
import websocket
import subprocess
import sys

# 配置
INSPECTOR_PORT = 62900
MANAGEMENT_PORT = 51000
STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"


def read_storage():
    """读取storage.json"""
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            icube_data = data.get('icube', {}).get('data', {})
            if icube_data:
                store_key = list(icube_data.keys())[0]
                return json.loads(icube_data[store_key])
    except Exception as e:
        print(f"读取storage失败: {e}")
    return None


def write_storage(activity_data):
    """写入storage.json"""
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        icube_data = data.get('icube', {}).get('data', {})
        if icube_data:
            store_key = list(icube_data.keys())[0]
            data['icube']['data'][store_key] = json.dumps(activity_data)

        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✓ 已更新storage.json")
        return True
    except Exception as e:
        print(f"写入storage失败: {e}")
        return False


async def test_inspector_connection():
    """测试Inspector连接"""
    print(f"\n=== 测试Inspector连接 (端口{INSPECTOR_PORT}) ===")

    ws_url = f"ws://127.0.0.1:{INSPECTOR_PORT}"
    print(f"连接URL: {ws_url}")

    try:
        ws = websocket.create_connection(ws_url, timeout=10)
        print("✓ Inspector连接成功")

        # 测试简单命令
        test_messages = [
            {"id": 1, "method": "Runtime.evaluate", "params": {"expression": "process.version"}},
            {"id": 2, "method": "Runtime.evaluate", "params": {"expression": "require('electron').ipcMain"}},
        ]

        for msg in test_messages:
            ws.send(json.dumps(msg))
            result = ws.recv()
            print(f"  命令{msg['id']}响应: {result[:200]}...")

        ws.close()
        return True

    except Exception as e:
        print(f"✗ Inspector连接失败: {e}")
        return False


async def test_management_port():
    """测试管理端口"""
    print(f"\n=== 测试管理端口 ({MANAGEMENT_PORT}) ===")

    try:
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', MANAGEMENT_PORT))
        print("✓ 管理端口连接成功")

        # 尝试不同的消息格式
        probes = [
            b'getClients',
            b'listTargets',
            b'{"command":"getClients"}',
            b'\x00\x00\x00\x0bgetClients\x00',
        ]

        for i, probe in enumerate(probes):
            try:
                sock.sendall(probe)
                time.sleep(0.5)
                response = sock.recv(512)
                print(f"  探测{i+1}: 收到 {len(response)} 字节")
                if response:
                    # 尝试解码
                    try:
                        text = response.decode('utf-8', errors='ignore')
                        print(f"    内容: {text[:100]}")
                    except:
                        print(f"    二进制: {response[:50].hex()}")
            except Exception as e:
                print(f"  探测{i+1}错误: {e}")

        sock.close()
        return True

    except Exception as e:
        print(f"✗ 管理端口连接失败: {e}")
        return False


async def check_process_status():
    """检查进程状态"""
    print("\n=== 检查Trae进程 ===")

    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq TraeCN.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, shell=True
        )

        pids = []
        for line in result.stdout.strip().split('\n')[1:]:
            if line:
                parts = line.split('","')
                pid = parts[0].replace('"', '')
                pids.append(pid)
                print(f"  PID: {pid}")

        return pids
    except Exception as e:
        print(f"获取进程失败: {e}")
        return []


def main():
    print("=" * 60)
    print("Trae CN 签到 - Inspector调试")
    print("=" * 60)

    # 1. 检查当前状态
    print("\n=== 当前签到状态 ===")
    status = read_storage()
    if status:
        work_extra = status.get('workExtra', {})
        print(f"活动ID: {status.get('activityId')}")
        print(f"work_credits: {work_extra.get('work_credits')}")
        print(f"granted: {work_extra.get('granted')}")
        print(f"grantable: {work_extra.get('grantable')}")
    else:
        print("无法读取签到状态")

    # 2. 检查进程
    pids = asyncio.run(check_process_status())
    if not pids:
        print("\n✗ 没有找到Trae进程，请先启动Trae CN")
        return

    # 3. 测试Inspector
    inspector_ok = asyncio.run(test_inspector_connection())

    # 4. 测试管理端口
    mgmt_ok = asyncio.run(test_management_port())

    print("\n" + "=" * 60)
    if inspector_ok:
        print("✓ Inspector连接可用")
    if mgmt_ok:
        print("✓ 管理端口连接可用")
    if not inspector_ok and not mgmt_ok:
        print("等待重新连接...")
    print("=" * 60)


if __name__ == "__main__":
    main()
