# Shell 脚本自动化模式

!!! note "引言"
    在机器人系统的日常运维中，大量重复性任务可以通过 Shell 脚本实现自动化。从开机自启动、进程监控到日志管理和数据备份，良好的自动化模式能够显著提升系统可靠性并减少人工干预。本文介绍机器人开发和部署中常用的 Shell 脚本自动化模式，涵盖 systemd 服务管理、定时任务、看门狗脚本、日志轮转、网络监控以及 CI/CD（持续集成/持续部署）流水线脚本等内容。


## 开机自启动

机器人上电后通常需要自动启动导航、感知等核心节点，常用方案有 systemd 服务和 crontab 定时任务两种。


### systemd 服务

systemd 是现代 Linux 发行版的默认初始化系统，用它管理机器人进程具有依赖管理、自动重启和日志集成等优势。

创建服务单元文件 `/etc/systemd/system/robot-nav.service`：

```bash
[Unit]
Description=Robot Navigation Stack
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=robot
WorkingDirectory=/home/robot/catkin_ws
ExecStartPre=/bin/bash -c "source /opt/ros/humble/setup.bash"
ExecStart=/bin/bash -c "source install/setup.bash && ros2 launch nav2_bringup bringup_launch.py"
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

启用并管理服务：

```bash
# 重新加载配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable robot-nav.service

# 手动启动/停止/查看状态
sudo systemctl start robot-nav.service
sudo systemctl stop robot-nav.service
sudo systemctl status robot-nav.service

# 查看服务日志
journalctl -u robot-nav.service -f
```


### crontab 定时任务

crontab 适合周期性任务，如定时采集传感器数据或清理临时文件。

```bash
# 编辑当前用户的定时任务表
crontab -e

# 常用格式：分 时 日 月 周 命令
# 每天凌晨 3 点清理 /tmp 下超过 7 天的 rosbag 文件
0 3 * * * find /tmp -name "*.bag" -mtime +7 -delete

# 每 5 分钟采集一次系统状态
*/5 * * * * /home/robot/scripts/collect_stats.sh >> /var/log/robot_stats.log 2>&1

# 开机后延迟 30 秒启动脚本（适合不使用 systemd 的场景）
@reboot sleep 30 && /home/robot/scripts/start_robot.sh
```

使用 `crontab -l` 可以列出当前所有定时任务。注意 crontab 环境变量有限，建议在脚本中显式设置 `PATH` 和 `source` 必要的环境文件。


## 进程监控看门狗

机器人软件在野外长期运行时可能出现崩溃，看门狗（Watchdog）脚本能自动检测异常并重启进程。

```bash
#!/bin/bash
# watchdog.sh —— 进程看门狗脚本
# 用法：watchdog.sh <进程名> <启动命令>

PROCESS_NAME="$1"
START_CMD="$2"
CHECK_INTERVAL=10   # 检测间隔（秒）
MAX_RESTART=5        # 最大连续重启次数
RESTART_COUNT=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

while true; do
    if ! pgrep -f "$PROCESS_NAME" > /dev/null; then
        log "警告：进程 $PROCESS_NAME 未运行，正在重启（第 $((RESTART_COUNT+1)) 次）..."
        eval "$START_CMD" &
        RESTART_COUNT=$((RESTART_COUNT + 1))

        if [ "$RESTART_COUNT" -ge "$MAX_RESTART" ]; then
            log "错误：已连续重启 $MAX_RESTART 次，发送告警并停止看门狗"
            # 发送邮件或消息通知运维人员
            echo "机器人进程 $PROCESS_NAME 异常" | mail -s "看门狗告警" admin@example.com
            exit 1
        fi
        sleep 5
    else
        RESTART_COUNT=0
    fi
    sleep "$CHECK_INTERVAL"
done
```

更高级的看门狗还可以检测进程的 CPU 和内存使用率，当资源占用异常时主动重启：

```bash
#!/bin/bash
# 检查进程内存占用是否超过阈值
PID=$(pgrep -f "robot_perception")
if [ -n "$PID" ]; then
    MEM_PERCENT=$(ps -o pmem= -p "$PID" | tr -d ' ')
    MEM_INT=${MEM_PERCENT%.*}
    if [ "$MEM_INT" -gt 80 ]; then
        echo "[$(date)] 内存占用 ${MEM_PERCENT}%，重启进程"
        kill "$PID"
        sleep 2
        /home/robot/scripts/start_perception.sh &
    fi
