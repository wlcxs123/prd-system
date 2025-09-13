import sqlite3
import json

conn = sqlite3.connect('questionnaires.db')
cursor = conn.cursor()

# 检查最新的问卷数据
cursor.execute('SELECT id, name, parent_phone, parent_wechat, parent_email, data FROM questionnaires ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()

if result:
    print(f'最新问卷数据:')
    print(f'ID: {result[0]}')
    print(f'姓名: {result[1]}')
    print(f'家长手机: {result[2]}')
    print(f'家长微信: {result[3]}')
    print(f'家长邮箱: {result[4]}')
    
    # 解析JSON数据
    try:
        data = json.loads(result[5])
        basic_info = data.get('basic_info', {})
        print(f'\nbasic_info中的家长信息:')
        print(f'parent_phone: {basic_info.get("parent_phone", "未找到")}')
        print(f'parent_wechat: {basic_info.get("parent_wechat", "未找到")}')
        print(f'parent_email: {basic_info.get("parent_email", "未找到")}')
    except Exception as e:
        print(f'解析JSON数据失败: {e}')
else:
    print('数据库中没有问卷数据')

conn.close()