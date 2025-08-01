"""
client.df() 和 client.info() 之外，Docker Python SDK 的 client 物件還提供了大量核心功能，讓您可以輕鬆管理 Docker 容器、映像檔、網路和資料卷等。

容器管理 (Containers)
client.containers.run(...): 建立並執行一個新的容器。這是最常用的功能之一，您可以指定映像檔、執行指令、連接埠映射、資料卷掛載等。

client.containers.get(name_or_id): 透過容器名稱或 ID 取得特定的 Container 物件。

client.containers.list(all=True): 列出所有容器（預設只列出執行中的容器，設定 all=True 則包含已停止的）。

client.containers.create(...): 建立一個容器，但不會立即啟動。

client.containers.prune(): 清理所有已停止的容器。

當您取得 Container 物件後，還可以對其執行更多操作：

container.start(): 啟動容器。

container.stop(): 停止容器。

container.remove(): 刪除容器。

container.pause() / container.unpause(): 暫停 / 取消暫停容器。

container.exec_run(cmd): 在執行中的容器內部執行指令。

container.logs(): 取得容器的日誌。

container.stats(): 取得容器的資源使用統計。

映像檔管理 (Images)
client.images.build(...): 從 Dockerfile 建構映像檔。

client.images.pull(repository): 從 Docker Hub 或其他註冊中心拉取映像檔。

client.images.get(name_or_id): 取得一個特定映像檔的 Image 物件。

client.images.list(): 列出所有本機映像檔。

client.images.remove(image): 刪除映像檔。

client.images.prune(): 清理所有未使用的映像檔。

網路管理 (Networks)
client.networks.create(name): 建立一個 Docker 網路。

client.networks.get(name_or_id): 取得一個特定網路的 Network 物件。

client.networks.list(): 列出所有 Docker 網路。

client.networks.remove(network): 刪除網路。

client.networks.prune(): 清理所有未使用的網路。

當您取得 Network 物件後，還可以對其執行更多操作：

network.connect(container): 將容器連接到網路。

network.disconnect(container): 將容器從網路斷開連接。

資料卷管理 (Volumes)
client.volumes.create(name): 建立一個 Docker 資料卷。

client.volumes.get(name): 取得一個特定資料卷的 Volume 物件。

client.volumes.list(): 列出所有 Docker 資料卷。

client.volumes.remove(volume): 刪除資料卷。

client.volumes.prune(): 清理所有未使用的資料卷。
"""

# sudo python3 -m utils.dockers
from  docker import from_env, errors
from docker.models.containers import Container as _Container
from docker.models.images import Image as _Image
from docker.types import DeviceRequest
from utils.utils import errorCallback, timestamp, format_bytes, get_local_ip
from utils.model import db, Container as ContainerDB
client = from_env()

@errorCallback("尋找containers失敗", 404)
def get_all_containers(container_id=None):
    containers = client.containers.list(all=True)
    result = []
    for container in containers:
        if container_id is None or container_id in container.id or container_id in container.name:
            result.append(container) 
    return [
        {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "image": c.image.tags[0] if c.image.tags else "none",
            "ports": c.ports,
            "labels": c.labels
        }
        for c in result
    ]

