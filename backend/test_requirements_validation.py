"""
测试验证模块是否满足具体需求
验证需求 1.1, 1.2, 1.3, 6.1, 6.2 的实现
"""

import unittest
from validation import (
    validate_questionnaire_with_schema,
    normalize_questionnaire_data,
    check_data_integrity,
    quick_validate,
    create_validation_error_response
)
from question_types import process_complete_questionnaire

class TestRequirement1DataStructureValidation(unittest.TestCase):
    """测试需求1：数据结构标准化和验证"""
    
    def test_requirement_1_1_basic_info_validation(self):
        """
        需求 1.1: WHEN 问卷页面提交数据 THEN 系统 SHALL 验证数据包含基本信息（姓名、年级、日期等）
        """
        # 测试完整的基本信息
        valid_data = {
            "type": "test_questionnaire",
            "basic_info": {
                "name": "张三",
                "grade": "五年级",
                "submission_date": "2024-01-15"
            },
            "questions": [{
                "id": 1,
                "type": "text_input",
                "question": "测试问题",
                "answer": "测试答案"
            }]
        }
        
        errors = quick_validate(valid_data)
        self.assertEqual(len(errors), 0, "完整基本信息应该通过验证")
        
        # 测试缺少姓名
        invalid_data = valid_data.copy()
        invalid_data["basic_info"]["name"] = ""
        errors = quick_validate(invalid_data)
        self.assertTrue(any("姓名" in error for error in errors), "应该检测到姓名为空")
        
        # 测试缺少年级
        invalid_data = valid_data.copy()
        invalid_data["basic_info"]["grade"] = ""
        errors = quick_validate(invalid_data)
        self.assertTrue(any("年级" in error for error in errors), "应该检测到年级为空")
        
        # 测试缺少日期 - 使用Schema直接验证（不经过标准化）
        invalid_data = valid_data.copy()
        del invalid_data["basic_info"]["submission_date"]
        
        # 直接使用Schema验证，不经过标准化
        is_valid, schema_errors, _ = validate_questionnaire_with_schema(invalid_data)
        self.assertFalse(is_valid, "缺少日期的数据应该验证失败")
        
        # 检查错误信息
        error_str = str(schema_errors)
        self.assertTrue("submission_date" in error_str or "required" in error_str, 
                       f"应该检测到日期字段缺失，实际错误: {schema_errors}")
    
    def test_requirement_1_2_multiple_choice_validation(self):
        """
        需求 1.2: WHEN 提交选择题数据 THEN 系统 SHALL 确保包含问题文本、所有选项和选中的选项
        """
        # 测试完整的选择题数据
        valid_data = {
            "type": "test_questionnaire",
            "basic_info": {
                "name": "张三",
                "grade": "五年级", 
                "submission_date": "2024-01-15"
            },
            "questions": [{
                "id": 1,
                "type": "multiple_choice",
                "question": "你最喜欢的颜色是什么？",
                "options": [
                    {"value": 0, "text": "红色"},
                    {"value": 1, "text": "蓝色"}
                ],
                "selected": [0]
            }]
        }
        
        errors = quick_validate(valid_data)
        self.assertEqual(len(errors), 0, "完整选择题数据应该通过验证")
        
        # 测试缺少问题文本
        invalid_data = valid_data.copy()
        invalid_data["questions"][0]["question"] = ""
        errors = quick_validate(invalid_data)
        self.assertTrue(any("问题文本" in error for error in errors), "应该检测到问题文本为空")
        
        # 测试缺少选项
        invalid_data = valid_data.copy()
        invalid_data["questions"][0]["options"] = []
        errors = quick_validate(invalid_data)
        self.assertTrue(any("选项" in error for error in errors), "应该检测到选项为空")
        
        # 测试缺少选中答案
        invalid_data = valid_data.copy()
        invalid_data["questions"][0]["selected"] = []
        errors = quick_validate(invalid_data)
        self.assertTrue(any("选择" in error or "答案" in error for error in errors), "应该检测到未选择答案")
    
    def test_requirement_1_3_text_input_validation(self):
        """
        需求 1.3: WHEN 提交填空题数据 THEN 系统 SHALL 确保包含问题文本和用户填写的答案
        """
        # 测试完整的填空题数据
        valid_data = {
            "type": "test_questionnaire",
            "basic_info": {
                "name": "张三",
                "grade": "五年级",
                "submission_date": "2024-01-15"
            },
            "questions": [{
                "id": 1,
                "type": "text_input",
                "question": "请描述你的兴趣爱好",
                "answer": "我喜欢阅读和运动"
            }]
        }
        
        errors = quick_validate(valid_data)
        self.assertEqual(len(errors), 0, "完整填空题数据应该通过验证")
        
        # 测试缺少问题文本
        invalid_data = valid_data.copy()
        invalid_data["questions"][0]["question"] = ""
        errors = quick_validate(invalid_data)
        self.assertTrue(any("问题文本" in error for error in errors), "应该检测到问题文本为空")
        
        # 测试缺少答案
        invalid_data = valid_data.copy()
        invalid_data["questions"][0]["answer"] = ""
        errors = quick_validate(invalid_data)
        self.assertTrue(any("答案" in error for error in errors), "应该检测到答案为空")

