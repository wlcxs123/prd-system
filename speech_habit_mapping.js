// 说话习惯记录问题ID到表格位置的映射
const speechHabitMapping = {
    // 家人
    'family_alone_passive': { row: 'family', col: 'alone_passive' },
    'family_alone_active': { row: 'family', col: 'alone_active' },
    'family_with_others_passive': { row: 'family', col: 'with_others_passive' },
    'family_with_others_active': { row: 'family', col: 'with_others_active' },
    'family_group_passive': { row: 'family', col: 'group_passive' },
    'family_group_active': { row: 'family', col: 'group_active' },
    
    // 熟人（合并朋友和经常联系的人）
    'friends_alone_passive': { row: 'acquaintances', col: 'alone_passive' },
    'friends_alone_active': { row: 'acquaintances', col: 'alone_active' },
    'friends_with_others_passive': { row: 'acquaintances', col: 'with_others_passive' },
    'friends_with_others_active': { row: 'acquaintances', col: 'with_others_active' },
    'friends_group_passive': { row: 'acquaintances', col: 'group_passive' },
    'friends_group_active': { row: 'acquaintances', col: 'group_active' },
    
    'frequent_contacts_alone_passive': { row: 'acquaintances', col: 'alone_passive' },
    'frequent_contacts_alone_active': { row: 'acquaintances', col: 'alone_active' },
    'frequent_contacts_with_others_passive': { row: 'acquaintances', col: 'with_others_passive' },
    'frequent_contacts_with_others_active': { row: 'acquaintances', col: 'with_others_active' },
    'frequent_contacts_group_passive': { row: 'acquaintances', col: 'group_passive' },
    'frequent_contacts_group_active': { row: 'acquaintances', col: 'group_active' },
    
    // 陌生人
    'strangers_alone_passive': { row: 'strangers', col: 'alone_passive' },
    'strangers_alone_active': { row: 'strangers', col: 'alone_active' },
    'strangers_with_others_passive': { row: 'strangers', col: 'with_others_passive' },
    'strangers_with_others_active': { row: 'strangers', col: 'with_others_active' },
    'strangers_group_passive': { row: 'strangers', col: 'group_passive' },
    'strangers_group_active': { row: 'strangers', col: 'group_active' }
};

// 行标题映射
const rowTitles = {
    'family': '家人',
    'acquaintances': '熟人',
    'strangers': '陌生人'
};

// 列标题映射
const colTitles = {
    'alone_passive': '独处时被动回应',
    'alone_active': '独处时主动发起',
    'with_others_passive': '与他人在一起时被动回应',
    'with_others_active': '与他人在一起时主动发起',
    'group_passive': '群体中被动回应',
    'group_active': '群体中主动发起'
};

// 选项映射
const optionMapping = {
    'normal': { text: '正常音量', symbol: '●' },
    'quiet': { text: '小声说话', symbol: '◐' },
    'whisper': { text: '悄声/耳语', symbol: '○' }
};