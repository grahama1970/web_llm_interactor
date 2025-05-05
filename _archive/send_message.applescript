
tell application "Google Chrome"
    activate
    set foundTab to false
    set targetURL to "https://chat.qwen.ai/"
    
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
        error "Could not find a tab with https://chat.qwen.ai/"
    end if
    
    tell active tab of front window
        set jsCode to "
            
        function createNaturalBezierCurve(startX, startY, endX, endY) {
            const numControlPoints = Math.floor(Math.random() * 4) + 2;
            const controlPoints = [];
            const totalDistance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
            for (let i = 0; i < numControlPoints; i++) {
                const t = (i + 1) / (numControlPoints + 1);
                const midX = startX + t * (endX - startX);
                const midY = startY + t * (endY - startY);
                const maxDeviation = totalDistance * (0.2 + Math.random() * 0.3);
                const deviation = Math.random() * maxDeviation - maxDeviation / 2;
                const angle = Math.random() * 2 * Math.PI;
                controlPoints.push({
                    x: midX + deviation * Math.cos(angle),
                    y: midY + deviation * Math.sin(angle)
                });
            }
            return { start: { x: startX, y: startY }, end: { x: endX, y: endY }, controlPoints: controlPoints };
        }

        function getPointOnBezierCurve(curve, t) {
            const { start, end, controlPoints } = curve;
            if (controlPoints.length === 1) {
                const cp = controlPoints[0];
                const x = Math.pow(1 - t, 2) * start.x + 2 * (1 - t) * t * cp.x + Math.pow(t, 2) * end.x;
                const y = Math.pow(1 - t, 2) * start.y + 2 * (1 - t) * t * cp.y + Math.pow(t, 2) * end.y;
                return { x, y };
            } else if (controlPoints.length === 2) {
                const cp1 = controlPoints[0];
                const cp2 = controlPoints[1];
                const x = Math.pow(1 - t, 3) * start.x + 3 * Math.pow(1 - t, 2) * t * cp1.x + 3 * (1 - t) * Math.pow(t, 2) * cp2.x + Math.pow(t, 3) * end.x;
                const y = Math.pow(1 - t, 3) * start.y + 3 * Math.pow(1 - t, 2) * t * cp1.y + 3 * (1 - t) * Math.pow(t, 2) * cp2.y + Math.pow(t, 3) * end.y;
                return { x, y };
            } else {
                const points = [start, ...controlPoints, end];
                let currentPoints = [...points];
                for (let k = points.length - 1; k > 0; k--) {
                    const newPoints = [];
                    for (let i = 0; i < k; i++) {
                        const x = (1 - t) * currentPoints[i].x + t * currentPoints[i + 1].x;
                        const y = (1 - t) * currentPoints[i].y + t * currentPoints[i + 1].y;
                        newPoints.push({ x, y });
                    }
                    currentPoints = newPoints;
                }
                return currentPoints[0];
            }
        }

        function simulateMouseMovement(curve, callback) {
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            function ensureInViewport(coord) {
                return { x: Math.max(0, Math.min(coord.x, viewportWidth)), y: Math.max(0, Math.min(coord.y, viewportHeight)) };
            }
            const numSteps = 100;
            let length = 0;
            let prevPoint = curve.start;
            for (let i = 1; i <= numSteps; i++) {
                const t = i / numSteps;
                const point = getPointOnBezierCurve(curve, t);
                length += Math.sqrt(Math.pow(point.x - prevPoint.x, 2) + Math.pow(point.y - prevPoint.y, 2));
                prevPoint = point;
            }
            const baseSpeed = 500 + Math.random() * 1000;
            const duration = length / baseSpeed * 1000;
            const steps = Math.max(50, Math.ceil(duration / 10));
            let step = 0;
            const initialDelay = 100 + Math.random() * 300;

            setTimeout(function moveStep() {
                if (step <= steps) {
                    const t = step / steps;
                    const easedT = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
                    const point = ensureInViewport(getPointOnBezierCurve(curve, easedT));
                    const mouseEvent = new MouseEvent("mousemove", {
                        clientX: point.x,
                        clientY: point.y,
                        bubbles: true,
                        cancelable: true
                    });
                    document.elementFromPoint(point.x, point.y)?.dispatchEvent(mouseEvent);
                    document.dispatchEvent(mouseEvent);
                    const pause = Math.random() < 0.1 ? 50 + Math.random() * 100 : 0;
                    const nextStepTime = (duration / steps) + (Math.random() * 10 - 5) + pause;
                    setTimeout(moveStep, nextStepTime);
                    step++;
                } else if (callback) callback();
            }, initialDelay);
        }

        function getElementCenter(element) {
            const rect = element.getBoundingClientRect();
            return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        }
    
            
        function simulateTyping(inputField, text) {
            let currentText = "";
            let charIndex = 0;
            const textArray = text.split("");
            function typeNextChar() {
                if (charIndex < textArray.length) {
                    currentText += textArray[charIndex];
                    if (inputField.tagName.toLowerCase() === "textarea") {
                        inputField.value = currentText;
                    } else {
                        inputField.innerHTML = currentText;
                    }
                    const inputEvent = document.createEvent("Event");
                    inputEvent.initEvent("input", true, true);
                    inputField.dispatchEvent(inputEvent);
                    const changeEvent = document.createEvent("Event");
                    changeEvent.initEvent("change", true, true);
                    inputField.dispatchEvent(changeEvent);
                    charIndex++;
                    const pauseChance = Math.random();
                    const delay = pauseChance < 0.2 ? 200 + Math.random() * 300 : 50 + Math.random() * 100;
                    setTimeout(typeNextChar, delay);
                } else {
                    if (typeof callback === "function") callback();
                }
            }
            typeNextChar();
        }
        const inputField = document.querySelector("textarea#chat-input") || 
                         document.querySelector("textarea") ||
                         document.querySelector("div[contenteditable=\"true\"]");
        if (inputField) {
            const textToType = "What is AI?";
            simulateTyping(inputField, textToType);
        } else {
            throw new Error("Chat input field not found");
        }
    
            
        let inputField = document.querySelector("textarea#chat-input") || 
                        document.querySelector("textarea") ||
                        document.querySelector("div[contenteditable=\"true\"]");
        if (!inputField) {
            throw new Error("Chat input field not found");
        }

        const edgePosition = Math.floor(Math.random() * 4);
        const startX = edgePosition === 1 ? window.innerWidth - 10 : 
                      edgePosition === 3 ? 10 : 
                      Math.random() * window.innerWidth;
        const startY = edgePosition === 0 ? 10 : 
                      edgePosition === 2 ? window.innerHeight - 10 : 
                      Math.random() * window.innerHeight;
        const targetPos = getElementCenter(inputField);
        const curve = createNaturalBezierCurve(startX, startY, targetPos.x, targetPos.y);

        simulateMouseMovement(curve, function() {
            setTimeout(function() {
                const clickEvent = document.createEvent("MouseEvent");
                clickEvent.initMouseEvent("click", true, true, window, 0, 0, 0, targetPos.x, targetPos.y, false, false, false, false, 0, null);
                inputField.dispatchEvent(clickEvent);
                inputField.focus();
                setTimeout(function() {
                    simulateTyping(inputField, textToType, function() {
                        const submitDelay = 500 + Math.random() * 1000;
                        setTimeout(function() {
                            let sendButton = document.querySelector("button[type=\"submit\"]") || 
                                            document.querySelector("button.send") ||
                                            document.querySelector("button:has(svg)");
                            if (sendButton) {
                                const sendButtonPos = getElementCenter(sendButton);
                                const curveToButton = createNaturalBezierCurve(targetPos.x, targetPos.y, sendButtonPos.x, sendButtonPos.y);
                                simulateMouseMovement(curveToButton, function() {
                                    const sendButtonClickEvent = document.createEvent("MouseEvent");
                                    sendButtonClickEvent.initMouseEvent("click", true, true, window, 0, 0, 0, sendButtonPos.x, sendButtonPos.y, false, false, false, false, 0, null);
                                    sendButton.dispatchEvent(sendButtonClickEvent);
                                    return "Message sent successfully";
                                });
                            } else {
                                const keydownEvent = document.createEvent("KeyboardEvent");
                                keydownEvent.initKeyboardEvent("keydown", true, true, window, "Enter", 0, "", false, "");
                                Object.defineProperty(keydownEvent, "keyCode", { value: 13 });
                                inputField.dispatchEvent(keydownEvent);
                                return "Message sent successfully via Enter key";
                            }
                        }, submitDelay);
                    });
                }, 100 + Math.random() * 200);
            }, 50 + Math.random() * 100);
        });
    
        "
        execute javascript "(function() { if (document.readyState !== 'complete') { return 'DOM not ready'; } try { 
        function createNaturalBezierCurve(startX, startY, endX, endY) {
            const numControlPoints = Math.floor(Math.random() * 4) + 2;
            const controlPoints = [];
            const totalDistance = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
            for (let i = 0; i < numControlPoints; i++) {
                const t = (i + 1) / (numControlPoints + 1);
                const midX = startX + t * (endX - startX);
                const midY = startY + t * (endY - startY);
                const maxDeviation = totalDistance * (0.2 + Math.random() * 0.3);
                const deviation = Math.random() * maxDeviation - maxDeviation / 2;
                const angle = Math.random() * 2 * Math.PI;
                controlPoints.push({
                    x: midX + deviation * Math.cos(angle),
                    y: midY + deviation * Math.sin(angle)
                });
            }
            return { start: { x: startX, y: startY }, end: { x: endX, y: endY }, controlPoints: controlPoints };
        }

        function getPointOnBezierCurve(curve, t) {
            const { start, end, controlPoints } = curve;
            if (controlPoints.length === 1) {
                const cp = controlPoints[0];
                const x = Math.pow(1 - t, 2) * start.x + 2 * (1 - t) * t * cp.x + Math.pow(t, 2) * end.x;
                const y = Math.pow(1 - t, 2) * start.y + 2 * (1 - t) * t * cp.y + Math.pow(t, 2) * end.y;
                return { x, y };
            } else if (controlPoints.length === 2) {
                const cp1 = controlPoints[0];
                const cp2 = controlPoints[1];
                const x = Math.pow(1 - t, 3) * start.x + 3 * Math.pow(1 - t, 2) * t * cp1.x + 3 * (1 - t) * Math.pow(t, 2) * cp2.x + Math.pow(t, 3) * end.x;
                const y = Math.pow(1 - t, 3) * start.y + 3 * Math.pow(1 - t, 2) * t * cp1.y + 3 * (1 - t) * Math.pow(t, 2) * cp2.y + Math.pow(t, 3) * end.y;
                return { x, y };
            } else {
                const points = [start, ...controlPoints, end];
                let currentPoints = [...points];
                for (let k = points.length - 1; k > 0; k--) {
                    const newPoints = [];
                    for (let i = 0; i < k; i++) {
                        const x = (1 - t) * currentPoints[i].x + t * currentPoints[i + 1].x;
                        const y = (1 - t) * currentPoints[i].y + t * currentPoints[i + 1].y;
                        newPoints.push({ x, y });
                    }
                    currentPoints = newPoints;
                }
                return currentPoints[0];
            }
        }

        function simulateMouseMovement(curve, callback) {
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;
            function ensureInViewport(coord) {
                return { x: Math.max(0, Math.min(coord.x, viewportWidth)), y: Math.max(0, Math.min(coord.y, viewportHeight)) };
            }
            const numSteps = 100;
            let length = 0;
            let prevPoint = curve.start;
            for (let i = 1; i <= numSteps; i++) {
                const t = i / numSteps;
                const point = getPointOnBezierCurve(curve, t);
                length += Math.sqrt(Math.pow(point.x - prevPoint.x, 2) + Math.pow(point.y - prevPoint.y, 2));
                prevPoint = point;
            }
            const baseSpeed = 500 + Math.random() * 1000;
            const duration = length / baseSpeed * 1000;
            const steps = Math.max(50, Math.ceil(duration / 10));
            let step = 0;
            const initialDelay = 100 + Math.random() * 300;

            setTimeout(function moveStep() {
                if (step <= steps) {
                    const t = step / steps;
                    const easedT = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
                    const point = ensureInViewport(getPointOnBezierCurve(curve, easedT));
                    const mouseEvent = new MouseEvent("mousemove", {
                        clientX: point.x,
                        clientY: point.y,
                        bubbles: true,
                        cancelable: true
                    });
                    document.elementFromPoint(point.x, point.y)?.dispatchEvent(mouseEvent);
                    document.dispatchEvent(mouseEvent);
                    const pause = Math.random() < 0.1 ? 50 + Math.random() * 100 : 0;
                    const nextStepTime = (duration / steps) + (Math.random() * 10 - 5) + pause;
                    setTimeout(moveStep, nextStepTime);
                    step++;
                } else if (callback) callback();
            }, initialDelay);
        }

        function getElementCenter(element) {
            const rect = element.getBoundingClientRect();
            return { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
        }
     
        function simulateTyping(inputField, text) {
            let currentText = "";
            let charIndex = 0;
            const textArray = text.split("");
            function typeNextChar() {
                if (charIndex < textArray.length) {
                    currentText += textArray[charIndex];
                    if (inputField.tagName.toLowerCase() === "textarea") {
                        inputField.value = currentText;
                    } else {
                        inputField.innerHTML = currentText;
                    }
                    const inputEvent = document.createEvent("Event");
                    inputEvent.initEvent("input", true, true);
                    inputField.dispatchEvent(inputEvent);
                    const changeEvent = document.createEvent("Event");
                    changeEvent.initEvent("change", true, true);
                    inputField.dispatchEvent(changeEvent);
                    charIndex++;
                    const pauseChance = Math.random();
                    const delay = pauseChance < 0.2 ? 200 + Math.random() * 300 : 50 + Math.random() * 100;
                    setTimeout(typeNextChar, delay);
                } else {
                    if (typeof callback === "function") callback();
                }
            }
            typeNextChar();
        }
        const inputField = document.querySelector("textarea#chat-input") || 
                         document.querySelector("textarea") ||
                         document.querySelector("div[contenteditable=\"true\"]");
        if (inputField) {
            const textToType = "What is AI?";
            simulateTyping(inputField, textToType);
        } else {
            throw new Error("Chat input field not found");
        }
     
        let inputField = document.querySelector("textarea#chat-input") || 
                        document.querySelector("textarea") ||
                        document.querySelector("div[contenteditable=\"true\"]");
        if (!inputField) {
            throw new Error("Chat input field not found");
        }

        const edgePosition = Math.floor(Math.random() * 4);
        const startX = edgePosition === 1 ? window.innerWidth - 10 : 
                      edgePosition === 3 ? 10 : 
                      Math.random() * window.innerWidth;
        const startY = edgePosition === 0 ? 10 : 
                      edgePosition === 2 ? window.innerHeight - 10 : 
                      Math.random() * window.innerHeight;
        const targetPos = getElementCenter(inputField);
        const curve = createNaturalBezierCurve(startX, startY, targetPos.x, targetPos.y);

        simulateMouseMovement(curve, function() {
            setTimeout(function() {
                const clickEvent = document.createEvent("MouseEvent");
                clickEvent.initMouseEvent("click", true, true, window, 0, 0, 0, targetPos.x, targetPos.y, false, false, false, false, 0, null);
                inputField.dispatchEvent(clickEvent);
                inputField.focus();
                setTimeout(function() {
                    simulateTyping(inputField, textToType, function() {
                        const submitDelay = 500 + Math.random() * 1000;
                        setTimeout(function() {
                            let sendButton = document.querySelector("button[type=\"submit\"]") || 
                                            document.querySelector("button.send") ||
                                            document.querySelector("button:has(svg)");
                            if (sendButton) {
                                const sendButtonPos = getElementCenter(sendButton);
                                const curveToButton = createNaturalBezierCurve(targetPos.x, targetPos.y, sendButtonPos.x, sendButtonPos.y);
                                simulateMouseMovement(curveToButton, function() {
                                    const sendButtonClickEvent = document.createEvent("MouseEvent");
                                    sendButtonClickEvent.initMouseEvent("click", true, true, window, 0, 0, 0, sendButtonPos.x, sendButtonPos.y, false, false, false, false, 0, null);
                                    sendButton.dispatchEvent(sendButtonClickEvent);
                                    return "Message sent successfully";
                                });
                            } else {
                                const keydownEvent = document.createEvent("KeyboardEvent");
                                keydownEvent.initKeyboardEvent("keydown", true, true, window, "Enter", 0, "", false, "");
                                Object.defineProperty(keydownEvent, "keyCode", { value: 13 });
                                inputField.dispatchEvent(keydownEvent);
                                return "Message sent successfully via Enter key";
                            }
                        }, submitDelay);
                    });
                }, 100 + Math.random() * 200);
            }, 50 + Math.random() * 100);
        });
     } catch (e) { return 'Error: ' + e.message; } })();"
    end tell
end tell
    