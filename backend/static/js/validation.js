/**
 * 前端数据验证模块
 * 提供问卷数据的客户端验证功能
 */

class QuestionnaireValidator {
    constructor() {
        this.errors = [];
    }

    /**
     * 验证完整的问卷数据
     * @param {Object} data - 问卷数据
     * @returns {Object} - {isValid: boolean, errors: string[]}
     */
    validateQuestionnaire(data) {
        this.errors = [];

        // 验证基本结构
        if (!data || typeof data !== 'object') {
            this.errors.push('问卷数据格式不正确');
            return this.getResult();
        }

        // 验证问卷类型
        this.validateType(data.type);

        // 验证基本信息
        this.validateBasicInfo(data.basic_info || data);

        // 验证问题列表
        this.validateQuestions(data.questions || []);

        // 验证统计信息（可选）
        if (data.statistics) {
            this.validateStatistics(data.statistics);
        }

        return this.getResult();
    }

    /**
     * 验证问卷类型
     * @param {string} type - 问卷类型
     */
    validateType(type) {
        if (!type || typeof type !== 'string' || type.trim().length === 0) {
            this.errors.push('问卷类型不能为空');
        } else if (type.length > 50) {
            this.errors.push('问卷类型长度不能超过50个字符');
        }
    }

    /**
     * 验证基本信息
     * @param {Object} basicInfo - 基本信息对象
     */
    validateBasicInfo(basicInfo) {
        if (!basicInfo || typeof basicInfo !== 'object') {
            this.errors.push('基本信息不能为空');
            return;
        }

        // 验证姓名
        const name = basicInfo.name;
        if (!name || typeof name !== 'string' || name.trim().length === 0) {
            this.errors.push('姓名不能为空');
        } else if (name.length > 50) {
            this.errors.push('姓名长度不能超过50个字符');
        }

        // 验证年级
        const grade = basicInfo.grade;
        if (!grade || typeof grade !== 'string' || grade.trim().length === 0) {
            this.errors.push('年级不能为空');
        } else if (grade.length > 20) {
            this.errors.push('年级长度不能超过20个字符');
        }

        // 验证提交日期
        const submissionDate = basicInfo.submission_date;
        if (!submissionDate) {
            this.errors.push('提交日期不能为空');
        } else if (!this.isValidDate(submissionDate)) {
            this.errors.push('提交日期格式不正确');
        }

        // 验证年龄（可选）
        if (basicInfo.age !== undefined && basicInfo.age !== null) {
            const age = parseInt(basicInfo.age);
            if (isNaN(age) || age < 1 || age > 150) {
                this.errors.push('年龄必须在1-150之间');
            }
        }
    }

    /**
     * 验证问题列表
     * @param {Array} questions - 问题数组
     */
    validateQuestions(questions) {
        if (!Array.isArray(questions)) {
            this.errors.push('问题列表格式不正确');
            return;
        }

        if (questions.length === 0) {
            this.errors.push('至少需要一个问题');
            return;
        }

        questions.forEach((question, index) => {
            this.validateQuestion(question, index + 1);
        });
    }

    /**
     * 验证单个问题
     * @param {Object} question - 问题对象
     * @param {number} questionNum - 问题编号
     */
    validateQuestion(question, questionNum) {
        if (!question || typeof question !== 'object') {
            this.errors.push(`第${questionNum}题格式不正确`);
            return;
        }

        // 验证问题ID
        if (!question.id || !Number.isInteger(question.id) || question.id < 1) {
            this.errors.push(`第${questionNum}题ID必须是正整数`);
        }

        // 验证问题文本
        if (!question.question || typeof question.question !== 'string' || question.question.trim().length === 0) {
            this.errors.push(`第${questionNum}题问题文本不能为空`);
        } else if (question.question.length > 500) {
            this.errors.push(`第${questionNum}题问题文本长度不能超过500个字符`);
        }

        // 根据问题类型进行具体验证
        const questionType = question.type;
        if (questionType === 'multiple_choice') {
            this.validateMultipleChoiceQuestion(question, questionNum);
        } else if (questionType === 'text_input') {
            this.validateTextInputQuestion(question, questionNum);
        } else {
            this.errors.push(`第${questionNum}题类型不支持: ${questionType}`);
        }
    }

