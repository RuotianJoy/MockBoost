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
    
    // 轮播图功能
    const carousel = document.querySelector('.carousel');
    if(carousel) {
        const slides = carousel.querySelectorAll('.carousel-slide');
        const prevBtn = carousel.querySelector('.prev');
        const nextBtn = carousel.querySelector('.next');
        const indicatorsContainer = carousel.querySelector('.carousel-indicators');
        
        let currentIndex = 0;
        let interval;
        
        // 创建指示器
        slides.forEach((_, index) => {
            const indicator = document.createElement('div');
            indicator.classList.add('carousel-indicator');
            if(index === 0) indicator.classList.add('active');
            
            indicator.addEventListener('click', () => {
                goToSlide(index);
                resetInterval();
            });
            
            indicatorsContainer.appendChild(indicator);
        });
        
        // 显示指定索引的幻灯片
        function goToSlide(index) {
            // 移除当前活动幻灯片的active类
            slides[currentIndex].classList.remove('active');
            const indicators = indicatorsContainer.querySelectorAll('.carousel-indicator');
            indicators[currentIndex].classList.remove('active');
            
            // 更新当前索引
            currentIndex = index;
            
            // 如果索引超出范围，则循环
            if(currentIndex < 0) currentIndex = slides.length - 1;
            if(currentIndex >= slides.length) currentIndex = 0;
            
            // 添加新的活动幻灯片的active类
            slides[currentIndex].classList.add('active');
            indicators[currentIndex].classList.add('active');
        }
        
        // 下一张幻灯片
        function nextSlide() {
            goToSlide(currentIndex + 1);
        }
        
        // 上一张幻灯片
        function prevSlide() {
            goToSlide(currentIndex - 1);
        }
        
        // 重置自动播放间隔
        function resetInterval() {
            clearInterval(interval);
            startAutoSlide();
        }
        
        // 开始自动播放
        function startAutoSlide() {
            interval = setInterval(nextSlide, 5000); // 每5秒切换一次
        }
        
        // 添加按钮事件监听器
        if(prevBtn) {
            prevBtn.addEventListener('click', () => {
                prevSlide();
                resetInterval();
            });
        }
        
        if(nextBtn) {
            nextBtn.addEventListener('click', () => {
                nextSlide();
                resetInterval();
            });
        }
        
        // 开始自动播放
        startAutoSlide();
    }
    
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
    // const downloadButtons = document.querySelectorAll('.download-btn');
    // downloadButtons.forEach(button => {
    //     button.addEventListener('click', function(e) {
    //         e.preventDefault();
    //         alert('下载功能即将上线，敬请期待！');
    //     });
    // });
    
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