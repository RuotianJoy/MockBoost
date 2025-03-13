// DOM Elements
const authContainer = document.getElementById('authContainer');
const chatContainer = document.getElementById('chatContainer');
const landingContainer = document.getElementById('landingContainer');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendMessage');
const chatMessages = document.getElementById('chatMessages');
const startVoiceButton = document.getElementById('startVoice');
const sendVerificationBtn = document.getElementById('sendVerificationBtn');
const howItWorksModal = document.getElementById('howItWorksModal');

// Landing page buttons
const loginNavBtn = document.getElementById('loginNavBtn');
const registerNavBtn = document.getElementById('registerNavBtn');
const getStartedBtn = document.getElementById('getStartedBtn');
const startNowBtn = document.getElementById('startNowBtn');
const backToHomeBtn = document.getElementById('backToHomeBtn');
const backToHomeFromRegister = document.getElementById('backToHomeFromRegister');
const closeHowItWorksBtn = document.getElementById('closeHowItWorksBtn');

// Audio Context and Recorder
let mediaRecorder;
let audioChunks = [];
let verificationCode = null; // 存储验证码
let conversationId = null; // 存储当前对话ID

// Landing Page Module
const LandingPageModule = (function() {
    function init() {
        console.log('Initializing landing page module');
        
        // IMPORTANT: Force clear any stored authentication data
        localStorage.removeItem('user_id');
        localStorage.removeItem('conversation_id');
        
        // Always show landing page on init
        landingContainer.classList.remove('hidden');
        authContainer.classList.add('hidden');
        chatContainer.classList.add('hidden');
        
        // Add event listeners for landing page buttons
        if (loginNavBtn) {
            loginNavBtn.addEventListener('click', showLoginForm);
        }
        
        if (registerNavBtn) {
            registerNavBtn.addEventListener('click', showRegisterForm);
        }
        
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', showLoginForm);
        }
        
        if (startNowBtn) {
            startNowBtn.addEventListener('click', showLoginForm);
        }
        
        if (backToHomeBtn) {
            backToHomeBtn.addEventListener('click', showLandingPage);
        }
        
        if (backToHomeFromRegister) {
            backToHomeFromRegister.addEventListener('click', showLandingPage);
        }


        
        // Add event listeners for "How It Works" modal
        const howItWorksLinks = document.querySelectorAll('.how-it-works-link');
        howItWorksLinks.forEach(link => {
            link.addEventListener('click', showHowItWorksModal);
        });
        
        if (closeHowItWorksBtn) {
            closeHowItWorksBtn.addEventListener('click', hideHowItWorksModal);
        }
        
        // Add animation to feature cards on scroll
        animateOnScroll();
    }
    
    function showLoginForm() {
        landingContainer.classList.add('hidden');
        authContainer.classList.remove('hidden');
        
        // Make sure login form is visible (not register)
        const authBoxes = document.querySelectorAll('.auth-box');
        if (authBoxes[0].classList.contains('hidden')) {
            AuthModule.toggleAuth(); // Switch to login if register is showing
        }
    }
    
    function showRegisterForm() {
        landingContainer.classList.add('hidden');
        authContainer.classList.remove('hidden');
        
        // Make sure register form is visible (not login)
        const authBoxes = document.querySelectorAll('.auth-box');
        if (!authBoxes[0].classList.contains('hidden')) {
            AuthModule.toggleAuth(); // Switch to register if login is showing
        }
    }
    
    function showLandingPage() {
        authContainer.classList.add('hidden');
        landingContainer.classList.remove('hidden');
    }
    
    function showHowItWorksModal() {
        if (howItWorksModal) {
            howItWorksModal.classList.add('active');
        }
    }
    
    function hideHowItWorksModal() {
        if (howItWorksModal) {
            howItWorksModal.classList.remove('active');
        }
    }
    
    function animateOnScroll() {
        // Add animation to elements when they come into view
        const animateElements = document.querySelectorAll('.feature-card, .testimonial-card');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });
        
        animateElements.forEach(element => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(element);
        });
    }
    
    // Function to verify if the user is authenticated
    async function verifyUserAuthentication(userId) {
        try {
            const response = await fetch('/verify-auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            
            if (!response.ok) {
                throw new Error('Authentication verification failed');
            }
            
            const data = await response.json();
            return data.authenticated;
        } catch (error) {
            console.error('Authentication verification failed:', error);
            // If verification fails, clear stored credentials as a safety measure
            localStorage.removeItem('user_id');
            localStorage.removeItem('conversation_id');
            return false;
        }
    }
    
    // Function to show loading overlay
    function showLoadingOverlay(message) {
        // Create loading overlay if it doesn't exist
        let loadingOverlay = document.getElementById('loadingOverlay');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loadingOverlay';
            loadingOverlay.className = 'loading-overlay';
            
            const loadingContent = document.createElement('div');
            loadingContent.className = 'loading-content';
            
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            const loadingMessage = document.createElement('div');
            loadingMessage.id = 'loadingMessage';
            loadingMessage.className = 'loading-message';
            
            loadingContent.appendChild(spinner);
            loadingContent.appendChild(loadingMessage);
            loadingOverlay.appendChild(loadingContent);
            
            document.body.appendChild(loadingOverlay);
        }
        
        // Set message and show overlay
        document.getElementById('loadingMessage').textContent = message || 'Loading...';
        loadingOverlay.classList.add('active');
    }
    
    // Function to hide loading overlay
    function hideLoadingOverlay() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
        }
    }
    
    return {
        init: init,
        showLoginForm: showLoginForm,
        showRegisterForm: showRegisterForm,
        showLandingPage: showLandingPage,
        showLoadingOverlay: showLoadingOverlay,
        hideLoadingOverlay: hideLoadingOverlay
    };
})();

