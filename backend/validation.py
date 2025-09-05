"""
数据验证模块
实现前端和后端的数据验证功能，支持多种问题类型
"""

from marshmallow import Schema, fields, validate, ValidationError, post_load, pre_load
from datetime import datetime, date
import re
import json
from question_types import question_processor

class BasicInfoSchema(Schema):
    """基本信息验证Schema - 增强版本"""
    name = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=1, max=50, error="姓名长度必须在1-50个字符之间"),
            validate.Regexp(r'^[\u4e00-\u9fa5a-zA-Z\s]+$', error="姓名只能包含中文、英文字母和空格")
        ],
        error_messages={'required': '姓名不能为空'}
    )
    grade = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=50, error="年级长度必须在1-50个字符之间"),
        error_messages={'required': '年级不能为空'}
    )
    submission_date = fields.Date(
        required=True,
        error_messages={'required': '提交日期不能为空', 'invalid': '日期格式不正确'}
    )
    age = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1, max=150, error="年龄必须在1-150之间")
    )
    gender = fields.Str(
        allow_none=True,
        validate=validate.OneOf(['男', '女', 'M', 'F', 'Male', 'Female'], error="性别必须为'男'、'女'、'M'、'F'、'Male'或'Female'")
    )
    birth_date = fields.Date(
        allow_none=True,
        error_messages={'invalid': '出生日期格式不正确'}
    )
    school = fields.Str(
        allow_none=True,
        validate=validate.Length(max=100, error="学校名称不能超过100个字符")
    )
    class_name = fields.Str(
        allow_none=True,
        validate=validate.Length(max=50, error="班级名称不能超过50个字符")
    )
    
    @post_load
    def validate_dates(self, data, **kwargs):
        """验证日期逻辑"""
        submission_date = data.get('submission_date')
        birth_date = data.get('birth_date')
        age = data.get('age')
        
        # 验证提交日期不能是未来日期
        if submission_date and submission_date > date.today():
            raise ValidationError({'submission_date': '提交日期不能是未来日期'})
        
        # 验证出生日期和年龄的一致性
        if birth_date and age:
            calculated_age = (date.today() - birth_date).days // 365
            if abs(calculated_age - age) > 1:  # 允许1岁的误差
                raise ValidationError({'age': '年龄与出生日期不匹配'})
        
        # 验证出生日期合理性
        if birth_date:
            if birth_date > date.today():
                raise ValidationError({'birth_date': '出生日期不能是未来日期'})
            if birth_date < date(1900, 1, 1):
                raise ValidationError({'birth_date': '出生日期不能早于1900年'})
        
        return data
    
    @pre_load
    def normalize_basic_info(self, data, **kwargs):
        """预处理基本信息数据"""
        # 标准化姓名（去除多余空格）
        if 'name' in data and data['name']:
            data['name'] = re.sub(r'\s+', ' ', str(data['name']).strip())
        
        # 标准化性别
        if 'gender' in data and data['gender']:
            gender_map = {
                'male': '男', 'female': '女', 'm': '男', 'f': '女',
                '1': '男', '0': '女', 'boy': '男', 'girl': '女'
            }
            gender_lower = str(data['gender']).lower()
            if gender_lower in gender_map:
                data['gender'] = gender_map[gender_lower]
        
        return data

class MultipleChoiceOptionSchema(Schema):
    """选择题选项Schema"""
    value = fields.Raw(required=True)  # 可以是数字或字符串
    text = fields.Str(required=True, validate=validate.Length(min=1, max=200))

