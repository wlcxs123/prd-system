import sqlite3

def check_parent_interview_data():
    try:
        conn = sqlite3.connect('backend/questionnaires.db')
        cursor = conn.cursor()
        
        # 检查家长访谈表的记录
        cursor.execute('''
            SELECT name, type, parent_phone, parent_wechat, parent_email, created_at 
            FROM questionnaires 
            WHERE type = "parent_interview" 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        
        rows = cursor.fetchall()
        print(f"找到 {len(rows)} 条家长访谈表记录:")
        print("-" * 80)
        
        for i, row in enumerate(rows, 1):
            name, qtype, phone, wechat, email, created_at = row
            print(f"记录 {i}:")
            print(f"  姓名: {name or '未填写'}")
            print(f"  类型: {qtype}")
            print(f"  手机: {phone or '未填写'}")
            print(f"  微信: {wechat or '未填写'}")
            print(f"  邮箱: {email or '未填写'}")
            print(f"  创建时间: {created_at}")
            print()
        
        # 检查其他类型问卷的家长联系方式情况
        cursor.execute('''
            SELECT type, COUNT(*) as total, 
                   COUNT(CASE WHEN parent_phone IS NOT NULL AND parent_phone != '' THEN 1 END) as has_phone,
                   COUNT(CASE WHEN parent_wechat IS NOT NULL AND parent_wechat != '' THEN 1 END) as has_wechat,
                   COUNT(CASE WHEN parent_email IS NOT NULL AND parent_email != '' THEN 1 END) as has_email
            FROM questionnaires 
            GROUP BY type
        ''')
        
        stats = cursor.fetchall()
        print("各类型问卷家长联系方式统计:")
        print("-" * 80)
        for stat in stats:
            qtype, total, has_phone, has_wechat, has_email = stat
            print(f"{qtype}: 总数={total}, 有手机={has_phone}, 有微信={has_wechat}, 有邮箱={has_email}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_parent_interview_data()