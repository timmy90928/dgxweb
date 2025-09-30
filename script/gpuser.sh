#! /bin/bash
# nvidia-smi | grep 'python' | awk '{ print $3 }' | xargs -n1 pwdx
GPUNUM=(`nvidia-smi | sed -n '25,$p' | awk '{print $2}'`)
GPUPID=(`nvidia-smi | sed -n '25,$p' | awk '{print $3}'`)
len=${#GPUNUM[@]}

printf "\n\nGPU  \t docker name \n";

for((i=2;i<len;i++));
do
    printf "%s  \t %s" ${GPUNUM[$i]} `docker inspect --format '{{.Name}}' "$(cat /proc/${GPUPID[$i]}/cgroup | grep "pids" |  cut -d\/ -f3)"`
    printf "\n"
done

printf "\n";

#len=${#containerID[@]}
#for((i=0;i<len;i++));
#do
#    printf "%s \t %d \t %s\n" ${GPUNUM[$i]} ${containerID[$i]} `docker inspect --format '{{.Name}}' "$(cat /proc/${containerID[$i]}/cgroup | grep "pids" |  cut -d\/ -f3)"` 
#done
## `cat /proc/${containerID[$i]}/cgroup | grep "pids" |  cut -d\/ -f3`
