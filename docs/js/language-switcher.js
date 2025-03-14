// Language Switcher for MockBoost Website

// Store translations for all text content
const translations = {
    // Page titles
    'page_title_home': {
        'zh': 'MockBoost - AI面试助手',
        'en': 'MockBoost - AI Interview Assistant'
    },
    'page_title_features': {
        'zh': '功能介绍 - MockBoost',
        'en': 'Features - MockBoost'
    },
    'page_title_download': {
        'zh': '下载 - MockBoost',
        'en': 'Download - MockBoost'
    },
    'page_title_contact': {
        'zh': '联系我们 - MockBoost',
        'en': 'Contact Us - MockBoost'
    },
    
    // Navigation
    'nav_home': {
        'zh': '首页',
        'en': 'Home'
    },
    'nav_features': {
        'zh': '功能介绍',
        'en': 'Features'
    },
    'nav_download': {
        'zh': '下载',
        'en': 'Download'
    },
    'nav_contact': {
        'zh': '联系我们',
        'en': 'Contact Us'
    },
    
    // Common sections
    'cta_title': {
        'zh': '准备好提升您的面试技能了吗？',
        'en': 'Ready to improve your interview skills?'
    },
    'cta_text': {
        'zh': '立即下载MockBoost，开始您的智能面试训练之旅',
        'en': 'Download MockBoost now and start your smart interview training journey'
    },
    'cta_button': {
        'zh': '免费下载',
        'en': 'Free Download'
    },
    'cta_button2': {
        'zh': '立即试用',
        'en': 'Free Use in Web'
    },
    'footer_links': {
        'zh': '快速链接',
        'en': 'Quick Links'
    },
    'footer_contact': {
        'zh': '联系我们',
        'en': 'Contact Us'
    },
    'footer_copyright': {
        'zh': '保留所有权利',
        'en': 'All Rights Reserved'
    },
    
    // Home page
    'hero_title': {
        'zh': 'MockBoost - 智能面试助手',
        'en': 'MockBoost - AI Interview Assistant'
    },
    'hero_text': {
        'zh': '利用AI技术提升您的面试技能，随时随地进行模拟面试训练',
        'en': 'Improve your interview skills with AI technology, practice mock interviews anytime, anywhere'
    },
    'features_title': {
        'zh': '核心功能',
        'en': 'Core Features'
    },
    'feature_interview': {
        'zh': '智能面试模拟',
        'en': 'Smart Interview Simulation'
    },
    'feature_interview_desc': {
        'zh': '基于深度学习技术，提供真实的面试场景模拟，针对不同岗位定制面试问题',
        'en': 'Based on deep learning technology, providing realistic interview scenarios customized for different positions'
    },
    'feature_voice': {
        'zh': '语音交互',
        'en': 'Voice Interaction'
    },
    'feature_voice_desc': {
        'zh': '支持语音识别和语音合成，让面试训练更加自然流畅',
        'en': 'Supports voice recognition and synthesis for more natural and fluid interview training'
    },
    'feature_analysis': {
        'zh': '表现分析',
        'en': 'Performance Analysis'
    },
    'feature_analysis_desc': {
        'zh': '智能分析您的回答，提供专业的反馈和改进建议',
        'en': 'Intelligently analyzes your answers, providing professional feedback and improvement suggestions'
    },
    'feature_history': {
        'zh': '历史记录',
        'en': 'History Records'
    },
    'feature_history_desc': {
        'zh': '保存面试历史，方便回顾和学习',
        'en': 'Saves interview history for easy review and learning'
    },
    'screenshots_title': {
        'zh': '产品展示',
        'en': 'Product Showcase'
    },
    'screenshot_login': {
        'zh': '简洁的登录界面',
        'en': 'Clean Login Interface'
    },
    'screenshot_conversation': {
        'zh': '智能对话系统',
        'en': 'Smart Conversation System'
    },
    'screenshot_history': {
        'zh': '面试历史记录',
        'en': 'Interview History Records'
    },
    
    // Features page
    'features_page_title': {
        'zh': '功能介绍',
        'en': 'Features'
    },
    'features_page_subtitle': {
        'zh': '探索MockBoost强大的AI面试助手功能',
        'en': 'Explore MockBoost\'s powerful AI interview assistant features'
    },
    'feature_interview_simulation': {
        'zh': '智能面试模拟',
        'en': 'Smart Interview Simulation'
    },
    'feature_interview_simulation_desc': {
        'zh': 'MockBoost采用先进的深度学习技术，提供真实的面试场景模拟。系统能够根据不同岗位和行业特点，生成针对性的面试问题，模拟真实面试官的提问方式和思路。',
        'en': 'MockBoost uses advanced deep learning technology to provide realistic interview simulations. The system can generate targeted interview questions based on different positions and industry characteristics, simulating the questioning methods of real interviewers.'
    },
    'feature_interview_point1': {
        'zh': '支持多种职位类型的面试模拟',
        'en': 'Supports interview simulations for various job types'
    },
    'feature_interview_point2': {
        'zh': '根据用户回答动态调整问题难度',
        'en': 'Dynamically adjusts question difficulty based on user responses'
    },
    'feature_interview_point3': {
        'zh': '模拟不同面试风格和场景',
        'en': 'Simulates different interview styles and scenarios'
    },
    'feature_interview_point4': {
        'zh': '提供专业的面试技巧指导',
        'en': 'Provides professional interview technique guidance'
    },
    'feature_voice_interaction': {
        'zh': '语音交互系统',
        'en': 'Voice Interaction System'
    },
    'feature_voice_interaction_desc': {
        'zh': 'MockBoost集成了高精度的语音识别和语音合成技术，让面试训练更加自然流畅。您可以通过语音与AI面试官进行对话，系统会实时识别您的回答并给出反馈。',
        'en': 'MockBoost integrates high-precision speech recognition and synthesis technology, making interview training more natural and smooth. You can converse with the AI interviewer through voice, and the system will recognize your answers in real-time and provide feedback.'
    },
    'feature_voice_point1': {
        'zh': '支持多种语言的语音识别',
        'en': 'Supports speech recognition in multiple languages'
    },
    'feature_voice_point2': {
        'zh': '自然流畅的AI语音合成',
        'en': 'Natural and fluid AI voice synthesis'
    },
    'feature_voice_point3': {
        'zh': '实时语音交互体验',
        'en': 'Real-time voice interaction experience'
    },
    'feature_voice_point4': {
        'zh': '语音节奏和语调分析',
        'en': 'Analysis of speech rhythm and intonation'
    },
    'feature_performance_analysis': {
        'zh': '表现分析与反馈',
        'en': 'Performance Analysis and Feedback'
    },
    'feature_performance_analysis_desc': {
        'zh': 'MockBoost不仅提供面试模拟，还能智能分析您的回答内容、语言表达、逻辑结构等方面，给出专业的评价和改进建议。',
        'en': 'MockBoost not only provides interview simulation but also intelligently analyzes your answer content, language expression, logical structure, and other aspects, giving professional evaluations and improvement suggestions.'
    },
    'feature_analysis_point1': {
        'zh': '回答内容的专业性评估',
        'en': 'Professional assessment of answer content'
    },
    'feature_analysis_point2': {
        'zh': '语言表达流畅度分析',
        'en': 'Analysis of language expression fluency'
    },
    'feature_analysis_point3': {
        'zh': '逻辑结构完整性检查',
        'en': 'Logical structure integrity check'
    },
    'feature_analysis_point4': {
        'zh': '针对性的改进建议',
        'en': 'Targeted improvement suggestions'
    },
    'feature_analysis_point5': {
        'zh': '面试技巧提升指导',
        'en': 'Interview skill improvement guidance'
    },
    'feature_history_learning': {
        'zh': '历史记录与学习',
        'en': 'History Records and Learning'
    },
    'feature_history_learning_desc': {
        'zh': '系统会自动保存您的面试历史记录，方便您随时回顾和学习。通过分析历史面试数据，系统还能为您提供个性化的学习计划和提升路径。',
        'en': 'The system automatically saves your interview history for easy review and learning. By analyzing historical interview data, the system can also provide personalized learning plans and improvement paths.'
    },
    'feature_history_point1': {
        'zh': '面试历史完整记录',
        'en': 'Complete record of interview history'
    },
    'feature_history_point2': {
        'zh': '面试表现趋势分析',
        'en': 'Interview performance trend analysis'
    },
    'feature_history_point3': {
        'zh': '个性化学习建议',
        'en': 'Personalized learning suggestions'
    },
    'feature_history_point4': {
        'zh': '弱项针对性训练',
        'en': 'Targeted training for weak areas'
    },
    
    // Download page
    'download_page_title': {
        'zh': '下载MockBoost',
        'en': 'Download MockBoost'
    },
    'download_page_subtitle': {
        'zh': '获取最新版本的AI面试助手',
        'en': 'Get the latest version of the AI interview assistant'
    },
    'download_version': {
        'zh': 'MockBoost v1.0.0',
        'en': 'MockBoost v1.0.0'
    },
    'download_release_date': {
        'zh': '发布日期: 2025年3月13日',
        'en': 'Release Date: March 13, 2025'
    },
    'download_feature_1': {
        'zh': '智能面试模拟功能',
        'en': 'Smart interview simulation'
    },
    'download_feature_2': {
        'zh': '语音交互系统',
        'en': 'Voice interaction system'
    },
    'download_feature_3': {
        'zh': '表现分析与反馈',
        'en': 'Performance analysis and feedback'
    },
    'download_feature_4': {
        'zh': '历史记录与学习',
        'en': 'History records and learning'
    },
    'download_button': {
        'zh': '下载Windows版本',
        'en': 'Download Windows Version'
    },
    'download_file_size': {
        'zh': '文件大小: 约30GB',
        'en': 'File Size: About 30GB'
    },
    'system_requirements': {
        'zh': '系统要求',
        'en': 'System Requirements'
    },
    'req_os': {
        'zh': '操作系统',
        'en': 'Operating System'
    },
    'req_os_desc': {
        'zh': 'Windows 10 64位或更高版本',
        'en': 'Windows 10 64-bit or higher'
    },
    'req_processor': {
        'zh': '处理器',
        'en': 'Processor'
    },
    'req_processor_desc': {
        'zh': 'Intel Core i5 或 AMD Ryzen 5 及以上',
        'en': 'Intel Core i5 or AMD Ryzen 5 and above'
    },
    'req_memory': {
        'zh': '内存',
        'en': 'Memory'
    },
    'req_memory_desc': {
        'zh': '12GB RAM 或更高',
        'en': '12GB RAM or higher'
    },
    'req_storage': {
        'zh': '存储空间',
        'en': 'Storage'
    },
    'req_storage_desc': {
        'zh': '至少50GB可用空间',
        'en': 'At least 50GB available space'
    },
    'req_device': {
        'zh': '设备',
        'en': 'Device'
    },
    'req_device_desc': {
        'zh': '4070Super及以上',
        'en': '4070Super or above'
    },
    'req_other': {
        'zh': '其他',
        'en': 'Other'
    },
    'req_other_desc': {
        'zh': '麦克风和扬声器（用于语音交互）',
        'en': 'Microphone and speakers (for voice interaction)'
    },
    'installation_guide': {
        'zh': '安装指南',
        'en': 'Installation Guide'
    },
    'install_step_1': {
        'zh': '下载MockBoost Zip文件',
        'en': 'Download the MockBoost Zip file'
    },
    'install_step_2': {
        'zh': '打开文件夹运行',
        'en': 'Open the folder and run'
    },
    'install_step_3': {
        'zh': '首次启动时，按照提示注册账号或登录',
        'en': 'When starting for the first time, follow the prompts to register or log in'
    },
    'install_step_4': {
        'zh': '开始您的智能面试训练之旅！',
        'en': 'Start your smart interview training journey!'
    },
    
    // Contact page
    'contact_page_title': {
        'zh': '联系我们',
        'en': 'Contact Us'
    },
    'contact_page_subtitle': {
        'zh': '有任何问题或建议？请随时与我们联系',
        'en': 'Any questions or suggestions? Feel free to contact us'
    },
    'contact_email': {
        'zh': '电子邮件',
        'en': 'Email'
    },
    'contact_social': {
        'zh': '社交媒体',
        'en': 'Social Media'
    },
    'contact_wechat': {
        'zh': '微信公众号：MockBoost',
        'en': 'WeChat Official Account: MockBoost'
    },
    'contact_zhihu': {
        'zh': '知乎：MockBoost官方',
        'en': 'Zhihu: MockBoost Official'
    },
    'contact_address': {
        'zh': '办公地址',
        'en': 'Office Address'
    },
    'contact_address_1': {
        'zh': '广东省珠海市横琴高级人才公寓',
        'en': 'Hengqin Advanced Talent Apartment, Zhuhai, Guangdong Province'
    },
    'contact_address_2': {
        'zh': '2栋 18楼',
        'en': 'Building 2, 18th Floor'
    },
    'contact_form_title': {
        'zh': '发送消息',
        'en': 'Send Message'
    },
    'contact_form_name': {
        'zh': '您的姓名',
        'en': 'Your Name'
    },
    'contact_form_email': {
        'zh': '电子邮箱',
        'en': 'Email'
    },
    'contact_form_subject': {
        'zh': '主题',
        'en': 'Subject'
    },
    'contact_form_message': {
        'zh': '消息内容',
        'en': 'Message'
    },
    'contact_form_submit': {
        'zh': '发送消息',
        'en': 'Send Message'
    },
    'faq_title': {
        'zh': '常见问题',
        'en': 'Frequently Asked Questions'
    },
    'faq_q1': {
        'zh': 'MockBoost是免费软件吗？',
        'en': 'Is MockBoost free software?'
    },
    'faq_a1': {
        'zh': '是的，MockBoost目前提供免费版本供所有用户使用。我们未来可能会推出包含更多高级功能的付费版本。',
        'en': 'Yes, MockBoost currently provides a free version for all users. We may introduce a paid version with more advanced features in the future.'
    },
    'faq_q2': {
        'zh': 'MockBoost支持哪些操作系统？',
        'en': 'Which operating systems does MockBoost support?'
    },
    'faq_a2': {
        'zh': '目前MockBoost仅支持Windows 10及以上版本。我们正在开发macOS和Linux版本，敬请期待。',
        'en': 'Currently, MockBoost only supports Windows 10 and above. We are developing macOS and Linux versions, stay tuned.'
    },
    'faq_q3': {
        'zh': '如何更新MockBoost？',
        'en': 'How do I update MockBoost?'
    },
    'faq_a3': {
        'zh': 'MockBoost会自动检查更新。您也可以在本网站下载页面获取最新版本。',
        'en': 'MockBoost automatically checks for updates. You can also get the latest version from the download page on this website.'
    },
    'faq_q4': {
        'zh': '我可以离线使用MockBoost吗？',
        'en': 'Can I use MockBoost offline?'
    },
    'faq_a4': {
        'zh': 'MockBoost可以离线运行，因为是基于本地大模型的。',
        'en': 'MockBoost can run offline because it is based on a local large model.'
    }
};

