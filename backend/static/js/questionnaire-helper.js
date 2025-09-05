/**
 * 问卷页面辅助工具
 * 提供统一的数据提交、验证和错误处理功能
 */

class QuestionnaireHelper {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.submitUrl = `${this.apiBaseUrl}/questionnaires`;
        
        // 确保错误处理器已加载
        if (typeof errorHandler === 'undefined') {
            console.error('ErrorHandler not loaded. Please include error-handler.js first.');
        }
    }
    
    /**
     * 验证基本信息
     */
    validateBasicInfo(basicInfo) {
        const errors = [];
        
        if (!basicInfo.name || !basicInfo.name.trim()) {
            errors.push('请填写姓名');
        }
        
        if (!basicInfo.grade || !basicInfo.grade.trim()) {
            errors.push('请填写年级');
        }
        
        if (!basicInfo.submission_date) {
            errors.push('请选择填表日期');
        }
        
        return errors;
    }
    
    /**
     * 验证问题答案
     */
    validateQuestions(questions) {
        const errors = [];
        
        if (!questions || questions.length === 0) {
            errors.push('请至少回答一个问题');
            return errors;
        }
        
        questions.forEach((question, index) => {
            const questionNum = index + 1;
            
            if (!question.question || !question.question.trim()) {
                errors.push(`第${questionNum}题问题文本不能为空`);
            }
            
            if (question.type === 'multiple_choice') {
                if (!question.selected || question.selected.length === 0) {
                    errors.push(`第${questionNum}题请选择答案`);
                }
                
                if (!question.options || question.options.length === 0) {
                    errors.push(`第${questionNum}题选项不能为空`);
                }
            } else if (question.type === 'text_input') {
                if (!question.answer || !question.answer.trim()) {
                    errors.push(`第${questionNum}题请填写答案`);
                }
            }
        });
        
        return errors;
    }
    
    /**
     * 验证完整问卷数据
     */
    validateQuestionnaire(data) {
        const errors = [];
        
        // 验证基本信息
        if (data.basic_info) {
            errors.push(...this.validateBasicInfo(data.basic_info));
        } else {
            errors.push('基本信息不能为空');
        }
        
        // 验证问题
        if (data.questions) {
            errors.push(...this.validateQuestions(data.questions));
        } else {
            errors.push('问题列表不能为空');
        }
        
        return errors;
    }
    
    /**
     * 标准化问卷数据格式
     */
    normalizeQuestionnaireData(data) {
        const normalized = {
            type: data.type || 'questionnaire',
            basic_info: {
                name: (data.basic_info?.name || '').trim(),
                grade: (data.basic_info?.grade || '').trim(),
                submission_date: data.basic_info?.submission_date || new Date().toISOString().split('T')[0]
            },
            questions: data.questions || [],
            statistics: data.statistics || {
                total_score: 0,
                completion_rate: 100,
                submission_time: new Date().toISOString()
            }
        };
        
        // 添加年龄信息（如果有）
        if (data.basic_info?.age) {
            normalized.basic_info.age = parseInt(data.basic_info.age);
        }
        
        return normalized;
    }
    
    /**
     * 提交问卷数据
     */
    async submitQuestionnaire(data, options = {}) {
        try {
            // 显示提交中状态
            if (options.showLoading) {
                errorHandler.showInfo('正在提交数据...', { autoClose: false });
            }
            
            // 标准化数据
            const normalizedData = this.normalizeQuestionnaireData(data);
            
            // 前端验证
            const validationErrors = this.validateQuestionnaire(normalizedData);
            if (validationErrors.length > 0) {
                errorHandler.showError('数据验证失败', '请检查以下信息：', 'error', {
                    details: validationErrors
                });
                return { success: false, errors: validationErrors };
            }
            
            // 发送请求
            const response = await errorHandler.post(this.submitUrl, normalizedData);
            
            if (!response) {
                return { success: false, error: '网络请求失败' };
            }
            
            const result = await response.json();
            
            if (result.success) {
                errorHandler.showSuccess('问卷提交成功！', {
                    details: `问卷ID: ${result.id}`
                });
                
                // 执行成功回调
                if (options.onSuccess) {
                    options.onSuccess(result);
                }
                
                return { success: true, data: result };
            } else {
                // 服务器返回的业务错误
                const errorMessage = result.error?.message || '提交失败';
                const errorDetails = result.error?.details;
                
                errorHandler.showError('提交失败', errorMessage, 'error', {
                    details: errorDetails
                });
                
                return { success: false, error: result.error };
            }
            
        } catch (error) {
            console.error('提交问卷失败:', error);
            errorHandler.showError('提交失败', '网络连接异常，请稍后重试', 'error');
            return { success: false, error: error.message };
        }
    }
    
    /**
     * 显示提交成功页面
     */
    showSuccessPage(questionnaireId, options = {}) {
        const container = options.container || document.body;
        
        const successHtml = `
            <div class="success-container" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            ">
                <div class="success-content" style="
                    background: white;
                    padding: 40px;
                    border-radius: 12px;
                    text-align: center;
                    max-width: 400px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                ">
                    <div style="font-size: 48px; color: #28a745; margin-bottom: 20px;">✅</div>
                    <h2 style="color: #333; margin-bottom: 16px;">提交成功！</h2>
                    <p style="color: #666; margin-bottom: 8px;">您的问卷已成功保存</p>
                    <p style="color: #999; font-size: 14px; margin-bottom: 24px;">问卷ID: ${questionnaireId}</p>
                    <button onclick="this.closest('.success-container').remove()" style="
                        background: #007bff;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 16px;
                    ">确定</button>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', successHtml);
        
        // 3秒后自动关闭
        setTimeout(() => {
            const successContainer = container.querySelector('.success-container');
            if (successContainer) {
                successContainer.remove();
            }
        }, 3000);
    }
    
    /**
     * 收集表单数据的通用方法
     */
    collectFormData(formSelector = 'form') {
        const form = document.querySelector(formSelector);
        if (!form) {
            throw new Error('找不到表单元素');
        }
        
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            // 处理复选框和单选框
            if (form.querySelector(`[name="${key}"]`).type === 'checkbox') {
                if (!data[key]) data[key] = [];
                data[key].push(value);
            } else {
                data[key] = value;
            }
        }
        
        return data;
    }
    
    /**
     * 自动保存功能
     */
    enableAutoSave(data, interval = 30000) {
        const autoSaveKey = `questionnaire_autosave_${Date.now()}`;
        
        const saveData = () => {
            try {
                localStorage.setItem(autoSaveKey, JSON.stringify({
                    data: data,
                    timestamp: Date.now()
                }));
                console.log('数据已自动保存');
            } catch (error) {
                console.warn('自动保存失败:', error);
            }
        };
        
        // 立即保存一次
        saveData();
        
        // 定期保存
        const intervalId = setInterval(saveData, interval);
        
        // 返回清理函数
        return () => {
            clearInterval(intervalId);
            localStorage.removeItem(autoSaveKey);
        };
    }
    
    /**
     * 恢复自动保存的数据
     */
    restoreAutoSavedData() {
        try {
            const keys = Object.keys(localStorage).filter(key => 
                key.startsWith('questionnaire_autosave_')
            );
            
            if (keys.length === 0) return null;
            
            // 获取最新的自动保存数据
            const latestKey = keys.sort().pop();
            const savedData = JSON.parse(localStorage.getItem(latestKey));
            
            // 检查数据是否过期（24小时）
            const maxAge = 24 * 60 * 60 * 1000;
            if (Date.now() - savedData.timestamp > maxAge) {
                localStorage.removeItem(latestKey);
                return null;
            }
            
            return savedData.data;
        } catch (error) {
            console.warn('恢复自动保存数据失败:', error);
            return null;
        }
    }
}

// 创建全局实例
const questionnaireHelper = new QuestionnaireHelper();

// 导出给其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuestionnaireHelper;
}