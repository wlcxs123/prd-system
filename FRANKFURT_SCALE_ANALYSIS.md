# Frankfurt Scale of Selective Mutism 问卷分析报告

## 问卷概述

**问卷名称**: Frankfurt Scale of Selective Mutism (选择性缄默筛查量表)  
**问卷类型**: 专业心理评估量表  
**目标用户**: 家长/监护人  
**适用年龄**: 3-18岁（分为3个年龄段：3-7岁、6-11岁、12-18岁）

## 当前数据流程分析

### 1. 数据收集结构

#### 基本信息
- `child`: 儿童姓名（可选）
- `guardian`: 家长/监护人（可选）
- `date`: 填表日期

#### A部分：快速筛查（DS - Diagnostic Scale）
- 10个是/否问题，每题1分或0分
- 总分范围：0-10分
- 不同年龄段有不同的风险阈值

#### B部分：说话情况评分（SS - Severity Scale）
- 三个场景：学校/幼儿园、公共场合、家庭
- 每个场景有不同数量的问题（根据年龄段）
- 评分：0=无问题，1=轻度限制，2=偶尔，3=几乎从不，4=完全不说

### 2. 当前数据存储方式

#### 本地存储
```javascript
// 存储在localStorage中
var d = {
    age: age,           // 年龄段
    ds: state.ds,       // DS部分答案
    ss: state.ss,       // SS部分答案
    child: childEl.value,
    guardian: guardianEl.value,
    date: dateEl.value
};
localStorage.setItem(KEY, JSON.stringify(d));
```

#### 导出格式
```javascript
// payload函数返回的数据结构
{
    date: "2024-12-15",
    child: "张三",
    guardian: "张父",
    age: "6_11",
    DS: 8,                    // DS总分
    SS_school: 12,           // 学校场景得分
    SS_public: 8,            // 公共场景得分
    SS_home: 2,              // 家庭场景得分
    SS_total: 22             // SS总分
}
```

## 问题识别

### 1. 缺少服务器端数据提交
- ❌ 只有本地存储和文件导出
- ❌ 没有与后端API的集成
- ❌ 无法进行数据管理和统计分析

### 2. 数据结构不完整
- ❌ 缺少详细的问题答案记录
- ❌ 只保存汇总分数，丢失原始答案
- ❌ 无法进行详细的数据分析

### 3. 用户体验问题
- ❌ 没有统一的错误处理
- ❌ 缺少提交成功反馈
- ❌ 没有数据验证机制

## 集成方案

### 1. 数据结构标准化

#### 转换为标准问卷格式
```javascript
{
    type: "frankfurt_scale_selective_mutism",
    basic_info: {
        name: child,
        grade: age,  // 年龄段作为年级
        submission_date: date,
        guardian: guardian
    },
    questions: [
        // DS部分问题
        {
            id: 1,
            type: "multiple_choice",
            question: "在家很能说话，但在公共/学校环境明显沉默或避免用语言。",
            question_en: "Is there a clear distinction between speaking behavior at home...",
            options: [
                { value: 1, text: "是 = 1分" },
                { value: 0, text: "否 = 0分" }
            ],
            selected: [1],
            section: "DS"
        },
        // SS部分问题
        {
            id: 11,
            type: "multiple_choice", 
            question: "在幼儿园与老师说话",
            question_en: "Does your child speak with teachers in kindergarten?",
            options: [
                { value: 0, text: "0 无问题" },
                { value: 1, text: "1 轻度限制" },
                { value: 2, text: "2 偶尔" },
                { value: 3, text: "3 几乎从不" },
                { value: 4, text: "4 完全不说" }
            ],
            selected: [2],
            section: "SS_school"
        }
        // ... 更多问题
    ],
    statistics: {
        ds_total: 8,
        ss_school_total: 12,
        ss_public_total: 8,
        ss_home_total: 2,
        ss_total: 22,
        age_group: "6_11",
        risk_level: "high",
        completion_rate: 100,
        submission_time: "2024-12-15T10:30:00Z"
    }
}
```

### 2. 后端API扩展

