"""调试storage.json结构"""
import json

STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"

with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Top-level keys:")
for key in data.keys():
    print(f"  {key}")

print("\nChecking 'icube' key:")
if 'icube' in data:
    print(f"  icube exists")
    icube = data['icube']
    print(f"  icube type: {type(icube)}")
    if isinstance(icube, dict):
        print(f"  icube keys: {list(icube.keys())}")
        if 'data' in icube:
            print(f"  icube.data exists")
            icube_data = icube['data']
            print(f"  icube.data type: {type(icube_data)}")
            if isinstance(icube_data, dict):
                print(f"  icube.data keys: {list(icube_data.keys())}")
                for k, v in icube_data.items():
                    print(f"    {k}: {type(v)}")
                    if isinstance(v, str):
                        try:
                            parsed = json.loads(v)
                            print(f"      JSON内容: {json.dumps(parsed, indent=2, ensure_ascii=False)[:500]}...")
                        except:
                            print(f"      不是JSON: {v[:200]}")
            else:
                print(f"  icube.data value: {icube_data}")
        else:
            print(f"  icube contents: {json.dumps(icube, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"  icube value: {icube}")
else:
    print("  icube key not found")

# 搜索所有包含checkin的key
print("\nSearching for 'checkin' in all keys:")
def search_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            if 'checkin' in k.lower():
                print(f"  Found: {new_path} = {v}")
            search_keys(v, new_path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            search_keys(v, f"{path}[{i}]")

search_keys(data)
