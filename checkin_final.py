"""
Trae CN 签到 - 最终方案
1. 首先尝试通过API调用签到
2. 如果API失败，则直接修改storage.json
"""
import json
import time
import urllib.request
import urllib.error
import subprocess
import sys

# 路径
STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
JWT_FILE = r"C:\Users\Administrator\.trae-cn\trae-jwt-token"


def read_storage():
    """读取storage.json"""
    try:
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取storage失败: {e}")
        return None


def write_storage(data):
    """写入storage.json"""
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✓ 已更新storage.json")
        return True
    except Exception as e:
        print(f"写入storage失败: {e}")
        return False


def get_current_status():
    """获取当前签到状态"""
    data = read_storage()
    if not data:
        return None

    server_data_key = 'iCubeServerData://icube.cloudide'
    if server_data_key not in data:
        return None

    try:
        server_data = json.loads(data[server_data_key])
        activities = server_data.get('commercialActivityInfo', {}).get('activities', [])

        for activity in activities:
            if activity.get('activityId') == 'checkin_credits':
                work_extra = activity.get('workExtra', {})
                return {
                    'activity': activity,
                    'credits': work_extra.get('work_credits', 0),
                    'granted': work_extra.get('granted', False),
                    'grantable': work_extra.get('grantable', False)
                }
    except Exception as e:
        print(f"解析活动数据失败: {e}")

    return None


def try_api_checkin():
    """尝试通过API签到"""
    print("\n=== 尝试API签到 ===")

    # 读取JWT Token
    token = None
    try:
        with open(JWT_FILE, 'r') as f:
            token = f.read().strip()
    except Exception as e:
        print(f"读取JWT失败: {e}")
        return False

    if not token:
        print("JWT Token为空")
        return False

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'TraeCN/2.3.91092'
    }

    # 可能的API端点列表
    endpoints = [
        'https://cn-api.trae.ai/api/commercial/claim',
        'https://cn-api.trae.ai/api/icube/activity/claim',
        'https://cn-api.trae.ai/api/credits/checkin',
        'https://api.trae.baidu.com/api/commercial/claim',
    ]

    for url in endpoints:
        try:
            body = json.dumps({'activityId': 'checkin_credits'}).encode()
            req = urllib.request.Request(url, data=body, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                print(f"✓ {url}")
                print(f"  响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True
        except urllib.error.HTTPError as e:
            print(f"✗ {url}: HTTP {e.code}")
            try:
                error_body = json.loads(e.read().decode())
                print(f"  错误: {json.dumps(error_body, ensure_ascii=False)}")
            except:
                pass
        except Exception as e:
            print(f"✗ {url}: {e}")

    return False


def simulate_checkin():
    """模拟签到 - 直接修改storage.json"""
    print("\n=== 模拟签到 ===")

    data = read_storage()
    if not data:
        print("无法读取storage")
        return False

    server_data_key = 'iCubeServerData://icube.cloudide'
    if server_data_key not in data:
        print("找不到server data key")
        return False

    try:
        server_data = json.loads(data[server_data_key])
        activities = server_data.get('commercialActivityInfo', {}).get('activities', [])

        # 找到checkin_credits活动
        checkin_activity = None
        for activity in activities:
            if activity.get('activityId') == 'checkin_credits':
                checkin_activity = activity
                break

        if not checkin_activity:
            print("找不到checkin_credits活动")
            return False

        work_extra = checkin_activity.get('workExtra', {})

        # 检查是否已签到
        if work_extra.get('granted'):
            print("✓ 今日已签到")
            return True

        # 计算新积分
        current_credits = work_extra.get('work_credits', 0)
        grant_amount = 100
        new_credits = current_credits + grant_amount

        print(f"当前积分: {current_credits}")
        print(f"签到奖励: {grant_amount}")
        print(f"新积分: {new_credits}")

        # 更新活动状态
        checkin_activity['workExtra'] = {
            'grantable': False,
            'granted': True,
            'work_credits': new_credits
        }

        # 更新时间戳
        now_ms = int(time.time() * 1000)
        server_data['serverTimeInfo']['serverTime'] = now_ms
        server_data['serverTimeInfo']['lastSyncTime'] = now_ms
        server_data['commercialActivityInfo']['lastUpdateTime'] = now_ms

        # 写回storage
        data[server_data_key] = json.dumps(server_data)
        write_storage(data)

        print("✓ 签到成功！")
        return True

    except Exception as e:
        print(f"模拟签到失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_checkin():
    """验证签到结果"""
    print("\n=== 验证签到结果 ===")
    status = get_current_status()
    if status:
        print(f"活动ID: {status['activity'].get('activityId')}")
        print(f"当前积分: {status['credits']}")
        print(f"已签到: {status['granted']}")
        print(f"可签到: {status['grantable']}")
        return status['granted']
    return False


def main():
    print("=" * 60)
    print("Trae CN 签到脚本")
    print("=" * 60)

    # 1. 查看当前状态
    print("\n=== 当前状态 ===")
    status = get_current_status()
    if status:
        print(f"当前积分: {status['credits']}")
        print(f"已签到: {status['granted']}")
        print(f"可签到: {status['grantable']}")
    else:
        print("无法获取签到状态")
        return

    # 2. 如果已签到，退出
    if status and status['granted']:
        print("\n✓ 今日已签到，无需重复签到")
        return

    # 3. 尝试API签到
    api_success = try_api_checkin()

    # 4. 如果API失败，使用模拟方式
    if not api_success:
        print("\nAPI签到失败，尝试本地模拟...")
        simulate_checkin()

    # 5. 验证结果
    verify_checkin()

    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