class MultipleChoiceQuestionSchema(Schema):
    """选择题Schema - 增强版本"""
    id = fields.Int(required=True, validate=validate.Range(min=1, max=9999, error="问题ID必须在1-9999之间"))
    type = fields.Str(required=True, validate=validate.Equal('multiple_choice'))
    question = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=1, max=500, error="问题文本长度必须在1-500个字符之间"),
            validate.Regexp(r'^(?!\s*$).+', error="问题文本不能只包含空白字符")
        ]
    )
    options = fields.List(
        fields.Nested(MultipleChoiceOptionSchema), 
        required=True,
        validate=validate.Length(min=1, max=20, error="选项数量必须在1-20之间")
    )
    selected = fields.List(
        fields.Raw(), 
        required=True,
        validate=validate.Length(min=1, max=10, error="选择的答案数量必须在1-10之间")
    )
    can_speak = fields.Bool(allow_none=True)
    is_required = fields.Bool(load_default=True)  # 是否必答题
    allow_multiple = fields.Bool(load_default=False)  # 是否允许多选
    section = fields.Str(allow_none=True, validate=validate.Length(max=50))  # 问题所属章节
    
    @post_load
    def validate_question_logic(self, data, **kwargs):
        """验证问题逻辑"""
        options = data.get('options', [])
        selected = data.get('selected', [])
        allow_multiple = data.get('allow_multiple', False)
        
        # 验证选项唯一性
        option_values = [opt['value'] for opt in options]
        if len(option_values) != len(set(option_values)):
            raise ValidationError("选项值不能重复")
        
        # 验证选项文本唯一性
        option_texts = [opt['text'].strip().lower() for opt in options]
        if len(option_texts) != len(set(option_texts)):
            raise ValidationError("选项文本不能重复")
        
        # 验证选中的选项是否在有效选项范围内
        valid_values = [opt['value'] for opt in options]
        for selected_value in selected:
            if selected_value not in valid_values:
                raise ValidationError(f"选中的选项 '{selected_value}' 不在有效选项范围内")
        
        # 验证单选/多选逻辑
        if not allow_multiple and len(selected) > 1:
            raise ValidationError("该题为单选题，不能选择多个答案")
        
        # 验证必答题逻辑
        if data.get('is_required', True) and not selected:
            raise ValidationError("该题为必答题，必须选择答案")
        
        return data
    
    @pre_load
    def normalize_question_data(self, data, **kwargs):
        """预处理问题数据"""
        # 标准化问题文本
        if 'question' in data and data['question']:
            data['question'] = str(data['question']).strip()
        
        # 确保selected是列表
        if 'selected' in data and not isinstance(data['selected'], list):
            data['selected'] = [data['selected']] if data['selected'] is not None else []
        
        return data

class TextInputQuestionSchema(Schema):
    """填空题Schema - 增强版本"""
    id = fields.Int(required=True, validate=validate.Range(min=1, max=9999, error="问题ID必须在1-9999之间"))
    type = fields.Str(required=True, validate=validate.Equal('text_input'))
    question = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=1, max=500, error="问题文本长度必须在1-500个字符之间"),
            validate.Regexp(r'^(?!\s*$).+', error="问题文本不能只包含空白字符")
        ]
    )
    answer = fields.Str(
        required=False,
        validate=validate.Length(min=0, max=5000, error="答案长度必须在0-5000个字符之间"),
        allow_none=True,
        load_default=''
    )
    max_length = fields.Int(
        allow_none=True, 
        validate=validate.Range(min=1, max=10000, error="最大长度必须在1-10000之间")
    )
    min_length = fields.Int(
        allow_none=True,
        validate=validate.Range(min=0, max=1000, error="最小长度必须在0-1000之间")
    )
    is_required = fields.Bool(load_default=True)
    input_type = fields.Str(
        load_default='text',
        validate=validate.OneOf(['text', 'textarea', 'number', 'email', 'phone'], error="输入类型无效")
    )
    placeholder = fields.Str(allow_none=True, validate=validate.Length(max=200))
    section = fields.Str(allow_none=True, validate=validate.Length(max=50))
    
    @post_load
    def validate_text_input_logic(self, data, **kwargs):
        """验证填空题逻辑"""
        answer = data.get('answer', '').strip()
        max_length = data.get('max_length')
        min_length = data.get('min_length', 0)
        input_type = data.get('input_type', 'text')
        is_required = data.get('is_required', True)
        
        # 验证必答题逻辑
        if is_required and not answer and answer != '':
            raise ValidationError("该题为必答题，答案不能为空")
        
        # 验证长度限制
        if max_length and len(answer) > max_length:
            raise ValidationError(f"答案长度不能超过{max_length}个字符")
        
        if min_length and len(answer) < min_length:
            raise ValidationError(f"答案长度不能少于{min_length}个字符")
        
        # 验证长度限制的逻辑性
        if max_length and min_length and min_length > max_length:
            raise ValidationError("最小长度不能大于最大长度")
        
        # 根据输入类型验证答案格式
        if answer and input_type == 'number':
            try:
                float(answer)
            except ValueError:
                raise ValidationError("数字类型的答案必须是有效数字")
        
        elif answer and input_type == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, answer):
                raise ValidationError("邮箱格式不正确")
        
        elif answer and input_type == 'phone':
            phone_pattern = r'^1[3-9]\d{9}$|^\d{3,4}-\d{7,8}$|^\+\d{1,3}-\d{1,14}$'
            if not re.match(phone_pattern, answer):
                raise ValidationError("电话号码格式不正确")
        
        return data
    
    @pre_load
    def normalize_text_input(self, data, **kwargs):
        """预处理填空题数据"""
        # 标准化答案（去除首尾空格，但保留内部空格）
        if 'answer' in data and data['answer'] is not None:
            data['answer'] = str(data['answer']).strip()
        
        return data

