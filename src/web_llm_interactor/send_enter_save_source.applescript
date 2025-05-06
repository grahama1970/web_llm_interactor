on run argv
    if (count of argv) < 3 then
        error "Usage: osascript send_enter_save_source.applescript \"Your message here\" \"targetURL\" \"outputHtmlFilePOSIX\" [--all] [--fields \"field1,field2\"]" number -1700
    end if
    set messageText to item 1 of argv
    set targetURL to item 2 of argv
    set outputHtmlFilePOSIX to item 3 of argv
    set responseWait to 30 -- Default wait time in seconds

    -- Process optional parameters
    set allFlag to ""
    set fieldsFlag to ""
    
    -- Start checking from the 4th argument
    set i to 4
    
    -- Parse all command line arguments
    repeat while i ≤ (count of argv)
        if item i of argv is "--all" then
            set allFlag to " --all"
        else if item i of argv is "--fields" and i + 1 ≤ (count of argv) then
            set fieldsFlag to " --fields " & quoted form of (item (i + 1) of argv)
            set i to i + 1 -- Skip the next item as we already used it
        end if
        set i to i + 1
    end repeat
    
    -- Get environment variable for response wait time
    set responseWaitEnv to do shell script "echo $RESPONSE_WAIT_TIME"
    if responseWaitEnv is not "" then
        try
            set responseWait to responseWaitEnv as integer
        on error
            -- If conversion fails, use default
            set responseWait to 30
        end try
    end if

    -- Get environment variable for selector
    set selectorEnv to do shell script "echo $CHAT_INPUT_SELECTOR"
    set chatInputSelector to "textarea#chat-input.text-area-box-web"
    if selectorEnv is not "" then
        set chatInputSelector to selectorEnv
    end if

    set pageSourceHTML to ""
    set foundWindow to missing value
    set foundTabIndex to -1

    tell application "Google Chrome"
        activate
        set windowList to every window
        repeat with w in windowList
            set tabList to every tab of w
            repeat with i from 1 to count of tabList
                set t to item i of tabList
                if URL of t contains targetURL then
                    set foundWindow to w
                    set foundTabIndex to i
                    exit repeat
                end if
            end repeat
            if foundWindow is not missing value then exit repeat
        end repeat

        if foundWindow is missing value then
            error "Could not find an open tab with URL containing: " & targetURL
        end if

        -- Switch to the window and tab
        set index of foundWindow to 1
        set active tab index of foundWindow to foundTabIndex
        delay 2 -- Ensure tab is fully loaded

        -- Inject JavaScript to input message and submit (only once)
        tell tab foundTabIndex of foundWindow
            execute javascript "
                (function() {
                    // Prevent re-injection
                    if (window.__messageSent) {
                        console.log('Message already sent, skipping re-injection');
                        return;
                    }

                    const message = `" & messageText & "`;
                    // Look specifically for chat input with the provided selector
                    let input = document.querySelector('" & chatInputSelector & "');
                    if (!input) {
                        // Fallback to other selectors
                        input = document.querySelector('textarea#chat-input, textarea.text-area-box-web, textarea, div[contenteditable=\"true\"]');
                        if (!input) throw new Error('Chat input not found with selector: " & chatInputSelector & "');
                    }

                    input.scrollIntoView({ behavior: 'auto', block: 'center' });
                    input.focus();

                    if (input.tagName === 'TEXTAREA') {
                        input.value = message;
                    } else if (input.tagName === 'DIV') {
                        input.innerText = message;
                    } else {
                        throw new Error('Unsupported input type: ' + input.tagName);
                    }

                    input.dispatchEvent(new InputEvent('input', { bubbles: true }));

                    // Try to submit via form if available
                    const form = input.closest('form');
                    if (form) {
                        if (typeof form.requestSubmit === 'function') {
                            form.requestSubmit();
                            window.__messageSent = true;
                            return;
                        } else if (typeof form.submit === 'function') {
                            form.submit();
                            window.__messageSent = true;
                            return;
                        }
                    }

                    // Try to find and click a send button
                    const sendBtn = Array.from(document.querySelectorAll('button'))
                        .find(btn => btn.innerText && btn.innerText.toLowerCase().includes('send'));
                    if (sendBtn) {
                        sendBtn.click();
                        window.__messageSent = true;
                        return;
                    }

                    // Last resort: Simulate Enter keypress - using both keydown and keypress events
                    const enterKeydown = new KeyboardEvent('keydown', {
                        key: 'Enter', 
                        code: 'Enter', 
                        keyCode: 13, 
                        which: 13, 
                        bubbles: true
                    });
                    
                    const enterKeypress = new KeyboardEvent('keypress', {
                        key: 'Enter', 
                        code: 'Enter', 
                        keyCode: 13, 
                        which: 13, 
                        bubbles: true
                    });
                    
                    // Fire both events to ensure better compatibility
                    input.dispatchEvent(enterKeydown);
                    input.dispatchEvent(enterKeypress);
                    
                    // Also try to submit directly if it's in a form
                    if (form) {
                        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                        form.dispatchEvent(submitEvent);
                    }
                    
                    window.__messageSent = true;
                })();
            "
        end tell
        
        -- Poll for response using simple HTML length measurement
        log "Starting simple HTML length polling for response completion..."
        
        set startTime to current date
        set endTime to startTime + responseWait
        set stableCount to 0
        set requiredStablePolls to 3 -- Default value
        set pollInterval to 2 -- Default value
        
        -- Get environment variables for poll settings if available
        set pollIntervalEnv to do shell script "echo $POLL_INTERVAL"
        if pollIntervalEnv is not "" then
            try
                set pollInterval to pollIntervalEnv as integer
            on error
                -- If conversion fails, use default
                set pollInterval to 2
            end try
        end if
        
        -- Get required stable polls from environment if available
        set stablePollsEnv to do shell script "echo $REQUIRED_STABLE_POLLS"
        if stablePollsEnv is not "" then
            try
                set requiredStablePolls to stablePollsEnv as integer
            on error
                -- If conversion fails, use default
                set requiredStablePolls to 3
            end try
        end if
        
        log "Using poll settings: interval=" & pollInterval & "s, required stable polls=" & requiredStablePolls
        
        set previousLength to 0
        
        -- Get initial HTML length
        tell tab foundTabIndex of foundWindow
            set initialHTML to execute javascript "document.documentElement.outerHTML;"
        end tell
        set initialLength to length of initialHTML
        
        log "Initial HTML length: " & initialLength
        
        -- Begin polling loop
        repeat
            -- Check if we've exceeded maximum wait time
            if (current date) > endTime then
                log "Reached maximum wait time, checking final content..."
                exit repeat
            end if
            
            -- Wait between polls
            delay pollInterval
            
            -- Get current HTML content
            tell tab foundTabIndex of foundWindow
                set currentHTML to execute javascript "document.documentElement.outerHTML;"
            end tell
            
            set currentLength to length of currentHTML
            
            log "Current HTML length: " & currentLength & ", Previous: " & previousLength & ", Initial: " & initialLength
            
            -- Check if content has stabilized
            if currentLength > initialLength + 500 then
                -- Content has grown significantly from initial
                if currentLength = previousLength and previousLength > 0 then
                    -- Length hasn't changed since last check
                    set stableCount to stableCount + 1
                    log "Content stable for " & stableCount & " polls"
                    
                    if stableCount ≥ requiredStablePolls then
                        log "Content has stabilized after " & stableCount & " stable polls"
                        set pageSourceHTML to currentHTML
                        exit repeat
                    end if
                else
                    -- Content is still changing or first significant change
                    set stableCount to 0
                end if
                -- Always update previous length when content has grown significantly
                set previousLength to currentLength
            end if
        end repeat
        
        -- If we exited due to timeout, get final content
        if not (pageSourceHTML is not "" and pageSourceHTML is not missing value) then
            tell tab foundTabIndex of foundWindow
                set pageSourceHTML to execute javascript "document.documentElement.outerHTML;"
            end tell
            log "Using final HTML after timeout, length: " & (length of pageSourceHTML)
        end if
        log "HTML captured, length: " & (length of pageSourceHTML)
    end tell

    -- Save HTML via shell (handles utf-8)
    if pageSourceHTML is not "" and pageSourceHTML is not missing value then
        set tmpFile to "/tmp/qwen_temp.html"
        do shell script "echo " & quoted form of pageSourceHTML & " > " & quoted form of tmpFile
        do shell script "iconv -f UTF-8 -t UTF-8 " & quoted form of tmpFile & " > " & quoted form of outputHtmlFilePOSIX
        do shell script "rm " & quoted form of tmpFile
        
        -- Run Python script and capture its stdout, including all flags
        set pythonResult to do shell script "python3 -m web_llm_interactor.extract_json_from_html " & quoted form of outputHtmlFilePOSIX & allFlag & fieldsFlag
        
        -- Store the result first before switching apps
        set finalResult to pythonResult
        
        -- Add a more substantial delay to ensure Python result is fully processed
        delay 3
        
        -- Return focus to VSCode after results are ready using a more robust approach
        do shell script "osascript -e 'tell application \"Visual Studio Code\" to activate'"
        
        -- Wait a bit more to ensure VSCode has focus
        delay 1
        
        -- Return the result after everything is ready
        return finalResult
    else
        error "Page HTML was empty or could not be retrieved."
    end if
end run