#!/usr/bin/env python3
"""
Trae CN 自动签到 v7 - 纯 Python CDP 实现（不依赖 websockets 库）
通过 Chrome DevTools Protocol 执行 JS 调用签到
"""

import json
import time
import sys
import os
import struct
import hashlib
import base64
import socket
import urllib.request
import urllib.error
import ssl
from datetime import datetime

CDP_PORT = 51000


def cdp_http(port, path):
    """发送 CDP HTTP 请求"""
    url = f"http://127.0.0.1:{port}{path}"
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=5)
        return json.loads(resp.read().decode())
    except Exception as e:
        return None


def ws_key():
    """生成 WebSocket key"""
    import secrets
    return base64.b64encode(secrets.token_bytes(16)).decode()


def ws_upgrade_key(server_key):
    """计算 WebSocket accept key"""
    GUID = "258EAFA5-E914-47DA-95CA-5AB5DC10BE69"
    return base64.b64encode(
        hashlib.sha1((server_key + GUID).encode()).digest()
    ).decode()


def ws_send_text(sock, data):
    """发送 WebSocket 文本帧"""
    data = data.encode('utf-8')
    length = len(data)

    # FIN + Text opcode (0x81)
    frame = bytearray([0x81])

    # Masking key (客户端必须掩码)
    masking_key = os.urandom(4)
    frame.extend(masking_key)

    # Length encoding
    if length < 126:
        frame.append(length | 0x80)  # 设置 MASK bit
    elif length < 65536:
        frame.append(126 | 0x80)
        frame.extend(struct.pack('>H', length))
    else:
        frame.append(127 | 0x80)
        frame.extend(struct.pack('>Q', length))

    # 掩码数据
    masked_data = bytearray(length)
    for i in range(length):
        masked_data[i] = data[i] ^ masking_key[i % 4]
    frame.extend(masked_data)

    sock.sendall(frame)


def ws_recv_text(sock, timeout=30):
    """接收 WebSocket 文本帧"""
    sock.settimeout(timeout)
    result = bytearray()

    while True:
        # 读取帧头
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

        if opcode == 0x8:  # Close
            return None
        if opcode == 0x80:  # Continuation
            pass  # 继续读取

        # 读取长度
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

        # 读取掩码密钥
        masking_key = b''
        if is_masked:
            while len(masking_key) < 4:
                chunk = sock.recv(4 - len(masking_key))
                if not chunk:
                    return None
                masking_key += chunk

        # 读取数据
        data = b''
        while len(data) < length:
            chunk = sock.recv(min(4096, length - len(data)))
            if not chunk:
                return None
            data += chunk

        # 解掩码
        if is_masked:
            data = bytes(b ^ masking_key[i % 4] for i, b in enumerate(data))

        # 解码文本
        try:
            text = data.decode('utf-8')
            result.extend(text.encode('utf-8'))
        except UnicodeDecodeError:
            return None

        # 如果是 FIN 帧，返回结果
        if first_byte & 0x80:  # FIN bit
            return result.decode('utf-8')


def ws_connect(host, port, path):
    """建立 WebSocket 连接"""
    key = ws_key()

    sock = socket.create_connection((host, port), timeout=10)

    # 发送 HTTP Upgrade 请求
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    sock.sendall(request.encode())

    # 读取响应
    response = b''
    while b'\r\n\r\n' not in response:
        chunk = sock.recv(4096)
        if not chunk:
            sock.close()
            return None
        response += chunk

    # 验证响应
    if b'101 Switching Protocols' not in response:
        sock.close()
        return None

    # 验证 accept key
    headers = response.split(b'\r\n\r\n')[0].decode()
    accept_line = [l for l in headers.split('\n') if l.lower().startswith('sec-websocket-accept:')]
    if not accept_line:
        sock.close()
        return None

    server_key = accept_line[0].split(':', 1)[1].strip()
    expected_key = ws_upgrade_key(key)
    if server_key != expected_key:
        sock.close()
        return None

    return sock


