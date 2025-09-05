#!/usr/bin/env python3
"""
调试Frankfurt Scale提交数据
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def debug_submit():
    """调试提交数据"""
    test_data = {
        "type": "frankfurt_scale_selective_mutism",
        "basic_info": {
            "name": "测试儿童",
            "grade": "小学",
            "submission_date": datetime.now().strftime("%Y-%m-%d"),
            "guardian": "测试家长"
        },
        "questions": [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "在家很能说话，但在公共/学校环境明显沉默或避免用语言。",
                "options": [
                    {"value": 1, "text": "是"},
                    {"value": 0, "text": "否"}
                ],
                "selected": [1],
                "can_speak": True,
                "section": "DS"
            }
        ]
    }
    
    print("🔍 调试提交数据:")
    print("=" * 50)
    print(f"发送的数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    print(f"\n第一个问题的section值: '{test_data['questions'][0]['section']}'")
    print(f"section值类型: {type(test_data['questions'][0]['section'])}")
    print(f"section值长度: {len(test_data['questions'][0]['section'])}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", 
                               json=test_data, 
                               timeout=10)
        
        print(f"\n📥 服务器响应:")
        print(f"状态码: {response.status_code}")
        
        response_data = response.json()
        print(f"响应内容:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    debug_submit()