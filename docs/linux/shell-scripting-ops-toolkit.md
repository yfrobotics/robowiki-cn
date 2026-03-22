# Shell 脚本运维工具箱

!!! note "引言"
    机器人系统在部署和运行阶段，运维工程师需要频繁与底层系统交互——监控资源使用、管理进程、调试网络、配置 USB 设备和串口通信。本文整理了机器人运维中最常用的命令行工具和脚本模式，涵盖系统资源监控、进程管理、网络调试、USB 与串口设备管理以及 Docker 容器化部署等内容，帮助开发者快速定位和解决现场问题。


## 系统资源监控

机器人通常运行在资源有限的嵌入式平台上，实时监控 CPU（中央处理器）、内存、磁盘和 GPU（图形处理器）的使用情况至关重要。


### CPU 与内存监控

```bash
# 实时查看系统整体负载（每 2 秒刷新）
top -d 2

# 更友好的交互式工具
htop

# 查看 CPU 核心数和型号
lscpu | grep -E "^(CPU|Thread|Core|Socket|Model name)"

# 查看内存使用情况（以人类可读格式显示）
free -h

# 查看每个进程的 CPU 和内存使用（按内存排序，取前 10）
ps aux --sort=-%mem | head -11
```

编写监控脚本将资源数据记录到 CSV（逗号分隔值）文件：

```bash
#!/bin/bash
# resource_monitor.sh —— 系统资源采集脚本
OUTPUT="/home/robot/logs/resources.csv"

# 写入 CSV 表头
if [ ! -f "$OUTPUT" ]; then
    echo "timestamp,cpu_percent,mem_used_mb,mem_total_mb,disk_used_percent,load_1m" > "$OUTPUT"
fi

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
    MEM_USED=$(free -m | awk '/Mem:/{print $3}')
    MEM_TOTAL=$(free -m | awk '/Mem:/{print $2}')
    DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
    LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk -F',' '{print $1}' | tr -d ' ')

    echo "${TIMESTAMP},${CPU},${MEM_USED},${MEM_TOTAL},${DISK},${LOAD}" >> "$OUTPUT"
    sleep 10
done
```


### 磁盘使用监控

```bash
# 查看各分区使用情况
df -h

# 查看当前目录下各子目录的大小
du -sh */ | sort -rh | head -20

# 查找大文件（超过 100MB）
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null

# 查看 inode 使用情况（小文件过多时可能耗尽）
df -i

# 监控指定目录的大小变化
watch -n 5 'du -sh /home/robot/logs /home/robot/bags'
```


### GPU 监控（NVIDIA）

机器人视觉和深度学习推理通常依赖 NVIDIA GPU，`nvidia-smi`（NVIDIA System Management Interface）是核心监控工具。

```bash
# 查看 GPU 状态概览
nvidia-smi

# 持续监控（每 1 秒刷新）
nvidia-smi -l 1

# 仅输出关键指标：GPU 利用率、显存使用、温度
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total,temperature.gpu \
    --format=csv,noheader,nounits

# 查看占用 GPU 的进程
nvidia-smi pmon -d 1

# Jetson 平台使用 jtop 替代
sudo pip3 install jetson-stats
jtop
```

GPU 资源告警脚本：

```bash
#!/bin/bash
# gpu_alert.sh —— GPU 温度和显存告警
TEMP_THRESHOLD=85
MEM_THRESHOLD=90

GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits)
GPU_MEM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
GPU_MEM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
MEM_PERCENT=$((GPU_MEM_USED * 100 / GPU_MEM_TOTAL))

if [ "$GPU_TEMP" -gt "$TEMP_THRESHOLD" ]; then
    echo "[警告] GPU 温度过高：${GPU_TEMP}°C（阈值 ${TEMP_THRESHOLD}°C）"
fi

if [ "$MEM_PERCENT" -gt "$MEM_THRESHOLD" ]; then
    echo "[警告] GPU 显存使用率：${MEM_PERCENT}%（阈值 ${MEM_THRESHOLD}%）"
fi
```