def delete_container(container_name):
    try:
        container = client.containers.get(container_name)
        container.remove(force=True)
        return {"status": "deleted", "container": container_name}
    except errors.NotFound:
        return {"status": "not found", "container": container_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_container(data):
    try:
        repo = data['repo']
        tag = data['tag']
        name = data['name']
        pw = data['password']
        image = f"{repo}:{tag}"
        library = repo.split('/')[-1]
        container_name = f"{name}_{library}_{tag}"

        ports = {"22/tcp": None, "8888/tcp": None}
        volumes = {
            f"/home/lab120/user_data/{name}": {"bind": f"/workspace/{name}", "mode": "rw"},
            f"/raid/DataSet/{name}": {"bind": "/workspace/DataSet", "mode": "rw"},
            "/raid/ShareDataSet": {"bind": "/workspace/Share", "mode": "rw"}
        }

        container = client.containers.run(
            image=image,
            name=container_name,
            detach=True,
            tty=True,
            ports=ports,
            volumes=volumes,
            command="bash"
        )
        return {"status": "started", "container": container_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class Container:
    def __init__(self, container_id = None):
        _containers = client.containers.list(all=True)
        containers:list[_Container] = []
        for container in _containers:
            if container_id is None or container_id in container.id or container_id in container.name:
                containers.append(container) 
        self.containers = containers

    @property
    def container(self):
        if len(self.containers) == 1:
            return self.containers[0]
        else:
            raise ValueError('Please enter the complete <container_id>.')

    def list(self, with_control:bool = False):
        results = [
            ['Name', 'User', 'Image', 'Created', 'StartedAt', 'Status','Run/stop', 'Remove']
        ]
        for container in self.containers:
            is_runing =  container.status == 'running'
            container_db:ContainerDB = ContainerDB.query.filter_by(container_id=container.id).first()
            user = f"{container_db.user.name}({container_db.user.username})"
            href = None if container.status != 'running' else f"http://{get_local_ip()}:{container.ports['8888/tcp'][0]['HostPort']}?token={container_db.password}"
            try:
                image = container.image.tags[0]
            except Exception as e:
                image = f"ERROR: {e}"

            results.append(
                [
                    f"<a href={href}>{container.name}</a>" if with_control and is_runing else container.name,
                    user, image,
                    timestamp(iso = container.attrs['Created']),
                    timestamp(iso = container.attrs['State']['StartedAt'])if is_runing else '-',
                    container.status,
                    f"<a href='/container/{'stop' if is_runing else 'start'}/{container.id}'>{'stop' if is_runing else 'start'}</a>" if with_control else '-',
                    f"<a href='/container/remove/{container.id}'>Remove</a>" if with_control else '-',
                ]
            )
        return results

    @classmethod
    def create(cls, username:str, image_name:str):
        """
        Args:
            image_name: ex: nvcr.io/nvidia/pytorch:24.05-py3
        """
        from utils.g import current_user
        library, tag = image_name.split(':') if ':' in image_name else (image_name, 'latest')
        library_name = library.split('/')[-1]
        container_name = f"{username}_{library_name}_{tag}"
        volumes = {
            f"/home/lab120/user_data/{username}": {"bind": f"/workspace/{username}", "mode": "rw"},
            f"/raid/DataSet/{username}": {"bind": "/workspace/DataSet", "mode": "rw"},
            "/raid/ShareDataSet": {"bind": "/workspace/Share", "mode": "rw"}
        }

        _container = client.containers.create(
            image = image_name,
            command = "bash",
            name = container_name,
            ports = {
                "22/tcp": None,     #? SSH
                "8888/tcp": None    #? Jupyter lab
            },
            volumes = volumes,
            tty = True,
            device_requests = [
                DeviceRequest(count=-1, capabilities=[['gpu']]) #? --gpus all
            ],
            detach = True
        )
    
        db.add(
            ContainerDB(_container.id, _container.name, '', user_id = current_user.id)
        )

        return _container

class Image:
    def __init__(self, image_id = None):
        _images = client.images.list(all=True)
        images:list[_Image] = []
        for image in _images:
            if image_id is None or image_id in image.id or image_id in image.name:
                images.append(image) 
        self.images = images

    def list(self):
        results = [
            ['Tags', 'Created', 'Size']
        ]
        for image in self.images:
            results.append(
                [
                    image.tags[0],
                    timestamp(iso = image.attrs['Created']),
                    format_bytes(image.attrs['Size'])
                ]
            )
        return results
    
if __name__ == '__main__':

    print(Image().list())
    exit()

    for network in client.networks.list():
        print(network.attrs)
        break
    # print(client.df())  # 硬碟使用狀況
    # print(client.info())    # Docker 的系統環境訊息
    # print(client.volumes.list())
