import PCMAudioPlayer from './audio_player.js';

(function () {
    /**
     * 生成32位随机字符串
     * @returns {string} 随机字符串
     */
    function generateUUID() {
        let d = new Date().getTime();
        let d2 = (performance && performance.now && (performance.now()*1000)) || 0;
        return 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            let r = Math.random() * 16; //random number between 0 and 16
            if(d > 0){
                r = (d + r)%16 | 0;
                d = Math.floor(d/16);
            } else {
                r = (d2 + r)%16 | 0;
                d2 = Math.floor(d2/16);
            }
            return (c == 'x' ? r :(r&0x3|0x8)).toString(16);
        });
    }

    /**
     * 生成 WebSocket 消息的头部信息
     * @returns {Object} 包含头部信息的对象
     */
    const getHeader = () => {
        const timestamp = Date.now(); // 获取当前时间戳
        return {
            message_id: generateUUID(), // 消息ID，包含随机值以确保唯一性
            task_id: task_id, // 任务ID，包含时间戳和随机值以确保唯一性
            namespace: 'FlowingSpeechSynthesizer', // 命名空间
            name: '', // 消息名称，初始化为空
            appkey: appkey, // 应用密钥
        };
    };
    /**
     * appkey和token需要替换为实际的值
     */
    let appkey = 'Fs8yrx1nEz5CQJEr'
    let token = '689cb460e87e4703be2719bc545c66cc'
    let ws = null; // WebSocket 实例
    let task_id = null;
    let isSynthesisStarted = false; // 状态变量，用于跟踪合成是否已经开始
    let player = new PCMAudioPlayer(24000);
    const textInput = document.getElementById('textInput');

    /**
     * 发送 RunSynthesis 指令
     * @param {string} text - 要合成的文本
     */
    const sendRunSynthesis = (text) => {
        if (ws && isSynthesisStarted) { // 确保 WebSocket 连接已经建立并且合成已经开始
            const header = getHeader(); // 获取新的头部信息
            const params = {
                header: { ...header, name: 'RunSynthesis' }, // 更新消息头部信息中的名称为 'RunSynthesis'
                payload: {
                    text, // 要合成的文本
                },
            };
            ws.send(JSON.stringify(params)); // 发送消息
        } else {
            console.error('Cannot send RunSynthesis: Synthesis has not started');
        }
    };

    /**
     * 发送 StopSynthesis 指令
     */
    const sendStopSynthesis = () => {
        if (ws && isSynthesisStarted) { // 确保 WebSocket 连接已经建立并且合成已经开始
            const header = getHeader(); // 获取新的头部信息
            const params = {
                header: { ...header, name: 'StopSynthesis' }, // 更新消息头部信息中的名称为 'StopSynthesis'
            };
            ws.send(JSON.stringify(params)); // 发送消息
        } else {
            console.error('Cannot send StopSynthesis: Synthesis has not started');
        }
    };

    /**
     * 开始连接 WebSocket 并处理语音合成数据
     */
    const connectAndStartSynthesis = () => {
        ws = new WebSocket('wss://nls-gateway-cn-beijing.aliyuncs.com/ws/v1?token=689cb460e87e4703be2719bc545c66cc' ); // 初始化 WebSocket 连接
        ws.binaryType = "arraybuffer";
        // 当 WebSocket 连接打开后发送 StartSynthesis 指令
        ws.onopen = () => {
            if (ws.readyState === WebSocket.OPEN) {
                task_id = generateUUID();
                const header = getHeader(); // 获取新的头部信息
                const params = {
                    header: { ...header, name: 'StartSynthesis' }, // 更新消息头部信息中的名称为 'StartSynthesis'
                    payload: {
                        voice: 'zhixiaoxia', // 选择音色
                        format: 'PCM', // 文件格式
                        sample_rate: 24000, // 采样率
                        volume: 100, // 音量
                        speech_rate: 0, // 语速
                        pitch_rate: 0, // 音调
                        enable_subtitle: true, // 是否启用字幕
                        platform: 'javascript'
                    },
                };
                ws.send(JSON.stringify(params)); // 发送开始合成消息
            }
        };
        // 当 WebSocket 连接发生错误时触发
        ws.onerror = (err) => {
            console.error(err);
        };
        // 当 WebSocket 连接关闭时触发
        ws.onclose = (err) => {
            console.info(err);
        };
        // 当 WebSocket 收到消息时触发
        ws.onmessage = (event) => {
            const data = event.data;
            // 如果收到的是二进制数据（Blob 类型）
            if (data instanceof ArrayBuffer) {
                player.pushPCM(data)
            } else { // 如果收到的是文本消息
                const body = JSON.parse(data); // 解析 JSON 数据
                console.log('* text msg', body);
                // 如果消息名称为 'SynthesisStarted' 指令 且状态为成功
                if (body.header.name === 'SynthesisStarted' && body.header.status === 20000000) {
                    isSynthesisStarted = true; // 更新合成状态为已经开始
                }
                // 如果消息名称为 'SynthesisCompleted' 指令 且状态为成功
                if (body.header.name === 'SynthesisCompleted' && body.header.status === 20000000) {
                    ws.close(); // 关闭 WebSocket 连接
                    ws = null; // 重置 WebSocket 实例
                    isSynthesisStarted = false; // 更新合成状态为未开始
                }
            }
        };
    };

    // 设置 start 按钮的点击事件
    document.querySelector('#button-start').addEventListener('click', () => {
        player.connect()
        player.stop()
        connectAndStartSynthesis(); // 开始 WebSocket 连接和语音合成
    });
    // 设置 run 按钮的点击事件，发送合成文本消息
    document.querySelector('#button-run').addEventListener('click', () => {
        const text = textInput.value.trim();
        console.log('sending text', text)
        sendRunSynthesis(text);
    });
    // 设置 stop 按钮的点击事件，发送停止合成消息
    document.querySelector('#button-stop').addEventListener('click', () => {
        sendStopSynthesis();
    });
})();
