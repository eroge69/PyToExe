import webview
import os
import sys
import json
from datetime import datetime
from base64 import b64encode
import requests
import base64
from flask import app


# ----- 前置變數 -----
window = None
html_path = os.path.join(os.path.dirname(__file__), 'web/index.html')
data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)

# ----- 建立 API -----
class API:
    def __init__(self):
        print("Initializing API...")
        self.settings = self.load_settings()
        self.conversations = self.load_conversations()
        print("API ready.")

    def load_settings(self):
        settings_path = os.path.join(data_dir, 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "api_key": "",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "language": "en",
            "theme": "light"
        }

    def load_conversations(self):
        conv_path = os.path.join(data_dir, 'conversations.json')
        if os.path.exists(conv_path):
            with open(conv_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def send_message(self, conversation_id, message_text):
        global window
        # 模擬回應，實作略
        ai_response = f"Echo: {message_text}"
        js_code = f"""
        const message = document.createElement('div');
        message.className = 'message ai-message';
        message.innerHTML = '<div class="message-content">{ai_response}</div>';
        document.getElementById('chatContainer').appendChild(message);
        document.getElementById('chatContainer').scrollTop = document.getElementById('chatContainer').scrollHeight;
        """
        if window:
            window.evaluate_js(js_code)
        return {"response": ai_response}

# ----- 當 UI 載入後觸發 -----
def on_loaded():
    global window, api
    window = webview.windows[0]
    print("[Window Ready] Injecting JS functions")
    # 你可以在這裡 inject JS 也可以做 UI 初始化

# ----- 主程式 -----
if __name__ == '__main__':
    api = API()
    webview.create_window("AI Chat", html_path)
    webview.start(func=on_loaded, debug=True, http_server=True, gui='edgechromium')


# Language translations
translations = {
    "en": {
        "welcome": "Welcome to AI Chat! I'm your AI assistant, ready to help with any questions or tasks.",
        "settings": "Settings",
        "newChat": "New Chat",
        "apiKey": "API Key",
        "apiKeyWarning": "Your API key is stored locally on your device.",
        "provider": "AI Provider",
        "model": "Model",
        "modelInfo": "GPT-3.5 is faster and cheaper, GPT-4 is more capable.",
        "customApiUrl": "Custom API URL",
        "customApiUrlInfo": "URL for your custom API endpoint",
        "systemPrompt": "System Prompt",
        "systemPromptInfo": "Instructions for the AI's behavior",
        "temperature": "Temperature",
        "temperatureInfo": "Higher = more creative, Lower = more focused",
        "maxTokens": "Max Tokens",
        "maxTokensInfo": "Maximum length of the response (leave empty for auto)",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "custom": "Custom",
        "customColors": "Custom Colors",
        "primary": "Primary Color",
        "secondary": "Secondary Color",
        "background": "Background Color",
        "textColor": "Text Color",
        "general": "General",
        "advanced": "Advanced",
        "appearance": "Appearance",
        "save": "Save",
        "cancel": "Cancel",
        "send": "Send",
        "typeMessage": "Type your message...",
        "errorLoadingSettings": "Error loading settings. Please try again.",
        "errorSendingMessage": "Failed to communicate with the AI. Please try again.",
        "setApiKeyError": "Please set your API key in the settings before sending messages.",
        "openai": "OpenAI (ChatGPT)",
        "custom": "Custom API",
        "current": "Current",
        "conversations": "Conversations",
        "deleteConversation": "Delete Conversation",
        "renameConversation": "Rename Conversation",
        "exportConversation": "Export Conversation",
        "importConversation": "Import Conversation",
        "clearConversation": "Clear Conversation",
        "conversationName": "Conversation Name",
        "untitledConversation": "Untitled Conversation",
        "today": "Today",
        "yesterday": "Yesterday",
        "previousDays": "Previous Days",
        "generateImage": "Generate Image",
        "imageSize": "Image Size",
        "imagePrompt": "Image Description",
        "generateImageButton": "Generate",
        "imageGenerationError": "Failed to generate image. Please try again.",
        "copyToClipboard": "Copy to Clipboard",
        "copied": "Copied!",
        "downloadImage": "Download Image",
        "imageGeneration": "Image Generation",
        "imageModel": "Image Model",
        "imageQuality": "Image Quality",
        "standard": "Standard",
        "hd": "HD",
        "animations": "Animations",
        "enableAnimations": "Enable Animations",
        "animationSpeed": "Animation Speed",
        "slow": "Slow",
        "medium": "Medium",
        "fast": "Fast",
        "apiProviders": "API Providers",
        "addProvider": "Add Provider",
        "providerName": "Provider Name",
        "providerApiKey": "Provider API Key",
        "providerApiUrl": "Provider API URL",
        "deleteProvider": "Delete Provider",
        "editProvider": "Edit Provider",
        "formatting": "Formatting",
        "bold": "Bold",
        "italic": "Italic",
        "code": "Code",
        "link": "Link",
        "heading1": "Heading 1",
        "heading2": "Heading 2",
        "heading3": "Heading 3",
        "quote": "Quote",
        "list": "List",
        "codeBlock": "Code Block",
        "table": "Table"
    },
    "zh": {
        "welcome": "欢迎使用AI聊天！我是您的AI助手，随时准备帮助您解答问题或完成任务。",
        "settings": "设置",
        "newChat": "新对话",
        "apiKey": "API密钥",
        "apiKeyWarning": "您的API密钥存储在您的设备本地。",
        "provider": "AI提供商",
        "model": "模型",
        "modelInfo": "GPT-3.5更快更便宜，GPT-4功能更强大。",
        "customApiUrl": "自定义API网址",
        "customApiUrlInfo": "您的自定义API端点的URL",
        "systemPrompt": "系统提示",
        "systemPromptInfo": "AI行为的指令",
        "temperature": "温度",
        "temperatureInfo": "更高 = 更有创意，更低 = 更专注",
        "maxTokens": "最大令牌数",
        "maxTokensInfo": "响应的最大长度（留空为自动）",
        "language": "语言",
        "theme": "主题",
        "light": "明亮",
        "dark": "暗黑",
        "custom": "自定义",
        "customColors": "自定义颜色",
        "primary": "主要颜色",
        "secondary": "次要颜色",
        "background": "背景颜色",
        "textColor": "文字颜色",
        "general": "常规",
        "advanced": "高级",
        "appearance": "外观",
        "save": "保存",
        "cancel": "取消",
        "send": "发送",
        "typeMessage": "输入您的消息...",
        "errorLoadingSettings": "加载设置时出错。请重试。",
        "errorSendingMessage": "与AI通信失败。请重试。",
        "setApiKeyError": "请在设置中设置您的API密钥后再发送消息。",
        "openai": "OpenAI (ChatGPT)",
        "custom": "自定义API",
        "current": "当前",
        "conversations": "对话",
        "deleteConversation": "删除对话",
        "renameConversation": "重命名对话",
        "exportConversation": "导出对话",
        "importConversation": "导入对话",
        "clearConversation": "清除对话",
        "conversationName": "对话名称",
        "untitledConversation": "未命名对话",
        "today": "今天",
        "yesterday": "昨天",
        "previousDays": "更早",
        "generateImage": "生成图片",
        "imageSize": "图片尺寸",
        "imagePrompt": "图片描述",
        "generateImageButton": "生成",
        "imageGenerationError": "生成图片失败。请重试。",
        "copyToClipboard": "复制到剪贴板",
        "copied": "已复制！",
        "downloadImage": "下载图片",
        "imageGeneration": "图片生成",
        "imageModel": "图片模型",
        "imageQuality": "图片质量",
        "standard": "标准",
        "hd": "高清",
        "animations": "动画",
        "enableAnimations": "启用动画",
        "animationSpeed": "动画速度",
        "slow": "慢",
        "medium": "中",
        "fast": "快",
        "apiProviders": "API提供商",
        "addProvider": "添加提供商",
        "providerName": "提供商名称",
        "providerApiKey": "提供商API密钥",
        "providerApiUrl": "提供商API网址",
        "deleteProvider": "删除提供商",
        "editProvider": "编辑提供商",
        "formatting": "格式化",
        "bold": "粗体",
        "italic": "斜体",
        "code": "代码",
        "link": "链接",
        "heading1": "标题1",
        "heading2": "标题2",
        "heading3": "标题3",
        "quote": "引用",
        "list": "列表",
        "codeBlock": "代码块",
        "table": "表格"
    },
    "ja": {
        "welcome": "AIチャットへようこそ！AIアシスタントとして、質問やタスクのお手伝いをします。",
        "settings": "設定",
        "newChat": "新しいチャット",
        "apiKey": "APIキー",
        "apiKeyWarning": "APIキーはデバイスにローカルに保存されます。",
        "provider": "AIプロバイダー",
        "model": "モデル",
        "modelInfo": "GPT-3.5は速くて安価、GPT-4はより高性能です。",
        "customApiUrl": "カスタムAPI URL",
        "customApiUrlInfo": "カスタムAPIエンドポイントのURL",
        "systemPrompt": "システムプロンプト",
        "systemPromptInfo": "AIの動作に関する指示",
        "temperature": "温度",
        "temperatureInfo": "高い = より創造的、低い = よりフォーカス",
        "maxTokens": "最大トークン数",
        "maxTokensInfo": "応答の最大長（空白で自動）",
        "language": "言語",
        "theme": "テーマ",
        "light": "ライト",
        "dark": "ダーク",
        "custom": "カスタム",
        "customColors": "カスタムカラー",
        "primary": "プライマリカラー",
        "secondary": "セカンダリカラー",
        "background": "背景色",
        "textColor": "文字色",
        "general": "一般",
        "advanced": "詳細",
        "appearance": "外観",
        "save": "保存",
        "cancel": "キャンセル",
        "send": "送信",
        "typeMessage": "メッセージを入力...",
        "errorLoadingSettings": "設定の読み込みエラー。もう一度お試しください。",
        "errorSendingMessage": "AIとの通信に失敗しました。もう一度お試しください。",
        "setApiKeyError": "メッセージを送信する前に設定でAPIキーを設定してください。",
        "openai": "OpenAI (ChatGPT)",
        "custom": "カスタムAPI",
        "current": "現在",
        "conversations": "会話",
        "deleteConversation": "会話を削除",
        "renameConversation": "会話の名前を変更",
        "exportConversation": "会話をエクスポート",
        "importConversation": "会話をインポート",
        "clearConversation": "会話をクリア",
        "conversationName": "会話名",
        "untitledConversation": "無題の会話",
        "today": "今日",
        "yesterday": "昨日",
        "previousDays": "過去の日",
        "generateImage": "画像を生成",
        "imageSize": "画像サイズ",
        "imagePrompt": "画像の説明",
        "generateImageButton": "生成",
        "imageGenerationError": "画像の生成に失敗しました。もう一度お試しください。",
        "copyToClipboard": "クリップボードにコピー",
        "copied": "コピーしました！",
        "downloadImage": "画像をダウンロード",
        "imageGeneration": "画像生成",
        "imageModel": "画像モデル",
        "imageQuality": "画像品質",
        "standard": "標準",
        "hd": "HD",
        "animations": "アニメーション",
        "enableAnimations": "アニメーションを有効にする",
        "animationSpeed": "アニメーション速度",
        "slow": "遅い",
        "medium": "中間",
        "fast": "速い",
        "apiProviders": "APIプロバイダー",
        "addProvider": "プロバイダーを追加",
        "providerName": "プロバイダー名",
        "providerApiKey": "プロバイダーAPIキー",
        "providerApiUrl": "プロバイダーAPI URL",
        "deleteProvider": "プロバイダーを削除",
        "editProvider": "プロバイダーを編集",
        "formatting": "フォーマット",
        "bold": "太字",
        "italic": "斜体",
        "code": "コード",
        "link": "リンク",
        "heading1": "見出し1",
        "heading2": "見出し2",
        "heading3": "見出し3",
        "quote": "引用",
        "list": "リスト",
        "codeBlock": "コードブロック",
        "table": "表"
    }
}

class API:
    # 修改 API 类的初始化方法，添加更多错误处理
    def __init__(self):
        try:
            print("Initializing API class...")
            self.settings = self.load_settings()
            self.conversations = self.load_conversations()
            print("API initialization complete")
        except Exception as e:
            print(f"Error during API initialization: {str(e)}")
            import traceback
            traceback.print_exc()
            # 设置默认值以防止进一步的错误
            self.settings = {
                "api_key": "", 
                "provider": "openai", 
                "model": "gpt-3.5-turbo",
                "language": "en",
                "theme": "light"
            }
            self.conversations = []
    
    def load_settings(self):
        settings_path = os.path.join(data_dir, 'settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "api_key": "", 
            "provider": "openai", 
            "model": "gpt-3.5-turbo",
            "custom_api_url": "",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "max_tokens": None,
            "language": "en",
            "theme": "light",
            "custom_colors": {
                "primary": "#4a6cf7",
                "secondary": "#6c757d",
                "background": "#f8f9fa",
                "text": "#212529"
            },
            "animations": {
                "enabled": True,
                "speed": "medium"
            },
            "providers": [
                {
                    "name": "openai",
                    "display_name": "OpenAI (ChatGPT)",
                    "api_key": "",
                    "api_url": "https://api.openai.com/v1"
                }
            ],
            "image_generation": {
                "model": "dall-e-3",
                "size": "1024x1024",
                "quality": "standard"
            }
        }
    
    def save_settings(self, settings):
        settings_path = os.path.join(data_dir, 'settings.json')
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f)
        self.settings = settings
        return True
    
    def get_settings(self):
        return self.settings
    
    def get_translations(self, lang_code=None):
        if not lang_code:
            lang_code = self.settings.get("language", "en")
        
        if lang_code not in translations:
            lang_code = "en"  # Fallback to English
            
        return translations[lang_code]
    
    def load_conversations(self):
        conversations_path = os.path.join(data_dir, 'conversations.json')
        if os.path.exists(conversations_path):
            with open(conversations_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_conversations(self, conversations):
        conversations_path = os.path.join(data_dir, 'conversations.json')
        with open(conversations_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f)
        self.conversations = conversations
        return True
    
    def get_conversations(self):
        return self.conversations
    
    def create_conversation(self, name=None):
        timestamp = datetime.now().isoformat()
        conversation = {
            "id": f"conv_{timestamp}",
            "name": name or f"Conversation {len(self.conversations) + 1}",
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": []
        }
        self.conversations.append(conversation)
        self.save_conversations(self.conversations)
        return conversation
    
    def update_conversation(self, conversation_id, data):
        for i, conv in enumerate(self.conversations):
            if conv["id"] == conversation_id:
                self.conversations[i].update(data)
                self.conversations[i]["updated_at"] = datetime.now().isoformat()
                self.save_conversations(self.conversations)
                return self.conversations[i]
        return None
    
    def delete_conversation(self, conversation_id):
        self.conversations = [conv for conv in self.conversations if conv["id"] != conversation_id]
        self.save_conversations(self.conversations)
        return True
    
    def add_message_to_conversation(self, conversation_id, message):
        for i, conv in enumerate(self.conversations):
            if conv["id"] == conversation_id:
                if "messages" not in self.conversations[i]:
                    self.conversations[i]["messages"] = []
                
                self.conversations[i]["messages"].append(message)
                self.conversations[i]["updated_at"] = datetime.now().isoformat()
                self.save_conversations(self.conversations)
                return self.conversations[i]
        return None
    
    def send_message(self, conversation_id, message_text):
        try:
            if not self.settings.get("api_key"):
                lang = self.settings.get("language", "en")
                return {"error": translations[lang]["setApiKeyError"]}
        
            provider = self.settings.get("provider", "openai")
        
            # Add user message to conversation
            timestamp = datetime.now().isoformat()
            user_message = {
                "id": f"msg_{timestamp}",
                "role": "user",
                "content": message_text,
                "timestamp": timestamp
            }
        
            self.add_message_to_conversation(conversation_id, user_message)
        
            # Get conversation history
            conversation = next((conv for conv in self.conversations if conv["id"] == conversation_id), None)
            if not conversation:
                return {"error": "Conversation not found"}
        
            conversation_history = conversation.get("messages", [])
        
            if provider == "openai":
                response = self.call_openai(message_text, conversation_history)
            else:
                # Find custom provider
                provider_config = next((p for p in self.settings.get("providers", []) if p["name"] == provider), None)
                if provider_config:
                    response = self.call_custom_api(message_text, conversation_history, provider_config)
                else:
                    return {"error": f"Provider {provider} not found"}
        
            if "error" in response:
                return response
        
            # Add AI response to conversation
            ai_message = {
                "id": f"msg_{datetime.now().isoformat()}",
                "role": "assistant",
                "content": response["response"],
                "timestamp": datetime.now().isoformat()
            }
        
            self.add_message_to_conversation(conversation_id, ai_message)
        
            # 直接通过 JavaScript 更新 UI
            print("Response generated, directly updating UI...")
        
            # 使用全局 window 变量直接执行 JavaScript
            try:
                if 'window' in globals():
                    js_code = f"""
                    (function() {{
                        console.log("Executing direct UI update");
                        const aiMessage = {{
                            content: {json.dumps(response["response"])},
                            role: "assistant"
                        }};
                    
                        // 移除打字指示器
                        const typingIndicators = document.querySelectorAll('.typing-indicator');
                        typingIndicators.forEach(indicator => indicator.remove());
                    
                        // 添加 AI 消息
                        const messageElement = document.createElement('div');
                        messageElement.classList.add('message', 'ai-message');
                    
                        const messageContent = document.createElement('div');
                        messageContent.classList.add('message-content');
                    
                        // 处理 markdown
                        messageContent.innerHTML = marked.parse(aiMessage.content);
                    
                        // 添加复制按钮到代码块
                        messageContent.querySelectorAll('pre').forEach(pre => {{
                            const copyBtn = document.createElement('button');
                            copyBtn.className = 'copy-code-btn';
                            copyBtn.textContent = 'Copy';
                            copyBtn.onclick = function() {{
                                const code = pre.querySelector('code').textContent;
                                navigator.clipboard.writeText(code).then(() => {{
                                    copyBtn.textContent = 'Copied!';
                                    setTimeout(() => {{
                                        copyBtn.textContent = 'Copy';
                                    }}, 2000);
                                }});
                            }};
                            pre.appendChild(copyBtn);
                        }});
                    
                        // 高亮代码块
                        messageContent.querySelectorAll('pre code').forEach(block => {{
                            hljs.highlightElement(block);
                        }});
                    
                        messageElement.appendChild(messageContent);
                        document.getElementById('chatContainer').appendChild(messageElement);
                    
                        // 滚动到底部
                        document.getElementById('chatContainer').scrollTop = document.getElementById('chatContainer').scrollHeight;
                    
                        // 重新启用输入
                        window.isWaitingForResponse = false;
                        document.getElementById('sendButton').disabled = false;
                        document.getElementById('messageInput').focus();
                    
                        console.log("Direct UI update completed");
                    }})();
                    """
                    window.evaluate_js(js_code)
                    print("JavaScript evaluation triggered")
            except Exception as e:
                print(f"Error during direct UI update: {str(e)}")
                import traceback
                traceback.print_exc()
        
            return {"response": response["response"], "conversation": conversation}
        except Exception as e:
            return {"error": str(e)}
    
    def call_openai(self, message, conversation_history):
        import requests
        
        api_key = self.settings.get("api_key")
        model = self.settings.get("model", "gpt-3.5-turbo")
        temperature = self.settings.get("temperature", 0.7)
        max_tokens = self.settings.get("max_tokens")
        system_prompt = self.settings.get("system_prompt", "You are a helpful assistant.")
        
        # Convert conversation history to OpenAI format
        messages = [{"role": "system", "content": system_prompt}]
        
        for entry in conversation_history:
            role = entry["role"]
            content = entry["content"]
            messages.append({"role": role, "content": content})
        
        # If the last message is already the user's message, don't add it again
        if not messages[-1]["role"] == "user" or not messages[-1]["content"] == message:
            messages.append({"role": "user", "content": message})
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            return {"error": f"OpenAI API Error: {error_message}"}
        
        response_data = response.json()
        return {"response": response_data["choices"][0]["message"]["content"]}
    
    def call_custom_api(self, message, conversation_history, provider_config):
        import requests
        
        api_key = provider_config.get("api_key") or self.settings.get("api_key")
        custom_url = provider_config.get("api_url")
        
        if not custom_url:
            return {"error": "Custom API URL is not set"}
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Convert conversation history to a simpler format
        history = []
        for entry in conversation_history:
            history.append({
                "role": entry["role"],
                "content": entry["content"]
            })
        
        data = {
            "message": message,
            "conversation_history": history,
            "system_prompt": self.settings.get("system_prompt", "You are a helpful assistant."),
            "temperature": self.settings.get("temperature", 0.7),
            "max_tokens": self.settings.get("max_tokens")
        }
        
        response = requests.post(
            custom_url,
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            return {"error": f"Custom API Error: Status code {response.status_code}"}
        
        try:
            response_data = response.json()
            return {"response": response_data.get("response", response_data.get("message", str(response_data)))}
        except:
            return {"error": "Failed to parse response from custom API"}
    
    def generate_image(self, prompt):
        try:
            api_key = self.settings.get("api_key")
            if not api_key:
                lang = self.settings.get("language", "en")
                return {"error": translations[lang]["setApiKeyError"]}
            
            image_settings = self.settings.get("image_generation", {})
            model = image_settings.get("model", "dall-e-3")
            size = image_settings.get("size", "1024x1024")
            quality = image_settings.get("quality", "standard")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": quality
            }
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                return {"error": f"Image Generation Error: {error_message}"}
            
            response_data = response.json()
            image_url = response_data["data"][0]["url"]
            
            # Download the image and convert to base64
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_data = base64.b64encode(image_response.content).decode('utf-8')
                return {
                    "image": image_data,
                    "prompt": prompt,
                    "model": model,
                    "size": size
                }
            else:
                return {"error": "Failed to download generated image"}
            
        except Exception as e:
            return {"error": str(e)}

# Create the HTML file with the chat interface
with open(html_path, 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat Application</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.7/dist/katex.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked@4.3.0/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.7/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.7/dist/contrib/auto-render.min.js"></script>
    <style id="theme-styles">
        :root {
            --primary-color: #4a6cf7;
            --primary-hover: #3a5ce6;
            --secondary-color: #6c757d;
            --background-color: #f8f9fa;
            --card-bg-color: #ffffff;
            --text-color: #212529;
            --border-color: #dee2e6;
            --sidebar-width: 280px;
            --header-height: 60px;
            --animation-speed: 0.3s;
            --message-user-bg: #4a6cf7;
            --message-user-color: #ffffff;
            --message-ai-bg: #f1f3f5;
            --message-ai-color: #212529;
            --error-color: #dc3545;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --info-color: #17a2b8;
            --code-bg: #f8f9fa;
            --code-color: #e83e8c;
            --quote-bg: #f8f9fa;
            --quote-border: #dee2e6;
            --scrollbar-thumb: #adb5bd;
            --scrollbar-track: #f1f3f5;
        }
        
        [data-theme="dark"] {
            --primary-color: #4a6cf7;
            --primary-hover: #3a5ce6;
            --secondary-color: #adb5bd;
            --background-color: #212529;
            --card-bg-color: #343a40;
            --text-color: #f8f9fa;
            --border-color: #495057;
            --message-user-bg: #4a6cf7;
            --message-user-color: #ffffff;
            --message-ai-bg: #343a40;
            --message-ai-color: #f8f9fa;
            --code-bg: #2b3035;
            --code-color: #f08c99;
            --quote-bg: #2b3035;
            --quote-border: #495057;
            --scrollbar-thumb: #495057;
            --scrollbar-track: #343a40;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: background-color var(--animation-speed), color var(--animation-speed), border-color var(--animation-speed);
        }
        
        body {
            display: flex;
            flex-direction: column;
            height: 100vh;
            background-color: var(--background-color);
            color: var(--text-color);
            overflow: hidden;
        }
        
        .app-container {
            display: flex;
            height: calc(100vh - var(--header-height));
            position: relative;
        }
        
        .header {
            height: var(--header-height);
            background-color: var(--primary-color);
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            z-index: 100;
        }
        
        .header h1 {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .header-actions {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .btn {
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.2s, transform 0.1s;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover {
            background-color: var(--primary-hover);
        }
        
        .btn-secondary {
            background-color: var(--secondary-color);
            color: white;
        }
        
        .btn-secondary:hover {
            background-color: #5a6268;
        }
        
        .btn-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            background: rgba(255, 255, 255, 0.2);
        }
        
        .btn-icon:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .sidebar {
            width: var(--sidebar-width);
            background-color: var(--card-bg-color);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            transition: transform var(--animation-speed);
            z-index: 10;
            height: 100%;
            overflow: hidden;
        }
        
        .sidebar.collapsed {
            transform: translateX(calc(-1 * var(--sidebar-width)));
        }
        
        .sidebar-header {
            padding: 15px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .new-chat-btn {
            width: 100%;
            padding: 10px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: background-color 0.2s;
        }
        
        .new-chat-btn:hover {
            background-color: var(--primary-hover);
        }
        
        .conversations-list {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        
        .conversation-group {
            margin-bottom: 15px;
        }
        
        .conversation-group-title {
            font-size: 0.8rem;
            color: var(--secondary-color);
            margin-bottom: 5px;
            padding: 0 5px;
        }
        
        .conversation-item {
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background-color 0.2s;
            position: relative;
        }
        
        .conversation-item:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }
        
        .conversation-item.active {
            background-color: rgba(74, 108, 247, 0.1);
            font-weight: 500;
        }
        
        .conversation-item-icon {
            color: var(--secondary-color);
            font-size: 0.9rem;
        }
        
        .conversation-item-title {
            flex: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 0.9rem;
        }
        
        .conversation-item-actions {
            display: none;
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background-color: var(--card-bg-color);
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .conversation-item:hover .conversation-item-actions {
            display: flex;
        }
        
        .conversation-action {
            padding: 5px;
            background: none;
            border: none;
            cursor: pointer;
            color: var(--secondary-color);
            font-size: 0.8rem;
        }
        
        .conversation-action:hover {
            color: var(--primary-color);
        }
        
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
            position: relative;
        }
        
        .chat-container {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 20px;
            scroll-behavior: smooth;
        }
        
        .message {
            max-width: 85%;
            padding: 15px;
            border-radius: 10px;
            line-height: 1.5;
            word-wrap: break-word;
            position: relative;
            animation: message-fade-in 0.3s ease-out;
        }
        
        @keyframes message-fade-in {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .user-message {
            align-self: flex-end;
            background-color: var(--message-user-bg);
            color: var(--message-user-color);
            border-bottom-right-radius: 0;
        }
        
        .ai-message {
            align-self: flex-start;
            background-color: var(--message-ai-bg);
            color: var(--message-ai-color);
            border-bottom-left-radius: 0;
        }
        
        .error-message {
            align-self: center;
            background-color: rgba(220, 53, 69, 0.1);
            color: var(--error-color);
            border: 1px solid var(--error-color);
            border-radius: 10px;
            max-width: 90%;
        }
        
        .message-content {
            white-space: pre-wrap;
        }
        
        .message-content h1, 
        .message-content h2, 
        .message-content h3 {
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        
        .message-content p {
            margin-bottom: 1em;
        }
        
        .message-content p:last-child {
            margin-bottom: 0;
        }
        
        .message-content ul, 
        .message-content ol {
            margin-bottom: 1em;
            padding-left: 2em;
        }
        
        .message-content pre {
            background-color: var(--code-bg);
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 1em;
            position: relative;
        }
        
        .message-content pre code {
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            tab-size: 2;
        }
        
        .message-content code {
            background-color: var(--code-bg);
            color: var(--code-color);
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }
        
        .message-content blockquote {
            border-left: 3px solid var(--quote-border);
            padding-left: 10px;
            margin-left: 0;
            margin-right: 0;
            background-color: var(--quote-bg);
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 1em;
        }
        
        .message-content table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 1em;
        }
        
        .message-content th, 
        .message-content td {
            border: 1px solid var(--border-color);
            padding: 8px;
            text-align: left;
        }
        
        .message-content th {
            background-color: var(--code-bg);
        }
        
        .message-content img {
            max-width: 100%;
            border-radius: 5px;
            margin-bottom: 1em;
        }
        
        .copy-code-btn {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: var(--card-bg-color);
            border: none;
            border-radius: 3px;
            padding: 3px 6px;
            font-size: 0.7em;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.2s;
        }
        
        .message-content pre:hover .copy-code-btn {
            opacity: 1;
        }
        
        .input-container {
            padding: 15px;
            background-color: var(--card-bg-color);
            border-top: 1px solid var(--border-color);
            position: relative;
        }
        
        .input-wrapper {
            display: flex;
            position: relative;
        }
        
        .formatting-toolbar {
            display: flex;
            gap: 5px;
            padding: 5px 0;
            margin-bottom: 5px;
            overflow-x: auto;
            scrollbar-width: thin;
        }
        
        .formatting-btn {
            background: none;
            border: none;
            color: var(--secondary-color);
            cursor: pointer;
            padding: 3px 6px;
            border-radius: 3px;
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            gap: 3px;
        }
        
        .formatting-btn:hover {
            background-color: rgba(0, 0, 0, 0.05);
            color: var(--primary-color);
        }
        
        .message-input {
            flex: 1;
            padding: 12px 15px;
            border: 1px solid var(--border-color);
            border-radius: 20px;
            outline: none;
            font-size: 1rem;
            resize: none;
            max-height: 200px;
            min-height: 40px;
            background-color: var(--card-bg-color);
            color: var(--text-color);
        }
        
        .message-input:focus {
            border-color: var(--primary-color);
        }
        
        .send-btn {
            margin-left: 10px;
            width: 40px;
            height: 40px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.2s, transform 0.1s;
        }
        
        .send-btn:hover {
            background-color: var(--primary-hover);
        }
        
        .send-btn:active {
            transform: scale(0.95);
        }
        
        .send-btn:disabled {
            background-color: var(--secondary-color);
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 10px 15px;
            background-color: var(--message-ai-bg);
            border-radius: 10px;
            align-self: flex-start;
            color: var(--secondary-color);
            font-size: 0.9rem;
            animation: message-fade-in 0.3s ease-out;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: var(--secondary-color);
            border-radius: 50%;
            animation: typing-animation 1.4s infinite ease-in-out;
        }
        
        .typing-dot:nth-child(1) {
            animation-delay: 0s;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing-animation {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-5px);
            }
        }
        
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
            animation: fade-in 0.2s ease-out;
        }
        
        @keyframes fade-in {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }
        
        .modal-content {
            background-color: var(--card-bg-color);
            padding: 20px;
            border-radius: 10px;
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            overflow-y: auto;
            animation: modal-slide-in 0.3s ease-out;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        @keyframes modal-slide-in {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .modal-header h2 {
            color: var(--text-color);
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--secondary-color);
            transition: color 0.2s;
        }
        
        .close-btn:hover {
            color: var(--primary-color);
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: var(--text-color);
            font-weight: 500;
        }
        
        .form-group input, 
        .form-group select, 
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            font-size: 1rem;
            background-color: var(--card-bg-color);
            color: var(--text-color);
        }
        
        .form-group input:focus, 
        .form-group select:focus, 
        .form-group textarea:focus {
            border-color: var(--primary-color);
            outline: none;
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 80px;
        }
        
        .form-buttons {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
        }
        
        .color-picker-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .color-picker {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }
        
        .color-picker label {
            font-size: 0.8rem;
        }
        
        .color-picker input[type="color"] {
            width: 40px;
            height: 40px;
            padding: 0;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            cursor: pointer;
        }
        
        .tabs {
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 15px;
        }
        
        .tab {
            padding: 10px 15px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .tab.active {
            border-bottom-color: var(--primary-color);
            color: var(--primary-color);
            font-weight: 500;
        }
        
        .tab-content {
            display: none;
            animation: fade-in 0.2s ease-out;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .language-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .language-btn {
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            background-color: var(--card-bg-color);
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-color);
        }
        
        .language-btn.active {
            background-color: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }
        
        .theme-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .theme-option {
            width: 100px;
            height: 70px;
            border-radius: 5px;
            cursor: pointer;
            overflow: hidden;
            position: relative;
            border: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .theme-option.active {
            border-color: var(--primary-color);
        }
        
        .theme-option-light {
            background-color: #f8f9fa;
        }
        
        .theme-option-light::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 20px;
            background-color: #4a6cf7;
        }
        
        .theme-option-dark {
            background-color: #212529;
        }
        
        .theme-option-dark::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 20px;
            background-color: #4a6cf7;
        }
        
        .theme-option-custom {
            background: linear-gradient(135deg, #f8f9fa 50%, #212529 50%);
        }
        
        .theme-option-custom::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 20px;
            background: linear-gradient(90deg, #4a6cf7 50%, #6c757d 50%);
        }
        
        .theme-label {
            text-align: center;
            font-size: 0.8rem;
            margin-top: 5px;
            color: var(--text-color);
        }
        
        .warning-text {
            color: var(--warning-color);
            margin-top: 5px;
            font-size: 0.85rem;
        }
        
        .info-text {
            color: var(--info-color);
            margin-top: 5px;
            font-size: 0.85rem;
        }
        
        .model-info {
            font-size: 0.8rem;
            color: var(--secondary-color);
            margin-top: 5px;
        }
        
        .toggle-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }
        
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: var(--secondary-color);
            transition: .4s;
            border-radius: 24px;
        }
        
        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .toggle-slider {
            background-color: var(--primary-color);
        }
        
        input:checked + .toggle-slider:before {
            transform: translateX(26px);
        }
        
        .toggle-label {
            font-size: 0.9rem;
            color: var(--text-color);
        }
        
        .image-generation-container {
            padding: 15px;
            background-color: var(--card-bg-color);
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
        }
        
        .image-generation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .image-generation-title {
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .image-generation-close {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            color: var(--secondary-color);
        }
        
        .image-generation-form {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .image-generation-textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            font-size: 1rem;
            resize: vertical;
            min-height: 80px;
            background-color: var(--card-bg-color);
            color: var(--text-color);
        }
        
        .image-generation-options {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .image-generation-option {
            flex: 1;
            min-width: 120px;
        }
        
        .image-generation-option label {
            display: block;
            margin-bottom: 5px;
            font-size: 0.9rem;
        }
        
        .image-generation-option select {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--border-color);
            border-radius: 5px;
            background-color: var(--card-bg-color);
            color: var(--text-color);
        }
        
        .image-generation-buttons {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 10px;
        }
        
        .generated-image-container {
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        
        .generated-image {
            max-width: 100%;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .generated-image-actions {
            display: flex;
            gap: 10px;
        }
        
        .image-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            padding: 20px;
        }
        
        .image-loading-spinner {
            width: 40px;
            height: 40px;
            border: 3px solid rgba(0, 0, 0, 0.1);
            border-top-color: var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
        
        .image-loading-text {
            font-size: 0.9rem;
            color: var(--secondary-color);
        }
        
        .sidebar-toggle {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 5;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: var(--card-bg-color);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s;
        }
        
        .sidebar-toggle.active {
            transform: translateX(var(--sidebar-width));
        }
        
        .sidebar-toggle i {
            color: var(--text-color);
            transition: transform 0.3s;
        }
        
        .sidebar-toggle.active i {
            transform: rotate(180deg);
        }
        
        .image-btn {
            position: absolute;
            right: 60px;
            bottom: 15px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background-color: var(--card-bg-color);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--secondary-color);
            transition: all 0.2s;
        }
        
        .image-btn:hover {
            color: var(--primary-color);
            border-color: var(--primary-color);
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--scrollbar-track);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--scrollbar-thumb);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary-color);
        }
        
        /* Animations */
        @keyframes pulse {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
            100% {
                transform: scale(1);
            }
        }
        
        @keyframes slide-in-right {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slide-in-left {
            from {
                transform: translateX(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slide-in-bottom {
            from {
                transform: translateY(100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes slide-in-top {
            from {
                transform: translateY(-100%);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .animate-pulse {
            animation: pulse 2s infinite;
        }
        
        .animate-slide-in-right {
            animation: slide-in-right 0.3s ease-out;
        }
        
        .animate-slide-in-left {
            animation: slide-in-left 0.3s ease-out;
        }
        
        .animate-slide-in-bottom {
            animation: slide-in-bottom 0.3s ease-out;
        }
        
        .animate-slide-in-top {
            animation: slide-in-top 0.3s ease-out;
        }
        
        /* Responsive styles */
        @media screen and (max-width: 768px) {
            .sidebar {
                position: absolute;
                top: 0;
                left: 0;
                height: 100%;
                z-index: 100;
                box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
            }
            
            .main-content {
                width: 100%;
            }
            
            .message {
                max-width: 90%;
            }
            
            .modal-content {
                width: 95%;
            }
            
            .theme-selector {
                flex-wrap: wrap;
            }
            
            .color-picker-container {
                flex-direction: column;
            }
            
            .color-picker {
                flex-direction: row;
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Chat</h1>
        <div class="header-actions">
            <button class="btn btn-icon" id="themeToggleBtn" title="Toggle Theme">
                <i class="fas fa-moon"></i>
            </button>
            <button class="btn btn-icon" id="settingsBtn" title="Settings">
                <i class="fas fa-cog"></i>
            </button>
        </div>
    </div>
    
    <div class="app-container">
        <button class="sidebar-toggle" id="sidebarToggle">
            <i class="fas fa-chevron-right"></i>
        </button>
        
        <div class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <button class="new-chat-btn" id="newChatBtn">
                    <i class="fas fa-plus"></i> <span id="newChatText">New Chat</span>
                </button>
            </div>
            
            <div class="conversations-list" id="conversationsList">
                <!-- Conversations will be populated here -->
            </div>
        </div>
        
        <div class="main-content">
            <div class="chat-container" id="chatContainer">
                <!-- Messages will be populated here -->
            </div>
            
            <div class="input-container">
                <div class="formatting-toolbar" id="formattingToolbar">
                    <button class="formatting-btn" data-format="bold" title="Bold">
                        <i class="fas fa-bold"></i>
                    </button>
                    <button class="formatting-btn" data-format="italic" title="Italic">
                        <i class="fas fa-italic"></i>
                    </button>
                    <button class="formatting-btn" data-format="heading1" title="Heading 1">
                        <i class="fas fa-heading"></i>1
                    </button>
                    <button class="formatting-btn" data-format="heading2" title="Heading 2">
                        <i class="fas fa-heading"></i>2
                    </button>
                    <button class="formatting-btn" data-format="heading3" title="Heading 3">
                        <i class="fas fa-heading"></i>3
                    </button>
                    <button class="formatting-btn" data-format="code" title="Inline Code">
                        <i class="fas fa-code"></i>
                    </button>
                    <button class="formatting-btn" data-format="codeblock" title="Code Block">
                        <i class="fas fa-file-code"></i>
                    </button>
                    <button class="formatting-btn" data-format="quote" title="Quote">
                        <i class="fas fa-quote-right"></i>
                    </button>
                    <button class="formatting-btn" data-format="list" title="List">
                        <i class="fas fa-list"></i>
                    </button>
                    <button class="formatting-btn" data-format="link" title="Link">
                        <i class="fas fa-link"></i>
                    </button>
                </div>
                
                <div class="input-wrapper">
                    <textarea class="message-input" id="messageInput" placeholder="Type your message..." rows="1"></textarea>
                    <button class="image-btn" id="imageBtn" title="Generate Image">
                        <i class="fas fa-image"></i>
                    </button>
                    <button class="send-btn" id="sendButton" disabled>
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Settings Modal -->
    <div class="modal-overlay" id="settingsModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="settingsTitle">Settings</h2>
                <button class="close-btn" onclick="closeModal('settingsModal')">&times;</button>
            </div>
            
            <div class="language-selector">
                <button class="language-btn" onclick="changeLanguage('en')">English</button>
                <button class="language-btn" onclick="changeLanguage('zh')">中文</button>
                <button class="language-btn" onclick="changeLanguage('ja')">日本語</button>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="switchTab('general')" id="generalTabBtn">General</div>
                <div class="tab" onclick="switchTab('appearance')" id="appearanceTabBtn">Appearance</div>
                <div class="tab" onclick="switchTab('advanced')" id="advancedTabBtn">Advanced</div>
            </div>
            
            <div class="tab-content active" id="generalTab">
                <div class="form-group">
                    <label for="apiKey" id="apiKeyLabel">API Key</label>
                    <input type="password" id="apiKey" placeholder="Enter your API key">
                    <div class="warning-text" id="apiKeyWarning">Your API key is stored locally on your device.</div>
                </div>
                
                <div class="form-group">
                    <label for="provider" id="providerLabel">AI Provider</label>
                    <select id="provider" onchange="toggleProviderOptions()">
                        <option value="openai" id="openaiOption">OpenAI (ChatGPT)</option>
                        <option value="custom" id="customOption">Custom API</option>
                    </select>
                </div>
                
                <div id="openaiOptions">
                    <div class="form-group">
                        <label for="model" id="modelLabel">Model</label>
                        <select id="model">
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                            <option value="gpt-4">GPT-4</option>
                            <option value="gpt-4-turbo">GPT-4 Turbo</option>
                            <option value="gpt-4o">GPT-4o</option>
                        </select>
                        <div class="model-info" id="modelInfo">GPT-3.5 is faster and cheaper, GPT-4 is more capable.</div>
                    </div>
                </div>
                
                <div id="customOptions" style="display: none;">
                    <div class="form-group">
                        <label for="customApiUrl" id="customApiUrlLabel">Custom API URL</label>
                        <input type="text" id="customApiUrl" placeholder="Enter custom API URL">
                        <div class="model-info" id="customApiUrlInfo">URL for your custom API endpoint</div>
                    </div>
                </div>
            </div>
            
            <div class="tab-content" id="appearanceTab">
                <div class="form-group">
                    <label id="themeLabel">Theme</label>
                    <div class="theme-selector">
                        <div class="theme-option theme-option-light" data-theme="light">
                            <div class="theme-label" id="lightThemeLabel">Light</div>
                        </div>
                        <div class="theme-option theme-option-dark" data-theme="dark">
                            <div class="theme-label" id="darkThemeLabel">Dark</div>
                        </div>
                        <div class="theme-option theme-option-custom" data-theme="custom">
                            <div class="theme-label" id="customThemeLabel">Custom</div>
                        </div>
                    </div>
                </div>
                
                <div class="form-group" id="customColorsContainer" style="display: none;">
                    <label id="customColorsLabel">Custom Colors</label>
                    <div class="color-picker-container">
                        <div class="color-picker">
                            <label id="primaryColorLabel">Primary</label>
                            <input type="color" id="primaryColor" value="#4a6cf7">
                        </div>
                        <div class="color-picker">
                            <label id="secondaryColorLabel">Secondary</label>
                            <input type="color" id="secondaryColor" value="#6c757d">
                        </div>
                        <div class="color-picker">
                            <label id="backgroundColorLabel">Background</label>
                            <input type="color" id="backgroundColor" value="#f8f9fa">
                        </div>
                        <div class="color-picker">
                            <label id="textColorLabel">Text</label>
                            <input type="color" id="textColor" value="#212529">
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label id="animationsLabel">Animations</label>
                    <div class="toggle-container">
                        <label class="toggle-switch">
                            <input type="checkbox" id="enableAnimations" checked>
                            <span class="toggle-slider"></span>
                        </label>
                        <span class="toggle-label" id="enableAnimationsLabel">Enable Animations</span>
                    </div>
                </div>
                
                <div class="form-group" id="animationSpeedContainer">
                    <label for="animationSpeed" id="animationSpeedLabel">Animation Speed</label>
                    <select id="animationSpeed">
                        <option value="slow" id="slowOption">Slow</option>
                        <option value="medium" id="mediumOption" selected>Medium</option>
                        <option value="fast" id="fastOption">Fast</option>
                    </select>
                </div>
            </div>
            
            <div class="tab-content" id="advancedTab">
                <div class="form-group">
                    <label for="systemPrompt" id="systemPromptLabel">System Prompt</label>
                    <textarea id="systemPrompt" placeholder="You are a helpful assistant."></textarea>
                    <div class="model-info" id="systemPromptInfo">Instructions for the AI's behavior</div>
                </div>
                
                <div class="form-group">
                    <label for="temperature" id="temperatureLabel">Temperature</label>
                    <input type="range" id="temperature" min="0" max="2" step="0.1" value="0.7" oninput="updateTemperatureValue()">
                    <div class="model-info"><span id="currentText">Current</span>: <span id="temperatureValue">0.7</span> (<span id="temperatureInfo">Higher = more creative, Lower = more focused</span>)</div>
                </div>
                
                <div class="form-group">
                    <label for="maxTokens" id="maxTokensLabel">Max Tokens</label>
                    <input type="number" id="maxTokens" placeholder="Auto" min="1" max="8000">
                    <div class="model-info" id="maxTokensInfo">Maximum length of the response (leave empty for auto)</div>
                </div>
                
                <div class="form-group">
                    <label id="imageGenerationLabel">Image Generation</label>
                    <div class="form-group">
                        <label for="imageModel" id="imageModelLabel">Image Model</label>
                        <select id="imageModel">
                            <option value="dall-e-3">DALL-E 3</option>
                            <option value="dall-e-2">DALL-E 2</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="imageSize" id="imageSizeLabel">Image Size</label>
                        <select id="imageSize">
                            <option value="1024x1024">1024x1024</option>
                            <option value="1792x1024">1792x1024</option>
                            <option value="1024x1792">1024x1792</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="imageQuality" id="imageQualityLabel">Image Quality</label>
                        <select id="imageQuality">
                            <option value="standard" id="standardOption">Standard</option>
                            <option value="hd" id="hdOption">HD</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="form-buttons">
                <button class="btn btn-secondary" onclick="closeModal('settingsModal')" id="cancelBtn">Cancel</button>
                <button class="btn btn-primary" onclick="saveSettings()" id="saveBtn">Save</button>
            </div>
        </div>
    </div>
    
    <!-- Image Generation Modal -->
    <div class="modal-overlay" id="imageModal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="imageGenerationTitle">Image Generation</h2>
                <button class="close-btn" onclick="closeModal('imageModal')">&times;</button>
            </div>
            
            <div class="form-group">
                <label for="imagePrompt" id="imagePromptLabel">Image Description</label>
                <textarea id="imagePrompt" placeholder="Describe the image you want to generate..." rows="4"></textarea>
            </div>
            
            <div class="form-group">
                <div class="image-generation-options">
                    <div class="image-generation-option">
                        <label for="modalImageSize" id="modalImageSizeLabel">Image Size</label>
                        <select id="modalImageSize">
                            <option value="1024x1024">1024x1024</option>
                            <option value="1792x1024">1792x1024</option>
                            <option value="1024x1792">1024x1792</option>
                        </select>
                    </div>
                    
                    <div class="image-generation-option">
                        <label for="modalImageQuality" id="modalImageQualityLabel">Quality</label>
                        <select id="modalImageQuality">
                            <option value="standard" id="modalStandardOption">Standard</option>
                            <option value="hd" id="modalHdOption">HD</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div id="generatedImageContainer" style="display: none;">
                <img id="generatedImage" class="generated-image" alt="Generated image">
                <div class="generated-image-actions">
                    <button class="btn btn-secondary" id="copyImageBtn">
                        <i class="fas fa-copy"></i> <span id="copyToClipboardText">Copy to Clipboard</span>
                    </button>
                    <button class="btn btn-primary" id="downloadImageBtn">
                        <i class="fas fa-download"></i> <span id="downloadImageText">Download</span>
                    </button>
                </div>
            </div>
            
            <div id="imageLoadingContainer" style="display: none;">
                <div class="image-loading">
                    <div class="image-loading-spinner"></div>
                    <div class="image-loading-text" id="imageLoadingText">Generating image...</div>
                </div>
            </div>
            
            <div class="form-buttons">
                <button class="btn btn-secondary" onclick="closeModal('imageModal')" id="imageModalCancelBtn">Cancel</button>
                <button class="btn btn-primary" id="generateImageBtn">
                    <i class="fas fa-magic"></i> <span id="generateImageButtonText">Generate</span>
                </button>
            </div>
        </div>
    </div>
    
    <script>
        // Global variables
        let settings = { 
            api_key: "", 
            provider: "openai", 
            model: "gpt-3.5-turbo",
            custom_api_url: "",
            system_prompt: "You are a helpful assistant.",
            temperature: 0.7,
            max_tokens: null,
            language: "en",
            theme: "light",
            custom_colors: {
                primary: "#4a6cf7",
                secondary: "#6c757d",
                background: "#f8f9fa",
                text: "#212529"
            },
            animations: {
                enabled: true,
                speed: "medium"
            },
            image_generation: {
                model: "dall-e-3",
                size: "1024x1024",
                quality: "standard"
            }
        };
        let translations = {};
        let conversations = [];
        let currentConversationId = null;
        let isWaitingForResponse = false;
        let sidebarCollapsed = false;
        
        // DOM Elements
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const conversationsList = document.getElementById('conversationsList');
        const settingsModal = document.getElementById('settingsModal');
        const imageModal = document.getElementById('imageModal');
        const themeToggleBtn = document.getElementById('themeToggleBtn');
        const formattingToolbar = document.getElementById('formattingToolbar');
        const imageBtn = document.getElementById('imageBtn');
        const newChatBtn = document.getElementById('newChatBtn');
            

              async function sendMessage() {
    const inputField = document.querySelector('.message-input');
    const message = inputField.value.trim();
    if (!message) return;

    // 顯示使用者訊息
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.innerHTML = `<div class="message-content">${message}</div>`;
    document.querySelector('.chat-container').appendChild(userMessage);
    inputField.value = '';

    // 顯示等待中...
    const aiMessage = document.createElement('div');
    aiMessage.className = 'message ai-message';
    aiMessage.innerHTML = `<div class="message-content">正在思考中...</div>`;
    document.querySelector('.chat-container').appendChild(aiMessage);

    try {
      const response = await fetch('/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      const data = await response.json();
      const result = data.response || data.error || '無回覆';
      aiMessage.innerHTML = `<div class="message-content">${result}</div>`;
    } catch (e) {
      aiMessage.innerHTML = `<div class="message-content">❌ 無法連接伺服器</div>`;
    }

    // 捲到底
    document.querySelector('.chat-container').scrollTop = document.querySelector('.chat-container').scrollHeight;
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.send-btn').addEventListener('click', sendMessage);
    document.querySelector('.message-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  });
            
        
        // Initialize the application
        window.addEventListener('load', async function() {
            try {
                // 检查 pywebview API 是否可用
                if (!window.pywebview || !window.pywebview.api) {
                    console.error("PyWebView API not available. Waiting and retrying...");
                    
                    // 显示一个友好的错误消息
                    addMessage("正在初始化应用程序，请稍候...", "error");
                    
                    // 尝试等待 API 加载
                    let attempts = 0;
                    const checkAPI = setInterval(() => {
                        attempts++;
                        console.log(`Checking for PyWebView API (attempt ${attempts})...`);
                        
                        if (window.pywebview && window.pywebview.api) {
                            console.log("PyWebView API now available!");
                            clearInterval(checkAPI);
                            initializeApp();
                        } else if (attempts > 10) {
                            console.error("Failed to load PyWebView API after multiple attempts");
                            clearInterval(checkAPI);
                            addMessage("无法加载应用程序。请尝试重新启动应用程序。", "error");
                        }
                    }, 1000);
                    
                    return;
                }
                
                // 如果 API 可用，继续初始化
                await initializeApp();
            } catch (error) {
                console.error("Error during initialization:", error);
                addMessage(`初始化错误: ${error.message}`, "error");
            }
        });

        // 将原来的初始化代码移到单独的函数中
        async function initializeApp() {
            try {
                // 原来的初始化代码
                // Load settings
                const loadedSettings = await window.pywebview.api.get_settings();
                settings = { ...settings, ...loadedSettings };
                
                // Load translations
                translations = await window.pywebview.api.get_translations(settings.language);
                
                // Update UI language
                updateUILanguage();
                
                // Apply theme
                applyTheme(settings.theme);
                
                // Apply animation settings
                applyAnimationSettings();
                
                // Update UI with loaded settings
                document.getElementById('apiKey').value = settings.api_key || "";
                document.getElementById('provider').value = settings.provider || "openai";
                document.getElementById('model').value = settings.model || "gpt-3.5-turbo";
                document.getElementById('customApiUrl').value = settings.custom_api_url || "";
                document.getElementById('systemPrompt').value = settings.system_prompt || "You are a helpful assistant.";
                document.getElementById('temperature').value = settings.temperature || 0.7;
                document.getElementById('temperatureValue').textContent = settings.temperature || 0.7;
                document.getElementById('maxTokens').value = settings.max_tokens || "";
                document.getElementById('enableAnimations').checked = settings.animations?.enabled !== false;
                document.getElementById('animationSpeed').value = settings.animations?.speed || "medium";
                
                // Update image generation settings
                document.getElementById('imageModel').value = settings.image_generation?.model || "dall-e-3";
                document.getElementById('imageSize').value = settings.image_generation?.size || "1024x1024";
                document.getElementById('imageQuality').value = settings.image_generation?.quality || "standard";
                document.getElementById('modalImageSize').value = settings.image_generation?.size || "1024x1024";
                document.getElementById('modalImageQuality').value = settings.image_generation?.quality || "standard";
                
                // Update custom colors
                if (settings.custom_colors) {
                    document.getElementById('primaryColor').value = settings.custom_colors.primary || "#4a6cf7";
                    document.getElementById('secondaryColor').value = settings.custom_colors.secondary || "#6c757d";
                    document.getElementById('backgroundColor').value = settings.custom_colors.background || "#f8f9fa";
                    document.getElementById('textColor').value = settings.custom_colors.text || "#212529";
                }
                
                // Update theme selector
                const themeOptions = document.querySelectorAll('.theme-option');
                themeOptions.forEach(option => {
                    option.classList.remove('active');
                    if (option.dataset.theme === settings.theme) {
                        option.classList.add('active');
                    }
                });
                
                if (settings.theme === 'custom') {
                    document.getElementById('customColorsContainer').style.display = 'block';
                }
                
                // Update language buttons
                updateLanguageButtons();
                
                toggleProviderOptions();
                
                // Load conversations
                await loadConversations();
                
                // Create a new conversation if none exists
                if (conversations.length === 0) {
                    await createNewConversation();
                } else {
                    // Select the most recent conversation
                    selectConversation(conversations[0].id);
                }
                
                // Initialize event listeners
                initEventListeners();
                
                // Show welcome message
                if (chatContainer.children.length === 0) {
                    addMessage(translations.welcome, "ai");
                }
                
                // Show settings if no API key is set
                if (!settings.api_key) {
                    openModal('settingsModal');
                }
            } catch (error) {
                console.error("Error initializing application:", error);
                addMessage(translations.errorLoadingSettings || "Error loading settings. Please try again.", "error");
            }
        }
        
        // Initialize event listeners
        function initEventListeners() {
            // Message input
            messageInput.addEventListener('input', function() {
                autoResizeTextarea(this);
                sendButton.disabled = this.value.trim() === '';
            });
            
            messageInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (!sendButton.disabled) {
                        sendMessage();
                    }
                }
            });
            
            // Send button
            sendButton.addEventListener('click', sendMessage);
            
            // Sidebar toggle
            sidebarToggle.addEventListener('click', toggleSidebar);
            
            // Theme toggle
            themeToggleBtn.addEventListener('click', toggleTheme);
            
            // Settings button
            document.getElementById('settingsBtn').addEventListener('click', function() {
                openModal('settingsModal');
            });
            
            // New chat button
            newChatBtn.addEventListener('click', createNewConversation);
            
            // Image button
            imageBtn.addEventListener('click', function() {
                openModal('imageModal');
            });
            
            // Generate image button
            document.getElementById('generateImageBtn').addEventListener('click', generateImage);
            
            // Theme options
            document.querySelectorAll('.theme-option').forEach(option => {
                option.addEventListener('click', function() {
                    const theme = this.dataset.theme;
                    document.querySelectorAll('.theme-option').forEach(opt => opt.classList.remove('active'));
                    this.classList.add('active');
                    
                    if (theme === 'custom') {
                        document.getElementById('customColorsContainer').style.display = 'block';
                    } else {
                        document.getElementById('customColorsContainer').style.display = 'none';
                    }
                    
                    applyTheme(theme);
                });
            });
            
            // Animation toggle
            document.getElementById('enableAnimations').addEventListener('change', function() {
                const animationSpeedContainer = document.getElementById('animationSpeedContainer');
                if (this.checked) {
                    animationSpeedContainer.style.display = 'block';
                } else {
                    animationSpeedContainer.style.display = 'none';
                }
                
                applyAnimationSettings();
            });
            
            // Animation speed
            document.getElementById('animationSpeed').addEventListener('change', applyAnimationSettings);
            
            // Formatting buttons
            document.querySelectorAll('.formatting-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const format = this.dataset.format;
                    applyFormatting(format);
                });
            });
            
            // Copy image button
            document.getElementById('copyImageBtn').addEventListener('click', copyImageToClipboard);
            
            // Download image button
            document.getElementById('downloadImageBtn').addEventListener('click', downloadGeneratedImage);
            
            // Language buttons
            document.querySelectorAll('.language-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const langCode = this.getAttribute('onclick').match(/'([^']+)'/)[1];
                    changeLanguage(langCode);
                });
            });
        }
        
        // Auto-resize textarea
        function autoResizeTextarea(textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
        }
        
        // Toggle sidebar
        function toggleSidebar() {
            sidebar.classList.toggle('collapsed');
            sidebarToggle.classList.toggle('active');
            sidebarCollapsed = !sidebarCollapsed;
        }
        
        // Toggle theme
        function toggleTheme() {
            const currentTheme = document.body.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            applyTheme(newTheme);
            
            // Update theme icon
            const themeIcon = themeToggleBtn.querySelector('i');
            themeIcon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
            
            // Update theme option in settings
            document.querySelectorAll('.theme-option').forEach(opt => opt.classList.remove('active'));
            document.querySelector(`.theme-option[data-theme="${newTheme}"]`).classList.add('active');
            
            // Hide custom colors if not custom theme
            document.getElementById('customColorsContainer').style.display = 'none';
        }
        
        // Apply theme
        function applyTheme(theme) {
            if (theme === 'custom') {
                const customColors = settings.custom_colors || {
                    primary: "#4a6cf7",
                    secondary: "#6c757d",
                    background: "#f8f9fa",
                    text: "#212529"
                };
                
                document.documentElement.style.setProperty('--primary-color', customColors.primary);
                document.documentElement.style.setProperty('--primary-hover', adjustColor(customColors.primary, -20));
                document.documentElement.style.setProperty('--secondary-color', customColors.secondary);
                document.documentElement.style.setProperty('--background-color', customColors.background);
                document.documentElement.style.setProperty('--text-color', customColors.text);
                
                // Set card background based on background color
                const isDark = isColorDark(customColors.background);
                document.documentElement.style.setProperty('--card-bg-color', isDark ? adjustColor(customColors.background, 20) : adjustColor(customColors.background, -10));
                
                // Set border color
                document.documentElement.style.setProperty('--border-color', isDark ? adjustColor(customColors.background, 40) : adjustColor(customColors.background, -20));
                
                // Set message colors
                document.documentElement.style.setProperty('--message-user-bg', customColors.primary);
                document.documentElement.style.setProperty('--message-user-color', '#ffffff');
                document.documentElement.style.setProperty('--message-ai-bg', isDark ? adjustColor(customColors.background, 20) : adjustColor(customColors.background, -5));
                document.documentElement.style.setProperty('--message-ai-color', customColors.text);
                
                // Set code and quote backgrounds
                document.documentElement.style.setProperty('--code-bg', isDark ? adjustColor(customColors.background, 10) : adjustColor(customColors.background, -10));
                document.documentElement.style.setProperty('--quote-bg', isDark ? adjustColor(customColors.background, 10) : adjustColor(customColors.background, -10));
                document.documentElement.style.setProperty('--quote-border', isDark ? adjustColor(customColors.background, 40) : adjustColor(customColors.background, -20));
                
                // Set scrollbar colors
                document.documentElement.style.setProperty('--scrollbar-thumb', isDark ? adjustColor(customColors.background, 60) : adjustColor(customColors.background, -30));
                document.documentElement.style.setProperty('--scrollbar-track', isDark ? adjustColor(customColors.background, 20) : adjustColor(customColors.background, -5));
                
                document.body.removeAttribute('data-theme');
            } else {
                document.body.setAttribute('data-theme', theme);
                document.documentElement.style.removeProperty('--primary-color');
                document.documentElement.style.removeProperty('--primary-hover');
                document.documentElement.style.removeProperty('--secondary-color');
                document.documentElement.style.removeProperty('--background-color');
                document.documentElement.style.removeProperty('--card-bg-color');
                document.documentElement.style.removeProperty('--text-color');
                document.documentElement.style.removeProperty('--border-color');
                document.documentElement.style.removeProperty('--message-user-bg');
                document.documentElement.style.removeProperty('--message-user-color');
                document.documentElement.style.removeProperty('--message-ai-bg');
                document.documentElement.style.removeProperty('--message-ai-color');
                document.documentElement.style.removeProperty('--code-bg');
                document.documentElement.style.removeProperty('--code-color');
                document.documentElement.style.removeProperty('--quote-bg');
                document.documentElement.style.removeProperty('--quote-border');
                document.documentElement.style.removeProperty('--scrollbar-thumb');
                document.documentElement.style.removeProperty('--scrollbar-track');
            }
            
            // Update theme icon
            const themeIcon = themeToggleBtn.querySelector('i');
            themeIcon.className = theme === 'dark' || (theme === 'custom' && isColorDark(settings.custom_colors?.background || "#f8f9fa")) ? 'fas fa-sun' : 'fas fa-moon';
            
            // Save theme setting
            settings.theme = theme;
        }
        
        // Apply animation settings
        function applyAnimationSettings() {
            const enabled = document.getElementById('enableAnimations').checked;
            const speed = document.getElementById('animationSpeed').value;
            
            let speedValue;
            switch (speed) {
                case 'slow':
                    speedValue = '0.5s';
                    break;
                case 'fast':
                    speedValue = '0.2s';
                    break;
                default:
                    speedValue = '0.3s';
            }
            
            document.documentElement.style.setProperty('--animation-speed', enabled ? speedValue : '0s');
            
            // Save animation settings
            settings.animations = {
                enabled: enabled,
                speed: speed
            };
        }
        
        // Helper function to adjust color brightness
        function adjustColor(color, amount) {
            const clamp = (val) => Math.min(255, Math.max(0, val));
            
            // Convert hex to RGB
            let hex = color.replace('#', '');
            if (hex.length === 3) {
                hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
            }
            
            let r = parseInt(hex.substring(0, 2), 16);
            let g = parseInt(hex.substring(2, 4), 16);
            let b = parseInt(hex.substring(4, 6), 16);
            
            // Adjust brightness
            r = clamp(r + amount);
            g = clamp(g + amount);
            b = clamp(b + amount);
            
            // Convert back to hex
            return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
        }
        
        // Helper function to determine if a color is dark
        function isColorDark(color) {
            // Convert hex to RGB
            let hex = color.replace('#', '');
            if (hex.length === 3) {
                hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
            }
            
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);
            
            // Calculate luminance
            const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
            
            return luminance < 0.5;
        }
        
        // Update UI language based on current translations
        function updateUILanguage() {
            if (!translations) return;
            
            // Update welcome message if it hasn't been replaced yet
            if (chatContainer.children.length === 0) {
                addMessage(translations.welcome, "ai");
            }
            
            // Update placeholders
            messageInput.placeholder = translations.typeMessage;
            
            // Update buttons
            document.getElementById('sendButton').title = translations.send;
            document.getElementById('settingsBtn').title = translations.settings;
            document.getElementById('newChatText').textContent = translations.newChat;
            document.getElementById('settingsTitle').textContent = translations.settings;
            document.getElementById('saveBtn').textContent = translations.save;
            document.getElementById('cancelBtn').textContent = translations.cancel;
            
            // Update tabs
            document.getElementById('generalTabBtn').textContent = translations.general;
            document.getElementById('advancedTabBtn').textContent = translations.advanced;
            document.getElementById('appearanceTabBtn').textContent = translations.appearance;
            
            // Update form labels
            document.getElementById('apiKeyLabel').textContent = translations.apiKey;
            document.getElementById('apiKeyWarning').textContent = translations.apiKeyWarning;
            document.getElementById('providerLabel').textContent = translations.provider;
            document.getElementById('openaiOption').textContent = translations.openai;
            document.getElementById('customOption').textContent = translations.custom;
            document.getElementById('modelLabel').textContent = translations.model;
            document.getElementById('modelInfo').textContent = translations.modelInfo;
            document.getElementById('customApiUrlLabel').textContent = translations.customApiUrl;
            document.getElementById('customApiUrlInfo').textContent = translations.customApiUrlInfo;
            document.getElementById('systemPromptLabel').textContent = translations.systemPrompt;
            document.getElementById('systemPromptInfo').textContent = translations.systemPromptInfo;
            document.getElementById('temperatureLabel').textContent = translations.temperature;
            document.getElementById('temperatureInfo').textContent = translations.temperatureInfo;
            document.getElementById('currentText').textContent = translations.current;
            document.getElementById('maxTokensLabel').textContent = translations.maxTokens;
            document.getElementById('maxTokensInfo').textContent = translations.maxTokensInfo;
            
            // Update theme labels
            document.getElementById('themeLabel').textContent = translations.theme;
            document.getElementById('lightThemeLabel').textContent = translations.light;
            document.getElementById('darkThemeLabel').textContent = translations.dark;
            document.getElementById('customThemeLabel').textContent = translations.custom;
            document.getElementById('customColorsLabel').textContent = translations.customColors;
            document.getElementById('primaryColorLabel').textContent = translations.primary;
            document.getElementById('secondaryColorLabel').textContent = translations.secondary;
            document.getElementById('backgroundColorLabel').textContent = translations.background;
            document.getElementById('textColorLabel').textContent = translations.textColor;
            
            // Update animation labels
            document.getElementById('animationsLabel').textContent = translations.animations;
            document.getElementById('enableAnimationsLabel').textContent = translations.enableAnimations;
            
            // Update image generation labels
            document.getElementById('imageGenerationLabel').textContent = translations.imageGeneration;
            document.getElementById('imageModelLabel').textContent = translations.imageModel;
            document.getElementById('imageSizeLabel').textContent = translations.imageSize;
            document.getElementById('imageQualityLabel').textContent = translations.imageQuality;
            document.getElementById('standardOption').textContent = translations.standard;
            document.getElementById('hdOption').textContent = translations.hd;
            
            // Update image modal
            document.getElementById('imageGenerationTitle').textContent = translations.imageGeneration;
            document.getElementById('imagePromptLabel').textContent = translations.imagePrompt;
            document.getElementById('modalImageSizeLabel').textContent = translations.imageSize;
            document.getElementById('modalImageQualityLabel').textContent = translations.imageQuality;
            document.getElementById('modalStandardOption').textContent = translations.standard;
            document.getElementById('modalHdOption').textContent = translations.hd;
            document.getElementById('generateImageButtonText').textContent = translations.generateImageButton;
            document.getElementById('imageModalCancelBtn').textContent = translations.cancel;
            document.getElementById('copyToClipboardText').textContent = translations.copyToClipboard;
        }

        // Update language buttons to show active state
        function updateLanguageButtons() {
            const buttons = document.querySelectorAll('.language-btn');
            buttons.forEach(button => {
                button.classList.remove('active');
            });
            
            const activeButton = document.querySelector(`.language-btn[onclick="changeLanguage('${settings.language}')"]`);
            if (activeButton) {
                activeButton.classList.add('active');
            }
        }
        
        // Change language
        async function changeLanguage(langCode) {
            try {
                // Update settings with new language
                settings.language = langCode;
                
                // Get translations for the new language
                translations = await window.pywebview.api.get_translations(langCode);
                
                // Update UI language
                updateUILanguage();
                
                // Update language buttons
                updateLanguageButtons();
            } catch (error) {
                console.error("Error changing language:", error);
            }
        }
        
        // Open modal
        function openModal(modalId) {
            document.getElementById(modalId).style.display = "flex";
        }
        
        // Close modal
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = "none";
            
            // Reset image generation modal
            if (modalId === 'imageModal') {
                document.getElementById('imagePrompt').value = '';
                document.getElementById('generatedImageContainer').style.display = 'none';
                document.getElementById('imageLoadingContainer').style.display = 'none';
            }
        }
        
        // Switch between settings tabs
        function switchTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName + 'Tab').classList.add('active');
            document.querySelector(`.tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
        }
        
        // Toggle provider-specific options
        function toggleProviderOptions() {
            const provider = document.getElementById('provider').value;
            
            if (provider === "openai") {
                document.getElementById('openaiOptions').style.display = "block";
                document.getElementById('customOptions').style.display = "none";
            } else if (provider === "custom") {
                document.getElementById('openaiOptions').style.display = "none";
                document.getElementById('customOptions').style.display = "block";
            }
        }
        
        // Update temperature value display
        function updateTemperatureValue() {
            const value = document.getElementById('temperature').value;
            document.getElementById('temperatureValue').textContent = value;
        }
        
        // Save settings
        async function saveSettings() {
            const newSettings = {
                api_key: document.getElementById('apiKey').value,
                provider: document.getElementById('provider').value,
                model: document.getElementById('model').value,
                custom_api_url: document.getElementById('customApiUrl').value,
                system_prompt: document.getElementById('systemPrompt').value,
                temperature: parseFloat(document.getElementById('temperature').value),
                max_tokens: document.getElementById('maxTokens').value ? parseInt(document.getElementById('maxTokens').value) : null,
                language: settings.language,
                theme: settings.theme,
                custom_colors: {
                    primary: document.getElementById('primaryColor').value,
                    secondary: document.getElementById('secondaryColor').value,
                    background: document.getElementById('backgroundColor').value,
                    text: document.getElementById('textColor').value
                },
                animations: {
                    enabled: document.getElementById('enableAnimations').checked,
                    speed: document.getElementById('animationSpeed').value
                },
                image_generation: {
                    model: document.getElementById('imageModel').value,
                    size: document.getElementById('imageSize').value,
                    quality: document.getElementById('imageQuality').value
                }
            };
            
            try {
                await window.pywebview.api.save_settings(newSettings);
                settings = newSettings;
                closeModal('settingsModal');
                
                // Apply theme and animation settings
                applyTheme(settings.theme);
                applyAnimationSettings();
            } catch (error) {
                console.error("Error saving settings:", error);
                alert("Failed to save settings. Please try again.");
            }
        }
        
        // Load conversations
        async function loadConversations() {
            try {
                conversations = await window.pywebview.api.get_conversations();
                renderConversationsList();
            } catch (error) {
                console.error("Error loading conversations:", error);
            }
        }
        
        // Render conversations list
        function renderConversationsList() {
            conversationsList.innerHTML = '';
            
            if (conversations.length === 0) {
                return;
            }
            
            // Group conversations by date
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);
            
            const todayConversations = [];
            const yesterdayConversations = [];
            const olderConversations = [];
            
            conversations.forEach(conversation => {
                const date = new Date(conversation.updated_at);
                
                if (date >= today) {
                    todayConversations.push(conversation);
                } else if (date >= yesterday) {
                    yesterdayConversations.push(conversation);
                } else {
                    olderConversations.push(conversation);
                }
            });
            
            // Render today's conversations
            if (todayConversations.length > 0) {
                const todayGroup = document.createElement('div');
                todayGroup.className = 'conversation-group';
                
                const todayTitle = document.createElement('div');
                todayTitle.className = 'conversation-group-title';
                todayTitle.textContent = translations.today || 'Today';
                todayGroup.appendChild(todayTitle);
                
                todayConversations.forEach(conversation => {
                    todayGroup.appendChild(createConversationItem(conversation));
                });
                
                conversationsList.appendChild(todayGroup);
            }
            
            // Render yesterday's conversations
            if (yesterdayConversations.length > 0) {
                const yesterdayGroup = document.createElement('div');
                yesterdayGroup.className = 'conversation-group';
                
                const yesterdayTitle = document.createElement('div');
                yesterdayTitle.className = 'conversation-group-title';
                yesterdayTitle.textContent = translations.yesterday || 'Yesterday';
                yesterdayGroup.appendChild(yesterdayTitle);
                
                yesterdayConversations.forEach(conversation => {
                    yesterdayGroup.appendChild(createConversationItem(conversation));
                });
                
                conversationsList.appendChild(yesterdayGroup);
            }
            
            // Render older conversations
            if (olderConversations.length > 0) {
                const olderGroup = document.createElement('div');
                olderGroup.className = 'conversation-group';
                
                const olderTitle = document.createElement('div');
                olderTitle.className = 'conversation-group-title';
                olderTitle.textContent = translations.previousDays || 'Previous Days';
                olderGroup.appendChild(olderTitle);
                
                olderConversations.forEach(conversation => {
                    olderGroup.appendChild(createConversationItem(conversation));
                });
                
                conversationsList.appendChild(olderGroup);
            }
        }
        
        // Create conversation item
        function createConversationItem(conversation) {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            if (conversation.id === currentConversationId) {
                item.classList.add('active');
            }
            
            const icon = document.createElement('div');
            icon.className = 'conversation-item-icon';
            icon.innerHTML = '<i class="fas fa-comment"></i>';
            
            const title = document.createElement('div');
            title.className = 'conversation-item-title';
            title.textContent = conversation.name || (translations.untitledConversation || 'Untitled Conversation');
            
            item.appendChild(icon);
            item.appendChild(title);
            
            // Add actions
            const actions = document.createElement('div');
            actions.className = 'conversation-item-actions';
            
            const renameBtn = document.createElement('button');
            renameBtn.className = 'conversation-action';
            renameBtn.innerHTML = '<i class="fas fa-edit"></i>';
            renameBtn.title = translations.renameConversation || 'Rename Conversation';
            renameBtn.onclick = (e) => {
                e.stopPropagation();
                renameConversation(conversation.id);
            };
            
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'conversation-action';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.title = translations.deleteConversation || 'Delete Conversation';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteConversation(conversation.id);
            };
            
            actions.appendChild(renameBtn);
            actions.appendChild(deleteBtn);
            
            item.appendChild(actions);
            
            // Add click event
            item.addEventListener('click', () => {
                selectConversation(conversation.id);
            });
            
            return item;
        }
        
        // Create new conversation
        async function createNewConversation() {
            try {
                const newConversation = await window.pywebview.api.create_conversation(translations.untitledConversation || 'Untitled Conversation');
                conversations.unshift(newConversation);
                renderConversationsList();
                selectConversation(newConversation.id);
            } catch (error) {
                console.error("Error creating new conversation:", error);
            }
        }
        
        // Select conversation
        function selectConversation(conversationId) {
            currentConversationId = conversationId;
            
            // Update active state in sidebar
            document.querySelectorAll('.conversation-item').forEach(item => {
                item.classList.remove('active');
            });
            
            const selectedItem = Array.from(document.querySelectorAll('.conversation-item')).find(item => {
                const titleEl = item.querySelector('.conversation-item-title');
                const conversation = conversations.find(c => c.id === conversationId);
                return titleEl.textContent === (conversation.name || (translations.untitledConversation || 'Untitled Conversation'));
            });
            
            if (selectedItem) {
                selectedItem.classList.add('active');
            }
            
            // Load conversation messages
            loadConversationMessages(conversationId);
            
            // Close sidebar on mobile
            if (window.innerWidth <= 768) {
                sidebar.classList.add('collapsed');
                sidebarToggle.classList.add('active');
                sidebarCollapsed = true;
            }
        }
        
        // Load conversation messages
        function loadConversationMessages(conversationId) {
            chatContainer.innerHTML = '';
            
            const conversation = conversations.find(c => c.id === conversationId);
            if (!conversation) return;
            
            const messages = conversation.messages || [];
            
            if (messages.length === 0) {
                // Show welcome message
                addMessage(translations.welcome, "ai");
            } else {
                // Render messages
                messages.forEach(message => {
                    addMessage(message.content, message.role === 'user' ? 'user' : 'ai', false);
                });
            }
            
            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Rename conversation
        function renameConversation(conversationId) {
            const conversation = conversations.find(c => c.id === conversationId);
            if (!conversation) return;
            
            const newName = prompt(translations.conversationName || 'Conversation Name', conversation.name);
            if (newName === null) return;
            
            window.pywebview.api.update_conversation(conversationId, { name: newName }).then(() => {
                conversation.name = newName;
                renderConversationsList();
            }).catch(error => {
                console.error("Error renaming conversation:", error);
            });
        }
        
        // Delete conversation
        function deleteConversation(conversationId) {
            if (!confirm(translations.deleteConversation + '?')) return;
            
            window.pywebview.api.delete_conversation(conversationId).then(() => {
                conversations = conversations.filter(c => c.id !== conversationId);
                
                if (currentConversationId === conversationId) {
                    if (conversations.length > 0) {
                        selectConversation(conversations[0].id);
                    } else {
                        createNewConversation();
                    }
                }
                
                renderConversationsList();
            }).catch(error => {
                console.error("Error deleting conversation:", error);
            });
        }
        
        // Add message to chat
        function addMessage(text, type = "ai", SaveToHistory = false) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message');
            
            if (type === "user") {
                messageElement.classList.add('user-message');
                if (SaveToHistory && currentConversationId) {
                    const message = {
                        role: "user",
                        content: text
                    };
                    window.pywebview.api.add_message_to_conversation(currentConversationId, message);
                }
            } else if (type === "ai") {
                messageElement.classList.add('ai-message');
                if (SaveToHistory && currentConversationId) {
                    const message = {
                        role: "assistant",
                        content: text
                    };
                    window.pywebview.api.add_message_to_conversation(currentConversationId, message);
                }
            } else if (type === "error") {
                messageElement.classList.add('error-message');
            }
            
            const messageContent = document.createElement('div');
            messageContent.classList.add('message-content');
            
            if (type === "ai" || type === "error") {
                // Process markdown for AI messages
                messageContent.innerHTML = marked.parse(text);
                
                // Add copy button to code blocks
                messageContent.querySelectorAll('pre').forEach(pre => {
                    const copyBtn = document.createElement('button');
                    copyBtn.className = 'copy-code-btn';
                    copyBtn.textContent = 'Copy';
                    copyBtn.onclick = function() {
                        const code = pre.querySelector('code').textContent;
                        navigator.clipboard.writeText(code).then(() => {
                            copyBtn.textContent = 'Copied!';
                            setTimeout(() => {
                                copyBtn.textContent = 'Copy';
                            }, 2000);
                        });
                    };
                    pre.appendChild(copyBtn);
                });
                
                // Highlight code blocks
                messageContent.querySelectorAll('pre code').forEach(block => {
                    hljs.highlightElement(block);
                });
                
                // Render math expressions
                renderMathInElement(messageContent, {
                    delimiters: [
                        {left: '$$', right: '$$', display: true},
                        {left: '$', right: '$', display: false}
                    ]
                });
            } else {
                // Plain text for user messages
                messageContent.textContent = text;
            }
            
            messageElement.appendChild(messageContent);
            chatContainer.appendChild(messageElement);
            
            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            return messageElement;
        }
        
        // Add typing indicator
        function addTypingIndicator() {
            const indicator = document.createElement('div');
            indicator.classList.add('typing-indicator');
            
            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('div');
                dot.classList.add('typing-dot');
                indicator.appendChild(dot);
            }
            
            chatContainer.appendChild(indicator);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            return indicator;
        }
        
        // Send message
        async function sendMessage() {
            const message = messageInput.value.trim();
            
            if (!message || isWaitingForResponse) return;
            
            // Clear input
            messageInput.value = "";
            messageInput.style.height = 'auto';
            sendButton.disabled = true;
            
            // Add user message to chat
            addMessage(message, "user");
            
            // Check if API key is set
            if (!settings.api_key) {
                addMessage(translations.setApiKeyError, "error");
                openModal('settingsModal');
                return;
            }
            
            // Check if conversation is selected
            if (!currentConversationId) {
                await createNewConversation();
            }
            
            // Disable input while waiting for response
            isWaitingForResponse = true;
            
            // Show typing indicator
            const typingIndicator = addTypingIndicator();
            
            try {
                // Send message to backend
                const response = await window.pywebview.api.send_message(currentConversationId, message);
                
                // Remove typing indicator
                typingIndicator.remove();
                
                // Handle response
                if (response.error) {
                    addMessage(response.error, "error");
                } else {
                    // 强制浏览器重绘
                    window.requestAnimationFrame(() => {
                        // 添加一个小延迟
                        setTimeout(() => {
                            // 强制重新计算布局
                            chatContainer.style.display = 'none';
                            void chatContainer.offsetHeight; // 触发重排
                            chatContainer.style.display = 'flex';
                            
                            // 然后加载对话消息
                            loadConversationMessages(currentConversationId);
                        }, 50);
                    });
                    
                    // Update conversation in the list
                    const conversation = conversations.find(c => c.id === currentConversationId);
                    if (conversation) {
                        conversation.updated_at = new Date().toISOString();
                        renderConversationsList();
                    }
                }
            } catch (error) {
                console.error("Error sending message:", error);
                typingIndicator.remove();
                addMessage(translations.errorSendingMessage, "error");
            } finally {
                // Re-enable input
                isWaitingForResponse = false;
                sendButton.disabled = false;
                messageInput.focus();
            }
        }
        
        // Apply formatting to message input
        function applyFormatting(format) {
            const input = messageInput;
            const start = input.selectionStart;
            const end = input.selectionEnd;
            const selectedText = input.value.substring(start, end);
            let replacement = '';
            
            switch (format) {
                case 'bold':
                    replacement = `**${selectedText}**`;
                    break;
                case 'italic':
                    replacement = `*${selectedText}*`;
                    break;
                case 'code':
                    replacement = `\`${selectedText}\``;
                    break;
                case 'codeblock':
                    replacement = `\`\`\`\n${selectedText}\n\`\`\``;
                    break;
                case 'heading1':
                    replacement = `# ${selectedText}`;
                    break;
                case 'heading2':
                    replacement = `## ${selectedText}`;
                    break;
                case 'heading3':
                    replacement = `### ${selectedText}`;
                    break;
                case 'quote':
                    replacement = `> ${selectedText}`;
                    break;
                case 'list':
                    replacement = `- ${selectedText}`;
                    break;
                case 'link':
                    replacement = `[${selectedText}](url)`;
                    break;
            }
            
            input.value = input.value.substring(0, start) + replacement + input.value.substring(end);
            input.selectionStart = start + replacement.length;
            input.selectionEnd = start + replacement.length;
            input.focus();
            
            // Trigger input event to resize textarea
            const event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
        }
        
        // Generate image
        async function generateImage() {
            const prompt = document.getElementById('imagePrompt').value.trim();
            if (!prompt) return;
            
            // Show loading indicator
            document.getElementById('generatedImageContainer').style.display = 'none';
            document.getElementById('imageLoadingContainer').style.display = 'block';
            document.getElementById('generateImageBtn').disabled = true;
            
            try {
                // Update image generation settings
                settings.image_generation.size = document.getElementById('modalImageSize').value;
                settings.image_generation.quality = document.getElementById('modalImageQuality').value;
                
                // Send request to backend
                const response = await window.pywebview.api.generate_image(prompt);
                
                if (response.error) {
                    alert(response.error);
                } else {
                    // Display the generated image
                    const imageElement = document.getElementById('generatedImage');
                    imageElement.src = `data:image/png;base64,${response.image}`;
                    
                    // Store image data for download
                    imageElement.dataset.imageData = response.image;
                    imageElement.dataset.prompt = prompt;
                    
                    document.getElementById('generatedImageContainer').style.display = 'block';
                    
                    // Add image to chat
                    const imageMarkdown = `![${prompt}](data:image/png;base64,${response.image})`;
                    addMessage(`**${translations.imageGeneration || 'Image Generation'}:** ${prompt}\n\n${imageMarkdown}`, "ai");
                }
            } catch (error) {
                console.error("Error generating image:", error);
                alert(translations.imageGenerationError || "Failed to generate image. Please try again.");
            } finally {
                document.getElementById('imageLoadingContainer').style.display = 'none';
                document.getElementById('generateImageBtn').disabled = false;
            }
        }
        
        // Copy image to clipboard
        function copyImageToClipboard() {
            const imageElement = document.getElementById('generatedImage');
            const imageData = imageElement.dataset.imageData;
            
            if (!imageData) return;
            
            // Create a canvas element
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = function() {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob(function(blob) {
                    // Create a ClipboardItem
                    const item = new ClipboardItem({ 'image/png': blob });
                    
                    // Write to clipboard
                    navigator.clipboard.write([item]).then(function() {
                        alert(translations.copied || 'Copied!');
                    }, function(err) {
                        console.error('Could not copy image: ', err);
                    });
                });
            };
            
            img.src = `data:image/png;base64,${imageData}`;
        }
        
        // Download generated image
        function downloadGeneratedImage() {
            const imageElement = document.getElementById('generatedImage');
            const imageData = imageElement.dataset.imageData;
            const prompt = imageElement.dataset.prompt || 'generated-image';
            
            if (!imageData) return;
            
            // Create download link
            const link = document.createElement('a');
            link.href = `data:image/png;base64,${imageData}`;
            link.download = `${prompt.substring(0, 30).replace(/[^a-z0-9]/gi, '-')}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
</body>
</html>''')

# 在 webview.create_window 行之前添加以下调试信息
print("Creating window with HTML path:", html_path)
print("API object initialized:", app is not None)

# 修改 webview.create_window 行，确保正确设置 js_api 参数
api = API()
from bottle import route, request, response

@route('/send_message', method='POST')
def send_message():
    data = request.json
    text = data.get('message')
    if not text:
        return {'error': 'Empty message'}
    
    if not api.conversations:
        api.create_conversation()

    conv_id = api.conversations[0]['id']
    result = api.send_message(conv_id, text)
    response.content_type = 'application/json'
    return result


webview.create_window('AI Chat Application', html_path, js_api=api, width=1000, height=700)

# 修改 webview.start 行，添加更多调试信息
print("Starting webview...")
webview.start(debug=True, http_server=True, gui='edgechromium')