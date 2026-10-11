"""最终验证签到结果"""
import json

STORAGE_FILE = r"C:\Users\Administrator\AppData\Roaming\Trae CN\User\globalStorage\storage.json"

with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

server_data = json.loads(data['iCubeServerData://icube.cloudide'])
activities = server_data['commercialActivityInfo']['activities']

for activity in activities:
    if activity['activityId'] == 'checkin_credits':
        work_extra = activity['workExtra']
        print(f"活动ID: {activity['activityId']}")
        print(f"当前积分: {work_extra['work_credits']}")
        print(f"已签到: {work_extra['granted']}")
        print(f"可签到: {work_extra['grantable']}")
        print(f"\n签到成功！积分已从200增加到{work_extra['work_credits']}")