// 聊天功能封装
const ChatModule = (function() {
    // 私有变量
    let isRecording = false;
    let typingIndicator = null;
    
    // 私有方法
    function createTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.classList.add('message', 'bot-message', 'typing-indicator');
        indicator.innerHTML = '<span></span><span></span><span></span>';
        return indicator;
    }
    
    function removeTypingIndicator() {
        if (typingIndicator && typingIndicator.parentNode) {
            typingIndicator.parentNode.removeChild(typingIndicator);
            typingIndicator = null;
        }
    }
    
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // 公共接口
    return {
        // 添加消息到聊天界面
        addMessage: function(message, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');
            messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
            messageDiv.textContent = message;
            
            // 添加动画效果
            if (!isUser) {
                messageDiv.style.opacity = '0';
                chatMessages.appendChild(messageDiv);
                
                setTimeout(() => {
                    messageDiv.style.opacity = '1';
                }, 100);
            } else {
                chatMessages.appendChild(messageDiv);
            }
            
            scrollToBottom();
        },
        
        // 显示AI正在输入状态
        showTyping: function() {
            typingIndicator = createTypingIndicator();
            chatMessages.appendChild(typingIndicator);
            scrollToBottom();
        },
        
        // 隐藏AI正在输入状态
        hideTyping: function() {
            removeTypingIndicator();
        },
        
        // 发送消息到服务器并处理响应
        sendMessage: async function(message) {
            if (!message.trim()) return;
            
            // 防止重复提交
            if (this.isSubmitting) {
                console.log('消息正在提交中，请等待...');
                return;
            }
            
            // 设置提交状态
            this.isSubmitting = true;
            
            // 显示用户消息
            this.addMessage(message, true);
            messageInput.value = '';
            
            // 显示"正在输入"状态
            this.showTyping();

            try {
                // 获取当前登录的用户ID
                const user_id = localStorage.getItem('user_id') || 'default_user';
                
                // 添加调试日志
                console.log('发送消息:', {
                    message,
                    user_id,
                    conversation_id: conversationId
                });
                
                // 发送消息到服务器，包含对话ID
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message,
                        user_id,
                        conversation_id: conversationId
                    })
                });
                const data = await response.json();
                
                // 保存返回的对话ID
                if (data.conversation_id) {
                    console.log('收到对话ID:', data.conversation_id);
                    conversationId = data.conversation_id;
                    localStorage.setItem('conversation_id', conversationId);
                }
                
                // 移除"正在输入"状态
                this.hideTyping();
                
                // 添加回复消息
                this.addMessage(data.response);
                
                return data.response;
            } catch (error) {
                console.error('发送消息失败:', error);
                this.hideTyping();
                this.addMessage('抱歉，发送消息失败，请重试。', false);
                return null;
            } finally {
                // 重置提交状态
                setTimeout(() => {
                    this.isSubmitting = false;
                }, 500); // 添加短暂延迟，防止快速连续点击
            }
        },
        
        // 开始面试
        startInterview: async function() {
            console.log('startInterview 方法被调用');
            
            // 防止重复点击
            if (this.isStartingInterview) {
                console.log('面试正在开始中，请等待...');
                return;
            }
            
            this.isStartingInterview = true;
            
            const startInterviewBtn = document.getElementById('startInterviewBtn');
            if (startInterviewBtn) {
                if (startInterviewBtn.disabled) {
                    console.log('按钮已禁用，防止重复提交');
                    this.isStartingInterview = false;
                    return;
                }
                startInterviewBtn.disabled = true;
                startInterviewBtn.style.opacity = '0.7';
                startInterviewBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            }
            
            // 获取用户信息
            const userId = localStorage.getItem('user_id');
            if (!userId) {
                this.addMessage('请先登录后再开始面试', false);
                resetButton();
                this.isStartingInterview = false;
                return;
            }
            
            try {
                // 获取用户输入的意向职业
                const jobInput = document.getElementById('jobInput');
                const customJob = jobInput ? jobInput.value.trim() : '';
                
                // 每次开始面试时，清除现有的对话ID
                conversationId = null;
                localStorage.removeItem('conversation_id');
                localStorage.removeItem('interview_started');
                
                // 清空聊天界面
                chatMessages.innerHTML = '';
                this.addMessage('Starting...', false);
                
                // 获取用户详细信息
                const response = await fetch('/user-profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const userInfo = data.user_info;
                    
                    // 使用用户输入的职业，如果没有输入则使用用户资料中的职业
                    const intendedJob = customJob || userInfo.Job;
                    
                    // 更新输入框显示
                    if (jobInput && !customJob && userInfo.Job) {
                        jobInput.value = userInfo.Job;
                    }
                    
                    // 构建固定格式的自我介绍
                    const selfIntroduction = `Hello, I am ${userInfo.Name}, My major is ${userInfo.Major}, I want be the ${intendedJob}.`;
                    
                    // 显示用户消息
                    this.addMessage(selfIntroduction, true);
                    
                    // 显示"正在输入"状态
                    this.showTyping();
                    
                    // 发送消息到服务器
                    const chatResponse = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: selfIntroduction,
                            user_id: userId,
                            conversation_id: null, // 强制创建新对话
                            job: intendedJob,
                            major: userInfo.Major
                        })
                    });
                    
                    const chatData = await chatResponse.json();
                    
                    // 保存返回的对话ID
                    if (chatData.conversation_id) {
                        conversationId = chatData.conversation_id;
                        localStorage.setItem('conversation_id', conversationId);
                        localStorage.setItem('interview_started', 'true'); // 标记面试已开始
                        console.log('新对话ID:', conversationId);
                    }
                    
                    // 移除"正在输入"状态
                    this.hideTyping();
                    
                    // 添加回复消息
                    this.addMessage(chatData.response);
                    
                    // 不隐藏开始面试按钮，让用户可以随时重新开始
                    console.log('面试已开始');
                } else {
                    this.addMessage('获取用户信息失败，请重试', false);
                }
            } catch (error) {
                console.error('开始面试失败:', error);
                this.addMessage('开始面试失败，请重试', false);
            } finally {
                // 重置按钮状态
                resetButton();
                
                // 延迟重置状态，防止快速连续点击
                setTimeout(() => {
                    this.isStartingInterview = false;
                }, 1000);
            }
            
            // 重置按钮状态的辅助函数
            function resetButton() {
                if (startInterviewBtn) {
                    startInterviewBtn.disabled = false;
                    startInterviewBtn.style.opacity = '1';
                    startInterviewBtn.innerHTML = '<i class="fas fa-play-circle"></i> New Start';
                }
            }
        },
        
        // 语音转文字
        startVoiceRecording: async function() {
            if (isRecording) {
                // 如果已经在录音，则停止录音
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                }
                return;
            }
            
            try {
                isRecording = true;
                startVoiceButton.classList.add('recording');
                startVoiceButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.addEventListener('dataavailable', (event) => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener('stop', async () => {
                    startVoiceButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('audio', audioBlob);

                    try {
                        const response = await fetch('/speech-to-text', {
                            method: 'POST',
                            body: formData
                        });
                        const data = await response.json();
                        if (data.text) {
                            messageInput.value = data.text;
                            this.sendMessage(data.text);
                        }
                    } catch (error) {
                        console.error('语音识别失败:', error);
                        alert('语音识别失败，请重试');
                    }

                    isRecording = false;
                    startVoiceButton.classList.remove('recording');
                    startVoiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
                    stream.getTracks().forEach(track => track.stop());
                });

                mediaRecorder.start();
            } catch (error) {
                console.error('麦克风访问失败:', error);
                isRecording = false;
                startVoiceButton.classList.remove('recording');
                startVoiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
                alert('无法访问麦克风');
            }
        },
        
        // 停止语音录制
        stopVoiceRecording: function() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        },
        
        // 初始化聊天模块
        init: function() {
            // 设置聊天模式样式
            document.getElementById('app').classList.add('in-chat-mode');
            
            // 尝试从本地存储恢复对话ID
            conversationId = localStorage.getItem('conversation_id');
            
            // 确保开始面试按钮可见
            const startInterviewBtn = document.getElementById('startInterviewBtn');
            if (startInterviewBtn) {
                console.log('ChatModule.init: 找到开始面试按钮');
                
                // 强制显示按钮
                startInterviewBtn.style.display = 'flex';
                startInterviewBtn.style.visibility = 'visible';
                startInterviewBtn.style.opacity = '1';
                
                // 移除可能存在的旧事件监听器
                startInterviewBtn.replaceWith(startInterviewBtn.cloneNode(true));
                
                // 重新获取按钮引用
                const newStartInterviewBtn = document.getElementById('startInterviewBtn');
                
                // 添加点击事件
                newStartInterviewBtn.addEventListener('click', (e) => {
                    console.log('ChatModule.init: 开始面试按钮被点击');
                    e.preventDefault(); // 阻止可能的默认行为
                    e.stopPropagation(); // 阻止事件冒泡
                    this.startInterview();
                });
                
                // 只有在确认有活跃对话时才隐藏按钮
                if (conversationId && localStorage.getItem('interview_started') === 'true') {
                    // 即使有活跃对话，也不隐藏按钮
                    // startInterviewBtn.style.display = 'none';
                }
            } else {
                console.error('ChatModule.init: 未找到开始面试按钮');
            }
            
            // 调整输入框宽度以匹配应用容器
            const adjustInputContainer = () => {
                const appWidth = document.getElementById('app').offsetWidth;
                const inputContainer = document.querySelector('.chat-input-container');
                if (inputContainer) {
                    inputContainer.style.maxWidth = `${appWidth}px`;
                }
            };
            
            // 初始调整和窗口大小变化时调整
            adjustInputContainer();
            window.addEventListener('resize', adjustInputContainer);
            
            // 确保聊天消息区域可以滚动到底部
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // 发送按钮点击事件
            sendButton.addEventListener('click', () => {
                const message = messageInput.value.trim();
                if (message) {
                    this.sendMessage(message);
                }
            });
            
            // 输入框回车事件
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = messageInput.value.trim();
                    if (message) {
                        this.sendMessage(message);
                    }
                }
            });
            
            // 语音按钮点击事件
            startVoiceButton.addEventListener('click', () => {
                this.startVoiceRecording();
            });
            
            // 输入框焦点事件
            messageInput.addEventListener('focus', () => {
                document.querySelector('.chat-input-container').style.boxShadow = '0 0 0 3px rgba(106, 17, 203, 0.2)';
            });
            
            messageInput.addEventListener('blur', () => {
                document.querySelector('.chat-input-container').style.boxShadow = 'none';
            });
            
            // 初始化用户信息模块
            UserProfileModule.init();
            
            // 添加清除聊天按钮
            const clearChatBtn = document.getElementById('clearChatBtn');
            if (clearChatBtn) {
                clearChatBtn.addEventListener('click', () => {
                    if (confirm('确定要清除所有聊天记录吗？')) {
                        this.clearChat();
                    }
                });
            }
            
            console.log('聊天模块初始化完成');
            
            // 加载用户信息并设置职业输入框
            loadUserProfile().then(userInfo => {
                if (userInfo && userInfo.Job) {
                    const jobInput = document.getElementById('jobInput');
                    if (jobInput) {
                        jobInput.value = userInfo.Job;
                        jobInput.setAttribute('placeholder', 'Intended Job: ' + userInfo.Job);
                    }
                }
            });
        },
        
        // 清除聊天记录
        clearChat: async function() {
            try {
                const user_id = localStorage.getItem('user_id') || 'default_user';
                
                const response = await fetch('/clear-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 清空聊天界面
                    chatMessages.innerHTML = '';
                    
                    // 添加欢迎消息
                    this.addMessage('Welcome to Interview!', false);
                    
                    // 更新对话ID
                    if (data.conversation_id) {
                        conversationId = data.conversation_id;
                        localStorage.setItem('conversation_id', conversationId);
                        localStorage.removeItem('interview_started'); // 重置面试状态
                    }
                    
                    // 显示开始面试按钮
                    const startInterviewBtn = document.getElementById('startInterviewBtn');
                    if (startInterviewBtn) {
                        startInterviewBtn.style.display = 'flex';
                    }
                }
            } catch (error) {
                console.error('清除聊天失败:', error);
            }
        }
    };
})();