| 工具 | 用途 | 适用平台 |
|------|------|----------|
| `top` / `htop` | CPU 和内存实时监控 | 通用 Linux |
| `free -h` | 内存概览 | 通用 Linux |
| `df -h` / `du -sh` | 磁盘空间监控 | 通用 Linux |
| `nvidia-smi` | NVIDIA GPU 监控 | x86 + NVIDIA |
| `jtop` | Jetson 平台全面监控 | NVIDIA Jetson |
| `tegrastats` | Jetson 原生状态输出 | NVIDIA Jetson |
| `iostat` | 磁盘 I/O 性能 | 通用 Linux |
| `vmstat` | 虚拟内存与 CPU 统计 | 通用 Linux |


## 进程管理

机器人软件往往由多个并行进程组成，需要灵活的进程管理手段。


### 基本进程操作

```bash
# 查看所有进程
ps aux

# 按名称查找进程
pgrep -a robot_navigation

# 杀死指定 PID 的进程
kill -15 12345    # SIGTERM，优雅终止
kill -9 12345     # SIGKILL，强制终止

# 按名称批量杀死进程
pkill -f "ros2.*navigation"

# 杀死占用某端口的进程
fuser -k 8080/tcp

# 查看进程树
pstree -p
```


### 后台运行与会话管理

```bash
# nohup：忽略挂断信号，后台运行
nohup ros2 launch robot_bringup robot.launch.py > /tmp/robot.log 2>&1 &
echo "进程 PID: $!"

# 使用 disown 将已启动的任务脱离终端
ros2 launch robot_bringup robot.launch.py &
disown %1
```

#### tmux 会话管理

tmux（Terminal Multiplexer，终端多路复用器）非常适合通过 SSH（安全外壳协议）远程管理机器人：

```bash
# 创建命名会话
tmux new -s robot

# 分割窗口：水平分割
tmux split-window -h

# 分割窗口：垂直分割
tmux split-window -v

# 切换窗格：Ctrl+B 然后按方向键

# 脱离会话（保持后台运行）：Ctrl+B 然后按 d

# 重新连接到会话
tmux attach -t robot

# 列出所有会话
tmux ls

# 在脚本中使用 tmux 启动多个节点
tmux new-session -d -s robot_session
tmux send-keys -t robot_session "source /opt/ros/humble/setup.bash && ros2 launch lidar lidar.launch.py" Enter
tmux split-window -t robot_session -h
tmux send-keys -t robot_session "source /opt/ros/humble/setup.bash && ros2 launch camera camera.launch.py" Enter
```

#### screen 会话管理

```bash
# 创建命名会话
screen -S robot

# 脱离：Ctrl+A 然后按 d

# 重新连接
screen -r robot

# 列出会话
screen -ls
```


## 网络调试

机器人多节点通信依赖可靠的网络，以下工具帮助定位网络问题。

```bash
# 基本连通性测试
ping -c 5 192.168.1.100

# 路由追踪
traceroute 192.168.1.100
# 或使用更现代的 mtr
mtr -c 10 192.168.1.100

# 查看网络接口信息
ip addr show
ip link show

# 查看路由表
ip route show
```


### 端口与连接检查

```bash
# ss：查看网络连接状态（替代 netstat）
ss -tlnp                        # TCP 监听端口
ss -ulnp                        # UDP 监听端口
ss -s                           # 连接统计摘要

# netstat：传统工具（部分系统需要安装 net-tools）
netstat -tlnp                   # TCP 监听端口
netstat -an | grep ESTABLISHED  # 已建立的连接

# 测试远程端口是否可达
nc -zv 192.168.1.100 11311      # 测试 ROS Master 端口
timeout 3 bash -c 'echo > /dev/tcp/192.168.1.100/22'  # 测试 SSH 端口
```


