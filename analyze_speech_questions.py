import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('backend/questionnaires.db')
cursor = conn.cursor()

# 查询说话习惯记录
cursor.execute("SELECT id, data FROM questionnaires WHERE type = 'speech_habit' LIMIT 1")
result = cursor.fetchone()

if result:
    record_id, data_str = result
    print(f"说话习惯记录 ID: {record_id}")
    
    try:
        data = json.loads(data_str)
        questions = data.get('questions', [])
        
        print(f"\n问题总数: {len(questions)}")
        print("\n问题详细结构:")
        
        for i, q in enumerate(questions):
            print(f"\n问题 {i+1}:")
            print(f"  ID: {q.get('id')}")
            print(f"  Question: {q.get('question')}")
            print(f"  Type: {q.get('type')}")
            print(f"  Options: {len(q.get('options', []))} 个选项")
            
            for j, opt in enumerate(q.get('options', [])):
                print(f"    选项 {j+1}: {opt.get('value')} - {opt.get('text')}")
            
            print(f"  Selected: {q.get('selected')}")
            print(f"  Selected_texts: {q.get('selected_texts')}")
            print(f"  Allow_multiple: {q.get('allow_multiple')}")
            print(f"  Is_multiple_choice: {q.get('is_multiple_choice')}")
            
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
else:
    print("未找到说话习惯记录")

conn.close()