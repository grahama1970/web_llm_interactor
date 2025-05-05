on run argv
    set responseWaitDelay to 30
    set outputHtmlFilePOSIX to "/Users/robert/Documents/dev/workspace/experiments/perplexity_spoof/qwen_response_final.html"
    set targetURL to "https://chat.qwen.ai/"

    if (count of argv) is 0 then
        error "Usage: osascript send_enter_save_source_final.applescript \"Your message here\"" number -1700
    end if
    set messageText to item 1 of argv

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

        -- Inject JavaScript to input message and click send
        tell tab foundTabIndex of foundWindow
            execute javascript "
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
                    const buttons = form.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.innerText.toLowerCase().includes('send')) {
                            btn.click();
                            break;
                        }
                    }
                } else {
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true
                    });
                    input.dispatchEvent(enterEvent);
                }
            "
        end tell

        delay responseWaitDelay

        -- Get the HTML content
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
        return "HTML saved to " & outputHtmlFilePOSIX
    else
        error "Page HTML was empty or could not be retrieved."
    end if
end run