class RatingScaleQuestionSchema(Schema):
    """评分量表题Schema"""
    id = fields.Int(required=True, validate=validate.Range(min=1, max=9999, error="问题ID必须在1-9999之间"))
    type = fields.Str(required=True, validate=validate.Equal('rating_scale'))
    question = fields.Str(
        required=True, 
        validate=[
            validate.Length(min=1, max=500, error="问题文本长度必须在1-500个字符之间"),
            validate.Regexp(r'^(?!\s*$).+', error="问题文本不能只包含空白字符")
        ]
    )
    rating = fields.Int(
        required=False,
        allow_none=True,
        validate=validate.Range(min=0, max=10, error="评分必须在0-10之间")
    )
    can_speak = fields.Bool(allow_none=True)
    max_rating = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1, max=10, error="最大评分必须在1-10之间"),
        load_default=5
    )
    min_rating = fields.Int(
        allow_none=True,
        validate=validate.Range(min=0, max=9, error="最小评分必须在0-9之间"),
        load_default=0
    )
    scale_labels = fields.List(
        fields.Str(validate=validate.Length(max=50)),
        allow_none=True
    )
    is_required = fields.Bool(load_default=True)
    section = fields.Str(allow_none=True, validate=validate.Length(max=50))
    
    @post_load
    def validate_rating_scale_logic(self, data, **kwargs):
        """验证评分量表逻辑"""
        rating = data.get('rating')
        max_rating = data.get('max_rating', 5)
        min_rating = data.get('min_rating', 0)
        is_required = data.get('is_required', True)
        
        # 验证评分范围
        if rating is not None and (rating < min_rating or rating > max_rating):
            raise ValidationError(f"评分必须在{min_rating}-{max_rating}之间")
        
        # 验证必答题逻辑
        if is_required and rating is None:
            raise ValidationError("该题为必答题，必须提供评分")
        
        # 验证评分范围的逻辑性
        if min_rating >= max_rating:
            raise ValidationError("最小评分必须小于最大评分")
        
        # 验证标签数量
        scale_labels = data.get('scale_labels', [])
        if scale_labels:
            expected_labels = max_rating - min_rating + 1
            if len(scale_labels) != expected_labels:
                raise ValidationError(f"标签数量({len(scale_labels)})必须等于评分范围({expected_labels})")
        
        return data
    
    @pre_load
    def normalize_rating_scale(self, data, **kwargs):
        """预处理评分量表数据"""
        # 确保rating是整数
        if 'rating' in data and data['rating'] is not None:
            try:
                data['rating'] = int(data['rating'])
            except (ValueError, TypeError):
                pass  # 让后续验证处理错误
        
        return data

class StatisticsSchema(Schema):
    """统计信息Schema"""
    total_score = fields.Int(allow_none=True, validate=validate.Range(min=0, max=1000))
    completion_rate = fields.Int(allow_none=True, validate=validate.Range(min=0, max=100))
    submission_time = fields.DateTime(allow_none=True)

class FrankfurtScaleStatisticsSchema(Schema):
    """Frankfurt Scale统计信息Schema"""
    ds_total = fields.Int(validate=validate.Range(min=0, max=10), allow_none=True)
    ss_school_total = fields.Int(validate=validate.Range(min=0), allow_none=True)
    ss_public_total = fields.Int(validate=validate.Range(min=0), allow_none=True)
    ss_home_total = fields.Int(validate=validate.Range(min=0), allow_none=True)
    ss_total = fields.Int(validate=validate.Range(min=0), allow_none=True)
    age_group = fields.Str(validate=validate.OneOf(['3_7', '6_11', '12_18']), allow_none=True)
    risk_level = fields.Str(validate=validate.OneOf(['low', 'mid', 'high']), allow_none=True)
    completion_rate = fields.Int(validate=validate.Range(min=0, max=100), allow_none=True)
    submission_time = fields.DateTime(allow_none=True)

