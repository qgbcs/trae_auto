"""
扫描Trae CN的调试端口
尝试找到CDP或其他可交互的端口
"""
import socket
import sys
import subprocess
import json
import urllib.request
sys.stdout.reconfigure(encoding='utf-8')

def find_trae_processes():
    """查找Trae进程"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Trae.exe", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split('\n')
        processes = []
        for line in lines[1:]:
            if line.strip():
                parts = line.replace('"', '').split(',')
                if len(parts) >= 2:
                    pid = int(parts[1])
                    cmd = parts[6] if len(parts) > 6 else ''
                    processes.append((pid, cmd))
        return processes
    except Exception as e:
        print(f"[-] 查找进程失败: {e}")
        return []

def get_process_ports(pid):
    """获取进程打开的端口"""
    try:
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", str(pid)],
            capture_output=True, text=True, timeout=5
        )
        # 直接执行netstat
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=5
        )
        ports = []
        for line in result.stdout.split('\n'):
            if f' {pid} ' in line or f':{pid}' in line:
                parts = line.split()
                if len(parts) >= 5:
                    local_addr = parts[1]
                    if ':' in local_addr:
                        port = local_addr.split(':')[-1]
                        if port.isdigit():
                            ports.append(int(port))
        return sorted(set(ports))
    except Exception as e:
        print(f"[-] 获取端口失败: {e}")
        return []

def try_cdp_port(port):
    """尝试连接CDP端口"""
    try:
        url = f"http://127.0.0.1:{port}/json/version"
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, timeout=2)
        data = json.loads(resp.read().decode())
        return data
    except:
        pass
    return None

def main():
    print("="*60)
    print("扫描Trae CN调试端口")
    print("="*60)

    # 1. 查找Trae进程
    print("\n[步骤1] 查找Trae进程...")
    processes = find_trae_processes()
    if not processes:
        print("[-] 未找到Trae进程")
        return

    for pid, cmd in processes:
        print(f"\n[+] PID: {pid}")
        print(f"    命令行: {cmd[:100]}...")

        # 2. 获取端口
        print(f"\n[步骤2] 获取PID {pid} 的端口...")
        ports = get_process_ports(pid)
        print(f"    端口: {ports[:20]}...")

        # 3. 尝试连接可能的CDP端口
        print(f"\n[步骤3] 扫描CDP端口...")
        cdp_ports = list(range(51000, 51100)) + [9222, 9223, 19222]
        found_cdp = []

        for port in cdp_ports:
            if port in ports:
                print(f"  [!] 发现端口 {port} (进程占用)")
                version = try_cdp_port(port)
                if version:
                    print(f"      CDP版本: {version.get('Browser', 'unknown')}")
                    found_cdp.append(port)

        # 4. 扫描所有监听端口
        print(f"\n[步骤4] 扫描所有监听端口...")
        for port in range(50000, 52000):
            try:
                sock = socket.create_connection(('127.0.0.1', port), timeout=0.5)
                sock.close()
                print(f"  [+] 端口 {port} 可连接")

                # 尝试CDP
                version = try_cdp_port(port)
                if version:
                    print(f"      这是CDP端口! 版本: {version.get('Browser', 'unknown')}")
                    found_cdp.append(port)
            except:
                pass

        if found_cdp:
            print(f"\n[成功] 找到CDP端口: {found_cdp}")
        else:
            print(f"\n[-] 未找到CDP端口")

    print("\n" + "="*60)

if __name__ == '__main__':
    main()
