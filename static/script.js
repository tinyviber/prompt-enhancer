document.addEventListener('DOMContentLoaded', () => {
    // 获取所有需要的 DOM 元素
    const enhanceButton = document.getElementById('enhance-button');
    const promptTextarea = document.getElementById('prompt-textarea');
    const statusContainer = document.getElementById('status-container');
    const resultContainer = document.getElementById('result-container');

    const addDocButton = document.getElementById('add-doc-button');
    const docTextarea = document.getElementById('doc-textarea');
    const sidebarStatus = document.getElementById('sidebar-status');

    // 为 "Enhance Prompt" 按钮添加点击事件监听
    enhanceButton.addEventListener('click', async () => {
        const rawPrompt = promptTextarea.value;
        if (!rawPrompt.trim()) {
            statusContainer.textContent = '⚠️ Please enter a prompt first.';
            return;
        }

        // 清空旧内容并显示加载状态
        statusContainer.textContent = '🚀 Starting enhancement process...';
        resultContainer.textContent = '';
        enhanceButton.disabled = true;

        try {
            // 调用后端的 /process_task API
            const response = await fetch('/process_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task_description: rawPrompt,
                    history: []
                })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            
            // 构建并显示结果
            let logMessage = '✅ Process finished successfully.\n\n';
            let resultText = '';

            if (data.rag_context) {
                logMessage += 'Retrieved RAG Context:\n' + data.rag_context.substring(0, 200) + '...\n\n';
                // 在这个简单版本中，我们直接将RAG上下文和摘要组合
                resultText += `--- RAG CONTEXT ---\n${data.rag_context}\n\n`;
            } else {
                logMessage += 'ℹ️ No relevant RAG context was found.\n\n';
            }

            if (data.summary) {
                logMessage += 'Generated Summary:\n' + data.summary;
                resultText += `--- SUMMARY ---\n${data.summary}`;
            }

            statusContainer.textContent = logMessage;
            resultContainer.textContent = resultText || 'No direct output to display, see log for details.';

        } catch (error) {
            statusContainer.textContent = `❌ An error occurred: ${error.message}`;
            console.error(error);
        } finally {
            enhanceButton.disabled = false;
        }
    });

    // 为 "Add Document" 按钮添加点击事件监听
    addDocButton.addEventListener('click', async () => {
        const docText = docTextarea.value;
        if (!docText.trim()) {
            sidebarStatus.textContent = '⚠️ Please enter document text.';
            sidebarStatus.className = 'error';
            return;
        }

        sidebarStatus.textContent = 'Adding...';
        sidebarStatus.className = '';
        addDocButton.disabled = true;

        try {
            const response = await fetch('/add_document', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ document: docText, source: 'frontend_input' })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            sidebarStatus.textContent = '✅ Document added!';
            sidebarStatus.className = 'success';
            docTextarea.value = ''; // 清空输入框

        } catch (error) {
            sidebarStatus.textContent = `❌ Error: ${error.message}`;
            sidebarStatus.className = 'error';
        } finally {
            addDocButton.disabled = false;
        }
    });
});