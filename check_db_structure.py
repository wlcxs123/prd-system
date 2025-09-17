import sqlite3

def check_database_structure():
    try:
        conn = sqlite3.connect('backend/questionnaires.db')
        cursor = conn.cursor()
        
        # 检查questionnaires表结构
        cursor.execute('PRAGMA table_info(questionnaires)')
        columns = cursor.fetchall()
        
        print('=== questionnaires表结构 ===')
        for col in columns:
            print(f'{col[1]} - {col[2]} (nullable: {"YES" if col[3] == 0 else "NO"})')
        
        # 检查是否包含家长联系方式字段
        column_names = [col[1] for col in columns]
        required_fields = ['parent_phone', 'parent_wechat', 'parent_email']
        
        print('\n=== 家长联系方式字段检查 ===')
        for field in required_fields:
            if field in column_names:
                print(f'✓ {field} - 存在')
            else:
                print(f'✗ {field} - 缺失')
        
        # 检查basic_info字段的JSON结构
        cursor.execute('SELECT basic_info FROM questionnaires WHERE type = "parent_interview" LIMIT 1')
        result = cursor.fetchone()
        if result:
            import json
            try:
                basic_info = json.loads(result[0])
                print('\n=== basic_info JSON结构示例 ===')
                for key, value in basic_info.items():
                    print(f'{key}: {value}')
            except json.JSONDecodeError:
                print('\n=== basic_info 不是有效的JSON格式 ===')
                print(result[0])
        
        conn.close()
        
    except Exception as e:
        print(f'检查数据库时出错: {e}')

if __name__ == '__main__':
    check_database_structure()