fi
```


## 日志轮转与管理

机器人长期运行会产生大量日志，不加管理会占满磁盘空间。


### 使用 logrotate

在 `/etc/logrotate.d/robot` 中创建配置：

```
/home/robot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    maxsize 100M
}
```

| 参数 | 说明 |
|------|------|
| `daily` | 每天轮转一次 |
| `rotate 7` | 保留最近 7 份日志 |
| `compress` | 使用 gzip 压缩旧日志 |
| `delaycompress` | 延迟一个周期再压缩 |
| `copytruncate` | 复制后截断原文件，避免重启进程 |
| `maxsize 100M` | 日志超过 100MB 时立即轮转 |

手动触发轮转进行测试：

```bash
sudo logrotate -f /etc/logrotate.d/robot
```


### 自定义日志清理脚本

```bash
#!/bin/bash
# clean_logs.sh —— 按磁盘使用率清理日志
LOG_DIR="/home/robot/logs"
THRESHOLD=80  # 磁盘使用率阈值（百分比）

USAGE=$(df "$LOG_DIR" | tail -1 | awk '{print $5}' | tr -d '%')

if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "[$(date)] 磁盘使用率 ${USAGE}%，开始清理旧日志..."
    # 删除 30 天前的日志
    find "$LOG_DIR" -name "*.log" -mtime +30 -delete
    # 压缩 7 天前的日志
    find "$LOG_DIR" -name "*.log" -mtime +7 -exec gzip {} \;
    echo "[$(date)] 清理完成，当前使用率：$(df "$LOG_DIR" | tail -1 | awk '{print $5}')"
fi
```


## 自动备份

定期备份配置文件、地图数据和标定参数对机器人系统至关重要。

```bash
#!/bin/bash
# backup_robot.sh —— 机器人数据增量备份脚本
BACKUP_SRC="/home/robot/catkin_ws/src /home/robot/maps /home/robot/calibration"
BACKUP_DST="/mnt/backup/robot"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DST}/robot_backup_${TIMESTAMP}.tar.gz"
LATEST_LINK="${BACKUP_DST}/latest"
MAX_BACKUPS=10

# 创建备份目录
mkdir -p "$BACKUP_DST"

# 增量备份：仅打包近 24 小时内修改的文件
find $BACKUP_SRC -newer "$LATEST_LINK" -type f 2>/dev/null | \
    tar czf "$BACKUP_FILE" -T - 2>/dev/null

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    ln -sf "$BACKUP_FILE" "$LATEST_LINK"
    echo "[$(date)] 备份成功：$BACKUP_FILE"
else
    echo "[$(date)] 无新文件需要备份或备份失败"
    rm -f "$BACKUP_FILE"
fi