    /**
     * 验证选择题
     * @param {Object} question - 选择题对象
     * @param {number} questionNum - 问题编号
     */
    validateMultipleChoiceQuestion(question, questionNum) {
        // 验证选项
        const options = question.options;
        if (!Array.isArray(options) || options.length === 0) {
            this.errors.push(`第${questionNum}题至少需要一个选项`);
            return;
        }

        // 验证每个选项
        const validValues = [];
        options.forEach((option, optionIndex) => {
            if (!option || typeof option !== 'object') {
                this.errors.push(`第${questionNum}题选项${optionIndex + 1}格式不正确`);
                return;
            }

            if (option.value === undefined || option.value === null) {
                this.errors.push(`第${questionNum}题选项${optionIndex + 1}缺少值`);
            } else {
                validValues.push(option.value);
            }

            if (!option.text || typeof option.text !== 'string' || option.text.trim().length === 0) {
                this.errors.push(`第${questionNum}题选项${optionIndex + 1}文本不能为空`);
            } else if (option.text.length > 200) {
                this.errors.push(`第${questionNum}题选项${optionIndex + 1}文本长度不能超过200个字符`);
            }
        });

        // 验证选中答案
        const selected = question.selected;
        if (!Array.isArray(selected) || selected.length === 0) {
            this.errors.push(`第${questionNum}题必须选择至少一个答案`);
        } else {
            // 检查选中的答案是否在有效选项中
            selected.forEach(selectedValue => {
                if (!validValues.includes(selectedValue)) {
                    this.errors.push(`第${questionNum}题选中的答案无效: ${selectedValue}`);
                }
            });
        }
    }

    /**
     * 验证填空题
     * @param {Object} question - 填空题对象
     * @param {number} questionNum - 问题编号
     */
    validateTextInputQuestion(question, questionNum) {
        const answer = question.answer;
        if (!answer || typeof answer !== 'string' || answer.trim().length === 0) {
            this.errors.push(`第${questionNum}题答案不能为空`);
        } else if (answer.length > 1000) {
            this.errors.push(`第${questionNum}题答案长度不能超过1000个字符`);
        }

        // 验证最大长度限制（可选）
        if (question.max_length !== undefined) {
            const maxLength = parseInt(question.max_length);
            if (isNaN(maxLength) || maxLength < 1 || maxLength > 5000) {
                this.errors.push(`第${questionNum}题最大长度设置不正确`);
            } else if (answer && answer.length > maxLength) {
                this.errors.push(`第${questionNum}题答案长度超过限制(${maxLength}个字符)`);
            }
        }
    }

    /**
     * 验证统计信息
     * @param {Object} statistics - 统计信息对象
     */
    validateStatistics(statistics) {
        if (typeof statistics !== 'object') {
            this.errors.push('统计信息格式不正确');
            return;
        }

        // 验证总分（可选）
        if (statistics.total_score !== undefined && statistics.total_score !== null) {
            const totalScore = parseInt(statistics.total_score);
            if (isNaN(totalScore) || totalScore < 0 || totalScore > 1000) {
                this.errors.push('总分必须在0-1000之间');
            }
        }

        // 验证完成率（可选）
        if (statistics.completion_rate !== undefined && statistics.completion_rate !== null) {
            const completionRate = parseInt(statistics.completion_rate);
            if (isNaN(completionRate) || completionRate < 0 || completionRate > 100) {
                this.errors.push('完成率必须在0-100之间');
            }
        }

        // 验证提交时间（可选）
        if (statistics.submission_time && !this.isValidDateTime(statistics.submission_time)) {
            this.errors.push('提交时间格式不正确');
        }
    }

    /**
     * 验证日期格式
     * @param {string} dateString - 日期字符串
     * @returns {boolean} - 是否有效
     */
    isValidDate(dateString) {
        // 支持 YYYY-MM-DD 格式
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(dateString)) {
            return false;
        }

        const date = new Date(dateString);
        return date instanceof Date && !isNaN(date.getTime());
    }

    /**
     * 验证日期时间格式
     * @param {string} dateTimeString - 日期时间字符串
     * @returns {boolean} - 是否有效
     */
    isValidDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        return date instanceof Date && !isNaN(date.getTime());
    }

    /**
     * 获取验证结果
     * @returns {Object} - {isValid: boolean, errors: string[]}
     */
    getResult() {
        return {
            isValid: this.errors.length === 0,
            errors: [...this.errors]
        };
    }
}

/**
 * 数据标准化函数
 */
class DataNormalizer {
    /**
     * 标准化问卷数据
     * @param {Object} data - 原始数据
     * @returns {Object} - 标准化后的数据
     */
    static normalizeQuestionnaire(data) {
        if (!data || typeof data !== 'object') {
            throw new Error('数据格式不正确');
        }

        const normalized = {};

        // 标准化问卷类型
        normalized.type = String(data.type || 'unknown').trim().toLowerCase();

        // 标准化基本信息
        normalized.basic_info = this.normalizeBasicInfo(data.basic_info || data);

        // 标准化问题列表
        normalized.questions = this.normalizeQuestions(data.questions || []);

        // 标准化统计信息
        if (data.statistics) {
            normalized.statistics = this.normalizeStatistics(data.statistics);
        }

        return normalized;
    }