// Current language (default is English now)
let currentLanguage = 'en';

// Function to toggle language
function toggleLanguage() {
    // Switch language
    currentLanguage = currentLanguage === 'zh' ? 'en' : 'zh';
    
    // Update language button text
    const langBtn = document.getElementById('language-toggle');
    if (langBtn) {
        langBtn.textContent = currentLanguage === 'zh' ? 'English' : '中文';
    }
    
    // Update all translatable elements
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key] && translations[key][currentLanguage]) {
            element.textContent = translations[key][currentLanguage];
        }
    });
    
    // Update page title
    const titleKey = document.querySelector('title').getAttribute('data-i18n');
    if (titleKey && translations[titleKey] && translations[titleKey][currentLanguage]) {
        document.title = translations[titleKey][currentLanguage];
    }
    
    // Update placeholders for form inputs
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[key] && translations[key][currentLanguage]) {
            element.placeholder = translations[key][currentLanguage];
        }
    });
    
    // Save language preference to localStorage
    localStorage.setItem('mockboost-language', currentLanguage);
}

// Function to apply the current language
function applyLanguage() {
    // Update language button text
    const langBtn = document.getElementById('language-toggle');
    if (langBtn) {
        langBtn.textContent = currentLanguage === 'zh' ? 'English' : '中文';
    }
    
    // Update all translatable elements
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key] && translations[key][currentLanguage]) {
            element.textContent = translations[key][currentLanguage];
        }
    });
    
    // Update page title
    const titleKey = document.querySelector('title').getAttribute('data-i18n');
    if (titleKey && translations[titleKey] && translations[titleKey][currentLanguage]) {
        document.title = translations[titleKey][currentLanguage];
    }
    
    // Update placeholders for form inputs
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[key] && translations[key][currentLanguage]) {
            element.placeholder = translations[key][currentLanguage];
        }
    });
}

// Initialize language switcher
document.addEventListener('DOMContentLoaded', function() {
    // Create language toggle button
    const header = document.querySelector('header .container');
    if (header) {
        const langBtn = document.createElement('button');
        langBtn.id = 'language-toggle';
        langBtn.className = 'lang-btn';
        langBtn.addEventListener('click', toggleLanguage);
        
        // Insert before the first child of header
        header.insertBefore(langBtn, header.firstChild);
        
        // Add CSS for the language button
        const style = document.createElement('style');
        style.textContent = `
            .lang-btn {
                background-color: #4a6cf7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
                transition: background-color 0.3s;
                margin-right: 15px;
            }
            .lang-btn:hover {
                background-color: #3a5ce5;
            }
            @media (max-width: 768px) {
                .lang-btn {
                    margin-bottom: 10px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Check if user has a language preference saved
    const savedLanguage = localStorage.getItem('mockboost-language');
    if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'zh')) {
        currentLanguage = savedLanguage;
    }
    
    // Apply the current language
    applyLanguage();
}); 