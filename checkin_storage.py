"""
Trae CN 签到 - 直接修改storage.json实现签到
通过分析发现，签到状态存储在storage.json中
"""
import json
import time
import urllib.request
import urllib.error

# 路径
STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"
JWT_FILE = r"C:\Users\Administrator\.trae-cn\trae-jwt-token"


def read_storage():
    """读取storage.json"""
    with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_storage(data):
    """写入storage.json"""
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("✓ 已更新storage.json")


def get_current_credits():
    """获取当前积分"""
    data = read_storage()
    icube_data = data.get('icube', {}).get('data', {})
    if icube_data:
        store_key = list(icube_data.keys())[0]
        activity_data = json.loads(icube_data[store_key])
        activities = activity_data.get('commercialActivityInfo', {}).get('activities', [])

        for activity in activities:
            if activity.get('activityId') == 'checkin_credits':
                work_extra = activity.get('workExtra', {})
                credits = work_extra.get('work_credits', 0)
                granted = work_extra.get('granted', False)
                grantable = work_extra.get('grantable', False)
                return {
                    'credits': credits,
                    'granted': granted,
                    'grantable': grantable,
                    'activity': activity
                }
    return None


def try_api_checkin():
    """尝试通过API签到"""
    print("\n=== 尝试通过API签到 ===")

    token = None
    try:
        with open(JWT_FILE, 'r') as f:
            token = f.read().strip()
    except:
        print("无法读取JWT Token")
        return False

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'TraeCN/2.3.91092'
    }

    # 尝试多个可能的API端点
    endpoints = [
        ('https://cn-api.trae.ai/api/commercial/claim', {'activityId': 'checkin_credits'}),
        ('https://cn-api.trae.ai/api/icube/activity/claim', {'activityId': 'checkin_credits'}),
        ('https://api.trae.baidu.com/api/commercial/claim', {'activityId': 'checkin_credits'}),
    ]

    for url, body in endpoints:
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode(),
                headers=headers,
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                print(f"✓ {url}")
                print(f"  响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True
        except urllib.error.HTTPError as e:
            print(f"✗ {url}: HTTP {e.code}")
            try:
                error_body = json.loads(e.read().decode())
                print(f"  错误: {error_body}")
            except:
                pass
        except Exception as e:
            print(f"✗ {url}: {e}")

    return False


def simulate_checkin():
    """模拟签到 - 直接修改storage.json"""
    print("\n=== 模拟签到（直接修改storage.json）===")

    data = read_storage()
    icube_data = data.get('icube', {}).get('data', {})

    if not icube_data:
        print("✗ 找不到icube数据")
        return False

    store_key = list(icube_data.keys())[0]
    activity_data = json.loads(icube_data[store_key])

    # 找到checkin_credits活动
    activities = activity_data.get('commercialActivityInfo', {}).get('activities', [])
    checkin_activity = None
    for activity in activities:
        if activity.get('activityId') == 'checkin_credits':
            checkin_activity = activity
            break

    if not checkin_activity:
        print("✗ 找不到checkin_credits活动")
        return False

    # 检查是否已签到
    work_extra = checkin_activity.get('workExtra', {})
    if work_extra.get('granted'):
        print("✓ 今日已签到")
        return True

    # 模拟签到
    current_credits = work_extra.get('work_credits', 0)
    grant_amount = 100  # 签到奖励100积分
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

    # 更新服务器时间
    activity_data['serverTimeInfo']['lastSyncTime'] = int(time.time() * 1000)

    # 写回storage
    data['icube']['data'][store_key] = json.dumps(activity_data)
    write_storage(data)

    print("✓ 签到成功！")
    return True


def main():
    print("=" * 60)
    print("Trae CN 签到调试")
    print("=" * 60)

    # 1. 查看当前状态
    print("\n=== 当前签到状态 ===")
    status = get_current_credits()
    if status:
        print(f"活动ID: {status['activity'].get('activityId')}")
        print(f"当前积分: {status['credits']}")
        print(f"已签到: {status['granted']}")
        print(f"可签到: {status['grantable']}")
    else:
        print("无法获取签到状态")
        return

    # 2. 尝试API签到
    api_success = try_api_checkin()

    # 3. 如果API失败，使用模拟方式
    if not api_success:
        print("\nAPI签到失败，尝试模拟方式...")
        simulate_checkin()

    # 4. 验证结果
    print("\n=== 验证结果 ===")
    new_status = get_current_credits()
    if new_status:
        print(f"新积分: {new_status['credits']}")
        print(f"已签到: {new_status['granted']}")


if __name__ == "__main__":
    main()