### 抓包分析

```bash
# tcpdump：抓取指定接口的网络包
sudo tcpdump -i eth0 -c 100                    # 抓取 100 个包
sudo tcpdump -i eth0 port 7400                  # 抓取 DDS 发现端口
sudo tcpdump -i eth0 host 192.168.1.100         # 抓取指定主机的流量
sudo tcpdump -i eth0 -w /tmp/capture.pcap       # 保存为 pcap 文件供 Wireshark 分析

# ROS 2 DDS 通信调试
sudo tcpdump -i any -n udp port 7400 or udp port 7401
```

| 工具 | 主要用途 | 示例 |
|------|----------|------|
| `ping` | 连通性测试 | `ping -c 3 host` |
| `traceroute` / `mtr` | 路由追踪 | `mtr -c 10 host` |
| `ss` | 查看端口和连接 | `ss -tlnp` |
| `tcpdump` | 网络抓包 | `tcpdump -i eth0 port 80` |
| `nc` (netcat) | 端口测试和数据传输 | `nc -zv host port` |
| `curl` / `wget` | HTTP 请求调试 | `curl -v http://host:8080` |
| `nmap` | 网络扫描 | `nmap -sn 192.168.1.0/24` |
| `iperf3` | 带宽测试 | `iperf3 -c host` |


## USB 设备管理

机器人连接的传感器（激光雷达、IMU、相机）大多通过 USB（通用串行总线）接入。


### 设备识别

```bash
# 列出所有 USB 设备
lsusb
# 详细信息
lsusb -v -d 10c4:ea60   # 查看指定设备详情

# 查看 USB 设备树形结构
lsusb -t

# 查看内核检测到的 USB 设备信息
dmesg | grep -i usb | tail -20

# 查看串口设备
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```


### udev 规则

udev 规则可以为 USB 设备创建固定的符号链接，避免因插拔顺序导致设备号变化。

```bash
# 获取设备属性（用于编写 udev 规则）
udevadm info -a -n /dev/ttyUSB0 | grep -E "(idVendor|idProduct|serial)"

# 创建 udev 规则文件
sudo tee /etc/udev/rules.d/99-robot-devices.rules > /dev/null <<'EOF'
# RPLIDAR A2 激光雷达
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", \
    SYMLINK+="rplidar", MODE="0666", GROUP="dialout"

# Xsens MTi IMU
SUBSYSTEM=="tty", ATTRS{idVendor}=="2639", ATTRS{idProduct}=="0300", \
    SYMLINK+="imu", MODE="0666", GROUP="dialout"

# Arduino 电机控制板
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", \
    SYMLINK+="motor_controller", MODE="0666", GROUP="dialout"

# RealSense 深度相机（USB 权限）
SUBSYSTEM=="usb", ATTRS{idVendor}=="8086", ATTRS{idProduct}=="0b07", \
    MODE="0666", GROUP="plugdev"
EOF

# 重新加载规则
sudo udevadm control --reload-rules
sudo udevadm trigger

# 验证符号链接
ls -la /dev/rplidar /dev/imu /dev/motor_controller
```

udev 规则中还可以触发脚本，在设备插入时自动执行初始化：

```bash
# 设备插入时执行脚本
ACTION=="add", SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", \
    RUN+="/home/robot/scripts/on_lidar_connect.sh"
```


## 串口通信工具

许多机器人底层控制器通过串口（RS-232/RS-485）通信。


### minicom

```bash
# 安装 minicom
sudo apt install minicom

# 连接串口设备
minicom -D /dev/ttyUSB0 -b 115200

# 常用快捷键：
# Ctrl+A Z  —— 帮助菜单
# Ctrl+A X  —— 退出
# Ctrl+A L  —— 开启日志记录
# Ctrl+A E  —— 开启本地回显
```


### screen 用于串口

