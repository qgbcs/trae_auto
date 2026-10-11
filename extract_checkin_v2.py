# -*- coding: utf-8 -*-
"""从 Trae JS 中提取签到 API 调用的完整代码"""
import re

js_file = r"D:\Trae CN\resources\app\out\vs\workbench\workbench.desktop.main.js"

with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 查找 rb 方法（签到请求的核心方法）
# 从之前的输出看到: this.rb(e,t) 和 fetchCheckinCreditsStatus

# 找到 claimCheckinCredits 的完整上下文
patterns = [
    # 查找 rb 方法定义
    r'rb\([a-z],[a-z]\).*?fetchJSON',
    # 查找 fetchCheckinCreditsStatus 的完整实现
    r'fetchCheckinCreditsStatus\(\)[^}]+\}',
    # 查找 claimCheckinCredits 的完整实现
    r'claimCheckinCredits\(\)[^}]+\}',
    # 查找 qb 方法（签到状态检查）
    r'qb\(\)[^{]*\{[^}]+fetchCheckinCreditsStatus[^}]+\}',
]

# 更直接的方法：找到包含 "Cloud-IDE-JWT" 和 checkin 的代码段
print("=== 查找 Cloud-IDE-JWT + checkin 相关代码 ===\n")
jwt_pattern = r'.{200}Cloud-IDE-JWT.*?checkin.{200}'
matches = re.findall(jwt_pattern, content, re.DOTALL | re.IGNORECASE)
for m in matches[:5]:
    m_clean = m.replace('\n', ' ').replace('\r', ' ')
    print(f"Match:\n  {m_clean[:500]}\n")

# 查找 fetchJSON 中带有 checkin url 的调用
print("\n=== 查找 checkin URL 的 fetchJSON 调用 ===\n")
url_patterns = [
    r'fetchJSON\(\{[^}]*checkin[^}]*\}',
    r'url:[^,}]*checkin[^,}]*',
    r'url:[^,}]*activity[^,}]*',
]
for pat in url_patterns:
    matches = re.findall(pat, content, re.DOTALL | re.IGNORECASE)
    for m in matches[:5]:
        m_clean = m.replace('\n', ' ').replace('\r', ' ')
        print(f"  {m_clean[:300]}")
    print()

# 直接搜索 URL 模式
print("\n=== 搜索可能的 API URL 模式 ===\n")
url_search = re.findall(r'https?://[^\s"\'`<>]+', content)
unique_urls = list(set(url_search))[:50]
for u in unique_urls:
    if 'checkin' in u.lower() or 'activity' in u.lower() or 'icube' in u.lower() or 'credit' in u.lower():
        print(f"  {u}")

# 搜索路径模式
print("\n=== 搜索路径模式 ===\n")
path_search = re.findall(r'["\'](/api/[^"\']+)["\']', content)
unique_paths = list(set(path_search))
for p in unique_paths[:50]:
    if any(k in p.lower() for k in ['checkin', 'activity', 'icube', 'credit', 'commerce']):
        print(f"  {p}")
