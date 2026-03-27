(function () {
  // 原有的密码强度检测功能
  function score(p) {
    var s = 0
    if (!p) return s
    if (p.length >= 8) s++
    if (/[a-zA-Z]/.test(p)) s++
    if (/[0-9]/.test(p)) s++
    if (/[^a-zA-Z0-9]/.test(p)) s++
    return s
  }
  function label(s) {
    if (s <= 1) return { t: "弱", c: "#ef4444" }
    if (s === 2) return { t: "一般", c: "#f59e0b" }
    if (s === 3) return { t: "良好", c: "#22c55e" }
    return { t: "很强", c: "#3b82f6" }
  }
  document.addEventListener("input", function (e) {
    var form = e.target && e.target.form
    if (!form || !form.hasAttribute("data-password-strength")) return
    if (e.target.name !== "password") return
    var m = form.querySelector(".meter")
    if (!m) return
    var sc = score(e.target.value)
    var l = label(sc)
    m.textContent = "密码强度：" + l.t
    m.style.color = l.c
  })

  // 代码高亮功能
  function processMessages() {
    var messageContents = document.querySelectorAll('#messages-box div[style="white-space:pre-wrap"]');
    messageContents.forEach(function (element) {
      // 检查是否已经处理过
      if (element.dataset.processed) return;

      var content = element.textContent;

      // 匹配代码块：```language\ncode\n```
      var codeBlockRegex = /```([a-zA-Z0-9]+)?\n([\s\S]*?)```/g;
      var match;
      var hasCodeBlock = false;
      var parts = [];
      var lastIndex = 0;

      // 分割内容为普通文本和代码块
      while ((match = codeBlockRegex.exec(content)) !== null) {
        hasCodeBlock = true;
        // 添加普通文本部分
        if (match.index > lastIndex) {
          parts.push(document.createTextNode(content.substring(lastIndex, match.index)));
        }

        // 处理代码块
        var language = match[1] || 'plain';
        var code = match[2];

        // 创建代码块元素
        var codeBlock = document.createElement('div');
        codeBlock.className = 'code-block';

        // 添加语言标签
        var languageDiv = document.createElement('div');
        languageDiv.className = 'language';
        languageDiv.textContent = language;
        codeBlock.appendChild(languageDiv);

        // 创建代码预格式化元素
        var pre = document.createElement('pre');
        pre.style.whiteSpace = 'pre';
        pre.style.fontFamily = 'Courier New, Courier, monospace';

        // 保持原始格式，逐行处理
        var codeLines = code.split('\n');
        codeLines.forEach(function (line, index) {
          var lineElement = document.createElement('span');
          
          // 处理缩进和空格
          var indentMatch = line.match(/^\s+/);
          if (indentMatch) {
            var indent = indentMatch[0];
            lineElement.appendChild(document.createTextNode(indent));
            line = line.substring(indent.length);
          }
          
          // 处理整行注释
          if (line.trim().startsWith('#')) {
            var span = document.createElement('span');
            span.className = 'code-comment';
            span.textContent = line;
            lineElement.appendChild(span);
          } else {
            // 处理行内注释
            var commentIndex = line.indexOf('#');
            var codePart = commentIndex !== -1 ? line.substring(0, commentIndex) : line;
            var commentPart = commentIndex !== -1 ? line.substring(commentIndex) : '';
            
            // 处理代码部分
            if (codePart) {
              // 处理字符串
              var pos = 0;
              var inString = false;
              var stringChar = '';
              
              while (pos < codePart.length) {
                var char = codePart[pos];
                
                if (!inString) {
                  // 检查是否开始字符串
                  if (char === '"' || char === "'") {
                    inString = true;
                    stringChar = char;
                    var stringStart = pos;
                    // 找到字符串结束位置
                    var stringEnd = codePart.indexOf(stringChar, pos + 1);
                    while (stringEnd !== -1 && codePart[stringEnd - 1] === '\\') {
                      stringEnd = codePart.indexOf(stringChar, stringEnd + 1);
                    }
                    if (stringEnd !== -1) {
                      // 处理字符串前的内容
                      if (pos > 0) {
                        var beforeString = codePart.substring(0, pos);
                        lineElement.appendChild(document.createTextNode(beforeString));
                      }
                      // 处理字符串
                      var stringContent = codePart.substring(stringStart, stringEnd + 1);
                      var span = document.createElement('span');
                      span.className = 'code-string';
                      span.textContent = stringContent;
                      lineElement.appendChild(span);
                      // 更新位置
                      pos = stringEnd + 1;
                      inString = false;
                    } else {
                      // 未闭合的字符串，按普通文本处理
                      lineElement.appendChild(document.createTextNode(char));
                      pos++;
                    }
                  } else if (char === '(') {
                    // 处理函数调用
                    var funcMatch = codePart.substring(0, pos).match(/([a-zA-Z_][a-zA-Z0-9_]*)$/);
                    if (funcMatch) {
                      var funcName = funcMatch[1];
                      // 移除函数名
                      lineElement.removeChild(lineElement.lastChild);
                      // 添加高亮的函数名
                      var funcSpan = document.createElement('span');
                      funcSpan.className = 'code-function';
                      funcSpan.textContent = funcName;
                      lineElement.appendChild(funcSpan);
                    }
                    // 添加括号
                    lineElement.appendChild(document.createTextNode('('));
                    pos++;
                  } else if (char === ')') {
                    // 添加括号
                    lineElement.appendChild(document.createTextNode(')'));
                    pos++;
                  } else if (char === '{') {
                    // 添加大括号
                    lineElement.appendChild(document.createTextNode('{'));
                    pos++;
                  } else if (char === '}') {
                    // 添加大括号
                    lineElement.appendChild(document.createTextNode('}'));
                    pos++;
                  } else if (char === '[') {
                    // 添加中括号
                    lineElement.appendChild(document.createTextNode('['));
                    pos++;
                  } else if (char === ']') {
                    // 添加中括号
                    lineElement.appendChild(document.createTextNode(']'));
                    pos++;
                  } else if (char === ';') {
                    // 添加分号
                    lineElement.appendChild(document.createTextNode(';'));
                    pos++;
                  } else if (char === ':') {
                    // 添加冒号
                    lineElement.appendChild(document.createTextNode(':'));
                    pos++;
                  } else if (char === ',') {
                    // 添加逗号
                    lineElement.appendChild(document.createTextNode(','));
                    pos++;
                  } else if (char === '.') {
                    // 添加点
                    lineElement.appendChild(document.createTextNode('.'));
                    pos++;
                  } else if (/[+\-*/%=<>!&|^~]/.test(char)) {
                    // 处理运算符
                    var opMatch = codePart.substring(pos).match(/^([+\-*/%=<>!&|^~]+)/);
                    if (opMatch) {
                      var op = opMatch[1];
                      var opSpan = document.createElement('span');
                      opSpan.className = 'code-operator';
                      opSpan.textContent = op;
                      lineElement.appendChild(opSpan);
                      pos += op.length;
                    } else {
                      lineElement.appendChild(document.createTextNode(char));
                      pos++;
                    }
                  } else if (/[0-9]/.test(char)) {
                    // 处理数字
                    var numMatch = codePart.substring(pos).match(/^\d+\.?\d*/);
                    if (numMatch) {
                      var num = numMatch[0];
                      var numSpan = document.createElement('span');
                      numSpan.className = 'code-number';
                      numSpan.textContent = num;
                      lineElement.appendChild(numSpan);
                      pos += num.length;
                    } else {
                      lineElement.appendChild(document.createTextNode(char));
                      pos++;
                    }
                  } else if (/[a-zA-Z_]/.test(char)) {
                    // 处理标识符
                    var idMatch = codePart.substring(pos).match(/^[a-zA-Z_][a-zA-Z0-9_]*/);
                    if (idMatch) {
                      var id = idMatch[0];
                      // 检查是否是关键词
                      var keywords = ['def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return', 'import', 'from', 'as', 'try', 'except', 'finally', 'with', 'lambda', 'pass'];
                      if (keywords.includes(id)) {
                        var keywordSpan = document.createElement('span');
                        keywordSpan.className = 'code-keyword';
                        keywordSpan.textContent = id;
                        lineElement.appendChild(keywordSpan);
                      } else {
                        lineElement.appendChild(document.createTextNode(id));
                      }
                      pos += id.length;
                    } else {
                      lineElement.appendChild(document.createTextNode(char));
                      pos++;
                    }
                  } else {
                    // 其他字符
                    lineElement.appendChild(document.createTextNode(char));
                    pos++;
                  }
                } else {
                  // 在字符串内，直接添加
                  lineElement.appendChild(document.createTextNode(char));
                  pos++;
                  // 检查是否结束字符串
                  if (char === stringChar && codePart[pos - 2] !== '\\') {
                    inString = false;
                  }
                }
              }
            }
            
            // 处理注释部分
            if (commentPart) {
              var commentSpan = document.createElement('span');
              commentSpan.className = 'code-comment';
              commentSpan.textContent = commentPart;
              lineElement.appendChild(commentSpan);
            }
          }
          
          pre.appendChild(lineElement);
          if (index < codeLines.length - 1) {
            pre.appendChild(document.createElement('br'));
          }
        });

        codeBlock.appendChild(pre);
        parts.push(codeBlock);
        lastIndex = match.index + match[0].length;
      }

      // 添加剩余的普通文本
      if (lastIndex < content.length) {
        parts.push(document.createTextNode(content.substring(lastIndex)));
      }

      if (hasCodeBlock) {
        // 清空元素并添加新内容
        element.innerHTML = '';
        parts.forEach(function (part) {
          element.appendChild(part);
        });
        element.dataset.processed = 'true';
        // 移除white-space:pre-wrap样式，因为我们现在使用HTML
        element.style.whiteSpace = 'normal';
      }
    });
  }

  // 页面加载时处理初始消息
  window.addEventListener('DOMContentLoaded', processMessages);

  // 暴露 processMessages 函数，供外部调用
  window.processMessages = processMessages;
})();
