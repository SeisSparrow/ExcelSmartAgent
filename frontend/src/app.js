// Main Application JavaScript

class ExcelSmartAgent {
    constructor() {
        this.ws = null;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
    }

    setupEventListeners() {
        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');

        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFile(files[0]);
            }
        });

        // Query submission
        document.getElementById('submitBtn').addEventListener('click', () => {
            this.submitQuery();
        });

        // Voice input
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.toggleVoiceRecording();
        });

        // Enter key in textarea
        document.getElementById('queryInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.submitQuery();
            }
        });
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.showStatus('正在连接服务器...', 'info');

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.showStatus('已连接到服务器', 'success');
            setTimeout(() => this.hideStatus(), 2000);
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showStatus('连接错误，请刷新页面重试', 'error');
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.showStatus('连接已断开，正在重新连接...', 'warning');
            setTimeout(() => this.connectWebSocket(), 3000);
        };
    }

    handleWebSocketMessage(message) {
        console.log('Received message:', message);

        switch (message.type) {
            case 'connection':
                console.log('Connected:', message.message);
                break;

            case 'status':
                this.showStatus(message.message, 'info');
                break;

            case 'transcription':
                document.getElementById('queryInput').value = message.text;
                this.showStatus(`语音识别: ${message.text}`, 'success');
                break;

            case 'analysis_plan':
                console.log('Analysis plan:', message.plan);
                this.showStatus('分析计划已生成', 'info');
                break;

            case 'code_generated':
                this.displayCode(message.code, message.explanation);
                this.showStatus('代码已生成，正在执行...', 'info');
                break;

            case 'result':
                if (message.success) {
                    this.displayResults(message);
                    this.showStatus('分析完成！', 'success');
                } else {
                    this.showStatus(`执行失败: ${message.error}`, 'error');
                }
                break;

            case 'file_processed':
                this.addFileToList(message.result);
                this.showStatus('文件处理完成', 'success');
                break;

            case 'error':
                this.showStatus(message.message, 'error');
                break;

            default:
                console.log('Unknown message type:', message.type);
        }
    }

    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            await this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        this.showStatus('正在上传文件...', 'info');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                // File uploaded successfully, let WebSocket handle the processing notification
                this.showStatus('文件已上传，正在处理...', 'info');
                
                // Notify WebSocket about new file (using correct path)
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'upload_file',
                        file_info: {
                            name: file.name,
                            path: result.file_name  // Use correct file_name from response
                        }
                    }));
                } else {
                    // If WebSocket not connected, add file directly
                    this.addFileToList(result.result);
                    this.showStatus('文件上传并处理成功！', 'success');
                }
            } else {
                this.showStatus('文件上传失败', 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showStatus('上传出错，请重试', 'error');
        }
    }

    submitQuery() {
        const query = document.getElementById('queryInput').value.trim();
        
        if (!query) {
            this.showStatus('请输入查询问题', 'warning');
            return;
        }

        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.showStatus('未连接到服务器，请稍候重试', 'error');
            return;
        }

        // Send query via WebSocket
        this.ws.send(JSON.stringify({
            type: 'query',
            query: query
        }));

        this.showStatus('正在分析您的问题...', 'info');
        document.getElementById('resultsSection').style.display = 'none';
    }

    async toggleVoiceRecording() {
        const voiceBtn = document.getElementById('voiceBtn');

        if (!this.isRecording) {
            // Start recording with Web Audio API for better format control
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        channelCount: 1,
                        sampleRate: 16000,
                        echoCancellation: true,
                        noiseSuppression: true
                    } 
                });
                
                // Use Web Audio API to get raw audio data
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                this.mediaStreamSource = this.audioContext.createMediaStreamSource(stream);
                this.audioWorkletSupported = false;
                
                // Use ScriptProcessor as fallback (deprecated but widely supported)
                this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);
                this.audioChunks = [];
                
                this.scriptProcessor.onaudioprocess = (e) => {
                    const inputData = e.inputBuffer.getChannelData(0);
                    // Convert Float32Array to Int16Array for WAV
                    const int16Data = new Int16Array(inputData.length);
                    for (let i = 0; i < inputData.length; i++) {
                        const s = Math.max(-1, Math.min(1, inputData[i]));
                        int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                    }
                    this.audioChunks.push(int16Data);
                };
                
                this.mediaStreamSource.connect(this.scriptProcessor);
                this.scriptProcessor.connect(this.audioContext.destination);
                this.mediaStream = stream;
                
                this.isRecording = true;
                voiceBtn.classList.add('recording');
                voiceBtn.innerHTML = '⏹️ 停止录音';
                this.showStatus('正在录音...', 'info');

            } catch (error) {
                console.error('Error accessing microphone:', error);
                this.showStatus('无法访问麦克风，请检查权限', 'error');
            }

        } else {
            // Stop recording and convert to WAV
            if (this.scriptProcessor) {
                this.scriptProcessor.disconnect();
                this.mediaStreamSource.disconnect();
            }
            if (this.mediaStream) {
                this.mediaStream.getTracks().forEach(track => track.stop());
            }
            if (this.audioContext) {
                this.audioContext.close();
            }
            
            this.isRecording = false;
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '🎤 语音输入';
            this.showStatus('录音已停止，正在识别...', 'info');
            
            // Convert collected audio chunks to WAV
            this.convertToWavAndSend();
        }
    }
    
    convertToWavAndSend() {
        if (this.audioChunks.length === 0) {
            this.showStatus('未录制到音频', 'warning');
            return;
        }
        
        // Calculate total length
        let totalLength = 0;
        for (let chunk of this.audioChunks) {
            totalLength += chunk.length;
        }
        
        // Merge all chunks
        const mergedData = new Int16Array(totalLength);
        let offset = 0;
        for (let chunk of this.audioChunks) {
            mergedData.set(chunk, offset);
            offset += chunk.length;
        }
        
        // Create WAV file
        const wavBlob = this.createWavBlob(mergedData, 16000);
        this.sendAudioData(wavBlob);
    }
    
    createWavBlob(audioData, sampleRate) {
        const numChannels = 1;
        const bitsPerSample = 16;
        const bytesPerSample = bitsPerSample / 8;
        const blockAlign = numChannels * bytesPerSample;
        
        const buffer = new ArrayBuffer(44 + audioData.length * bytesPerSample);
        const view = new DataView(buffer);
        
        // WAV header
        // "RIFF" chunk descriptor
        this.writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + audioData.length * bytesPerSample, true);
        this.writeString(view, 8, 'WAVE');
        
        // "fmt " sub-chunk
        this.writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
        view.setUint16(20, 1, true); // AudioFormat (1 for PCM)
        view.setUint16(22, numChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * blockAlign, true); // ByteRate
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, bitsPerSample, true);
        
        // "data" sub-chunk
        this.writeString(view, 36, 'data');
        view.setUint32(40, audioData.length * bytesPerSample, true);
        
        // Write audio data
        let offset = 44;
        for (let i = 0; i < audioData.length; i++) {
            view.setInt16(offset, audioData[i], true);
            offset += 2;
        }
        
        return new Blob([buffer], { type: 'audio/wav' });
    }
    
    writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    }

    async sendAudioData(audioBlob) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const arrayBuffer = await audioBlob.arrayBuffer();
            this.ws.send(arrayBuffer);
        } else {
            this.showStatus('未连接到服务器', 'error');
        }
    }

    displayCode(code, explanation) {
        document.getElementById('generatedCode').querySelector('code').textContent = code;
        document.getElementById('codeExplanation').textContent = explanation || '';
        document.getElementById('resultsSection').style.display = 'block';
    }

    displayResults(result) {
        // Display columns used
        const columnsDiv = document.getElementById('columnsUsed');
        columnsDiv.innerHTML = result.columns_used
            .map(col => `<span class="column-tag">${col}</span>`)
            .join('');

        // Display summary
        document.getElementById('analysisSummary').textContent = result.summary || '分析完成';

        // Display data result
        const dataResultDiv = document.getElementById('dataResult');
        if (result.result && result.result.display) {
            dataResultDiv.innerHTML = result.result.display;
        } else {
            dataResultDiv.textContent = '无数据结果';
        }

        // Display visualizations
        if (result.visualizations && result.visualizations.length > 0) {
            const vizSection = document.getElementById('visualizationsSection');
            const vizDiv = document.getElementById('visualizations');
            
            vizDiv.innerHTML = result.visualizations.map(viz => `
                <div class="visualization-item">
                    <img src="data:image/png;base64,${viz.data}" alt="Visualization">
                </div>
            `).join('');
            
            vizSection.style.display = 'block';
        } else {
            document.getElementById('visualizationsSection').style.display = 'none';
        }

        document.getElementById('resultsSection').style.display = 'block';
    }

    addFileToList(fileResult) {
        const fileList = document.getElementById('fileList');
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const sheetCount = Object.keys(fileResult.sheets || {}).length;
        
        fileItem.innerHTML = `
            <div class="file-item-info">
                <span class="file-item-name">📄 ${fileResult.file_name}</span>
                <span class="file-item-status">✓ ${sheetCount} 个工作表已处理</span>
            </div>
        `;
        
        fileList.appendChild(fileItem);
    }

    showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('statusMessage');
        statusDiv.textContent = message;
        statusDiv.className = `status-message ${type} show`;
    }

    hideStatus() {
        const statusDiv = document.getElementById('statusMessage');
        statusDiv.classList.remove('show');
    }
}

// Utility function for copying code
function copyCode() {
    const code = document.getElementById('generatedCode').querySelector('code').textContent;
    navigator.clipboard.writeText(code).then(() => {
        alert('代码已复制到剪贴板！');
    });
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ExcelSmartAgent();
});