class TestRequirement6DataIntegrityValidation(unittest.TestCase):
    """测试需求6：数据完整性验证"""
    
    def test_requirement_6_1_basic_info_integrity(self):
        """
        需求 6.1: WHEN 验证基本信息 THEN 系统 SHALL 确保姓名、年级、日期字段不为空
        """
        # 测试完整的基本信息
        complete_data = {
            "basic_info": {
                "name": "李四",
                "grade": "六年级",
                "submission_date": "2024-01-15"
            },
            "questions": []
        }
        
        errors = check_data_integrity(complete_data)
        # 只检查基本信息相关的错误，忽略问题为空的错误
        basic_info_errors = [e for e in errors if any(field in e for field in ["姓名", "年级", "日期"])]
        self.assertEqual(len(basic_info_errors), 0, "完整基本信息不应该有错误")
        
        # 测试姓名为空
        data_empty_name = complete_data.copy()
        data_empty_name["basic_info"]["name"] = ""
        errors = check_data_integrity(data_empty_name)
        self.assertTrue(any("姓名不能为空" in error for error in errors), "应该检测到姓名为空")
        
        # 测试年级为空
        data_empty_grade = complete_data.copy()
        data_empty_grade["basic_info"]["grade"] = ""
        errors = check_data_integrity(data_empty_grade)
        self.assertTrue(any("年级不能为空" in error for error in errors), "应该检测到年级为空")
        
        # 测试日期为空
        data_empty_date = complete_data.copy()
        data_empty_date["basic_info"]["submission_date"] = None
        errors = check_data_integrity(data_empty_date)
        self.assertTrue(any("提交日期不能为空" in error for error in errors), "应该检测到日期为空")
    
    def test_requirement_6_2_choice_answer_integrity(self):
        """
        需求 6.2: WHEN 验证选择题答案 THEN 系统 SHALL 确保选中的选项在有效选项范围内
        """
        # 测试有效的选择
        valid_data = {
            "basic_info": {
                "name": "王五",
                "grade": "四年级",
                "submission_date": "2024-01-15"
            },
            "questions": [{
                "id": 1,
                "type": "multiple_choice",
                "question": "你最喜欢的运动是什么？",
                "options": [
                    {"value": 0, "text": "篮球"},
                    {"value": 1, "text": "足球"},
                    {"value": 2, "text": "乒乓球"}
                ],
                "selected": [1]  # 选择足球
            }]
        }
        
        errors = check_data_integrity(valid_data)
        choice_errors = [e for e in errors if "选中的答案无效" in e]
        self.assertEqual(len(choice_errors), 0, "有效选择不应该有错误")
        
        # 测试无效的选择
        invalid_data = valid_data.copy()
        invalid_data["questions"][0]["selected"] = [99]  # 不存在的选项
        errors = check_data_integrity(invalid_data)
        self.assertTrue(any("选中的答案无效" in error for error in errors), "应该检测到无效选择")
        
        # 测试多个选择，其中包含无效选择
        invalid_data["questions"][0]["selected"] = [0, 99]  # 一个有效，一个无效
        errors = check_data_integrity(invalid_data)
        self.assertTrue(any("选中的答案无效" in error for error in errors), "应该检测到包含无效选择")

