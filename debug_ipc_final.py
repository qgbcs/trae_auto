"""
Trae CN 签到 - IPC接口深度调试
直接调用IPC方法，避免UI自动化
"""
import asyncio
import json
import time
import urllib.request
import urllib.error
import websocket
import subprocess
import sys

# 路径
STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
JWT_FILE = r"C:\Users\Administrator\.trae-cn\trae-jwt-token"
TRAEE_SOURCE = r"D:\Trae CN\resources\app\out\main.js"


def read_storage():
    """读取storage.json中的签到数据"""
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            icube_data = data.get('icube', {}).get('data', {})
            store_key = list(icube_data.keys())[0] if icube_data else None
            if store_key:
                activity_data = json.loads(icube_data[store_key])
                return activity_data
    except Exception as e:
        print(f"读取storage失败: {e}")
    return None


def get_jwt_token():
    """获取JWT Token"""
    try:
        with open(JWT_FILE, 'r') as f:
            return f.read().strip()
    except:
        return None


def analyze_source_code():
    """分析源码，找到签到实现"""
    print("\n=== 分析源码中的签到实现 ===")

    try:
        with open(TRAEE_SOURCE, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # 查找签到相关代码
        checkin_patterns = [
            'claimCheckinCredits',
            'fetchCheckinCreditsStatus',
            'checkin_credits',
            'icubeServerData',
            'SANDBOX_TO_MAIN'
        ]

        print("\n查找关键模式:")
        for pattern in checkin_patterns:
            count = content.count(pattern)
            print(f"  {pattern}: 出现 {count} 次")

        # 提取包含claimCheckinCredits的代码段
        print("\n=== claimCheckinCredits 相关代码 ===")
        idx = content.find('claimCheckinCredits')
        if idx != -1:
            start = max(0, idx - 200)
            end = min(len(content), idx + 500)
            print(content[start:end])
            print("...")

        # 查找IPC handler注册
        print("\n=== IPC Handler 注册 ===")
        handler_patterns = [
            'ipcMain.handle',
            'ipcMain.on',
            'SANDBOX_TO_MAIN_INVOKE'
        ]
        for pattern in handler_patterns:
            if pattern in content:
                idx = content.find(pattern)
                start = max(0, idx - 50)
                end = min(len(content), idx + 300)
                print(f"\n{pattern}:")
                print(content[start:end])
                print("...")

    except Exception as e:
        print(f"分析源码失败: {e}")


async def test_electron_api():
    """测试Electron内部API"""
    print("\n=== 测试Electron API ===")

    # 尝试通过端口51000发送命令
    try:
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 51000))
        print("✓ 连接到管理端口51000")

        # 尝试发送各种格式的探测消息
        probes = [
            # 简单的测试消息
            b'\x00\x00\x00\x10getClients\x00',
            # JSON格式
            b'{"command":"getClients"}',
            # 另一种Electron格式
            b'\x00Electron\x00getClients',
        ]

        for i, probe in enumerate(probes):
            try:
                sock.sendall(probe)
                time.sleep(1)
                response = sock.recv(1024)
                print(f"  探测{i+1}: 收到 {len(response)} 字节")
                if response:
                    print(f"    内容: {response[:100]}")
            except Exception as e:
                print(f"  探测{i+1}: {e}")

        sock.close()

    except Exception as e:
        print(f"Electron API测试失败: {e}")


async def test_ipc_via_process():
    """通过子进程测试IPC"""
    print("\n=== 测试IPC通过子进程 ===")

    # 创建一个临时的IPC测试脚本
    ipc_test_code = '''
const { ipcRenderer } = require('electron');

async function claimCheckin() {
    try {
        console.log('开始调用claimCheckinCredits...');
        const result = await ipcRenderer.invoke('vscode:sandbox::main-invoke-claimCheckinCredits');
        console.log('签到结果:', JSON.stringify(result));
        return result;
    } catch (error) {
        console.error('签到失败:', error);
        throw error;
    }
}

async function fetchStatus() {
    try {
        const status = await ipcRenderer.invoke('vscode:sandbox::main-invoke-fetchCheckinCreditsStatus');
        console.log('签到状态:', JSON.stringify(status));
        return status;
    } catch (error) {
        console.error('获取状态失败:', error);
        throw error;
    }
}

// 执行
(async () => {
    const status = await fetchStatus();
    if (!status || !status.hasClaimed) {
        const result = await claimCheckin();
    }
    process.exit(0);
})();
'''

    # 保存临时脚本
    test_script = r'C:\test\github\trae_auto\ipc_test_temp.js'
    with open(test_script, 'w', encoding='utf-8') as f:
        f.write(ipc_test_code)

    print(f"已创建临时IPC测试脚本: {test_script}")
    print("注意: 此脚本需要在Trae的渲染进程中运行才能访问ipcRenderer")
    print("暂时跳过，改用其他方法...")


def try_direct_api_call():
    """尝试直接API调用"""
    print("\n=== 尝试直接API调用 ===")

    token = get_jwt_token()
    if not token:
        print("无法获取JWT Token")
        return

    # 构建请求头
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # 尝试多个可能的API端点
    endpoints = [
        'https://cn-api.trae.ai/api/commercial/checkin',
        'https://cn-api.trae.ai/api/icube/checkin',
        'https://cn-api.trae.ai/api/credits/checkin',
        'https://api.trae.baidu.com/api/commercial/checkin',
    ]

    for endpoint in endpoints:
        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps({}).encode(),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode())
                print(f"✓ {endpoint}")
                print(f"  响应: {result}")
                return result
        except urllib.error.HTTPError as e:
            print(f"✗ {endpoint}: HTTP {e.code}")
        except Exception as e:
            print(f"✗ {endpoint}: {e}")

    return None


def main():
    print("=" * 60)
    print("Trae CN 签到 - IPC接口调试")
    print("=" * 60)

    # 1. 分析源码
    analyze_source_code()

    # 2. 读取当前状态
    print("\n=== 当前签到状态 ===")
    status = read_storage()
    if status:
        print(f"活动ID: {status.get('activityId')}")
        print(f"活动类型: {status.get('activityType')}")
        print(f"work_credits: {status.get('workExtra', {}).get('work_credits')}")
        print(f"granted: {status.get('workExtra', {}).get('granted')}")
        print(f"grantable: {status.get('workExtra', {}).get('grantable')}")

    # 3. 测试Electron API
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_electron_api())

    # 4. 尝试直接API调用
    result = try_direct_api_call()

    print("\n" + "=" * 60)
    if result:
        print("✓ 签到成功！")
    else:
        print("等待下一步调试...")
    print("=" * 60)


if __name__ == "__main__":
    main()