// 登录和注册功能封装
const AuthModule = (function() {
    // 切换登录和注册表单
    function toggleAuth() {
        const authBoxes = document.querySelectorAll('.auth-box');
        
        // 添加动画类
        if (authBoxes[0].classList.contains('hidden')) {
            authBoxes[1].classList.add('slide-out');
            setTimeout(() => {
                authBoxes[1].classList.add('hidden');
                authBoxes[1].classList.remove('slide-out');
                authBoxes[0].classList.remove('hidden');
                authBoxes[0].classList.add('slide-in');
                setTimeout(() => {
                    authBoxes[0].classList.remove('slide-in');
                }, 500);
            }, 450);
        } else {
            authBoxes[0].classList.add('slide-out');
            setTimeout(() => {
                authBoxes[0].classList.add('hidden');
                authBoxes[0].classList.remove('slide-out');
                authBoxes[1].classList.remove('hidden');
                authBoxes[1].classList.add('slide-in');
                setTimeout(() => {
                    authBoxes[1].classList.remove('slide-in');
                }, 500);
            }, 450);
        }
    }
    
    // 初始化认证模块
    function init() {
        // 设置切换认证方式的事件
        document.querySelectorAll('a[onclick="toggleAuth()"]').forEach(link => {
            link.onclick = function(e) {
                e.preventDefault();
                toggleAuth();
            };
        });
        
        // 添加输入框动画效果
        const inputGroups = document.querySelectorAll('.input-group');
        inputGroups.forEach(group => {
            const input = group.querySelector('input');
            const icon = group.querySelector('i');
            
            if (input && icon) {
                input.addEventListener('focus', () => {
                    icon.style.color = '#6a11cb';
                });
                
                input.addEventListener('blur', () => {
                    icon.style.color = '';
                });
            }
        });
        
        // 登录表单提交
        loginForm.addEventListener('submit', handleLogin);
        
        // 注册表单提交
        registerForm.addEventListener('submit', handleRegister);
        
        // 发送验证码
        sendVerificationBtn.addEventListener('click', sendVerificationCode);
    }
    
    // 处理登录
    async function handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        // Show loading overlay
        LandingPageModule.showLoadingOverlay('Logging in...');
        
        // 显示加载动画
        const submitBtn = loginForm.querySelector('button');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i></div> 登录中...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();

            if (data.success) {
                // 保存用户ID
                if (data.user_id) {
                    localStorage.setItem('user_id', data.user_id);
                }
                
                // 成功动画
                submitBtn.innerHTML = '<i class="fas fa-check"></i> Success';
                submitBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #218838 100%)';
                
                setTimeout(() => {
                    // Hide loading overlay
                    LandingPageModule.hideLoadingOverlay();
                    
                    // Hide both landing and auth containers
                    landingContainer.classList.add('hidden');
                    authContainer.classList.add('hidden');
                    chatContainer.classList.remove('hidden');
                    // 初始化聊天模块
                    ChatModule.init();
                }, 1000);
            } else {
                // Hide loading overlay
                LandingPageModule.hideLoadingOverlay();
                
                // 失败动画
                submitBtn.innerHTML = '<i class="fas fa-times"></i> 登录失败';
                submitBtn.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.style.background = '';
                    submitBtn.disabled = false;
                    alert('登录失败：' + data.message);
                }, 1000);
            }
        } catch (error) {
            // Hide loading overlay
            LandingPageModule.hideLoadingOverlay();
            
            submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> 错误';
            submitBtn.style.background = 'linear-gradient(135deg, #ffc107 0%, #e0a800 100%)';
            
            setTimeout(() => {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.style.background = '';
                submitBtn.disabled = false;
                alert('登录出错，请重试');
            }, 1000);
        }
    }
    
    // 发送验证码
    async function sendVerificationCode() {
        const email = document.getElementById('registerEmail').value;
        if (!email) {
            alert('请输入邮箱地址');
            return;
        }

        try {
            sendVerificationBtn.disabled = true;
            const originalBtnText = sendVerificationBtn.innerHTML;
            sendVerificationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';

            const response = await fetch('/send-verification', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            const data = await response.json();

            if (data.success) {
                verificationCode = data.code;
                sendVerificationBtn.innerHTML = '<i class="fas fa-check"></i> 已发送';
                setTimeout(() => {
                    sendVerificationBtn.innerHTML = '<i class="fas fa-clock"></i> 60秒';
                }, 1000);
                
                // 倒计时60秒
                let countdown = 60;
                
                const timer = setInterval(() => {
                    countdown--;
                    sendVerificationBtn.innerHTML = `<i class="fas fa-clock"></i> ${countdown}秒`;
                    
                    if (countdown <= 0) {
                        clearInterval(timer);
                        sendVerificationBtn.disabled = false;
                        sendVerificationBtn.innerHTML = originalBtnText;
                    }
                }, 1000);
            } else {
                sendVerificationBtn.innerHTML = '<i class="fas fa-times"></i> 发送失败';
                setTimeout(() => {
                    sendVerificationBtn.disabled = false;
                    sendVerificationBtn.innerHTML = originalBtnText;
                    alert('发送验证码失败：' + data.message);
                }, 1000);
            }
        } catch (error) {
            sendVerificationBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> 错误';
            setTimeout(() => {
                sendVerificationBtn.disabled = false;
                sendVerificationBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发送验证码';
                alert('发送验证码出错，请重试');
            }, 1000);
        }
    }
    
    // 处理注册
    async function handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const job = document.getElementById('registerJob').value;
        const major = document.getElementById('registerMajor').value;
        const email = document.getElementById('registerEmail').value;
        const inputVerificationCode = document.getElementById('verificationCode').value;

        // 验证密码一致性
        if (password !== confirmPassword) {
            alert('两次输入的密码不一致');
            return;
        }

        // 验证所有字段都已填写
        if (!username || !password || !job || !major || !email || !inputVerificationCode) {
            alert('请填写所有必填字段');
            return;
        }

        // 显示加载动画
        const submitBtn = registerForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 注册中...';
        submitBtn.disabled = true;

        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    username, 
                    password, 
                    job,
                    major,
                    email, 
                    verification_code: inputVerificationCode,
                    stored_code: verificationCode
                })
            });
            const data = await response.json();

            if (data.success) {
                // 成功动画
                submitBtn.innerHTML = '<i class="fas fa-check"></i> 注册成功';
                submitBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #218838 100%)';
                
                setTimeout(() => {
                    alert('注册成功，请登录');
                    toggleAuth();
                    // 清空注册表单
                    registerForm.reset();
                    // 将用户名填入登录表单
                    document.getElementById('loginUsername').value = username;
                    // 恢复按钮状态
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.style.background = '';
                    submitBtn.disabled = false;
                }, 1000);
            } else {
                // 失败动画
                submitBtn.innerHTML = '<i class="fas fa-times"></i> 注册失败';
                submitBtn.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.style.background = '';
                    submitBtn.disabled = false;
                    alert('注册失败：' + data.message);
                }, 1000);
            }
        } catch (error) {
            submitBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> 错误';
            submitBtn.style.background = 'linear-gradient(135deg, #ffc107 0%, #e0a800 100%)';
            
            setTimeout(() => {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.style.background = '';
                submitBtn.disabled = false;
                alert('注册出错，请重试');
            }, 1000);
        }
    }
    
    return {
        init: init,
        toggleAuth: toggleAuth
    };
})();