# 保留最近 N 份备份，删除旧备份
BACKUP_COUNT=$(ls -1 "${BACKUP_DST}"/robot_backup_*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    ls -1t "${BACKUP_DST}"/robot_backup_*.tar.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f
    echo "[$(date)] 已清理旧备份，当前保留 $MAX_BACKUPS 份"
fi
```

配合 crontab 每天自动执行：

```bash
0 2 * * * /home/robot/scripts/backup_robot.sh >> /home/robot/logs/backup.log 2>&1
```


## 网络监控

机器人常通过 Wi-Fi 与上位机通信，网络不稳定会导致遥控失联。

```bash
#!/bin/bash
# network_monitor.sh —— 网络连通性监控
GATEWAY="192.168.1.1"
SERVER="10.0.0.100"
LOG_FILE="/home/robot/logs/network.log"
WIFI_INTERFACE="wlan0"

check_connectivity() {
    local target="$1"
    local name="$2"
    if ping -c 3 -W 2 "$target" > /dev/null 2>&1; then
        echo "[$(date)] $name ($target) 连接正常"
    else
        echo "[$(date)] 警告：$name ($target) 不可达"
        return 1
    fi
}

restart_wifi() {
    echo "[$(date)] 正在重启无线网络接口 $WIFI_INTERFACE ..."
    sudo ip link set "$WIFI_INTERFACE" down
    sleep 2
    sudo ip link set "$WIFI_INTERFACE" up
    sleep 5
    # 等待重新连接
    for i in $(seq 1 10); do
        if iwconfig "$WIFI_INTERFACE" 2>/dev/null | grep -q "ESSID"; then
            echo "[$(date)] 无线网络已重新连接"
            return 0
        fi
        sleep 2
    done
    echo "[$(date)] 错误：无线网络重连失败"
    return 1
}

# 主循环
while true; do
    {
        check_connectivity "$GATEWAY" "网关"
        GW_STATUS=$?

        if [ $GW_STATUS -ne 0 ]; then
            restart_wifi
        else
            check_connectivity "$SERVER" "上位机"
        fi

        # 记录信号强度
        SIGNAL=$(iwconfig "$WIFI_INTERFACE" 2>/dev/null | grep "Signal level" | awk -F'=' '{print $3}')
        [ -n "$SIGNAL" ] && echo "[$(date)] 信号强度：$SIGNAL"
    } >> "$LOG_FILE" 2>&1

    sleep 30
done
```


## 环境配置自动化

新机器人或新开发环境的初始化可以通过脚本实现一键部署。

```bash
#!/bin/bash
# setup_robot_env.sh —— 机器人开发环境一键配置
set -euo pipefail

ROS_DISTRO="humble"
WORKSPACE="$HOME/robot_ws"

echo "===== 机器人开发环境自动配置 ====="

# 1. 系统更新
echo "[1/6] 更新系统软件包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装 ROS 2
echo "[2/6] 安装 ROS 2 ${ROS_DISTRO}..."
if ! dpkg -l | grep -q "ros-${ROS_DISTRO}-desktop"; then
    sudo apt install -y software-properties-common
    sudo add-apt-repository universe
    sudo apt update
    sudo apt install -y ros-${ROS_DISTRO}-desktop ros-dev-tools
fi

# 3. 安装常用依赖
echo "[3/6] 安装开发依赖..."
sudo apt install -y \
    python3-pip python3-colcon-common-extensions \
    git curl wget htop tmux \
    librealsense2-dev ros-${ROS_DISTRO}-realsense2-camera \
    ros-${ROS_DISTRO}-nav2-bringup ros-${ROS_DISTRO}-slam-toolbox

# 4. 配置环境变量
echo "[4/6] 配置环境变量..."
BASHRC="$HOME/.bashrc"
grep -q "ros/${ROS_DISTRO}/setup.bash" "$BASHRC" || \
    echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> "$BASHRC"
grep -q "ROS_DOMAIN_ID" "$BASHRC" || \
    echo "export ROS_DOMAIN_ID=42" >> "$BASHRC"

# 5. 创建工作空间
echo "[5/6] 创建工作空间..."
mkdir -p "${WORKSPACE}/src"
cd "$WORKSPACE"
source /opt/ros/${ROS_DISTRO}/setup.bash
colcon build --symlink-install

# 6. 配置 udev 规则
echo "[6/6] 配置传感器 udev 规则..."
sudo tee /etc/udev/rules.d/99-robot-sensors.rules > /dev/null <<'UDEV'
# IMU (例如 Xsens)
SUBSYSTEM=="tty", ATTRS{idVendor}=="2639", SYMLINK+="imu", MODE="0666"
# 激光雷达 (例如 RPLIDAR)
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", SYMLINK+="lidar", MODE="0666"
UDEV
sudo udevadm control --reload-rules && sudo udevadm trigger

echo "===== 环境配置完成！请执行 source ~/.bashrc 使环境变量生效 ====="
```


## CI/CD 脚本

机器人软件项目同样需要持续集成流水线来保证代码质量。

```bash
#!/bin/bash
# ci_build_test.sh —— CI 流水线构建与测试脚本
set -euo pipefail

WORKSPACE="/workspace/robot_ws"
ROS_DISTRO="humble"

source /opt/ros/${ROS_DISTRO}/setup.bash

echo "===== 阶段 1：代码静态检查 ====="
# 使用 ament 工具进行代码风格检查
ament_cpplint src/ --filter=-whitespace/braces
ament_flake8 src/
echo "静态检查通过"

echo "===== 阶段 2：编译 ====="
cd "$WORKSPACE"
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release \
    --event-handlers console_direct+
echo "编译成功"

echo "===== 阶段 3：单元测试 ====="
source install/setup.bash
colcon test --return-code-on-test-failure
colcon test-result --verbose
echo "测试通过"

echo "===== 阶段 4：打包 ====="
TIMESTAMP=$(date +%Y%m%d%H%M%S)
tar czf "/artifacts/robot_release_${TIMESTAMP}.tar.gz" \
    -C install .
echo "打包完成：robot_release_${TIMESTAMP}.tar.gz"
```

GitHub Actions 工作流配置示例（`.github/workflows/robot-ci.yml`）：

```bash
# 在本地测试 GitHub Actions 工作流
# 安装 act 工具：https://github.com/nektos/act
act -W .github/workflows/robot-ci.yml --container-architecture linux/amd64
```


## 常用自动化模式


### 重试逻辑

网络请求或硬件初始化可能暂时失败，重试模式能提高成功率：

```bash
retry() {
    local max_attempts=$1
    local delay=$2
    shift 2
    local cmd="$@"

    for ((i=1; i<=max_attempts; i++)); do
        echo "第 ${i}/${max_attempts} 次尝试：$cmd"
        if eval "$cmd"; then
            return 0
        fi
        echo "失败，${delay} 秒后重试..."
        sleep "$delay"
    done
    echo "错误：已达最大重试次数 $max_attempts"
    return 1
}

# 使用示例：最多重试 5 次，每次间隔 3 秒
retry 5 3 ping -c 1 192.168.1.100
```


### 锁文件防止重复执行

```bash
LOCK_FILE="/tmp/robot_backup.lock"

acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        LOCK_PID=$(cat "$LOCK_FILE")
        if kill -0 "$LOCK_PID" 2>/dev/null; then
            echo "脚本已在运行（PID: $LOCK_PID），退出"
            exit 1
        else
            echo "发现过期锁文件，清理后继续"
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

release_lock() {
    rm -f "$LOCK_FILE"
}

# 确保退出时释放锁
trap release_lock EXIT

acquire_lock
# ... 执行主要逻辑 ...
```


### 信号处理与优雅退出

机器人进程需要在收到终止信号时安全关闭硬件：

```bash
#!/bin/bash
# 优雅退出：收到信号时安全停止电机并保存数据
RUNNING=true

cleanup() {
    echo "[$(date)] 收到终止信号，正在安全关闭..."
    # 停止电机
    rostopic pub -1 /cmd_vel geometry_msgs/Twist '{linear: {x: 0}, angular: {z: 0}}'
    # 保存最后的地图数据
    ros2 service call /map_saver/save_map nav2_msgs/srv/SaveMap "{map_url: '/home/robot/maps/final_map'}"
    RUNNING=false
    echo "[$(date)] 安全关闭完成"
    exit 0
}

trap cleanup SIGINT SIGTERM SIGHUP

# 主循环
while $RUNNING; do
    # 执行正常的机器人控制逻辑
    sleep 1
done
```


### 并行任务执行

同时启动多个传感器节点并等待全部就绪：

```bash
#!/bin/bash
# 并行启动多个节点
PIDS=()

start_node() {
    local name="$1"
    local cmd="$2"
    echo "[$(date)] 启动 $name ..."
    eval "$cmd" &
    PIDS+=($!)
    echo "[$(date)] $name 已启动（PID: ${PIDS[-1]}）"
}

start_node "激光雷达" "ros2 launch rplidar_ros rplidar.launch.py"
start_node "IMU" "ros2 launch imu_driver imu.launch.py"
start_node "相机" "ros2 launch realsense2_camera rs_launch.py"

echo "等待所有节点启动完成..."
sleep 5

# 检查所有节点是否正常运行
ALL_OK=true
for pid in "${PIDS[@]}"; do
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "错误：PID $pid 对应的节点已退出"
        ALL_OK=false
    fi
done

if $ALL_OK; then
    echo "所有传感器节点启动成功"
else
    echo "部分节点启动失败，请检查日志"
    exit 1
fi

# 等待任一子进程退出
wait -n
echo "警告：有节点异常退出，正在关闭所有节点..."
for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null
done
```


## 参考资料

- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html) —— GNU Bash 官方手册
- [systemd 服务管理文档](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [logrotate 配置指南](https://linux.die.net/man/8/logrotate)
- [ROS 2 Launch 系统文档](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html)
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/) —— 高级 Bash 脚本编程指南
