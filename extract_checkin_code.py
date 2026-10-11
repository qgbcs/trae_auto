# -*- coding: utf-8 -*-
"""提取 Trae JS 中的签到 API 调用代码"""
import re

js_file = r"D:\Trae CN\resources\app\out\vs\workbench\workbench.desktop.main.js"

with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 查找 claimCheckinCredits 相关的代码
patterns = [
    r'claimCheckinCredits.{0,500}',
    r'fetchCheckinCreditsStatus.{0,500}',
    r'SANDBOX_TO_MAIN_INVOKE_CLAIM_CHECKIN_CREDITS.{0,200}',
    r'checkin.*fetchJSON|fetchJSON.*checkin',
    r'url.*checkin|checkin.*url',
]

print("=== 查找签到相关代码 ===\n")
for i, pattern in enumerate(patterns):
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    if matches:
        print(f"\n--- Pattern {i+1}: {pattern[:50]} ---")
        for m in matches[:3]:
            # 清理输出
            m_clean = m.replace('\n', ' ').replace('\r', ' ')
            print(f"  {m_clean[:300]}")
            print()

# 特别查找 IPC invoke 调用的上下文
print("\n=== 查找 IPC invoke 调用上下文 ===\n")
ipc_pattern = r'Tt\.invoke\(oi\.SANDBOX_TO_MAIN_INVOKE_CLAIM_CHECKIN_CREDITS\)'
match = re.search(ipc_pattern, content)
if match:
    start = max(0, match.start() - 500)
    end = min(len(content), match.end() + 500)
    context = content[start:end]
    context = context.replace('\n', ' ').replace('\r', ' ')
    print(f"找到 IPC invoke 调用上下文:\n{context[:1000]}")

# 查找 fetchJSON 调用
print("\n=== 查找 fetchJSON 调用 ===\n")
fetch_pattern = r'fetchJSON\([^)]*checkin[^)]*\)|fetchJSON\([^)]*\)'
matches = re.findall(fetch_pattern, content, re.DOTALL | re.IGNORECASE)
for m in matches[:5]:
    m_clean = m.replace('\n', ' ').replace('\r', ' ')
    print(f"  {m_clean[:400]}")
    print()