class QuestionnaireSchema(Schema):
    """完整问卷数据Schema"""
    type = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50, error="问卷类型长度必须在1-50个字符之间"),
        error_messages={'required': '问卷类型不能为空'}
    )
    basic_info = fields.Nested(BasicInfoSchema, required=True)
    questions = fields.List(
        fields.Raw(),  # 使用Raw字段，在post_load中进行类型判断
        required=True,
        validate=validate.Length(min=1, error="至少需要一个问题")
    )
    statistics = fields.Raw(allow_none=True)  # 使用Raw字段支持不同类型的统计信息
    
    @post_load
    def validate_questions(self, data, **kwargs):
        """验证问题列表，根据类型使用不同的Schema和问题类型处理器"""
        validated_questions = []
        questionnaire_type = data.get('type', '')
        
        for i, question in enumerate(data.get('questions', [])):
            try:
                question_type = question.get('type')
                
                # 对于Frankfurt Scale问卷，允许更灵活的验证
                if questionnaire_type == 'frankfurt_scale_selective_mutism':
                    # Frankfurt Scale问卷的特殊验证
                    if question_type == 'multiple_choice':
                        # 验证必要字段
                        if not question.get('question'):
                            raise ValidationError("问题文本不能为空")
                        if not question.get('options'):
                            raise ValidationError("选项不能为空")
                        if 'selected' not in question:
                            raise ValidationError("必须有选中答案")
                        
                        # 验证section字段（Frankfurt Scale特有）
                        section = question.get('section', '')
                        valid_sections = ['DS', 'SS_school', 'SS_public', 'SS_home']
                        if section not in valid_sections:
                            raise ValidationError(f"无效的section: {section}")
                        
                        validated_questions.append(question)
                    else:
                        raise ValidationError(f"Frankfurt Scale问卷不支持问题类型: {question_type}")
                else:
                    # 标准问卷验证
                    # 首先使用问题类型处理器进行验证
                    type_errors = question_processor.validate_question(question)
                    if type_errors:
                        raise ValidationError(type_errors)
                    
                    # 然后使用Marshmallow Schema进行详细验证
                    if question_type == 'multiple_choice':
                        schema = MultipleChoiceQuestionSchema()
                    elif question_type == 'text_input':
                        schema = TextInputQuestionSchema()
                    elif question_type == 'rating_scale':
                        schema = RatingScaleQuestionSchema()
                    else:
                        raise ValidationError(f"不支持的问题类型: {question_type}")
                    
                    validated_question = schema.load(question)
                    
                    # 使用问题类型处理器处理答案数据
                    processed_question = question_processor.process_question(validated_question)
                    validated_questions.append(processed_question)
                
            except ValidationError as e:
                # 为错误信息添加问题索引
                raise ValidationError({f'questions.{i}': e.messages})
        
        data['questions'] = validated_questions
        
        # 验证统计信息（如果是Frankfurt Scale）
        if questionnaire_type == 'frankfurt_scale_selective_mutism' and data.get('statistics'):
            try:
                stats_schema = FrankfurtScaleStatisticsSchema()
                validated_stats = stats_schema.load(data['statistics'])
                data['statistics'] = validated_stats
            except ValidationError as e:
                raise ValidationError({'statistics': e.messages})
        
        return data

