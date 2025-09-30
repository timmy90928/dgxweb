
from application import *

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Ollama API 的基礎 URL
OLLAMA_API_URL = "http://140.123.106.226:11434/api/generate"

# 載入你想要使用的模型名稱
OLLAMA_MODEL = "gpt-oss:20b"

# 新增一個固定的 system prompt，要求輸出 Markdown 格式
SYSTEM_PROMPT = "你的回應以markdown的格式輸出, 並以繁體中文輸出"

@chat_bp.route('/')
def index():
    """
    提供一個簡單的聊天介面 HTML 頁面
    """
    return render_template('chat.html')

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    處理聊天請求，將訊息發送給 Ollama 並返回其回應
    """
    try:
        # 從 POST 請求中取得使用者訊息
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # 準備要發送給 Ollama 的 JSON 數據
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": SYSTEM_PROMPT+user_message,
            "stream": False  # 如果設為 True，你需要處理串流回應
        }

        # 將請求發送給 Ollama API
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status() # 檢查是否有 HTTP 錯誤

        ollama_response_data = response.json()
        
        # 從 Ollama 的回應中提取生成的內容
        generated_content = ollama_response_data.get('response', '...')

        # 返回給前端的 JSON 格式回應
        return jsonify({'response': generated_content})

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return jsonify({'error': f"無法連線至 Ollama API: {e}"}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f"發生未知錯誤: {e}"}), 500