    /**
     * 标准化基本信息
     * @param {Object} basicInfo - 基本信息
     * @returns {Object} - 标准化后的基本信息
     */
    static normalizeBasicInfo(basicInfo) {
        const normalized = {
            name: String(basicInfo.name || '').trim(),
            grade: String(basicInfo.grade || '').trim(),
            submission_date: basicInfo.submission_date || new Date().toISOString().split('T')[0]
        };

        if (basicInfo.age !== undefined && basicInfo.age !== null) {
            const age = parseInt(basicInfo.age);
            if (!isNaN(age)) {
                normalized.age = age;
            }
        }

        return normalized;
    }

    /**
     * 标准化问题列表
     * @param {Array} questions - 问题数组
     * @returns {Array} - 标准化后的问题数组
     */
    static normalizeQuestions(questions) {
        if (!Array.isArray(questions)) {
            return [];
        }

        return questions.map(question => this.normalizeQuestion(question)).filter(q => q !== null);
    }

    /**
     * 标准化单个问题
     * @param {Object} question - 问题对象
     * @returns {Object|null} - 标准化后的问题对象
     */
    static normalizeQuestion(question) {
        if (!question || typeof question !== 'object' || !question.type) {
            return null;
        }

        const normalized = {
            id: parseInt(question.id) || 0,
            type: question.type,
            question: String(question.question || '').trim()
        };

        if (question.type === 'multiple_choice') {
            // 标准化选择题
            normalized.options = this.normalizeOptions(question.options || []);
            normalized.selected = Array.isArray(question.selected) ? question.selected : 
                                 (question.selected !== undefined ? [question.selected] : []);

            if (question.can_speak !== undefined) {
                normalized.can_speak = Boolean(question.can_speak);
            }
        } else if (question.type === 'text_input') {
            // 标准化填空题
            normalized.answer = String(question.answer || '').trim();

            if (question.max_length !== undefined) {
                const maxLength = parseInt(question.max_length);
                if (!isNaN(maxLength)) {
                    normalized.max_length = maxLength;
                }
            }
        }

        return normalized;
    }

    /**
     * 标准化选项列表
     * @param {Array} options - 选项数组
     * @returns {Array} - 标准化后的选项数组
     */
    static normalizeOptions(options) {
        if (!Array.isArray(options)) {
            return [];
        }

        return options.map(option => {
            if (!option || typeof option !== 'object') {
                return null;
            }

            return {
                value: option.value,
                text: String(option.text || '').trim()
            };
        }).filter(option => option !== null);
    }

    /**
     * 标准化统计信息
     * @param {Object} statistics - 统计信息
     * @returns {Object} - 标准化后的统计信息
     */
    static normalizeStatistics(statistics) {
        const normalized = {};

        if (statistics.total_score !== undefined && statistics.total_score !== null) {
            const totalScore = parseInt(statistics.total_score);
            if (!isNaN(totalScore)) {
                normalized.total_score = totalScore;
            }
        }

        if (statistics.completion_rate !== undefined && statistics.completion_rate !== null) {
            const completionRate = parseInt(statistics.completion_rate);
            if (!isNaN(completionRate)) {
                normalized.completion_rate = completionRate;
            }
        } else {
            normalized.completion_rate = 100;
        }

        if (statistics.submission_time) {
            normalized.submission_time = statistics.submission_time;
        } else {
            normalized.submission_time = new Date().toISOString();
        }

        return normalized;
    }
}

/**
 * 便捷的验证函数
 */
function validateQuestionnaireData(data) {
    const validator = new QuestionnaireValidator();
    return validator.validateQuestionnaire(data);
}

/**
 * 便捷的标准化函数
 */
function normalizeQuestionnaireData(data) {
    return DataNormalizer.normalizeQuestionnaire(data);
}

/**
 * 组合验证和标准化
 */
function validateAndNormalize(data) {
    try {
        // 先标准化
        const normalized = normalizeQuestionnaireData(data);
        
        // 再验证
        const validation = validateQuestionnaireData(normalized);
        
        return {
            isValid: validation.isValid,
            errors: validation.errors,
            data: validation.isValid ? normalized : null
        };
    } catch (error) {
        return {
            isValid: false,
            errors: [error.message],
            data: null
        };
    }
}

// 导出到全局作用域（用于HTML页面）
if (typeof window !== 'undefined') {
    window.QuestionnaireValidator = QuestionnaireValidator;
    window.DataNormalizer = DataNormalizer;
    window.validateQuestionnaireData = validateQuestionnaireData;
    window.normalizeQuestionnaireData = normalizeQuestionnaireData;
    window.validateAndNormalize = validateAndNormalize;
}

// 导出模块（用于Node.js环境）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        QuestionnaireValidator,
        DataNormalizer,
        validateQuestionnaireData,
        normalizeQuestionnaireData,
        validateAndNormalize
    };
}