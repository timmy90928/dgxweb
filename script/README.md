腳本
===

這裡存放 DGX大更新(2025) 前, 學長所寫的腳本

- { } 內是需要輸入的資料類型
-  DGX (物理關機): sudo shutdown -h now 
- ~/user_data 裡面是所有user的workspace

使用
===

使用腳本前都需先使用以下指令進入此資料夾, 並請使用 sudo 指令，全部的檔案可前往實驗室的NAS查看

```bash
cd ~/dgxweb/script
```

總覽
----
|功能|指令|
|:--:|:---|
|創建container|./run.sh nvcr.io/partners/matlab r2022b {account}  {password}|
|刪除container|./del.sh {account}_matlab_r2022b|
|查看GPU誰在使用|./gpuser.sh|
|進入container|docker exec -it {Container ID} bash|

 p.s.  設定檔: /tmp/lab.sh → 有密碼，可設定此人的資料
 
砍gpu占用
---------

 ```bash
nvtop   # 查看 pid
sudo kill -9 {pid}
```
或是
 ```bash
./gpuser.sh
docker ps | grep {account}  # 找到 UID
docker container top {UID}  # 找到沒release 的 PID
kill -9 {PID} 
```

 清除多餘IMAGE(慎用)
 -----------------

```bash
docker image ls  # 列出image
docker rmi {image id}
```

https://hackmd.io/@falconjk/DgxIT/%2Ffzy0DP2zQQq0PwgxSv905g
