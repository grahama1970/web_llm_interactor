on run argv
    if (count of argv) < 3 then
        error "Usage: osascript send_enter_save_source.applescript \"Your message here\" \"targetURL\" \"outputHtmlFilePOSIX\" [--all]" number -1700
    end if
    set messageText to item 1 of argv
    set targetURL to item 2 of argv
    set outputHtmlFilePOSIX to item 3 of argv

    -- Check for optional --all parameter
    set allFlag to ""
    if (count of argv) > 3 then
        if item 4 of argv is "--all" then
            set allFlag to " --all"
        end if
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
        delay 1

        -- Inject JavaScript to input message and submit
        tell tab foundTabIndex of foundWindow
            execute javascript "
                (function() {
                    const message = `" & messageText & "`;
                    const input = document.querySelector('textarea, div[contenteditable=\"true\"]');
                    if (!input) throw new Error('Chat input not found');
                    input.focus();
                    if (input.tagName === 'DIV') {
                        input.innerText = message;
                    } else {
                        input.value = message;
                    }
                    input.dispatchEvent(new InputEvent('input', { bubbles: true }));
                    const form = input.closest('form');
                    if (form) {
                        if (typeof form.requestSubmit === 'function') {
                            form.requestSubmit();
                            return;
                        } else if (typeof form.submit === 'function') {
                            form.submit();
                            return;
                        }
                    }
                    const sendBtn = Array.from(document.querySelectorAll('button'))
                        .find(btn => btn.innerText && btn.innerText.toLowerCase().includes('send'));
                    if (sendBtn) {
                        sendBtn.click();
                        return;
                    }
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                    });
                    input.dispatchEvent(enterEvent);
                })();
            "
        end tell

        -- Inject JavaScript to poll for when the assistant response stabilizes
        tell tab foundTabIndex of foundWindow
            execute javascript "
                (async function() {
                    function getLastAssistantText() {
                        const elems = Array.from(document.querySelectorAll('div, p, span'));
                        const aiElems = elems.filter(el => el.textContent && /answer|thinking/i.test(el.textContent));
                        return aiElems.map(el => el.textContent).join(' ').trim();
                    }

                    const sleep = ms => new Promise(res => setTimeout(res, ms));
                    let last = '', sameCount = 0;

                    for (let i = 0; i < 60; i++) {
                        const current = getLastAssistantText();
                        if (current === last && current.length > 100) {
                            sameCount++;
                        } else {
                            sameCount = 0;
                            last = current;
                        }
                        if (sameCount >= 3) break;
                        await sleep(2000);
                    }
                })();
            "
        end tell

        -- After polling, get the HTML content
        tell tab foundTabIndex of foundWindow
            set pageSourceHTML to execute javascript "document.documentElement.outerHTML;"
        end tell
    end tell

    -- Save HTML via shell (handles utf-8)
    if pageSourceHTML is not "" and pageSourceHTML is not missing value then
        set tmpFile to "/tmp/qwen_temp.html"
        do shell script "echo " & quoted form of pageSourceHTML & " > " & quoted form of tmpFile
        do shell script "iconv -f UTF-8 -t UTF-8 " & quoted form of tmpFile & " > " & quoted form of outputHtmlFilePOSIX
        do shell script "rm " & quoted form of tmpFile
        
        -- Run Python script and capture its stdout, including --all if present
        set pythonResult to do shell script "python3 -m web_llm_interactor.extract_json_from_html " & quoted form of outputHtmlFilePOSIX & allFlag
        
        -- Add a small delay to ensure Python result is processed before switching
        delay 1
        
        -- Return focus to VSCode after results are ready
        -- tell application "Visual Studio Code"
        --     activate
        -- end tell
        
        return pythonResult
    else
        error "Page HTML was empty or could not be retrieved."
    end if
end run