#### 新增问卷类型支持
```python
# 在validation.py中添加Frankfurt Scale验证
class FrankfurtScaleSchema(Schema):
    """Frankfurt Scale问卷验证Schema"""
    age_group = fields.Str(required=True, validate=validate.OneOf(['3_7', '6_11', '12_18']))
    ds_total = fields.Int(validate=validate.Range(min=0, max=10))
    ss_school_total = fields.Int(validate=validate.Range(min=0))
    ss_public_total = fields.Int(validate=validate.Range(min=0))
    ss_home_total = fields.Int(validate=validate.Range(min=0))
    ss_total = fields.Int(validate=validate.Range(min=0))
    risk_level = fields.Str(validate=validate.OneOf(['low', 'mid', 'high']))
```

### 3. 前端集成改造

#### 添加数据提交功能
```javascript
// 在问卷中添加提交到服务器的功能
async function submitToServer() {
    try {
        // 转换数据格式
        const questionnaireData = convertToStandardFormat();
        
        // 使用统一错误处理系统提交
        const result = await questionnaireHelper.submitQuestionnaire(questionnaireData, {
            showLoading: true,
            onSuccess: (result) => {
                errorHandler.showSuccess('问卷提交成功！', {
                    details: `问卷ID: ${result.id}`
                });
                // 显示成功页面或继续当前流程
            }
        });
        
        return result;
    } catch (error) {
        errorHandler.showError('提交失败', error.message, 'error');
        return null;
    }
}
```

## 实施步骤

### 第一步：创建数据转换函数
1. 分析现有数据结构
2. 创建转换函数将Frankfurt Scale数据转为标准格式
3. 保持向后兼容性

### 第二步：集成统一错误处理
1. 引入error-handler.js和questionnaire-helper.js
2. 替换现有的toast提示为统一错误处理
3. 添加网络重试机制

### 第三步：添加服务器提交功能
1. 在现有保存按钮旁添加"提交到服务器"按钮
2. 实现数据验证和提交逻辑
3. 保持现有的本地保存和导出功能

### 第四步：后端支持
1. 扩展问卷验证模式支持Frankfurt Scale
2. 在管理后台中支持查看和管理此类问卷
3. 添加专门的统计分析功能

## 预期效果

### 数据管理改进
- ✅ 统一的数据存储和管理
- ✅ 完整的问题答案记录
- ✅ 支持批量导出和分析
- ✅ 数据备份和恢复

### 用户体验提升
- ✅ 统一的错误提示和处理
- ✅ 自动重试机制
- ✅ 数据提交状态反馈
- ✅ 网络异常处理

### 系统集成
- ✅ 与现有问卷管理系统无缝集成
- ✅ 统一的管理后台界面
- ✅ 标准化的数据格式
- ✅ 支持多种导出格式

## 技术实现细节

### 数据映射规则
```javascript
// DS部分问题映射
const DS_QUESTIONS = [
    {
        id: 1,
        zh: "在家很能说话，但在公共/学校环境明显沉默或避免用语言。",
        en: "Is there a clear distinction between speaking behavior at home (rather talkative) and in public (avoiding the use of words or even mute)?"
    },
    // ... 其他9个问题
];

// SS部分问题映射（按年龄段）
const SS_QUESTIONS = {
    '3_7': {
        school: [...],
        public: [...], 
        home: [...]
    },
    // ... 其他年龄段
};
```

### 风险评估逻辑
```javascript
function calculateRiskLevel(dsScore, ageGroup) {
    const cutoffs = {'3_7': 7, '6_11': 7, '12_18': 6};
    const cutoff = cutoffs[ageGroup];
    
    if (dsScore >= cutoff) return 'high';
    if (dsScore >= cutoff - 2) return 'mid';
    return 'low';
}
```

## 兼容性考虑

### 保持现有功能
- ✅ 本地存储功能继续工作
- ✅ JSON/CSV导出功能保留
- ✅ PDF/PNG报告生成保留
- ✅ 可视化图表功能保留

### 渐进式升级
- ✅ 新功能作为可选项添加
- ✅ 不影响现有用户工作流程
- ✅ 支持离线使用模式
- ✅ 数据同步机制

## 总结

Frankfurt Scale of Selective Mutism问卷是一个功能完善的专业评估工具，但缺少与服务器端的集成。通过实施上述集成方案，可以：

1. **保持专业性**：不改变问卷的专业评估功能
2. **提升管理性**：将数据纳入统一管理系统
3. **改善体验**：提供更好的错误处理和用户反馈
4. **增强分析**：支持批量数据分析和统计

这个集成将使Frankfurt Scale问卷成为问卷管理系统中的一个重要组成部分，同时保持其专业性和独特性。