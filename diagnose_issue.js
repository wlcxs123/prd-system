// 诊断管理员界面问题的脚本
// 在浏览器控制台中运行此脚本

console.log('=== 管理员界面诊断脚本 ===');

// 1. 检查页面元素
console.log('1. 检查关键元素是否存在:');
const viewModal = document.getElementById('viewModal');
const viewModalBody = document.getElementById('viewModalBody');
const editModal = document.getElementById('editModal');

console.log('- viewModal:', viewModal ? '✓ 存在' : '✗ 不存在');
console.log('- viewModalBody:', viewModalBody ? '✓ 存在' : '✗ 不存在');
console.log('- editModal:', editModal ? '✓ 存在' : '✗ 不存在');

// 2. 检查函数是否定义
console.log('\n2. 检查关键函数是否定义:');
console.log('- viewQuestionnaire:', typeof viewQuestionnaire !== 'undefined' ? '✓ 已定义' : '✗ 未定义');
console.log('- showViewModal:', typeof showViewModal !== 'undefined' ? '✓ 已定义' : '✗ 未定义');
console.log('- renderQuestionnaireView:', typeof renderQuestionnaireView !== 'undefined' ? '✓ 已定义' : '✗ 未定义');

// 3. 测试模态框显示
console.log('\n3. 测试模态框基本功能:');
if (viewModal && viewModalBody) {
    // 测试基本显示
    viewModalBody.innerHTML = '<p>测试内容 - 如果你能看到这个，说明模态框可以正常显示内容</p>';
    viewModal.style.display = 'block';
    
    setTimeout(() => {
        viewModal.style.display = 'none';
        console.log('✓ 模态框基本显示功能正常');
    }, 2000);
} else {
    console.log('✗ 模态框元素缺失，无法测试');
}

// 4. 测试API连接
console.log('\n4. 测试API连接:');
fetch('/api/questionnaires')
    .then(response => {
        console.log('- API响应状态:', response.status);
        if (response.status === 401) {
            console.log('✗ 需要登录认证');
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (data) {
            console.log('✓ API连接正常');
            console.log('- 问卷数量:', data.data ? data.data.length : 0);
            
            // 如果有问卷，测试获取详情
            if (data.success && data.data && data.data.length > 0) {
                const firstId = data.data[0].id;
                console.log('- 测试获取问卷详情, ID:', firstId);
                
                return fetch(`/api/questionnaires/${firstId}`);
            }
        }
    })
    .then(response => {
        if (response) {
            return response.json();
        }
    })
    .then(detailData => {
        if (detailData) {
            console.log('✓ 问卷详情获取成功');
            console.log('- 问卷数据结构:', Object.keys(detailData.data.data || {}));
            
            // 测试渲染函数
            if (typeof renderQuestionnaireView !== 'undefined') {
                try {
                    const html = renderQuestionnaireView(detailData.data);
                    console.log('✓ 渲染函数执行成功');
                    console.log('- 生成HTML长度:', html.length);
                    
                    if (html.length < 100) {
                        console.log('⚠️ 生成的HTML内容较短，可能存在问题');
                        console.log('- HTML内容:', html);
                    }
                } catch (error) {
                    console.log('✗ 渲染函数执行失败:', error.message);
                }
            }
        }
    })
    .catch(error => {
        console.log('✗ API测试失败:', error.message);
    });

// 5. 提供手动测试函数
console.log('\n5. 手动测试函数已准备就绪:');
console.log('运行 testViewModal() 来手动测试查看功能');

window.testViewModal = function() {
    // 创建测试数据
    const testData = {
        id: 999,
        type: 'communication_rating',
        created_at: '2024-01-01 12:00:00',
        updated_at: '2024-01-01 12:00:00',
        data: {
            basic_info: {
                name: '测试学生',
                gender: '男',
                age: '8',
                grade: '二年级'
            },
            detailedData: [
                {
                    questionNumber: 1,
                    questionText: '在家里和亲密的家人交谈',
                    selectedText: '非常容易(没有焦虑)',
                    score: 0,
                    speechIssue: false
                }
            ],
            totalScore: 0,
            averageScore: 0.0,
            speechIssueCount: 0
        }
    };
    
    console.log('使用测试数据调用 showViewModal...');
    if (typeof showViewModal !== 'undefined') {
        showViewModal(testData);
    } else {
        console.log('showViewModal 函数未定义');
    }
};

console.log('\n=== 诊断完成 ===');
console.log('请检查上面的输出，找出问题所在。');
console.log('如果需要手动测试，请运行: testViewModal()');