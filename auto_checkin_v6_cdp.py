#!/usr/bin/env python3
"""
Trae CN 自动签到 v6 - 通过 CDP (Chrome DevTools Protocol) 执行 JS 调用 IPC
不依赖 UI 点击，直接调用全局变量触发签到

策略：
1. 尝试连接 Trae 的 Chrome DevTools 端口（51000-51020）
2. 通过 CDP Runtime.evaluate 执行 JavaScript
3. 调用 globalThis.vscode.ipcRenderer.invoke() 触发签到
"""

import json
import time
import sys
import os
import urllib.request
import urllib.error

# ─── 配置 ──────────────────────────────────────────────────────────────────────
TRAJ_PATH = os.path.expanduser(r"C:\Users\Administrator\.trae-cn\trae-jwt-token")
TRAEE_PATH = os.path.expanduser(r"C:\Users\Administrator\AppData\Roaming\Trae CN\ModularData\ckg_server\local_env.json")

# 可能的 CDP 端口范围（Electron 默认通常在 51000-51020）
CDP_PORTS = list(range(51000, 51025))


def find_trae_pid():
    """查找 Trae 进程 PID 和命令行参数"""
    import subprocess
    try:
        # 用 tasklist 查找 Trae 进程
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Trae.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            # CSV 格式: "名称","PID","会话名","会话#","内存使用","状态","CPU 时间","窗口标题"
            parts = lines[1].strip().replace('"', '').split(',')
            if len(parts) >= 2:
                pid = int(parts[1])
                print(f"[CDP] 找到 Trae 进程 PID={pid}")
                return pid

        # 备选：用 WMIC
        result = subprocess.run(
            ["wmic", "process", "where", "name='Trae.exe'", "get", "ProcessId,CommandLine", "/FORMAT:CSV"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'Trae.exe' in line:
                parts = line.split(',')
                for p in parts:
                    if p.strip().isdigit():
                        print(f"[CDP] 找到 Trae 进程 PID={p.strip()}")
                        return int(p.strip())
    except Exception as e:
        print(f"[CDP] 查找进程失败: {e}")
    return None


def get_command_line(pid):
    """获取进程的完整命令行"""
    import subprocess
    try:
        result = subprocess.run(
            ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine", "/FORMAT:CSV"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'Trae.exe' in line or 'CommandLine=' in line:
                cmd = line.replace('CommandLine=', '').strip().strip('"')
                return cmd
    except Exception:
        pass
    return ""


def read_jwt():
    """读取 JWT Token"""
    try:
        with open(TRAJ_PATH, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"[CDP] 读取 JWT 失败: {e}")
        return None


def read_env_config():
    """读取本地环境配置"""
    try:
        with open(TRAEE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[CDP] 读取配置失败: {e}")
        return None


def cdp_request(port, path, body=None, timeout=5):
    """发送 CDP HTTP 请求"""
    url = f"http://127.0.0.1:{port}{path}"
    try:
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers={
            'Content-Type': 'application/json' if body else {}
        })
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read().decode())
    except Exception as e:
        return None


def cdp_evaluate(port, expression, timeout=10):
    """通过 CDP 在渲染进程中执行 JavaScript"""
    # 1. 获取 targets
    targets = cdp_request(port, '/json')
    if not targets:
        return None, "无法连接到 CDP 端口"

    # 2. 找到 Trae 的主页面（通常第一个或包含 vscode 的）
    target = None
    for t in targets:
        if 'Trae' in t.get('title', '') or 'vscode' in t.get('url', ''):
            target = t
            break
    if not target:
        target = targets[0]

    ws_url = target.get('webSocketDebuggerUrl')
    if not ws_url:
        return None, "无法获取 WebSocket URL"

    # 3. 通过 WebSocket 执行（如果 websockets 库可用）
    try:
        import websockets
        async def _eval():
            async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
                # 启用 Runtime
                await ws.send(json.dumps({
                    "id": 1,
                    "method": "Runtime.enable",
                    "params": {}
                }))
                await ws.recv()  # 确认

                # 执行 JS
                await ws.send(json.dumps({
                    "id": 2,
                    "method": "Runtime.evaluate",
                    "params": {
                        "expression": expression,
                        "returnByValue": True,
                        "awaitPromise": True,
                        "timeout": timeout * 1000
                    }
                }))
                result = await ws.recv()
                return result

        import asyncio
        return asyncio.run(_eval()), None

    except ImportError:
        # websockets 不可用，尝试用 HTTP-only 方式
        pass

    # 4. 备用方案：使用 CDP HTTP API（有限功能）
    result = cdp_request(port, '/json/version')
    if result:
        return {"browser": result.get('Browser', 'Unknown')}, None

    return None, "无法执行 CDP 操作（缺少 websockets 库）"


def checkin_via_cdp(port):
    """通过 CDP 执行签到"""
    print(f"\n[CDP] 尝试端口 {port} ...")

    # 先检查端口是否可达
    version = cdp_request(port, '/json/version')
    if not version:
        return None, f"端口 {port} 不可达"

    print(f"[CDP] 连接到 {version.get('Browser', 'unknown')}")

    # 尝试执行 JS
    js_code = """
    (async () => {
        // 检查 ipcRenderer 是否存在
        if (!globalThis.vscode || !globalThis.vscode.ipcRenderer) {
            return {error: 'ipcRenderer 不可用'};
        }

        const channel = 'vscode:sandbox::main-invoke-claimCheckinCredits';
        console.log('[JS] 调用签到:', channel);

        try {
            const result = await globalThis.vscode.ipcRenderer.invoke(channel);
            console.log('[JS] 签到结果:', JSON.stringify(result));
            return {success: true, result: result};
        } catch (e) {
            console.error('[JS] 签到失败:', e);
            return {error: e.message || String(e)};
        }
    })()
    """

    result, error = cdp_evaluate(port, js_code)
    if error:
        return None, error

    print(f"[CDP] 结果: {json.dumps(result, ensure_ascii=False)[:500]}")
    return result, None


def fetch_status_via_cdp(port):
    """通过 CDP 查询签到状态"""
    print(f"\n[CDP] 查询状态，端口 {port} ...")

    js_code = """
    (async () => {
        if (!globalThis.vscode || !globalThis.vscode.ipcRenderer) {
            return {error: 'ipcRenderer 不可用'};
        }

        const channel = 'vscode:sandbox::main-invoke-fetchCheckinCreditsStatus';
        console.log('[JS] 查询状态:', channel);

        try {
            const result = await globalThis.vscode.ipcRenderer.invoke(channel);
            console.log('[JS] 状态:', JSON.stringify(result));
            return {success: true, result: result};
        } catch (e) {
            console.error('[JS] 查询失败:', e);
            return {error: e.message || String(e)};
        }
    })()
    """

    result, error = cdp_evaluate(port, js_code)
    if error:
        return None, error

    print(f"[CDP] 状态结果: {json.dumps(result, ensure_ascii=False)[:500]}")
    return result, None


def main():
    print("=" * 60)
    print("Trae CN 自动签到 v6 (CDP 方式)")
    print("=" * 60)

    # 1. 读取 JWT
    jwt = read_jwt()
    if not jwt:
        print("[错误] 无法读取 JWT Token")
        return 1
    print(f"[OK] JWT Token: {jwt[:30]}...")

    # 2. 读取环境配置
    env = read_env_config()
    if env:
        print(f"[OK] API Host: {env.get('host', 'unknown')}")
        print(f"[OK] Device ID: {env.get('device_id', 'unknown')}")

    # 3. 查找 Trae 进程
    pid = find_trae_pid()
    if pid:
        cmd = get_command_line(pid)
        if cmd:
            # 检查命令行中是否有 --remote-debugging-port
            import re
            match = re.search(r'--remote-debugging-port=(\d+)', cmd)
            if match:
                print(f"[CDP] 命令行指定调试端口: {match.group(1)}")
                CDP_PORTS = [int(match.group(1))]

    # 4. 遍历端口尝试连接
    print(f"\n[CDP] 扫描端口 {CDP_PORTS[0]}-{CDP_PORTS[-1]} ...")
    connected_port = None

    for port in CDP_PORTS:
        version = cdp_request(port, '/json/version')
        if version:
            print(f"[CDP] 找到 CDP 端口: {port} ({version.get('Browser', 'unknown')})")
            connected_port = port
            break

    if not connected_port:
        print("\n[错误] 无法连接到 Trae 的 CDP 端口")
        print("提示: 启动 Trae 时添加 --remote-debugging-port=9222 参数")
        print("      或在 Trae 设置中启用 '远程调试'")
        return 1

    # 5. 先查询当前状态
    print("\n" + "-" * 40)
    print("[步骤 1] 查询当前签到状态...")
    status_result, status_error = fetch_status_via_cdp(connected_port)

    if status_error:
        print(f"[警告] 状态查询失败: {status_error}")
        print("尝试直接签到...")
    else:
        print(f"[状态] {json.dumps(status_result, ensure_ascii=False, indent=2)}")

    # 6. 执行签到
    print("\n" + "-" * 40)
    print("[步骤 2] 执行签到...")
    checkin_result, checkin_error = checkin_via_cdp(connected_port)

    if checkin_error:
        print(f"\n[错误] 签到失败: {checkin_error}")
        return 1

    if checkin_result and checkin_result.get('success'):
        print(f"\n[成功] 签到完成!")
        print(f"[结果] {json.dumps(checkin_result, ensure_ascii=False, indent=2)}")
        return 0
    elif checkin_result and checkin_result.get('error'):
        print(f"\n[错误] 签到失败: {checkin_result['error']}")
        return 1
    else:
        print(f"\n[未知] 签到结果: {json.dumps(checkin_result, ensure_ascii=False)[:200]}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
