"""
问题类型处理模块
实现不同问题类型的数据处理逻辑
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import json

class QuestionTypeHandler(ABC):
    """问题类型处理器基类"""
    
    @abstractmethod
    def validate_question_data(self, question_data: Dict[str, Any]) -> List[str]:
        """验证问题数据，返回错误列表"""
        pass
    
    @abstractmethod
    def process_answer(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理答案数据，返回处理后的数据"""
        pass
    
    @abstractmethod
    def format_for_display(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化数据用于显示"""
        pass
    
    @abstractmethod
    def calculate_score(self, question_data: Dict[str, Any]) -> Optional[float]:
        """计算问题得分（如果适用）"""
        pass

class MultipleChoiceHandler(QuestionTypeHandler):
    """选择题处理器 - 支持单选和多选模式"""
    
    def validate_question_data(self, question_data: Dict[str, Any]) -> List[str]:
        """验证选择题数据"""
        errors = []
        
        # 验证基本字段
        if not question_data.get('question', '').strip():
            errors.append('问题文本不能为空')
        
        # 验证选项
        options = question_data.get('options', [])
        if not options:
            errors.append('至少需要一个选项')
        else:
            for i, option in enumerate(options):
                if not isinstance(option, dict):
                    errors.append(f'选项{i+1}格式不正确')
                    continue
                
                if 'value' not in option:
                    errors.append(f'选项{i+1}缺少值')
                
                if not option.get('text', '').strip():
                    errors.append(f'选项{i+1}文本不能为空')
        
        # 验证选中答案
        selected = question_data.get('selected', [])
        question_type = question_data.get('type', 'multiple_choice')
        
        # 对于single_choice类型，允许空选择（特别是Frankfurt Scale问卷的SS部分）
        if not selected and question_type != 'single_choice':
            errors.append('必须选择至少一个答案')
        elif selected:
            if not isinstance(selected, list):
                errors.append('选中答案格式不正确')
            else:
                valid_values = [opt.get('value') for opt in options if isinstance(opt, dict)]
                for sel in selected:
                    if sel not in valid_values:
                        errors.append(f'选中的答案无效: {sel}')
        
        # 验证单选/多选模式 (需求 2.1)
        if question_type == 'single_choice' and len(selected) > 1:
            errors.append('单选题只能选择一个答案')
        elif question_type == 'multiple_choice':
            is_multiple_choice = question_data.get('is_multiple_choice', len(selected) > 1)
            if not is_multiple_choice and len(selected) > 1:
                errors.append('单选题只能选择一个答案')
        
        return errors
    
    def process_answer(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理选择题答案 - 支持单选和多选模式 (需求 2.1)"""
        processed = question_data.copy()
        
        # 确保selected是列表格式
        selected = question_data.get('selected', [])
        if not isinstance(selected, list):
            selected = [selected] if selected is not None else []
        
        processed['selected'] = selected
        
        # 添加选中选项的文本
        options = question_data.get('options', [])
        selected_texts = []
        
        for sel_value in selected:
            for option in options:
                if isinstance(option, dict) and option.get('value') == sel_value:
                    selected_texts.append(option.get('text', ''))
                    break
        
        processed['selected_texts'] = selected_texts
        
        # 处理单选/多选标识 (需求 2.1)
        # 优先使用显式设置，否则根据选择数量判断
        is_multiple_choice = question_data.get('is_multiple_choice')
        if is_multiple_choice is None:
            is_multiple_choice = len(selected) > 1 or len(options) > 2
        
        processed['is_multiple_choice'] = is_multiple_choice
        processed['choice_mode'] = 'multiple' if is_multiple_choice else 'single'
        
        # 记录问题类型、题目内容和答案选项 (需求 2.3)
        processed['question_type_info'] = {
            'type': 'multiple_choice',
            'mode': processed['choice_mode'],
            'question_text': question_data.get('question', ''),
            'total_options': len(options),
            'selected_count': len(selected)
        }
        
        return processed
    
    def format_for_display(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化选择题用于显示"""
        formatted = {
            'question': question_data.get('question', ''),
            'type': 'multiple_choice',
            'options': question_data.get('options', []),
            'selected': question_data.get('selected', []),
            'selected_texts': question_data.get('selected_texts', [])
        }
        
        # 添加可读性更好的答案描述
        if formatted['selected_texts']:
            formatted['answer_display'] = ', '.join(formatted['selected_texts'])
        else:
            formatted['answer_display'] = '未选择'
        
        return formatted
    
    def calculate_score(self, question_data: Dict[str, Any]) -> Optional[float]:
        """计算选择题得分"""
        # 基础得分逻辑：有选择答案得1分，否则得0分
        selected = question_data.get('selected', [])
        return 1.0 if selected else 0.0

class TextInputHandler(QuestionTypeHandler):
    """填空题处理器 - 支持短文本和长文本输入"""
    
    def validate_question_data(self, question_data: Dict[str, Any]) -> List[str]:
        """验证填空题数据 (需求 2.2, 2.4)"""
        errors = []
        
        # 验证基本字段
        if not question_data.get('question', '').strip():
            errors.append('问题文本不能为空')
        
        # 验证答案
        answer = question_data.get('answer', '').strip()
        if not answer:
            errors.append('答案不能为空')
        
        # 验证文本类型和长度限制 (需求 2.2)
        text_type = question_data.get('text_type', 'short')  # 'short' 或 'long'
        max_length = question_data.get('max_length')
        
        # 根据文本类型设置默认长度限制
        if max_length is None:
            if text_type == 'short':
                max_length = 200  # 短文本默认200字符
            else:  # long
                max_length = 2000  # 长文本默认2000字符
        
        if isinstance(max_length, (int, str)):
            try:
                max_length = int(max_length)
                if len(answer) > max_length:
                    errors.append(f'答案长度超过限制({max_length}个字符)')
                
                # 验证文本类型的合理性
                if text_type == 'short' and max_length > 500:
                    errors.append('短文本类型的最大长度不应超过500字符')
                elif text_type == 'long' and max_length < 100:
                    errors.append('长文本类型的最大长度不应少于100字符')
                    
            except ValueError:
                errors.append('最大长度设置不正确')
        
        # 验证文本类型值
        if text_type not in ['short', 'long']:
            errors.append('文本类型必须是 "short" 或 "long"')
        
        return errors
    
    def process_answer(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理填空题答案 - 支持短文本和长文本 (需求 2.2)"""
        processed = question_data.copy()
        
        # 清理答案文本
        answer = str(question_data.get('answer', '')).strip()
        processed['answer'] = answer
        
        # 确定文本类型 (需求 2.2)
        text_type = question_data.get('text_type', 'short')
        max_length = question_data.get('max_length')
        
        # 根据文本类型设置默认长度限制
        if max_length is None:
            if text_type == 'short':
                max_length = 200
            else:  # long
                max_length = 2000
        
        processed['text_type'] = text_type
        processed['max_length'] = max_length
        
        # 添加答案统计信息
        processed['answer_length'] = len(answer)
        processed['word_count'] = len(answer.split()) if answer else 0
        processed['line_count'] = len(answer.split('\n')) if answer else 0
        
        # 检查是否为空答案
        processed['is_empty'] = not bool(answer)
        
        # 文本类型分析
        processed['is_short_text'] = text_type == 'short'
        processed['is_long_text'] = text_type == 'long'
        processed['length_utilization'] = (len(answer) / max_length) * 100 if max_length > 0 else 0
        
        # 记录问题类型、题目内容和答案 (需求 2.3)
        processed['question_type_info'] = {
            'type': 'text_input',
            'text_type': text_type,
            'question_text': question_data.get('question', ''),
            'max_length': max_length,
            'actual_length': len(answer)
        }
        
        return processed
    
    def format_for_display(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化填空题用于显示"""
        answer = question_data.get('answer', '')
        
        formatted = {
            'question': question_data.get('question', ''),
            'type': 'text_input',
            'answer': answer,
            'answer_length': len(answer),
            'word_count': len(answer.split()) if answer else 0
        }
        
        # 添加答案预览（如果答案太长则截断）
        if len(answer) > 100:
            formatted['answer_preview'] = answer[:100] + '...'
        else:
            formatted['answer_preview'] = answer
        
        return formatted
    
    def calculate_score(self, question_data: Dict[str, Any]) -> Optional[float]:
        """计算填空题得分"""
        # 基础得分逻辑：有答案得1分，否则得0分
        answer = question_data.get('answer', '').strip()
        return 1.0 if answer else 0.0

class RatingScaleHandler(QuestionTypeHandler):
    """评分量表处理器 - 支持数值评分"""
    
    def validate_question_data(self, question_data: Dict[str, Any]) -> List[str]:
        """验证评分量表数据"""
        errors = []
        
        # 验证基本字段
        if not question_data.get('question', '').strip():
            errors.append('问题文本不能为空')
        
        # 验证评分
        rating = question_data.get('rating')
        if rating is None:
            errors.append('评分不能为空')
        else:
            try:
                rating = float(rating)
                if rating < 0 or rating > 10:
                    errors.append('评分必须在0-10之间')
            except (ValueError, TypeError):
                errors.append('评分必须是数字')
        
        # 验证评分范围设置
        max_rating = question_data.get('max_rating', 5)
        min_rating = question_data.get('min_rating', 0)
        
        try:
            max_rating = float(max_rating)
            min_rating = float(min_rating)
            if min_rating >= max_rating:
                errors.append('最小评分必须小于最大评分')
        except (ValueError, TypeError):
            errors.append('评分范围设置不正确')
        
        return errors
    
    def process_answer(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理评分量表答案"""
        processed = question_data.copy()
        
        # 处理评分
        rating = question_data.get('rating')
        if rating is not None:
            try:
                processed['rating'] = float(rating)
            except (ValueError, TypeError):
                processed['rating'] = 0.0
        
        # 设置评分范围
        processed['max_rating'] = float(question_data.get('max_rating', 5))
        processed['min_rating'] = float(question_data.get('min_rating', 0))
        
        # 计算评分百分比
        rating_range = processed['max_rating'] - processed['min_rating']
        if rating_range > 0:
            processed['rating_percentage'] = ((processed['rating'] - processed['min_rating']) / rating_range) * 100
        else:
            processed['rating_percentage'] = 0
        
        # 处理can_speak字段（如果存在）
        if 'can_speak' in question_data:
            processed['can_speak'] = bool(question_data['can_speak'])
        
        # 记录问题类型信息
        processed['question_type_info'] = {
            'type': 'rating_scale',
            'question_text': question_data.get('question', ''),
            'rating_range': f"{processed['min_rating']}-{processed['max_rating']}",
            'actual_rating': processed['rating']
        }
        
        return processed
    
    def format_for_display(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化评分量表用于显示"""
        rating = question_data.get('rating', 0)
        max_rating = question_data.get('max_rating', 5)
        min_rating = question_data.get('min_rating', 0)
        
        formatted = {
            'question': question_data.get('question', ''),
            'type': 'rating_scale',
            'rating': rating,
            'max_rating': max_rating,
            'min_rating': min_rating,
            'rating_display': f"{rating}/{max_rating}"
        }
        
        # 添加can_speak信息（如果存在）
        if 'can_speak' in question_data:
            formatted['can_speak'] = question_data['can_speak']
            formatted['can_speak_display'] = '能说话' if question_data['can_speak'] else '不能说话'
        
        return formatted
    
    def calculate_score(self, question_data: Dict[str, Any]) -> Optional[float]:
        """计算评分量表得分"""
        rating = question_data.get('rating', 0)
        max_rating = question_data.get('max_rating', 5)
        
        # 返回标准化得分（0-1之间）
        if max_rating > 0:
            return float(rating) / float(max_rating)
        return 0.0

class QuestionTypeProcessor:
    """问题类型处理器管理类"""
    
    def __init__(self):
        self.handlers = {
            'multiple_choice': MultipleChoiceHandler(),
            'single_choice': MultipleChoiceHandler(),  # 单选题使用相同的处理器
            'text_input': TextInputHandler(),
            'rating_scale': RatingScaleHandler()
        }
    
    def get_handler(self, question_type: str) -> Optional[QuestionTypeHandler]:
        """获取问题类型处理器"""
        return self.handlers.get(question_type)
    
    def validate_question(self, question_data: Dict[str, Any]) -> List[str]:
        """验证问题数据"""
        question_type = question_data.get('type')
        handler = self.get_handler(question_type)
        
        if not handler:
            return [f'不支持的问题类型: {question_type}']
        
        return handler.validate_question_data(question_data)
    
    def process_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理问题数据"""
        question_type = question_data.get('type')
        handler = self.get_handler(question_type)
        
        if not handler:
            return question_data
        
        return handler.process_answer(question_data)
    
    def format_question_for_display(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化问题用于显示"""
        question_type = question_data.get('type')
        handler = self.get_handler(question_type)
        
        if not handler:
            return question_data
        
        return handler.format_for_display(question_data)
    
    def calculate_question_score(self, question_data: Dict[str, Any]) -> Optional[float]:
        """计算问题得分"""
        question_type = question_data.get('type')
        handler = self.get_handler(question_type)
        
        if not handler:
            return None
        
        return handler.calculate_score(question_data)
    
    def process_questionnaire(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理完整问卷数据"""
        processed = questionnaire_data.copy()
        
        questions = questionnaire_data.get('questions', [])
        processed_questions = []
        total_score = 0
        answered_questions = 0
        
        for question in questions:
            # 处理单个问题
            processed_question = self.process_question(question)
            processed_questions.append(processed_question)
            
            # 计算得分
            score = self.calculate_question_score(processed_question)
            if score is not None:
                total_score += score
                answered_questions += 1
        
        processed['questions'] = processed_questions
        
        # 更新统计信息
        if 'statistics' not in processed:
            processed['statistics'] = {}
        
        # 根据问卷类型决定统计字段
        questionnaire_type = questionnaire_data.get('type', '')
        
        if questionnaire_type == 'frankfurt_scale_selective_mutism':
            # Frankfurt Scale 使用特定的统计字段
            # 不添加 total_score 字段，因为其Schema不支持
            pass
        else:
            # 其他问卷类型使用标准统计字段
            processed['statistics']['total_score'] = total_score
        
        processed['statistics']['answered_questions'] = answered_questions
        processed['statistics']['total_questions'] = len(questions)
        
        if len(questions) > 0:
            completion_rate = (answered_questions / len(questions)) * 100
            processed['statistics']['completion_rate'] = round(completion_rate, 2)
        else:
            processed['statistics']['completion_rate'] = 0
        
        return processed
    
    def validate_questionnaire(self, questionnaire_data: Dict[str, Any]) -> List[str]:
        """验证完整问卷数据"""
        errors = []
        
        questions = questionnaire_data.get('questions', [])
        if not questions:
            errors.append('问卷至少需要一个问题')
            return errors
        
        for i, question in enumerate(questions):
            question_errors = self.validate_question(question)
            for error in question_errors:
                errors.append(f'第{i+1}题: {error}')
        
        return errors
    
    def get_supported_types(self) -> List[str]:
        """获取支持的问题类型列表"""
        return list(self.handlers.keys())
    
    def add_handler(self, question_type: str, handler: QuestionTypeHandler):
        """添加新的问题类型处理器"""
        self.handlers[question_type] = handler
    
    def validate_answer_format_by_type(self, question_data: Dict[str, Any]) -> List[str]:
        """根据问题类型验证答案格式 (需求 2.4)"""
        errors = []
        question_type = question_data.get('type')
        
        if question_type == 'multiple_choice':
            # 验证选择题答案格式
            selected = question_data.get('selected', [])
            if not isinstance(selected, list):
                errors.append('选择题答案必须是列表格式')
            else:
                options = question_data.get('options', [])
                valid_values = [opt.get('value') for opt in options if isinstance(opt, dict)]
                
                for sel in selected:
                    if sel not in valid_values:
                        errors.append(f'选择的答案值 {sel} 不在有效选项中')
                
                # 检查单选/多选模式
                is_multiple = question_data.get('is_multiple_choice', len(selected) > 1)
                if not is_multiple and len(selected) > 1:
                    errors.append('单选题不能选择多个答案')
                    
        elif question_type == 'text_input':
            # 验证填空题答案格式
            answer = question_data.get('answer')
            if not isinstance(answer, str):
                errors.append('填空题答案必须是字符串格式')
            else:
                answer = answer.strip()
                if not answer:
                    errors.append('填空题答案不能为空')
                
                # 验证长度限制
                text_type = question_data.get('text_type', 'short')
                max_length = question_data.get('max_length')
                
                if max_length is None:
                    max_length = 200 if text_type == 'short' else 2000
                
                if len(answer) > max_length:
                    errors.append(f'{text_type}文本答案长度超过限制({max_length}字符)')
        else:
            errors.append(f'不支持的问题类型: {question_type}')
        
        return errors

# 全局处理器实例
question_processor = QuestionTypeProcessor()

# 便捷函数
def validate_question_by_type(question_data: Dict[str, Any]) -> List[str]:
    """验证问题数据的便捷函数"""
    return question_processor.validate_question(question_data)

def process_question_by_type(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理问题数据的便捷函数"""
    return question_processor.process_question(question_data)

def format_question_for_display(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """格式化问题显示的便捷函数"""
    return question_processor.format_question_for_display(question_data)

def process_complete_questionnaire(questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理完整问卷的便捷函数"""
    return question_processor.process_questionnaire(questionnaire_data)

def validate_complete_questionnaire(questionnaire_data: Dict[str, Any]) -> List[str]:
    """验证完整问卷的便捷函数"""
    return question_processor.validate_questionnaire(questionnaire_data)

def validate_answer_format_by_type(question_data: Dict[str, Any]) -> List[str]:
    """根据问题类型验证答案格式的便捷函数 (需求 2.4)"""
    return question_processor.validate_answer_format_by_type(question_data)