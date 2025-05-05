on run argv
    -- Configuration
    set responseWaitDelay to 15 -- STILL NEED A DELAY - adjust as needed!
    set targetURL to "https://chat.qwen.ai/"
    set outputHtmlFile to "/tmp/qwen_response.html" -- Or choose a better path

    -- Argument Handling
    if (count of argv) is 0 then
        error "Usage: osascript save_page_source.applescript \"Your message here\"" number -1700
    end if
    set messageText to item 1 of argv

    log "Starting script..."
    log "Target URL: " & targetURL
    log "Message to send: '" & messageText & "'"
    log "Response wait delay: " & responseWaitDelay & " seconds"
    log "Output HTML file: " & outputHtmlFile

    tell application "Google Chrome"
        activate
        set foundTab to missing value

        -- Find Tab (Same as before)
        log "Searching for tab..."
        try
            repeat with w in windows
                set tabIndex to 1
                repeat with t in tabs of w
                    try
                        if URL of t contains targetURL then
                            set active tab index of w to tabIndex
                            set index of w to 1
                            set foundTab to t
                            log "Found target tab."
                            exit repeat
                        end if
                    end try
                    set tabIndex to tabIndex + 1
                end repeat
                if foundTab is not missing value then exit repeat
            end repeat
        on error errMsgWin number errNumWin
            error "Error finding Chrome tab: " & errMsgWin
        end try
        if foundTab is missing value then error "Could not find tab with URL: " & targetURL

        -- Ensure tab is active (optional, but good practice)
        try
            tell front window to set active tab to foundTab
            delay 0.5
        end try

        -- Send Message (Same JavaScript as before)
        log "Sending message..."
        tell active tab of front window
            try
                execute javascript "
                    // --- PASTE SENDING JAVASCRIPT HERE ---
                    // (Find input, set value, dispatch events, click/Enter)
                    const message = `" & messageText & "`;
                    const inputField = document.querySelector('textarea#chat-input') || /* other selectors */;
                    if (!inputField) { throw new Error('Input field not found'); }
                    inputField.focus();
                    inputField.value = message; // Or .textContent for DIVs
                    inputField.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
                    inputField.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
                    setTimeout(function() {
                        const sendButton = document.querySelector('button[type=\"submit\"]:not(:disabled)') || /* other selectors */;
                        if (sendButton) { sendButton.click(); }
                        else { inputField.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', which: 13, keyCode: 13, bubbles: true, cancelable: true })); }
                    }, 300);
                    'Send initiated';
                "
                log "Message sending JS executed."
            on error errMsg number errNum
                error "AppleScript Error sending message: " & errMsg
            end try
        end tell

        -- Wait for Response (STILL CRITICAL)
        log "Waiting " & responseWaitDelay & " seconds..."
        delay responseWaitDelay

        -- Get Page Source
        log "Getting page source HTML..."
        set pageSourceHTML to ""
        try
            tell active tab of front window
                set pageSourceHTML to execute javascript "document.documentElement.outerHTML;"
            end tell
        on error errMsg number errNum
            error "Failed to get page source: " & errMsg
        end try

        if pageSourceHTML is "" or pageSourceHTML is missing value then
            error "Failed to retrieve page source HTML. It was empty."
        end if

        -- Save HTML to File
        log "Saving HTML to: " & outputHtmlFile
        try
            set fileRef to open for access file outputHtmlFile with write permission
            set eof of fileRef to 0 -- Clear the file
            write pageSourceHTML to fileRef starting at eof as Çclass utf8È -- Ensure UTF-8
            close access fileRef
            log "HTML saved successfully."
        on error errMsg number errNum
            try
                close access file outputHtmlFile
            end try
            error "Failed to write HTML to file: " & errMsg
        end try

    end tell -- End Chrome interaction

    log "AppleScript finished."
    return "HTML saved to " & outputHtmlFile -- Return success message

end run