on run argv
    set targetURL to "https://chat.qwen.ai/"
    
    tell application "Google Chrome"
        activate
        set foundTab to false
        
        -- Loop through all windows and tabs to find the target tab
        repeat with w in windows
            set tabIndex to 1
            repeat with t in tabs of w
                if URL of t contains targetURL then
                    set active tab index of w to tabIndex
                    set index of w to 1
                    set foundTab to true
                    exit repeat
                end if
                set tabIndex to tabIndex + 1
            end repeat
            if foundTab then exit repeat
        end repeat
        
        if not foundTab then
            error "Could not find a tab with " & targetURL
        end if
        
        tell active tab of front window
            execute javascript "
                const conversation = {
                    conversation: [],
                    pageTitle: document.title,
                    url: window.location.href,
                    capturedAt: new Date().toISOString()
                };

                const qwenThinkingPanel = document.querySelector('.ThinkingPanel__Body__Content');
                const qwenResponseContainer = document.querySelector('#response-content-container');

                if (window.location.href.includes('qwen.ai') && (qwenThinkingPanel || qwenResponseContainer)) {
                    conversation.platform = 'qwen.ai';
                    conversation.conversation = [];

                    const userMessages = document.querySelectorAll('.chat-item-user');
                    if (userMessages && userMessages.length > 0) {
                        for (const msg of userMessages) {
                            conversation.conversation.push({
                                role: 'user',
                                content: msg.innerText || msg.textContent || 'No content found'
                            });
                        }
                    }

                    const thinkingPanels = document.querySelectorAll('.ThinkingPanel__Body__Content');
                    const responseContainers = document.querySelectorAll('#response-content-container, .markdown-content-container');

                    const maxLength = Math.max(
                        thinkingPanels ? thinkingPanels.length : 0,
                        responseContainers ? responseContainers.length : 0
                    );

                    for (let i = 0; i < maxLength; i++) {
                        const thinking = thinkingPanels && i < thinkingPanels.length 
                            ? thinkingPanels[i].innerText || thinkingPanels[i].textContent 
                            : '';
                        const response = responseContainers && i < responseContainers.length 
                            ? responseContainers[i].innerText || responseContainers[i].textContent 
                            : '';
                        conversation.conversation.push({
                            role: 'assistant',
                            thinking: thinking,
                            response: response
                        });
                    }

                    if (conversation.conversation.length === 0) {
                        if (qwenThinkingPanel) {
                            conversation.thinking = qwenThinkingPanel.innerText || qwenThinkingPanel.textContent;
                        }
                        if (qwenResponseContainer) {
                            conversation.response = qwenResponseContainer.innerText || qwenResponseContainer.textContent;
                        }
                    }
                } else {
                    const messageElements = document.querySelectorAll('.message, .chat-message, .message-container, .chat-item');
                    if (messageElements && messageElements.length > 0) {
                        for (let i = 0; i < messageElements.length; i++) {
                            const el = messageElements[i];
                            const isUser = (el.classList.contains('user') || 
                                           el.classList.contains('user-message') ||
                                           !!el.querySelector('.user'));
                            conversation.conversation.push({
                                role: isUser ? 'user' : 'assistant',
                                content: el.innerText || el.textContent || 'No content found'
                            });
                        }
                    } else {
                        conversation.fullPageContent = document.body.innerText || document.body.textContent;
                    }
                }

                return JSON.stringify(conversation);
            "
        end tell
    end tell
end run