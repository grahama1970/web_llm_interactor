on run argv
	set messageText to item 1 of argv
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
			execute javascript "\n                const inputField = document.querySelector('textarea#chat-input') || \n                                 document.querySelector('textarea') ||\n                                 document.querySelector('div[contenteditable=\"true\"]');\n                if (inputField) {\n                    inputField.focus();\n                    inputField.value = '" & messageText & "';\n                    const inputEvent = document.createEvent('Event');\n                    inputEvent.initEvent('input', true, true);\n                    inputField.dispatchEvent(inputEvent);\n                    setTimeout(function() {\n                        const sendButton = document.querySelector('button[type=\"submit\"]') || \n                                         document.querySelector('button.send') ||\n                                         document.querySelector('button:has(svg)');\n                        if (sendButton) {\n                            sendButton.click();\n                            return 'Message sent successfully';\n                        } else {\n                            inputField.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));\n                            return 'Message sent successfully via Enter key';\n                        }\n                    }, 500);\n                } else {\n                    throw new Error('Chat input field not found');\n                }\n            "
		end tell
	end tell
end run