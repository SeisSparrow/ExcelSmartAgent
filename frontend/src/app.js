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
                // Display the processed file info
                this.addFileToList(result.result);
                this.showStatus('文件上传并处理成功！', 'success');
                
                // Notify WebSocket about new file (using correct path)
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'upload_file',
                        file_info: {
                            name: file.name,
                            path: result.file_name  // Use correct file_name from response
                        }
                    }));
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
            // Start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                this.mediaRecorder = new MediaRecorder(stream);
                this.audioChunks = [];

                this.mediaRecorder.ondataavailable = (event) => {
                    this.audioChunks.push(event.data);
                };

                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.sendAudioData(audioBlob);
                };

                this.mediaRecorder.start();
                this.isRecording = true;
                voiceBtn.classList.add('recording');
                voiceBtn.innerHTML = '⏹️ 停止录音';
                this.showStatus('正在录音...', 'info');

            } catch (error) {
                console.error('Error accessing microphone:', error);
                this.showStatus('无法访问麦克风，请检查权限', 'error');
            }

        } else {
            // Stop recording
            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
                this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            this.isRecording = false;
            voiceBtn.classList.remove('recording');
            voiceBtn.innerHTML = '🎤 语音输入';
            this.showStatus('录音已停止，正在识别...', 'info');
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

