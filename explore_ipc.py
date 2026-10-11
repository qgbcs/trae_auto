# -*- coding: utf-8 -*-
"""
方案探索：尝试通过VS Code IPC通道发送签到命令
VS Code/Trae使用特定的IPC协议进行进程间通信
"""
import struct
import socket
import time
import os

print("=== VS Code IPC协议分析 ===")

# VS Code IPC使用Unix domain socket（Linux/Mac）或命名管道（Windows）
# 在Windows上，路径通常是：\\.\pipe\vscode-git-xxxxxx 或类似格式

print("\n1. 检查命名管道...")
try:
    import win32file
    import pywintypes
    
    # 尝试查找VS Code相关的命名管道
    pipe_pattern = r"\\.\pipe\vscode-*"
    print(f"   搜索模式: {pipe_pattern}")
    
    # 列出所有命名管道
    try:
        import winreg
        # Windows命名管道列表
        pipe_list = []
        for root_key, sub_key in [
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services"),
        ]:
            try:
                with winreg.OpenKey(root_key, sub_key) as key:
                    for i in range(100):  # 限制数量
                        try:
                            service_name = winreg.EnumValue(key, i)[0]
                            if 'vscode' in service_name.lower() or 'trae' in service_name.lower():
                                pipe_list.append(service_name)
                        except:
                            break
            except:
                pass
        
        if pipe_list:
            print(f"   找到相关服务: {pipe_list[:10]}")
        else:
            print(f"   未找到命名管道服务")
    except Exception as e:
        print(f"   错误: {e}")
        
except ImportError as e:
    print(f"   win32file未安装: {e}")

# 2. 检查Trae进程打开的文件描述符（Windows上用Handle工具或另一种方式）
print("\n2. 检查Trae的调试端口配置...")
import subprocess

# 获取Trae进程ID
result = subprocess.run(
    ['tasklist', '/FI', 'IMAGENAME eq Trae CN.exe', '/FO', 'CSV', '/NH'],
    capture_output=True, text=True
)
print(f"   tasklist输出: {result.stdout[:500]}")

# 3. 尝试通过TCP发送IPC消息（如果有的话）
print("\n3. 尝试连接调试端口并发送IPC消息...")
debug_ports = [51000, 51001, 51002, 9222]
for port in debug_ports:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(('127.0.0.1', port))
        print(f"   ✓ 端口{port}可连接")
        
        # 尝试发送IPC协议头
        # VS Code IPC协议的魔术字节是 'IC'
        magic = b'IC'
        version = struct.pack('<I', 1)
        length = struct.pack('<I', 0)  # 空消息体
        header = magic + version + length
        sock.send(header)
        time.sleep(0.5)
        
        try:
            response = sock.recv(1024)
            print(f"   响应: {response[:50].hex()}")
        except socket.timeout:
            print(f"   无响应（可能不是IPC协议）")
        
        sock.close()
    except Exception as e:
        pass  # 静默失败

# 4. 检查环境变量中的VS Code相关设置
print("\n4. 检查环境变量...")
vscode_env = {k: v for k, v in os.environ.items() if 'VSCode' in k.upper() or 'TRA�' in k.upper() or 'CODE' in k.upper()}
if vscode_env:
    for k, v in vscode_env.items():
        print(f"   {k}={v[:100]}...")
else:
    print("   无相关环境变量")

print("\n=== 结论 ===")
print("VS Code/Trae IPC需要通过进程内部机制触发，外部直接发送IPC协议比较困难。")
print("最可行的方案仍然是：")
print("1. UI自动化（pyautogui）- 稳定但慢")
print("2. 如果找到Electron DevTools端口，可以通过CDP执行JS代码")
