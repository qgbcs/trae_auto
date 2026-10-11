"""解析iCubeServerData"""
import json

STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"

with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取iCubeServerData
server_data_key = 'iCubeServerData://icube.cloudide'
if server_data_key in data:
    server_data_str = data[server_data_key]
    print(f"Key: {server_data_key}")
    print(f"Value type: {type(server_data_str)}")

    # 解析JSON
    try:
        server_data = json.loads(server_data_str)
        print(f"\n解析成功:")
        print(json.dumps(server_data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        print(f"原始内容(前500字符): {server_data_str[:500]}")
else:
    print(f"Key '{server_data_key}' not found")
    print(f"Available keys: {list(data.keys())}")
