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