class TestDataValidationErrorHandling(unittest.TestCase):
    """测试数据验证错误处理"""
    
    def test_requirement_1_4_incomplete_data_error_response(self):
        """
        需求 1.4: WHEN 数据结构不完整 THEN 系统 SHALL 返回具体的错误信息并拒绝保存
        """
        # 测试不完整数据
        incomplete_data = {
            "type": "",  # 空类型
            "basic_info": {
                "name": "",  # 空姓名
                "grade": "",  # 空年级
            },
            "questions": []  # 空问题列表
        }
        
        errors = quick_validate(incomplete_data)
        
        # 验证返回了具体的错误信息
        self.assertGreater(len(errors), 0, "不完整数据应该返回错误")
        
        # 验证错误信息是具体的
        error_text = " ".join(errors)
        self.assertTrue(any(keyword in error_text for keyword in ["姓名", "年级", "问题", "类型"]), 
                       "错误信息应该包含具体的字段名称")
        
        # 测试创建标准错误响应
        error_response = create_validation_error_response(errors)
        self.assertFalse(error_response["success"], "错误响应应该标记为失败")
        self.assertEqual(error_response["error"]["code"], "VALIDATION_ERROR", "应该返回验证错误代码")
        self.assertIn("details", error_response["error"], "应该包含详细错误信息")
        self.assertIn("timestamp", error_response, "应该包含时间戳")

class TestDataNormalizationAndProcessing(unittest.TestCase):
    """测试数据标准化和处理"""
    
    def test_data_normalization_and_validation_integration(self):
        """测试数据标准化和验证的集成"""
        # 测试需要标准化的数据
        raw_data = {
            "type": "  STUDENT_EVALUATION  ",  # 需要清理的类型
            "name": "  张三  ",  # 根级别的姓名（向后兼容）
            "grade": "  五年级  ",  # 根级别的年级
            "submission_date": "2024-01-15",
            "questions": [{
                "id": "1",  # 字符串ID需要转换
                "type": "multiple_choice",
                "question": "  你最喜欢的科目？  ",  # 需要清理的问题文本
                "options": [
                    {"value": 0, "text": "  数学  "},  # 需要清理的选项文本
                    {"value": 1, "text": "  语文  "}
                ],
                "selected": 0  # 非数组格式需要转换
            }]
        }
        
        # 标准化数据
        normalized = normalize_questionnaire_data(raw_data)
        
        # 验证标准化结果
        self.assertEqual(normalized["type"], "student_evaluation", "类型应该被标准化")
        self.assertEqual(normalized["basic_info"]["name"], "张三", "姓名应该被清理")
        self.assertEqual(normalized["basic_info"]["grade"], "五年级", "年级应该被清理")
        self.assertEqual(normalized["questions"][0]["id"], 1, "ID应该被转换为整数")
        self.assertEqual(normalized["questions"][0]["question"], "你最喜欢的科目？", "问题文本应该被清理")
        self.assertEqual(normalized["questions"][0]["selected"], [0], "选择应该被转换为数组")
        
        # 验证标准化后的数据能通过验证
        errors = quick_validate(normalized)
        self.assertEqual(len(errors), 0, "标准化后的数据应该通过验证")
        
        # 验证能被问题类型处理器处理
        processed = process_complete_questionnaire(normalized)
        self.assertIn("statistics", processed, "应该包含统计信息")
        self.assertIn("selected_texts", processed["questions"][0], "选择题应该包含选中文本")

if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)