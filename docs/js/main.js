// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 平滑滚动效果
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if(targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // 联系表单验证
    const contactForm = document.getElementById('contactForm');
    if(contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 简单验证
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const subject = document.getElementById('subject').value.trim();
            const message = document.getElementById('message').value.trim();
            
            if(!name || !email || !subject || !message) {
                alert('请填写所有必填字段');
                return;
            }
            
            // 验证邮箱格式
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if(!emailRegex.test(email)) {
                alert('请输入有效的电子邮箱地址');
                return;
            }
            
            // 模拟表单提交
            alert('感谢您的留言！我们会尽快回复您。');
            contactForm.reset();
        });
    }
    
    // 添加下载按钮点击事件
    const downloadButtons = document.querySelectorAll('.download-btn');
    downloadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            alert('下载功能即将上线，敬请期待！');
        });
    });
    
    // 添加特性卡片动画效果
    const featureCards = document.querySelectorAll('.feature-card');
    if(featureCards.length > 0) {
        window.addEventListener('scroll', function() {
            featureCards.forEach(card => {
                const cardPosition = card.getBoundingClientRect().top;
                const screenPosition = window.innerHeight / 1.3;
                
                if(cardPosition < screenPosition) {
                    card.classList.add('animate');
                }
            });
        });
    }
});