```bash
# 使用 screen 连接串口（更简便）
screen /dev/ttyUSB0 115200

# 退出：Ctrl+A 然后按 k，确认 y
```


### 脚本化串口通信

```bash
#!/bin/bash
# serial_cmd.sh —— 向串口发送命令并读取响应
DEVICE="/dev/motor_controller"
BAUDRATE=115200

# 配置串口参数
stty -F "$DEVICE" "$BAUDRATE" cs8 -cstopb -parenb raw -echo

# 发送命令
echo -ne "GET_STATUS\r\n" > "$DEVICE"

# 读取响应（超时 2 秒）
timeout 2 cat "$DEVICE"
```

| 工具 | 特点 | 适用场景 |
|------|------|----------|
| `minicom` | 功能丰富的终端仿真器 | 交互式调试 |
| `screen` | 轻量级串口连接 | 快速查看数据 |
| `picocom` | 最小化串口终端 | 简单通信 |
| `stty` + `cat`/`echo` | 脚本化控制 | 自动化测试 |
| `python3 -m serial.tools.miniterm` | Python pyserial 自带 | 跨平台调试 |


## Docker 容器化部署

Docker 容器能为机器人软件提供一致的运行环境，简化多机部署。


### 常用 Docker 命令

```bash
# 拉取 ROS 2 镜像
docker pull ros:humble-perception

# 运行容器（带 GPU 支持和设备映射）
docker run -it --rm \
    --gpus all \
    --network host \
    --privileged \
    -v /dev:/dev \
    -v /home/robot/workspace:/workspace \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY=$DISPLAY \
    --name robot_container \
    ros:humble-perception \
    bash

# 查看运行中的容器
docker ps

# 查看容器日志
docker logs -f robot_container

# 进入运行中的容器
docker exec -it robot_container bash

# 查看容器资源使用
docker stats

# 清理未使用的镜像和容器
docker system prune -a
```


### Docker Compose 多容器编排

创建 `docker-compose.yml` 管理多个机器人服务：

```bash
# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看指定服务日志
docker compose logs -f navigation

# 停止所有服务
docker compose down

# 重新构建并启动
docker compose up -d --build
```


### Docker 运维脚本

```bash
#!/bin/bash
# docker_deploy.sh —— 机器人 Docker 部署脚本
IMAGE_NAME="robot-app"
IMAGE_TAG="latest"
CONTAINER_NAME="robot_runtime"

echo "===== 机器人 Docker 部署 ====="

# 停止旧容器
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "停止旧容器..."
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
fi

# 拉取最新镜像
echo "拉取最新镜像..."
docker pull "${IMAGE_NAME}:${IMAGE_TAG}"

# 启动新容器
echo "启动新容器..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    --gpus all \
    --network host \
    --privileged \
    -v /dev:/dev \
    -v /home/robot/maps:/maps:ro \
    -v /home/robot/logs:/logs \
    "${IMAGE_NAME}:${IMAGE_TAG}"

# 验证启动状态
sleep 3
if docker ps -f name="$CONTAINER_NAME" --format '{{.Status}}' | grep -q "Up"; then
    echo "部署成功！容器状态正常"
    docker logs --tail 20 "$CONTAINER_NAME"
else
    echo "部署失败！请检查日志"
    docker logs "$CONTAINER_NAME"
    exit 1
fi
```


## 参考资料

- [Linux 命令大全](https://man7.org/linux/man-pages/) —— Linux man pages 在线版
- [tmux 速查表](https://tmuxcheatsheet.com/) —— tmux 快捷键参考
- [udev 规则编写指南](https://www.freedesktop.org/software/systemd/man/udev.html)
- [Docker 官方文档](https://docs.docker.com/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/overview.html)
- [ROS 2 与 Docker 最佳实践](https://docs.ros.org/en/humble/How-To-Guides/Run-2-nodes-in-single-or-separate-docker-containers.html)
