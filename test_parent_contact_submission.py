import requests
import json
from datetime import datetime

def test_parent_interview_submission():
    """测试家长访谈表数据提交功能"""
    
    # 测试数据
    test_data = {
        "type": "parent_interview",
        "basic_info": {
            "name": "测试儿童",
            "grade": "男 - 测试幼儿园",
            "submission_date": "2020-05-15",
            "gender": "男",
            "birth_date": "2020-05-15",
            "parent_phone": "13800138000",
            "parent_wechat": "test_wechat",
            "parent_email": "test@example.com"
        },
        "questions": [
            {
                "id": 1,
                "type": "text_input",
                "question": "测试问题1",
                "answer": "测试答案1"
            },
            {
                "id": 2,
                "type": "text_input",
                "question": "测试问题2",
                "answer": "测试答案2"
            },
            {
                "id": 3,
                "type": "text_input",
                "question": "测试问题3",
                "answer": "测试答案3"
            },
            {
                "id": 4,
                "type": "text_input",
                "question": "测试问题4",
                "answer": "测试答案4"
            },
            {
                "id": 5,
                "type": "text_input",
                "question": "测试问题5",
                "answer": "测试答案5"
            }
        ],
        "statistics": {
            "total_score": 5,
            "completion_rate": 100,
            "submission_time": datetime.now().isoformat()
        }
    }
    
    try:
        # 发送POST请求
        url = "http://localhost:5002/api/submit"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        print("正在提交测试数据...")
        print(f"URL: {url}")
        print(f"数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 提交成功!")
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if 'id' in result or 'record_id' in result:
                record_id = result.get('id') or result.get('record_id')
                print(f"\n记录ID: {record_id}")
                return record_id
        else:
            print(f"❌ 提交失败")
            try:
                error_data = response.json()
                print(f"错误信息: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"错误信息: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到服务器，请确保Flask服务器正在运行")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        
    return None

def verify_data_in_database(record_id=None):
    """验证数据是否正确存储到数据库"""
    import sqlite3
    
    try:
        conn = sqlite3.connect('backend/questionnaires.db')
        cursor = conn.cursor()
        
        if record_id:
            cursor.execute('''
                SELECT name, parent_phone, parent_wechat, parent_email, gender, birthdate, created_at 
                FROM questionnaires 
                WHERE id = ? AND type = "parent_interview"
            ''', (record_id,))
        else:
            cursor.execute('''
                SELECT id, name, parent_phone, parent_wechat, parent_email, gender, birthdate, created_at 
                FROM questionnaires 
                WHERE type = "parent_interview" 
                ORDER BY created_at DESC 
                LIMIT 1
            ''')
        
        result = cursor.fetchone()
        if result:
            if record_id:
                name, phone, wechat, email, gender, birthdate, created_at = result
                print(f"\n✅ 数据库验证成功:")
                print(f"  记录ID: {record_id}")
            else:
                record_id, name, phone, wechat, email, gender, birthdate, created_at = result
                print(f"\n✅ 数据库验证成功:")
                print(f"  记录ID: {record_id}")
            
            print(f"  姓名: {name}")
            print(f"  家长手机: {phone}")
            print(f"  家长微信: {wechat}")
            print(f"  家长邮箱: {email}")
            print(f"  性别: {gender}")
            print(f"  出生日期: {birthdate}")
            print(f"  创建时间: {created_at}")
        else:
            print(f"❌ 数据库中未找到记录")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库验证失败: {e}")

if __name__ == '__main__':
    print("=== 家长访谈表数据提交测试 ===")
    record_id = test_parent_interview_submission()
    
    print("\n=== 数据库验证 ===")
    verify_data_in_database(record_id)