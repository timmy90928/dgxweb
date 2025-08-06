DGX Web
=======
架設在AI實驗室的NVIDIA DGXS-V100的網頁

連線
---

### SSH
以下為 `~/.ssh/config`，密碼親自交接

```SSH Config
Host DGX
  HostName 140.123.106.239
  User lab120
  Port 22
  IdentityFile ~/.ssh/dgx
```


安裝
------

### 安裝依賴完竟
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