def cdp_evaluate(port, expression, timeout=30):
    """通过 CDP 执行 JavaScript"""
    # 1. 获取 targets
    targets = cdp_http(port, '/json')
    if not targets:
        return None, f"无法连接到 CDP 端口 {port}"

    # 2. 找到目标页面
    target = None
    for t in targets:
        title = t.get('title', '')
        url = t.get('url', '')
        # 优先选择 Trae 主窗口
        if 'Trae' in title or 'vscode' in url.lower():
            target = t
            break
    if not target and targets:
        target = targets[0]

    if not target:
        return None, "未找到有效的 CDP target"

    ws_url = target.get('webSocketDebuggerUrl')
    if not ws_url:
        return None, "无法获取 WebSocket URL"

    # 解析 WebSocket URL
    # 格式: ws://127.0.0.1:51000/devtools/page/XXXX
    try:
        from urllib.parse import urlparse
        parsed = urlparse(ws_url)
        host = parsed.hostname or '127.0.0.1'
        port_num = parsed.port or port
        path = parsed.path
    except:
        parts = ws_url.replace('ws://', '').split('/', 2)
        host_port = parts[0].split(':')
        host = host_port[0]
        port_num = int(host_port[1]) if len(host_port) > 1 else port
        path = '/' + parts[1] if len(parts) > 1 else '/'

    # 3. 建立 WebSocket 连接
    sock = ws_connect(host, port_num, path)
    if not sock:
        return None, "无法建立 WebSocket 连接"

    try:
        msg_id = 1

        # 启用 Runtime
        ws_send_text(sock, json.dumps({
            "id": msg_id,
            "method": "Runtime.enable",
            "params": {}
        }))
        msg_id += 1

        # 执行 JS
        ws_send_text(sock, json.dumps({
            "id": msg_id,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
                "timeout": timeout * 1000
            }
        }))
        msg_id += 1

        # 读取响应（可能有多条消息）
        results = []
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            try:
                resp = ws_recv_text(sock, timeout=5)
                if resp is None:
                    break
                results.append(json.loads(resp))

                # 检查是否是我们要的结果
                for r in results:
                    if r.get('id') == msg_id - 1:  # evaluate 的结果
                        return r, None
            except socket.timeout:
                break
            except Exception as e:
                print(f"[WS] 接收错误: {e}")
                break

        return {"results": results}, None

    finally:
        sock.close()


def main():
    print("=" * 60)
    print("Trae CN 自动签到 v7 (纯 Python CDP)")
    print("=" * 60)

    port = CDP_PORT
    print(f"\n[CDP] 连接端口: {port}")

    # 测试连接
    version = cdp_http(port, '/json/version')
    if not version:
        print(f"[错误] 无法连接到 CDP 端口 {port}")
        print("提示: 确保 Trae 正在运行且 CDP 端口已启用")
        return 1

    print(f"[OK] CDP 版本: {version.get('Browser', 'unknown')}")
    print(f"[OK] WebSocket URL: {version.get('webSocketDebuggerUrl', 'unknown')[:80]}...")

    # 查询目标列表
    targets = cdp_http(port, '/json')
    if targets:
        print(f"[OK] 发现 {len(targets)} 个 target")
        for i, t in enumerate(targets[:3]):
            print(f"  [{i}] {t.get('type', '?')}: {t.get('title', t.get('url', ''))[:60]}")

    # 执行签到 JS
    js_checkin = """
    (async () => {
        const vscode = globalThis.vscode;
        if (!vscode || !vscode.ipcRenderer) {
            return {error: 'ipcRenderer not found'};
        }

        const channel = 'vscode:sandbox::main-invoke-claimCheckinCredits';
        console.log('[JS] 调用签到:', channel);

        try {
            const result = await vscode.ipcRenderer.invoke(channel);
            console.log('[JS] 签到结果:', JSON.stringify(result));
            return {success: true, result: result};
        } catch (e) {
            console.error('[JS] 签到失败:', e);
            return {error: e.message || String(e)};
        }
    })()
    """

    js_status = """
    (async () => {
        const vscode = globalThis.vscode;
        if (!vscode || !vscode.ipcRenderer) {
            return {error: 'ipcRenderer not found'};
        }

        const channel = 'vscode:sandbox::main-invoke-fetchCheckinCreditsStatus';
        console.log('[JS] 查询状态:', channel);

        try {
            const result = await vscode.ipcRenderer.invoke(channel);
            console.log('[JS] 状态:', JSON.stringify(result));
            return {success: true, result: result};
        } catch (e) {
            console.error('[JS] 查询失败:', e);
            return {error: e.message || String(e)};
        }
    })()
    """

    print("\n" + "-" * 40)
    print("[步骤 1] 查询当前签到状态...")

    status_result, status_error = cdp_evaluate(port, js_status)
    if status_error:
        print(f"[警告] 状态查询失败: {status_error}")
    else:
        print(f"[状态] {json.dumps(status_result, ensure_ascii=False, indent=2)[:300]}")

    print("\n" + "-" * 40)
    print("[步骤 2] 执行签到...")

    checkin_result, checkin_error = cdp_evaluate(port, js_checkin)
    if checkin_error:
        print(f"\n[错误] 签到失败: {checkin_error}")
        return 1

    print(f"\n[结果] {json.dumps(checkin_result, ensure_ascii=False, indent=2)}")

    if checkin_result and checkin_result.get('success'):
        print("\n[成功] 签到完成!")
        return 0
    elif checkin_result and checkin_result.get('error'):
        print(f"\n[错误] 签到失败: {checkin_result['error']}")
        return 1
    else:
        print(f"\n[未知] 签到结果不明确")
        return 1


if __name__ == "__main__":
    sys.exit(main())