# 数据标准化函数
def normalize_questionnaire_data(data):
    """
    标准化问卷数据格式
    确保数据结构符合系统标准
    """
    normalized = {}
    
    # 标准化问卷类型
    normalized['type'] = str(data.get('type', 'unknown')).strip().lower()
    
    # 标准化基本信息
    basic_info = data.get('basic_info', {})
    
    # 支持向后兼容 - 如果没有basic_info，从根级别提取
    if not basic_info and any(key in data for key in ['name', 'grade', 'submission_date']):
        basic_info = {
            'name': data.get('name', ''),
            'grade': data.get('grade', ''),
            'submission_date': data.get('submission_date', datetime.now().strftime('%Y-%m-%d'))
        }
        if 'age' in data:
            basic_info['age'] = data.get('age')
    
    # 标准化姓名和年级
    normalized['basic_info'] = {
        'name': str(basic_info.get('name', '')).strip(),
        'grade': str(basic_info.get('grade', '')).strip(),
        'submission_date': basic_info.get('submission_date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    if basic_info.get('age'):
        try:
            normalized['basic_info']['age'] = int(basic_info['age'])
        except (ValueError, TypeError):
            pass
    
    # 标准化问题列表
    questions = data.get('questions', [])
    normalized['questions'] = []
    
    for question in questions:
        normalized_question = normalize_question_data(question)
        if normalized_question:
            normalized['questions'].append(normalized_question)
    
    # 标准化统计信息
    statistics = data.get('statistics', {})
    if statistics:
        questionnaire_type = normalized.get('type', '')
        
        if questionnaire_type == 'frankfurt_scale_selective_mutism':
            # Frankfurt Scale 不使用 total_score 字段
            normalized['statistics'] = {
                'ds_total': statistics.get('ds_total'),
                'ss_school_total': statistics.get('ss_school_total'),
                'ss_public_total': statistics.get('ss_public_total'),
                'ss_home_total': statistics.get('ss_home_total'),
                'ss_total': statistics.get('ss_total'),
                'age_group': statistics.get('age_group'),
                'risk_level': statistics.get('risk_level'),
                'completion_rate': statistics.get('completion_rate', 100),
                'submission_time': statistics.get('submission_time', datetime.now())
            }
            # 移除None值
            normalized['statistics'] = {k: v for k, v in normalized['statistics'].items() if v is not None}
        else:
            # 其他问卷类型使用标准统计字段
            normalized['statistics'] = {
                'total_score': statistics.get('total_score'),
                'completion_rate': statistics.get('completion_rate', 100),
                'submission_time': statistics.get('submission_time', datetime.now())
            }
    
    return normalized

def normalize_question_data(question):
    """标准化单个问题数据"""
    if not question or not question.get('type'):
        return None
    
    question_type = question.get('type')
    normalized = {
        'id': int(question.get('id', 0)),
        'type': question_type,
        'question': str(question.get('question', '')).strip()
    }
    
    if question_type == 'multiple_choice':
        # 标准化选择题
        options = question.get('options', [])
        normalized['options'] = []
        
        for option in options:
            if isinstance(option, dict):
                normalized['options'].append({
                    'value': option.get('value'),
                    'text': str(option.get('text', '')).strip()
                })
        
        # 标准化选中答案
        selected = question.get('selected', [])
        if not isinstance(selected, list):
            selected = [selected] if selected is not None else []
        normalized['selected'] = selected
        
        # 可选字段
        if 'can_speak' in question:
            normalized['can_speak'] = bool(question['can_speak'])
        
        # 保留allow_multiple字段
        if 'allow_multiple' in question:
            normalized['allow_multiple'] = bool(question['allow_multiple'])
        
        # 保留is_required字段
        if 'is_required' in question:
            normalized['is_required'] = bool(question['is_required'])
        
        # 保留section字段（Frankfurt Scale需要）
        if 'section' in question:
            normalized['section'] = str(question['section']).strip()
            
    elif question_type == 'text_input':
        # 标准化填空题
        normalized['answer'] = str(question.get('answer', '')).strip()
        
        if 'max_length' in question:
            try:
                normalized['max_length'] = int(question['max_length'])
            except (ValueError, TypeError):
                normalized['max_length'] = 1000
        
        # 保留is_required字段
        if 'is_required' in question:
            normalized['is_required'] = bool(question['is_required'])
        
        # 保留section字段（Frankfurt Scale需要）
        if 'section' in question:
            normalized['section'] = str(question['section']).strip()
    
    elif question_type == 'rating_scale':
        # 标准化评分量表
        if 'rating' in question:
            try:
                normalized['rating'] = float(question['rating'])
            except (ValueError, TypeError):
                normalized['rating'] = 0.0
        
        # 可选字段
        if 'can_speak' in question:
            normalized['can_speak'] = bool(question['can_speak'])
        
        if 'max_rating' in question:
            try:
                normalized['max_rating'] = float(question['max_rating'])
            except (ValueError, TypeError):
                normalized['max_rating'] = 5.0
        
        if 'min_rating' in question:
            try:
                normalized['min_rating'] = float(question['min_rating'])
            except (ValueError, TypeError):
                normalized['min_rating'] = 0.0
        
        # 保留is_required字段
        if 'is_required' in question:
            normalized['is_required'] = bool(question['is_required'])
        
        # 保留section字段
        if 'section' in question:
            normalized['section'] = str(question['section']).strip()
    
    return normalized

# 数据完整性检查函数 - 增强版本
def check_data_integrity(data):
    """
    检查数据完整性 - 增强版本
    返回错误列表，如果为空则表示数据完整
    """
    errors = []
    
    # 检查数据结构完整性
    structure_errors = check_data_structure(data)
    errors.extend(structure_errors)
    
    # 检查基本信息完整性
    basic_info_errors = check_basic_info_integrity(data.get('basic_info', {}))
    errors.extend(basic_info_errors)
    
    # 检查问题完整性
    questions_errors = check_questions_integrity(data.get('questions', []))
    errors.extend(questions_errors)
    
    # 检查业务逻辑完整性
    business_logic_errors = check_business_logic_integrity(data)
    errors.extend(business_logic_errors)
    
    return errors

def check_data_structure(data):
    """检查数据结构完整性"""
    errors = []
    
    if not isinstance(data, dict):
        errors.append("数据必须是字典格式")
        return errors
    
    # 检查必需的顶级字段
    required_fields = ['type', 'basic_info', 'questions']
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")
    
    # 检查字段类型
    if 'basic_info' in data and not isinstance(data['basic_info'], dict):
        errors.append("basic_info必须是字典格式")
    
    if 'questions' in data and not isinstance(data['questions'], list):
        errors.append("questions必须是列表格式")
    
    if 'statistics' in data and data['statistics'] is not None and not isinstance(data['statistics'], dict):
        errors.append("statistics必须是字典格式或null")
    
    return errors

def check_basic_info_integrity(basic_info):
    """检查基本信息完整性"""
    errors = []
    
    if not isinstance(basic_info, dict):
        errors.append("基本信息必须是字典格式")
        return errors
    
    # 检查必需字段
    required_fields = ['name', 'grade', 'submission_date']
    for field in required_fields:
        if not basic_info.get(field, ''):
            errors.append(f"基本信息中缺少必需字段: {field}")
    
    # 检查字段值的合理性
    name = basic_info.get('name', '').strip()
    if name and len(name) > 50:
        errors.append("姓名长度不能超过50个字符")
    
    grade = basic_info.get('grade', '').strip()
    if grade and len(grade) > 20:
        errors.append("年级长度不能超过20个字符")
    
    # 检查年龄合理性
    age = basic_info.get('age')
    if age is not None:
        try:
            age_int = int(age)
            if age_int < 1 or age_int > 150:
                errors.append("年龄必须在1-150之间")
        except (ValueError, TypeError):
            errors.append("年龄必须是有效数字")
    
    return errors

def check_questions_integrity(questions):
    """检查问题列表完整性"""
    errors = []
    
    if not isinstance(questions, list):
        errors.append("问题列表必须是列表格式")
        return errors
    
    if not questions:
        errors.append("至少需要一个问题")
        return errors
    
    # 检查问题数量限制
    if len(questions) > 100:
        errors.append("问题数量不能超过100个")
    
    # 检查问题ID唯一性
    question_ids = []
    for i, question in enumerate(questions):
        if isinstance(question, dict) and 'id' in question:
            qid = question['id']
            if qid in question_ids:
                errors.append(f"问题ID重复: {qid}")
            else:
                question_ids.append(qid)
        
        # 检查单个问题完整性
        question_errors = check_question_integrity(question, i + 1)
        errors.extend(question_errors)
    
    return errors

def check_business_logic_integrity(data):
    """检查业务逻辑完整性"""
    errors = []
    
    questionnaire_type = data.get('type', '')
    questions = data.get('questions', [])
    
    # 根据问卷类型检查特定的业务逻辑
    if questionnaire_type == 'frankfurt_scale_selective_mutism':
        # Frankfurt Scale特定验证
        required_sections = ['DS', 'SS_school', 'SS_public', 'SS_home']
        found_sections = set()
        
        for question in questions:
            if isinstance(question, dict):
                section = question.get('section', '')
                if section in required_sections:
                    found_sections.add(section)
        
        missing_sections = set(required_sections) - found_sections
        if missing_sections:
            errors.append(f"Frankfurt Scale问卷缺少必需的章节: {', '.join(missing_sections)}")
    
    elif questionnaire_type in ['parent_interview', 'student_report']:
        # 检查是否有足够的问题（放宽限制，允许测试数据）
        if len(questions) < 1:
            errors.append(f"{questionnaire_type}问卷至少需要1个问题")
    
    # 检查统计信息的一致性
    statistics = data.get('statistics', {})
    if statistics and isinstance(statistics, dict):
        completion_rate = statistics.get('completion_rate')
        if completion_rate is not None:
            try:
                rate = float(completion_rate)
                if rate < 0 or rate > 100:
                    errors.append("完成率必须在0-100之间")
            except (ValueError, TypeError):
                errors.append("完成率必须是有效数字")
    
    return errors

def check_question_integrity(question, question_num):
    """检查单个问题的完整性 - 增强版本"""
    errors = []
    
    if not isinstance(question, dict):
        errors.append(f"第{question_num}题必须是字典格式")
        return errors
    
    # 检查必需字段
    required_fields = ['id', 'type', 'question']
    for field in required_fields:
        if field not in question:
            errors.append(f"第{question_num}题缺少必需字段: {field}")
    
    # 检查问题文本
    question_text = question.get('question', '').strip()
    if not question_text:
        errors.append(f"第{question_num}题问题文本不能为空")
    elif len(question_text) > 500:
        errors.append(f"第{question_num}题问题文本长度不能超过500个字符")
    
    # 检查问题ID
    question_id = question.get('id')
    if question_id is not None:
        try:
            qid = int(question_id)
            if qid < 1 or qid > 9999:
                errors.append(f"第{question_num}题ID必须在1-9999之间")
        except (ValueError, TypeError):
            errors.append(f"第{question_num}题ID必须是有效数字")
    
    question_type = question.get('type')
    
    if question_type == 'multiple_choice':
        errors.extend(check_multiple_choice_integrity(question, question_num))
    elif question_type == 'text_input':
        errors.extend(check_text_input_integrity(question, question_num))
    elif question_type:
        errors.append(f"第{question_num}题类型不支持: {question_type}")
    else:
        errors.append(f"第{question_num}题缺少问题类型")
    
    return errors

def check_multiple_choice_integrity(question, question_num):
    """检查选择题完整性"""
    errors = []
    
    options = question.get('options', [])
    selected = question.get('selected', [])
    
    # 检查选项
    if not options:
        errors.append(f"第{question_num}题至少需要一个选项")
    elif not isinstance(options, list):
        errors.append(f"第{question_num}题选项必须是列表格式")
    else:
        if len(options) > 20:
            errors.append(f"第{question_num}题选项数量不能超过20个")
        
        # 检查每个选项的格式
        option_values = []
        option_texts = []
        for i, option in enumerate(options):
            if not isinstance(option, dict):
                errors.append(f"第{question_num}题第{i+1}个选项必须是字典格式")
                continue
            
            if 'value' not in option:
                errors.append(f"第{question_num}题第{i+1}个选项缺少value字段")
            else:
                option_values.append(option['value'])
            
            if 'text' not in option:
                errors.append(f"第{question_num}题第{i+1}个选项缺少text字段")
            else:
                text = str(option['text']).strip()
                if not text:
                    errors.append(f"第{question_num}题第{i+1}个选项文本不能为空")
                elif len(text) > 200:
                    errors.append(f"第{question_num}题第{i+1}个选项文本长度不能超过200个字符")
                else:
                    option_texts.append(text.lower())
        
        # 检查选项值唯一性
        if len(option_values) != len(set(option_values)):
            errors.append(f"第{question_num}题选项值不能重复")
        
        # 检查选项文本唯一性
        if len(option_texts) != len(set(option_texts)):
            errors.append(f"第{question_num}题选项文本不能重复")
    
    # 检查选中答案
    if not isinstance(selected, list):
        errors.append(f"第{question_num}题选中答案必须是列表格式")
    elif not selected:
        # 检查是否为必答题
        is_required = question.get('is_required', True)
        if is_required:
            errors.append(f"第{question_num}题必须选择答案")
    else:
        if len(selected) > 10:
            errors.append(f"第{question_num}题选择的答案数量不能超过10个")
        
        # 检查选中的答案是否在有效选项中
        if options:
            valid_values = [opt.get('value') for opt in options if isinstance(opt, dict) and 'value' in opt]
            for sel in selected:
                if sel not in valid_values:
                    errors.append(f"第{question_num}题选中的答案'{sel}'不在有效选项中")
                    break
        
        # 检查单选/多选逻辑
        allow_multiple = question.get('allow_multiple', False)
        if not allow_multiple and len(selected) > 1:
            errors.append(f"第{question_num}题为单选题，不能选择多个答案")
    
    return errors

def check_text_input_integrity(question, question_num):
    """检查填空题完整性"""
    errors = []
    
    answer = question.get('answer', '')
    max_length = question.get('max_length')
    min_length = question.get('min_length', 0)
    input_type = question.get('input_type', 'text')
    is_required = question.get('is_required', True)
    
    # 检查答案
    if not isinstance(answer, str):
        answer = str(answer) if answer is not None else ''
    
    answer = answer.strip()
    
    if is_required and not answer:
        errors.append(f"第{question_num}题为必答题，答案不能为空")
    
    if answer:
        # 检查长度限制
        if len(answer) > 5000:
            errors.append(f"第{question_num}题答案长度不能超过5000个字符")
        
        if max_length and len(answer) > max_length:
            errors.append(f"第{question_num}题答案长度不能超过{max_length}个字符")
        
        if min_length and len(answer) < min_length:
            errors.append(f"第{question_num}题答案长度不能少于{min_length}个字符")
        
        # 根据输入类型验证格式
        if input_type == 'number':
            try:
                float(answer)
            except ValueError:
                errors.append(f"第{question_num}题答案必须是有效数字")
        
        elif input_type == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, answer):
                errors.append(f"第{question_num}题答案必须是有效邮箱格式")
        
        elif input_type == 'phone':
            phone_pattern = r'^1[3-9]\d{9}$|^\d{3,4}-\d{7,8}$|^\+\d{1,3}-\d{1,14}$'
            if not re.match(phone_pattern, answer):
                errors.append(f"第{question_num}题答案必须是有效电话号码格式")
    
    # 检查长度限制的逻辑性
    if max_length and min_length and min_length > max_length:
        errors.append(f"第{question_num}题最小长度不能大于最大长度")
    
    # 检查输入类型
    valid_input_types = ['text', 'textarea', 'number', 'email', 'phone']
    if input_type not in valid_input_types:
        errors.append(f"第{question_num}题输入类型无效: {input_type}")
    
    return errors

# 验证工具函数
def validate_questionnaire_with_schema(data):
    """
    使用Marshmallow Schema验证问卷数据
    返回 (is_valid, errors, validated_data)
    """
    try:
        schema = QuestionnaireSchema()
        validated_data = schema.load(data)
        return True, [], validated_data
    except ValidationError as e:
        return False, e.messages, None

def create_validation_error_response(errors):
    """创建标准的验证错误响应"""
    return {
        'success': False,
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': '数据验证失败',
            'details': errors if isinstance(errors, list) else [str(errors)]
        },
        'timestamp': datetime.now().isoformat()
    }

# 快速验证函数（用于简单场景）
def quick_validate(data):
    """
    快速验证函数，返回错误列表
    结合了Schema验证和完整性检查
    """
    # 首先进行数据标准化
    try:
        normalized_data = normalize_questionnaire_data(data)
    except Exception as e:
        return [f"数据标准化失败: {str(e)}"]
    
    # 使用Schema验证
    is_valid, schema_errors, _ = validate_questionnaire_with_schema(normalized_data)
    if not is_valid:
        # 将嵌套的错误信息展平
        flat_errors = []
        def flatten_errors(errors, prefix=""):
            if isinstance(errors, dict):
                for key, value in errors.items():
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    flatten_errors(value, new_prefix)
            elif isinstance(errors, list):
                for error in errors:
                    if isinstance(error, str):
                        flat_errors.append(f"{prefix}: {error}" if prefix else error)
                    else:
                        flatten_errors(error, prefix)
            else:
                flat_errors.append(f"{prefix}: {errors}" if prefix else str(errors))
        
        flatten_errors(schema_errors)
        return flat_errors
    
    # 进行完整性检查
    integrity_errors = check_data_integrity(normalized_data)
    
    return integrity_errors