// Make toggleAuth globally accessible
window.toggleAuth = AuthModule.toggleAuth;

// 添加CSS样式
const style = document.createElement('style');
style.textContent = `
.input-group {
    position: relative;
}

.input-group i {
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
    color: rgba(255, 255, 255, 0.5);
    transition: color 0.3s ease;
}

.input-group input {
    padding-left: 45px;
}

.typing-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 15px 20px;
    max-width: 100px;
}

.typing-indicator span {
    height: 8px;
    width: 8px;
    margin: 0 2px;
    background-color: rgba(255, 255, 255, 0.7);
    border-radius: 50%;
    display: inline-block;
    animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
    animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0% {
        transform: scale(0);
    }
    50% {
        transform: scale(1);
    }
    100% {
        transform: scale(0);
    }
}

.loading-spinner {
    display: inline-block;
    margin-right: 8px;
}
`;
document.head.appendChild(style);

// 修改 DOMContentLoaded 事件处理函数，移除重复的事件绑定
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成');
    
    // Force clear any stored authentication data
    localStorage.removeItem('user_id');
    localStorage.removeItem('conversation_id');
    
    // Ensure correct initial state - always start with landing page
    if (landingContainer) landingContainer.classList.remove('hidden');
    if (authContainer) authContainer.classList.add('hidden');
    if (chatContainer) chatContainer.classList.add('hidden');
    
    // Initialize landing page module
    LandingPageModule.init();
    
    // 初始化认证模块
    AuthModule.init();
    
    // 检查开始面试按钮是否存在，但不再绑定事件
    const startInterviewBtn = document.getElementById('startInterviewBtn');
    if (startInterviewBtn) {
        console.log('找到开始面试按钮');
        console.log('按钮当前显示状态:', window.getComputedStyle(startInterviewBtn).display);
        
        // 强制显示按钮
        startInterviewBtn.style.display = 'flex';
        startInterviewBtn.style.visibility = 'visible';
        startInterviewBtn.style.opacity = '1';
    } else {
        console.error('未找到开始面试按钮');
    }
});

