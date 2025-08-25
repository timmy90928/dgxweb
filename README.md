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
#! 需安裝在 root 使用者
sudo pip3 install -r requirements.txt

# Update requirements.txt
pip freeze > requirements.txt
```

### Migrate
在 `migrations/env.py` 加入：
```python
from application import APP, db

# ... 其他程式碼 ...

def run_migrations_online():
    """Run migrations in 'online' mode."""

    context.configure(
        connection=connection,
        target_metadata=db.metadata, # 改這裡
    )

    with context.begin_transaction():
        context.run_migrations()

    # ... 其他程式碼 ...
```
接著在終端機執行：
```bash
sudo alembic init migrations
sudo alembic revision --autogenerate -m "Initial migration"
sudo alembic upgrade head
```



### 執行
```bash
cd dgxweb
sudo python3 app.py --mode development
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

DGX NAS
=======

硬體安裝指南：
[Synology RackStation RS3617xs+](https://global.download.synology.com/download/Document/Hardware/HIG/RackStation/17-year/RS3617xs+/cht/Syno_HIG_RS3617xs_Plus_cht.pdf)

連線至 [AILAB-DGX-NAS](http://quickconnect.to/ailabdgx)


Synology NAS 啟用 NFS
---------------------

1. 開啟 `控制台 -> 檔案服務 -> NFS`, 勾選 `啟用 NFS 服務`
3. 選擇你要共用的資料夾。如果資料夾還沒建立，先到 `控制台 -> 共用資料夾` 建立一個
4. 在共用資料夾上點擊右鍵，選擇 `編輯`, 並填入以下的值
    | 選項 | key | value |
    |:---:|:----:|:-----:|
    | 權限 | guest | 自訂 |
    | NFS 權限 | 主機名稱或 IP 位址 | 主機IP位址 |
    | NFS 權限 | 權限 | 自訂 |
    | NFS 權限 | 安全 | sys_all |
    | NFS 權限 | Squash | 將所有使用者調整為 guest |
    | NFS 權限 | 非同步 | 勾選 |



DGX 掛載
-------

#### 安裝 NFS 支援套件
```bash
sudo apt install nfs-common
```
使用以下指令來列出 NAS 上的 NFS 共享
```bash
##* showmount -e <NAS_IP_位址>

showmount -e 140.123.106.247
# Export list for 140.123.106.247:
# /volume1/dgx      140.123.106.239
# /volume1/nasfiles 140.123.106.239
# /volume1/DGXNas   140.123.106.239
```
掛載 NAS 
```bash
##* sudo mount -t nfs <NAS_IP>:/<共用資料夾名稱> /mnt/nas_data

sudo mount -t nfs 140.123.106.247:/volume1/dgx ~/nas

###* 取消掛載 ###
sudo umount -f ~/nas
```
確認是否掛載成功
```bash
df -h

# Filesystem                    Size  Used Avail Use% Mounted on
# tmpfs                          26G  2.8M   26G   1% /run
# /dev/sda2                     1.8T   48G  1.6T   3% /
# tmpfs                         126G   16K  126G   1% /dev/shm
# tmpfs                         5.0M  4.0K  5.0M   1% /run/lock
# /dev/sda1                     511M  6.1M  505M   2% /boot/efi
# tmpfs                          26G  116K   26G   1% /run/user/1000
# 140.123.106.247:/volume1/dgx   91T  149M   91T   1% /home/lab120/nas
```

開機自動掛載
-----------
```bash
sudo nano /etc/fstab

# 在檔案最後新增一行
# 140.123.106.247:/volume1/dgx  ~/nas  nfs  defaults  0  0
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