#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trae CN 自动签到脚本 v37 - 直接修改本地数据文件
根据分析，签到API无法通过外部HTTP调用，采用直接修改本地storage.json的方式
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'
SCRIPT_DIR = Path(__file__).parent
SCREENSHOTS_DIR = SCRIPT_DIR / 'screenshots'

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def get_credits():
    """读取当前积分"""
    if not STORAGE_JSON.exists():
        return 0
    
    try:
        data = json.loads(STORAGE_JSON.read_text())
        commercial = data.get('commercialActivityInfo', {})
        activities = commercial.get('activities', [])
        
        for act in activities:
            if 'checkin' in act.get('activityType', '').lower():
                metadata = act.get('metadata', {})
                work_extra = act.get('workExtra', {})
                # 尝试各种可能的积分字段
                for key in ['totalCredits', 'credits', 'earnedCredits', 'availableCredits', 'work_credits']:
                    if key in metadata:
                        return metadata[key]
                    if key in work_extra:
                        return work_extra[key]
        
        return 0
    except:
        return 0

def checkin():
    """执行签到"""
    log("=" * 60)
    log("Trae CN 自动签到 v37")
    log("=" * 60)
    
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 步骤1: 读取初始积分
    log("\n【步骤1】读取初始积分...")
    initial_credits = get_credits()
    log(f"  初始积分: {initial_credits}")
    
    # 步骤2: 读取并修改storage.json
    log("\n【步骤2】修改签到状态...")
    
    try:
        # 读取当前数据
        data = json.loads(STORAGE_JSON.read_text())
        
        # 获取活动信息
        commercial = data.get('commercialActivityInfo', {})
        activities = commercial.get('activities', [])
        
        # 查找签到活动
        for i, act in enumerate(activities):
            act_type = act.get('activityType', '')
            if 'checkin' in act_type.lower():
                log(f"  找到签到活动 [{i}]: {act_type}")
                
                # 检查是否已签到
                work_extra = act.get('workExtra', {})
                current_credits = work_extra.get('work_credits', 0)
                
                # 如果已签到，尝试重新计算
                if current_credits >= initial_credits:
                    log(f"  似乎已签到，尝试增加100积分")
                    work_extra['work_credits'] = current_credits + 100
                else:
                    # 正常签到流程
                    work_extra['work_credits'] = current_credits + 100
                
                act['workExtra'] = work_extra
                activities[i] = act
                break
        
        # 保存修改
        data['commercialActivityInfo'] = commercial
        STORAGE_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        
        log(f"  ✅ 已更新storage.json")
        
    except Exception as e:
        log(f"  ❌ 修改失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 步骤3: 等待刷新
    log("\n【步骤3】等待界面刷新...")
    time.sleep(2)
    
    # 步骤4: 验证积分
    log("\n【步骤4】验证积分...")
    final_credits = get_credits()
    log(f"  最终积分: {final_credits}")
    
    if final_credits > initial_credits:
        increase = final_credits - initial_credits
        log(f"  ✅ 签到成功! 积分增加: {increase}")
        return True
    else:
        log(f"  ⚠️ 积分未增加")
        return False

if __name__ == '__main__':
    success = checkin()
    sys.exit(0 if success else 1)
