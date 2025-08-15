DGX Web
=======
架設在AI實驗室的NVIDIA DGXS-V100的網頁

使用
===

### 連線 (SSH)
以下為 `~/.ssh/config`，密碼親自交接

```SSH Config
Host DGX
  HostName 140.123.106.239
  User lab120
  Port 22
  IdentityFile ~/.ssh/dgx
```

其他的詳細使用方法可參考我的筆記: [SSH筆記](https://hackmd.io/@timmy90928/ssh)

### 開機
使用 tmux, 如下所示
```bash
tmux new -s dgxweb -c ~/dgxweb/
sudo python3 app.py
```

###  關機
安全的物理關機
```bash
sudo shutdown -h now 
```

安裝與執行
---------
若是第一次使用請先執行此節

### 安裝依賴環境
依照自己的需求備註

```bash
pip install -r requirements.txt

# Update requirements.txt
pip freeze > requirements.txt
```

### 執行
```bash
cd dgxweb
sudo python3 app.py
```

Tmux (Server 持久化)
-------------------
- Tmux 結構: Session -> Window -> Pane
- 在 Tmux 中使用快速鍵, 都需要先按 `Ctrl+b`

#### 創建新 Session 並執行 Server
```bash
tmux new -s dgxweb -c ~/dgxweb/
sudo python3 app.py

# 離開 Session ([Ctrl+b]+ [d])
tmux detach
```

#### 列出所有當前正在運行的 Tmux Sessions
```bash
tmux ls
# Output: dgxweb: 1 windows (created Fri Aug 15 21:59:56 2025)
```

#### 重新連線到一個已存在的 Session
```bash
tmux attach -t dgxweb
```

#### 終止與關閉 Session
```bash
tmux kill-session -t dgxweb

#! 終止所有正在運行的 Tmux sessions
tmux kill-server
```

檔案介紹
-------
```bash
LAB120
├─ dgxweb       # This system
|  ├─ routes
|  |  └─ ...
|  ├─ script
|  |  └─ ...
|  ├─ static
|  |  └─ ...
|  ├─ templates
|  |  └─ ...
|  ├─ utils
|  |  └─ ...
|  ├─ dgx.db    # Database (please back up regularly)
|  └─ app.py    # Main program
├─ .ssh         # Storing SSH Public Key
|  └─ authorized_keys
└─ user_data    # All User Workspaces
   ├─ 613415071
   └─ ...
```

API
===

[GET] /api/
-----------
連線測試, 以下所有回傳結果都會在 `response` 裡

### Response 200 (application/json)
```json
{
    "method": "GET",
    "status_code": 200,
    "status": "OK",
    "time": "2025-08-05 10:52:00",
    "timestamp": 1754362320.0,
    "response": "Connection test successful."
}
```

[GET] /api/info
---------------
取得 Docker 系統資訊

[GET] /api/df
-------------
取得 Docker 磁碟使用量


[POST] /api/sendemail
---------------------

寄送電子郵件

### Request (application/json)
```json
{
    "Subject": "Title",
    "From": "AILAB",    // Optional(default: AILAB DGX API)
    "To": "weiwen@alum.ccu.edu.tw", // Union[str, list]
    "Cc": [""],     // Union[str, list]
    "Bcc": [""],    // Union[str, list]
    "Text": [
        "第一段", 
        "第二段"
    ]
}
```

[POST] /api/auth
---------------------
身份驗證

### Request (application/json)
```json
{
    "username": "...",
    "password": "..."
}
```

### Response 200 (application/json)
```json
{
    "method": "POST",
    "status_code": 200,
    "status": "OK",
    "time": "2025-08-05 11:20:58",
    "timestamp": 1754364058.0,
    "response": {
        "name": "吳維文",
        "email": "weiwen@alum.ccu.edu.tw"
    }
}
```

### Response 401 (application/json)
```json
{
    "method": "POST",
    "status_code": 401,
    "status": "Unauthorized",
    "time": "2025-08-05 11:22:59",
    "timestamp": 1754364179.0,
    "response": "吳維文's identity authentication failed."
}
```

### Response 404 (application/json)
```json
{
    "method": "POST",
    "status_code": 404,
    "status": "Not Found",
    "time": "2025-08-05 11:21:23",
    "timestamp": 1754364083.0,
    "response": "admi user not found."
}
```