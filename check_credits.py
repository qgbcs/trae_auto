#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前积分状态
"""
import json
import sys
from pathlib import Path
from datetime import datetime

STORAGE_JSON = Path.home() / 'AppData' / 'Roaming' / 'Trae CN' / 'User' / 'globalStorage' / 'storage.json'

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def check_credits():
    log("=" * 60)
    log("检查 Trae CN 积分状态")
    log("=" * 60)
    
    if not STORAGE_JSON.exists():
        log(f"ERROR: {STORAGE_JSON} 不存在")
        return
    
    try:
        data = json.loads(STORAGE_JSON.read_text())
        
        log(f"\n文件修改时间: {datetime.fromtimestamp(STORAGE_JSON.stat().st_mtime)}")
        
        # 获取活动信息
        activities = data.get('commercialActivityInfo', {}).get('activities', [])
        log(f"\n活动数量: {len(activities)}")
        
        for i, act in enumerate(activities):
            act_type = act.get('activityType', 'N/A')
            log(f"\n[{i}] 活动类型: {act_type}")
            
            # 打印完整活动信息
            log(f"    活动数据: {json.dumps(act, ensure_ascii=False, indent=6)}")
            
            # 查找积分字段
            metadata = act.get('metadata', {})
            work_extra = act.get('workExtra', {})
            
            # 尝试各种可能的积分字段
            all_data = {**metadata, **work_extra, **act}
            
            for key, value in all_data.items():
                if 'credit' in key.lower() or 'score' in key.lower() or 'point' in key.lower():
                    log(f"    💰 积分字段 '{key}': {value}")
        
        # 检查其他可能的字段
        log("\n检查所有字段:")
        for key in data.keys():
            if 'credit' in key.lower() or 'score' in key.lower():
                log(f"  {key}: {data[key]}")
        
        # 打印 commercialActivityInfo 的完整内容
        commercial = data.get('commercialActivityInfo', {})
        log(f"\ncommercialActivityInfo 完整内容:")
        log(json.dumps(commercial, ensure_ascii=False, indent=2))
        
    except Exception as e:
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_credits()
