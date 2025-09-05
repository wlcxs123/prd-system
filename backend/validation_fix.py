"""
修复验证模块中的年级验证问题
"""

def fix_grade_validation():
    """修复年级验证的正则表达式"""
    import re
    
    # 读取原文件
    with open('backend/validation.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找并替换年级验证部分
    pattern = r'grade = fields\.Str\(\s*required=True,\s*validate=\[.*?\],\s*error_messages=\{\'required\': \'年级不能为空\'\}\s*\)'
    
    replacement = '''grade = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=50, error="年级长度必须在1-50个字符之间"),
        error_messages={'required': '年级不能为空'}
    )'''
    
    # 执行替换
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 如果没有找到匹配，尝试更简单的替换
    if new_content == content:
        # 查找年级字段的开始
        start_pattern = r'grade = fields\.Str\('
        end_pattern = r'\s*\)'
        
        # 找到年级字段的位置
        start_match = re.search(start_pattern, content)
        if start_match:
            start_pos = start_match.start()
            # 从开始位置查找对应的结束括号
            bracket_count = 0
            pos = start_pos
            while pos < len(content):
                if content[pos] == '(':
                    bracket_count += 1
                elif content[pos] == ')':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = pos + 1
                        break
                pos += 1
            
            if bracket_count == 0:
                # 替换整个字段定义
                new_content = content[:start_pos] + replacement + content[end_pos:]
    
    # 写回文件
    with open('backend/validation.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("年级验证已修复")

if __name__ == "__main__":
    fix_grade_validation()