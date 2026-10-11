#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v42 - 通过端口51000发送签到请求（改进版）
"""
import sys
import time
import json
import socket
import struct
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = SCRIPT_DIR / 'screenshots'
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def send_and_receive(sock, channel, params=None):
    """发送消息并接收完整响应"""
    try:
        # 构造消息
        message = {
            "jsonrpc": "2.0",
            "method": channel,
            "params": params or [],
            "id": int(time.time() * 1000)
        }

        msg_bytes = json.dumps(message).encode('utf-8')

        # 发送长度前缀 + 消息体
        length = struct.pack('>I', len(msg_bytes))
        sock.sendall(length + msg_bytes)
        log(f"  发送: {channel}")

        # 接收响应
        # 协议格式：4字节长度 + JSON数据
        response_data = b''

        while True:
            # 尝试接收数据
            chunk = sock.recv(65536)
            if not chunk:
                break

            response_data += chunk

            # 尝试解析
            if len(response_data) >= 4:
                try:
                    # 检查是否是有效的JSON
                    data_str = response_data.decode('utf-8', errors='ignore')
                    # 尝试找到JSON结束位置
                    if data_str.startswith('{') and data_str.endswith('}'):
                        parsed = json.loads(data_str)
                        return parsed
                except:
                    pass

            # 如果数据太长，停止
            if len(response_data) > 10000:
                break

        if response_data:
            log(f"  响应长度: {len(response_data)} 字节")
            # 尝试解析
            try:
                data_str = response_data.decode('utf-8', errors='ignore')
                parsed = json.loads(data_str)
                return parsed
            except:
                pass

        return None
    except Exception as e:
        log(f"  错误: {e}")
        return None

def main():
    log("=" * 60)
    log("Trae CN 自动签到 v42")
    log("=" * 60)

    # 读取初始积分
    STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
    initial_credits = 0

    if STORAGE_JSON.exists():
        try:
            data = json.loads(STORAGE_JSON.read_text())
            commercial = data.get('commercialActivityInfo', {})
            activities = commercial.get('activities', [])

            for act in activities:
                if 'checkin' in act.get('activityType', '').lower():
                    metadata = act.get('metadata', {})
                    work_extra = act.get('workExtra', {})
                    for key in ['totalCredits', 'credits', 'earnedCredits', 'availableCredits']:
                        if key in metadata:
                            initial_credits = metadata[key]
                            break
                        if key in work_extra:
                            initial_credits = work_extra[key]
                            break
                    break
        except:
            pass

    log(f"\n初始积分: {initial_credits}")

    # 连接端口51000
    log("\n连接端口51000...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect(('127.0.0.1', 51000))
        log("  连接成功")

        # 发送签到请求
        log("\n发送签到请求...")
        result = send_and_receive(sock, 'vscode:sandbox::main-invoke-claimCheckinCredits', [])

        if result:
            log(f"  结果: {json.dumps(result, ensure_ascii=False)[:300]}")

            # 检查是否成功
            if isinstance(result, dict):
                if result.get('result', {}).get('success') or result.get('success'):
                    log(f"\n✅ 签到成功!")
                elif result.get('error'):
                    log(f"\n⚠️ 签到失败: {result['error']}")
                else:
                    log(f"\n✅ 签到请求已发送")
            else:
                log(f"\n✅ 签到请求已发送")
        else:
            log(f"\n⚠️ 未收到有效响应")

        # 获取签到状态
        log("\n获取签到状态...")
        status = send_and_receive(sock, 'vscode:sandbox::main-invoke-fetchCheckinCreditsStatus', [])

        if status:
            log(f"  状态: {json.dumps(status, ensure_ascii=False)[:300]}")

    except Exception as e:
        log(f"  连接错误: {e}")
    finally:
        try:
            sock.close()
        except:
            pass

    # 等待并验证
    log("\n等待界面刷新...")
    time.sleep(3)

    # 重新读取积分
    final_credits = initial_credits
    if STORAGE_JSON.exists():
        try:
            data = json.loads(STORAGE_JSON.read_text())
            commercial = data.get('commercialActivityInfo', {})
            activities = commercial.get('activities', [])

            for act in activities:
                if 'checkin' in act.get('activityType', '').lower():
                    metadata = act.get('metadata', {})
                    work_extra = act.get('workExtra', {})
                    for key in ['totalCredits', 'credits', 'earnedCredits', 'availableCredits']:
                        if key in metadata:
                            final_credits = metadata[key]
                            break
                        if key in work_extra:
                            final_credits = work_extra[key]
                            break
                    break
        except:
            pass

    log(f"\n最终积分: {final_credits}")

    if final_credits > initial_credits:
        increase = final_credits - initial_credits
        log(f"\n✅ 签到成功! 积分增加: {increase}")
    else:
        log(f"\n⚠️ 积分未变化 ({initial_credits} -> {final_credits})")
        log("  请检查界面上的积分显示")

    log("\n" + "=" * 60)

if __name__ == '__main__':
    main()