// 在 UserProfileModule 中添加历史对话功能
const UserProfileModule = (function() {
    // 私有变量
    let userProfileSidebar;
    let overlay;
    let userAvatarBtn;
    let closeProfileBtn;
    let logoutBtn;
    let historyList;
    let historyDialog;
    let closeHistoryBtn;
    let userInfo = null;
    
    // 初始化
    function init() {
        userProfileSidebar = document.getElementById('userProfileSidebar');
        overlay = document.getElementById('overlay');
        userAvatarBtn = document.getElementById('userAvatarBtn');
        closeProfileBtn = document.getElementById('closeProfileBtn');
        logoutBtn = document.getElementById('logoutBtn');
        historyList = document.getElementById('historyList');
        historyDialog = document.getElementById('historyDialog');
        closeHistoryBtn = document.getElementById('closeHistoryBtn');
        
        if (!userProfileSidebar || !overlay || !userAvatarBtn || !closeProfileBtn || !logoutBtn) {
            console.error('用户信息界面元素未找到');
            return;
        }
        
        // 绑定事件
        userAvatarBtn.addEventListener('click', toggleProfileSidebar);
        closeProfileBtn.addEventListener('click', closeProfileSidebar);
        overlay.addEventListener('click', closeProfileSidebar);
        logoutBtn.addEventListener('click', logout);
        
        if (closeHistoryBtn) {
            closeHistoryBtn.addEventListener('click', closeHistoryDialog);
        }
        
        // 加载用户信息
        loadUserProfile();
        
        // 加载历史对话
        loadUserHistory();
    }
    
    // 切换侧边栏显示状态
    function toggleProfileSidebar() {
        userProfileSidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }
    
    // 关闭侧边栏
    function closeProfileSidebar() {
        userProfileSidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
    
    // 打开历史对话详情
    function openHistoryDialog(dialogId, mode) {
        // 设置对话框标题和信息
        document.getElementById('historyDialogTitle').textContent = 'History';
        document.getElementById('historyDialogId').textContent = dialogId;
        document.getElementById('historyDialogMode').textContent = mode || 'Interview';
        
        // 显示加载中
        document.getElementById('historyChatContent').innerHTML = '<div class="loading-history">加载中...</div>';
        
        // 显示对话框
        historyDialog.classList.add('active');
        
        // 加载对话历史
        loadChatHistory(dialogId);
    }
    
    // 关闭历史对话详情
    function closeHistoryDialog() {
        historyDialog.classList.remove('active');
    }
    
    // 加载用户信息
    async function loadUserProfile() {
        const userId = localStorage.getItem('user_id');
        if (!userId) {
            console.error('未找到用户ID');
            return;
        }
        
        try {
            const response = await fetch('/user-profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                userInfo = data.user_info;
                updateProfileUI(userInfo);
            } else {
                console.error('加载用户信息失败:', data.message);
            }
        } catch (error) {
            console.error('获取用户信息出错:', error);
        }
    }
    
    // 加载用户历史对话
    async function loadUserHistory() {
        if (!historyList) return;
        
        const userId = localStorage.getItem('user_id');
        if (!userId) {
            historyList.innerHTML = '<div class="loading-history">未登录</div>';
            return;
        }
        
        try {
            const response = await fetch('/user-history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                updateHistoryList(data.history);
            } else {
                historyList.innerHTML = `<div class="loading-history">加载失败: ${data.message}</div>`;
            }
        } catch (error) {
            console.error('获取历史对话出错:', error);
            historyList.innerHTML = '<div class="loading-history">加载出错</div>';
        }
    }
    
    // 加载对话历史详情
    async function loadChatHistory(dialogId) {
        const historyChatContent = document.getElementById('historyChatContent');
        
        try {
            const response = await fetch('/chat-history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dialog_id: dialogId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayChatHistory(data.messages);
            } else {
                historyChatContent.innerHTML = `<div class="loading-history">加载失败: ${data.message}</div>`;
            }
        } catch (error) {
            console.error('获取对话历史详情出错:', error);
            historyChatContent.innerHTML = '<div class="loading-history">加载出错</div>';
        }
    }
    
    // 更新用户信息界面
    function updateProfileUI(userInfo) {
        if (!userInfo) return;
        
        document.getElementById('profileUsername').textContent = userInfo.Name || '未设置';
        document.getElementById('profileJob').textContent = userInfo.Job || '未设置';
        document.getElementById('profileMajor').textContent = userInfo.Major || '未设置';
        document.getElementById('profileEmail').textContent = userInfo.Email || '未设置';
    }
    
    // 更新历史对话列表
    function updateHistoryList(historyData) {
        if (!historyList) return;
        
        if (!historyData || historyData.length === 0) {
            historyList.innerHTML = '<div class="loading-history">暂无历史对话</div>';
            return;
        }
        
        let historyHtml = '';
        
        historyData.forEach(item => {
            historyHtml += `
                <div class="history-item" data-id="${item.dialog_id}" data-mode="${item.mode}">
                    <div class="history-item-header">
                        <div class="history-item-id">ID: ${item.dialog_id.substring(0, 8)}...</div>
                    </div>
                    <div class="history-item-mode">Type: ${item.mode}</div>
                    <div class="history-item-hint">Click to check</div>
                </div>
            `;
        });
        
        historyList.innerHTML = historyHtml;
        
        // 添加点击事件
        const historyItems = historyList.querySelectorAll('.history-item');
        historyItems.forEach(item => {
            item.addEventListener('click', () => {
                const dialogId = item.getAttribute('data-id');
                const mode = item.getAttribute('data-mode');
                openHistoryDialog(dialogId, mode);
            });
        });
    }
    
    // 显示对话历史详情
    function displayChatHistory(messages) {
        const historyChatContent = document.getElementById('historyChatContent');
        
        if (!messages || messages.length === 0) {
            historyChatContent.innerHTML = '<div class="loading-history">无对话内容</div>';
            return;
        }
        
        let chatHtml = '';
        
        messages.forEach(message => {
            if (message.role === 'system') {
                // 系统消息不显示
                return;
            }
            
            if (message.role === 'user') {
                chatHtml += `
                    <div class="history-message">
                        <div class="history-message-user">You:</div>
                        <div class="history-message-content">${message.content}</div>
                    </div>
                `;
            } else if (message.role === 'assistant') {
                chatHtml += `
                    <div class="history-message">
                        <div class="history-message-assistant">Interviewer:</div>
                        <div class="history-message-content">${message.content}</div>
                    </div>
                `;
            }
        });
        
        historyChatContent.innerHTML = chatHtml || '<div class="loading-history">无对话内容</div>';
    }
    
    // 退出登录
    function logout() {
        if (confirm('确定要退出登录吗？')) {
            // 清除本地存储
            localStorage.removeItem('user_id');
            localStorage.removeItem('conversation_id');
            
            // 返回登录界面
            document.getElementById('chatContainer').classList.add('hidden');
            document.getElementById('authContainer').classList.remove('hidden');
            
            // 关闭侧边栏
            closeProfileSidebar();
        }
    }
    
    // 公共接口
    return {
        init: init,
        closeProfileSidebar: closeProfileSidebar,
        openHistoryDialog: openHistoryDialog,
        closeHistoryDialog: closeHistoryDialog
    };
})();