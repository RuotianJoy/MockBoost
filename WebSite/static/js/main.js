// DOM Elements
const authContainer = document.getElementById('authContainer');
const chatContainer = document.getElementById('chatContainer');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendMessage');
const chatMessages = document.getElementById('chatMessages');
const startVoiceButton = document.getElementById('startVoice');
const sendVerificationBtn = document.getElementById('sendVerificationBtn');

// Audio Context and Recorder
let mediaRecorder;
let audioChunks = [];
let verificationCode = null; // 存储验证码

// Toggle between login and register forms
function toggleAuth() {
    const authBoxes = document.querySelectorAll('.auth-box');
    authBoxes.forEach(box => box.classList.toggle('hidden'));
}

// Handle login
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();

        if (data.success) {
            authContainer.classList.add('hidden');
            chatContainer.classList.remove('hidden');
        } else {
            alert('登录失败：' + data.message);
        }
    } catch (error) {
        alert('登录出错，请重试');
    }
});

// Send verification code
sendVerificationBtn.addEventListener('click', async () => {
    const email = document.getElementById('registerEmail').value;
    if (!email) {
        alert('请输入邮箱地址');
        return;
    }

    try {
        sendVerificationBtn.disabled = true;
        sendVerificationBtn.textContent = '发送中...';

        const response = await fetch('/send-verification', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await response.json();

        if (data.success) {
            verificationCode = data.code;
            alert('验证码已发送到您的邮箱');
            
            // 倒计时60秒
            let countdown = 60;
            sendVerificationBtn.textContent = `${countdown}秒后重试`;
            
            const timer = setInterval(() => {
                countdown--;
                sendVerificationBtn.textContent = `${countdown}秒后重试`;
                
                if (countdown <= 0) {
                    clearInterval(timer);
                    sendVerificationBtn.disabled = false;
                    sendVerificationBtn.textContent = '发送验证码';
                }
            }, 1000);
        } else {
            alert('发送验证码失败：' + data.message);
            sendVerificationBtn.disabled = false;
            sendVerificationBtn.textContent = '发送验证码';
        }
    } catch (error) {
        alert('发送验证码出错，请重试');
        sendVerificationBtn.disabled = false;
        sendVerificationBtn.textContent = '发送验证码';
    }
});

// Handle registration
registerForm.addEventListener('submit', async (e) => {
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
            alert('注册成功，请登录');
            toggleAuth();
            // 清空注册表单
            registerForm.reset();
            // 将用户名填入登录表单
            document.getElementById('loginUsername').value = username;
        } else {
            alert('注册失败：' + data.message);
        }
    } catch (error) {
        alert('注册出错，请重试');
    }
});

// Add message to chat
function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message
async function sendMessage(message) {
    addMessage(message, true);
    messageInput.value = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        
        // Convert response to speech
        const audioResponse = await fetch('/text-to-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: data.response })
        });
        const audioData = await audioResponse.json();

        // Play audio response
        const audio = new Audio('data:audio/wav;base64,' + audioData.audio_data);
        audio.play();

        addMessage(data.response);
    } catch (error) {
        alert('发送消息失败，请重试');
    }
}

// Handle send button click
sendButton.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

// Handle enter key press
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
        }
    }
});

// Voice recording functionality
startVoiceButton.addEventListener('click', async () => {
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.addEventListener('dataavailable', (event) => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', async () => {
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
                        sendMessage(data.text);
                    }
                } catch (error) {
                    alert('语音识别失败，请重试');
                }

                startVoiceButton.classList.remove('recording');
                stream.getTracks().forEach(track => track.stop());
            });

            mediaRecorder.start();
            startVoiceButton.classList.add('recording');
        } catch (error) {
            alert('无法访问麦克风');
        }
    } else {
        mediaRecorder.stop();
    }
});