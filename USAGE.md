```
uv run src/poc/llm_web_interactor.py --question "What is AI?" --url "https://chat.qwen.ai/" --output-dir "./responses"
```

```
uv run src/llm_web_interactor.py --question "What is AI?" --url "https://chat.qwen.ai/" --output-dir "./responses"
```

```
 osascript src/send_message.applescript "This is my message to send"
 ```

 ```
  osascript src/capture_response.applescript
  ```

```
osascript src/send_message_and_capture.applescript "Answer concisely: What is the most common color of an apple?"
```

```
osascript src/send_enter_save_source.applescript "What is the capital of Oklahoma. return in well ordered Json with the fields: question, thinking, answer"
```

```
osascript src/send_enter_save_source.applescript "What is the capital of Georgia. return in well ordered Json with the fields: question, thinking, answer"
```

```
Use the -all flag if you want all the results in the chat window
osascript src/send_enter_save_source.applescript "What is the capital of Florida. return in well ordered Json with the fields: question, thinking, answer" --all
```

```
osascript send_enter_save_source.applescript "Your message here" "https://chat.qwen.ai/" "/Users/robert/output.html" --all
```
