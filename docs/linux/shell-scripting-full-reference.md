# Shell 脚本参考资料

!!! note "引言"
    本文是 Bash Shell 脚本的综合参考手册，涵盖变量与数组、条件判断、循环、函数、字符串操作、文件测试、正则表达式等核心语法，并收录常用单行命令、推荐工具和编码风格指南。无论是编写简单的自动化脚本还是复杂的机器人部署工具，都可以在此快速查阅所需语法。


## 变量与数据类型


### 变量基础

```bash
# 变量赋值（等号两侧不能有空格）
NAME="robot_01"
COUNT=42

# 只读变量
readonly PI=3.14159

# 引用变量
echo "机器人名称：$NAME"
echo "机器人名称：${NAME}"     # 花括号形式，避免歧义

# 删除变量
unset COUNT

# 环境变量（子进程可见）
export ROS_DOMAIN_ID=42

# 命令替换
CURRENT_DIR=$(pwd)
FILE_COUNT=$(ls -1 | wc -l)
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# 默认值
ROBOT_NAME=${ROBOT_NAME:-"default_robot"}   # 未设置时使用默认值
ROBOT_IP=${ROBOT_IP:="192.168.1.100"}       # 未设置时赋值并使用
```


### 特殊变量

| 变量 | 含义 |
|------|------|
| `$0` | 脚本文件名 |
| `$1` ~ `$9` | 位置参数（第 1 至第 9 个参数） |
| `${10}` | 第 10 个及以后的参数需花括号 |
| `$#` | 参数个数 |
| `$@` | 所有参数（各自独立引用） |
| `$*` | 所有参数（作为一个整体） |
| `$?` | 上一个命令的退出状态码 |
| `$$` | 当前脚本的 PID（进程标识符） |
| `$!` | 最近一个后台进程的 PID |
| `$_` | 上一个命令的最后一个参数 |


### 数组

```bash
# 索引数组
SENSORS=("lidar" "imu" "camera" "gps")

# 访问元素
echo "${SENSORS[0]}"        # lidar
echo "${SENSORS[-1]}"       # gps（最后一个元素）

# 所有元素
echo "${SENSORS[@]}"

# 数组长度
echo "${#SENSORS[@]}"       # 4

# 添加元素
SENSORS+=("ultrasonic")

# 遍历数组
for sensor in "${SENSORS[@]}"; do
    echo "传感器：$sensor"
done

# 数组切片
echo "${SENSORS[@]:1:2}"    # imu camera

# 关联数组（Bash 4.0 及以上）
declare -A SENSOR_PORTS
SENSOR_PORTS[lidar]="/dev/rplidar"
SENSOR_PORTS[imu]="/dev/imu"
SENSOR_PORTS[motor]="/dev/motor_controller"

# 遍历关联数组
for key in "${!SENSOR_PORTS[@]}"; do
    echo "$key -> ${SENSOR_PORTS[$key]}"
done
```


## 条件判断


### if 语句

```bash
# 基本 if-elif-else 结构
if [ "$ROBOT_MODE" = "auto" ]; then
    echo "自动驾驶模式"
elif [ "$ROBOT_MODE" = "manual" ]; then
    echo "手动控制模式"
else
    echo "未知模式：$ROBOT_MODE"
fi

# 使用 [[ ]] 进行更安全的判断（支持模式匹配）
if [[ "$HOSTNAME" == robot-* ]]; then
    echo "这是一台机器人主机"
fi

# 逻辑组合
if [[ -f "/dev/rplidar" && -f "/dev/imu" ]]; then
    echo "所有传感器设备就绪"
fi
```


### 数值比较运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `-eq` | 等于 | `[ "$a" -eq "$b" ]` |
| `-ne` | 不等于 | `[ "$a" -ne "$b" ]` |
| `-gt` | 大于 | `[ "$a" -gt "$b" ]` |
| `-ge` | 大于等于 | `[ "$a" -ge "$b" ]` |
| `-lt` | 小于 | `[ "$a" -lt "$b" ]` |
| `-le` | 小于等于 | `[ "$a" -le "$b" ]` |


### 字符串比较运算符

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `=` / `==` | 相等 | `[ "$a" = "$b" ]` |
| `!=` | 不相等 | `[ "$a" != "$b" ]` |
| `-z` | 长度为零 | `[ -z "$a" ]` |
| `-n` | 长度非零 | `[ -n "$a" ]` |
| `<` | 字典序小于（需 `[[ ]]`） | `[[ "$a" < "$b" ]]` |
| `>` | 字典序大于（需 `[[ ]]`） | `[[ "$a" > "$b" ]]` |


### case 语句

```bash
case "$1" in
    start)
        echo "启动机器人..."
        ;;
    stop)
        echo "停止机器人..."
        ;;
    restart)
        echo "重启机器人..."
        ;;
    status)
        echo "查询状态..."
        ;;
    *)
        echo "用法：$0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```


## 循环


### for 循环

```bash
# 遍历列表
for node in navigation perception localization; do
    echo "启动节点：$node"
done

# C 风格 for 循环
for ((i=0; i<10; i++)); do
    echo "迭代 $i"
done

# 遍历文件
for bag_file in /data/bags/*.bag; do
    echo "处理：$bag_file"
    rosbag info "$bag_file"
done

# 遍历命令输出
for pid in $(pgrep -f "ros2"); do
    echo "ROS 2 进程：$pid"
done

# 使用 seq 生成数列
for i in $(seq 1 5); do
    echo "第 $i 次测试"
done
```


### while 循环

```bash
# 基本 while 循环
counter=0
while [ "$counter" -lt 10 ]; do
    echo "计数：$counter"
    counter=$((counter + 1))
done

# 读取文件逐行处理
while IFS= read -r line; do
    echo "配置项：$line"
done < /home/robot/config/params.txt

# 无限循环
while true; do
    ros2 topic echo /odom --once
    sleep 1
done

# 等待条件满足
while ! ping -c 1 -W 1 192.168.1.100 > /dev/null 2>&1; do
    echo "等待网络连接..."
    sleep 2
done
echo "网络已连接"
```


### until 循环

```bash
# until：条件为假时执行
until ros2 node list 2>/dev/null | grep -q "robot_state_publisher"; do
    echo "等待 robot_state_publisher 启动..."
    sleep 1
done
echo "节点已就绪"
```


## 函数

```bash
# 函数定义
check_sensor() {
    local device="$1"       # local 声明局部变量
    local name="$2"

    if [ -e "$device" ]; then
        echo "[OK] $name ($device) 已连接"
        return 0
    else
        echo "[FAIL] $name ($device) 未检测到"
        return 1
    fi
}

# 调用函数
check_sensor "/dev/rplidar" "激光雷达"
check_sensor "/dev/imu" "惯性测量单元"

# 获取函数返回值
if check_sensor "/dev/rplidar" "激光雷达"; then
    echo "可以启动导航"
fi

# 函数返回字符串（通过 echo 捕获）
get_robot_ip() {
    local interface="${1:-eth0}"
    ip addr show "$interface" | grep -oP 'inet \K[\d.]+'
}

ROBOT_IP=$(get_robot_ip "wlan0")
echo "机器人 IP：$ROBOT_IP"

# 带默认参数的函数
log_message() {
    local level="${1:-INFO}"
    local message="$2"
    echo "[$(date '+%H:%M:%S')] [$level] $message"
}

log_message "INFO" "系统启动"
log_message "ERROR" "传感器连接失败"
```


## 字符串操作

```bash
STR="Hello_Robot_World"

# 字符串长度
echo "${#STR}"                 # 17

# 子字符串截取
echo "${STR:6:5}"              # Robot

# 删除前缀（最短匹配）
FILE="/home/robot/data/map.yaml"
echo "${FILE#*/}"              # home/robot/data/map.yaml

# 删除前缀（最长匹配）
echo "${FILE##*/}"             # map.yaml（相当于 basename）

# 删除后缀（最短匹配）
echo "${FILE%/*}"              # /home/robot/data（相当于 dirname）

# 删除后缀（最长匹配）
echo "${FILE%%/*}"             # （空，因为以 / 开头）

# 替换（第一个匹配）
echo "${STR/Robot/Drone}"      # Hello_Drone_World

# 替换（所有匹配）
echo "${STR//_/-}"             # Hello-Robot-World

# 大小写转换（Bash 4.0 及以上）
NAME="robot"
echo "${NAME^^}"               # ROBOT（全部大写）
echo "${NAME^}"                # Robot（首字母大写）
UPPER="ROBOT"
echo "${UPPER,,}"              # robot（全部小写）
```


## 文件测试运算符

| 运算符 | 含义 |
|--------|------|
| `-e file` | 文件存在 |
| `-f file` | 是普通文件 |
| `-d file` | 是目录 |
| `-L file` | 是符号链接 |
| `-r file` | 可读 |
| `-w file` | 可写 |
| `-x file` | 可执行 |
| `-s file` | 文件大小大于零 |
| `-b file` | 块设备 |
| `-c file` | 字符设备 |
| `-p file` | 命名管道 |
| `-S file` | 套接字文件 |
| `file1 -nt file2` | file1 比 file2 新 |
| `file1 -ot file2` | file1 比 file2 旧 |

使用示例：

```bash
CONFIG="/home/robot/config/nav_params.yaml"

if [ -f "$CONFIG" ] && [ -r "$CONFIG" ]; then
    echo "配置文件存在且可读"
elif [ -d "$CONFIG" ]; then
    echo "错误：这是一个目录而非文件"
else
    echo "错误：配置文件不存在"
fi

# 检查设备文件
if [ -c "/dev/ttyUSB0" ]; then
    echo "串口设备就绪"
fi
```


## 常用单行命令

```bash
# 查找并替换文件内容
grep -rl "old_param" /home/robot/config/ | xargs sed -i 's/old_param/new_param/g'

# 统计代码行数（排除空行和注释）
find src/ -name "*.py" | xargs grep -v -E '^\s*(#|$)' | wc -l

# 批量重命名文件
for f in *.JPG; do mv "$f" "${f%.JPG}.jpg"; done

# 监控文件变化
inotifywait -m /home/robot/config/ -e modify -e create | while read dir event file; do
    echo "[$(date)] $dir$file 发生 $event 事件"
done

# 并行执行命令（使用 xargs）
cat hosts.txt | xargs -P 4 -I {} ssh {} "uptime"

# 查看最近修改的文件
find /home/robot/logs -type f -mmin -30 -ls

# 比较两个目录的差异
diff <(ls dir1/) <(ls dir2/)

# 快速创建指定大小的测试文件
dd if=/dev/zero of=test_100mb.bin bs=1M count=100

# 按列排序 CSV 文件（按第 3 列数值降序）
sort -t',' -k3 -rn data.csv

# 提取 IP 地址
grep -oP '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' /var/log/syslog | sort -u

# 实时跟踪多个日志文件
tail -f /home/robot/logs/*.log

# 计算文件 MD5 校验和
find firmware/ -type f | xargs md5sum > checksums.md5
```


## Bash 正则表达式

Bash 3.0 及以上版本支持 `=~` 运算符进行正则匹配，需要在 `[[ ]]` 中使用。

```bash
# 基本正则匹配
IP="192.168.1.100"
if [[ "$IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "有效的 IP 地址格式"
fi

# 使用捕获组
LOG_LINE="[2026-03-21 14:30:00] ERROR: sensor timeout"
if [[ "$LOG_LINE" =~ \[([0-9-]+)\ ([0-9:]+)\]\ ([A-Z]+):\ (.*) ]]; then
    DATE="${BASH_REMATCH[1]}"      # 2026-03-21
    TIME="${BASH_REMATCH[2]}"      # 14:30:00
    LEVEL="${BASH_REMATCH[3]}"     # ERROR
    MESSAGE="${BASH_REMATCH[4]}"   # sensor timeout
    echo "日期=$DATE 时间=$TIME 级别=$LEVEL 消息=$MESSAGE"
fi

# 验证 ROS 话题名称格式
TOPIC="/robot/cmd_vel"
if [[ "$TOPIC" =~ ^/[a-zA-Z_][a-zA-Z0-9_/]*$ ]]; then
    echo "有效的 ROS 话题名称"
fi

# 提取版本号
VERSION_STR="ROS 2 Humble Hawksbill (22.04)"
if [[ "$VERSION_STR" =~ ([0-9]+)\.([0-9]+) ]]; then
    MAJOR="${BASH_REMATCH[1]}"
    MINOR="${BASH_REMATCH[2]}"
    echo "版本：${MAJOR}.${MINOR}"
fi
```

常用正则表达式元字符：

| 元字符 | 含义 | 示例 |
|--------|------|------|
| `.` | 任意单个字符 | `a.c` 匹配 abc、aXc |
| `*` | 前一字符零次或多次 | `ab*c` 匹配 ac、abc、abbc |
| `+` | 前一字符一次或多次 | `ab+c` 匹配 abc、abbc |
| `?` | 前一字符零次或一次 | `ab?c` 匹配 ac、abc |
| `^` | 行首 | `^Error` |
| `$` | 行尾 | `done$` |
| `[abc]` | 字符集合 | `[aeiou]` 匹配元音 |
| `[^abc]` | 排除字符集合 | `[^0-9]` 匹配非数字 |
| `\d` | 数字（等价于 `[0-9]`） | |
| `\w` | 单词字符 | |
| `\s` | 空白字符 | |
| `{n,m}` | 重复 n 到 m 次 | `a{2,4}` 匹配 aa、aaa、aaaa |
| `(...)` | 分组和捕获 | |
| `\|` | 或 | `cat\|dog` |


## ShellCheck 静态分析

ShellCheck 是一款强大的 Shell 脚本静态分析工具，能自动检测常见错误和不良实践。

```bash
# 安装 ShellCheck
sudo apt install shellcheck

# 检查脚本
shellcheck my_script.sh

# 检查时排除特定规则
shellcheck -e SC2034,SC2086 my_script.sh

# 指定 Shell 类型
shellcheck --shell=bash my_script.sh

# 输出为 JSON 格式（用于 CI 集成）
shellcheck -f json my_script.sh
```

ShellCheck 常见警告及修复：

| 编号 | 问题 | 修复前 | 修复后 |
|------|------|--------|--------|
| SC2086 | 变量未加引号 | `rm $file` | `rm "$file"` |
| SC2046 | 命令替换未加引号 | `rm $(find . -name "*.tmp")` | 改用 `find ... -exec` |
| SC2034 | 变量已赋值但未使用 | `unused_var=1` | 删除或使用该变量 |
| SC2164 | `cd` 可能失败 | `cd /some/dir` | `cd /some/dir \|\| exit 1` |
| SC2155 | 声明和赋值应分开 | `local x=$(cmd)` | `local x; x=$(cmd)` |


## 编码风格指南

以下风格建议参考 Google Shell Style Guide，适用于机器人项目的脚本编写。


### 文件头

```bash
#!/bin/bash
# 文件名：deploy_robot.sh
# 描述：机器人软件部署脚本
# 作者：Team Name
# 日期：2026-03-21
set -euo pipefail    # 严格模式：出错即退出，未定义变量报错，管道错误传播
```


### 命名规范

```bash
# 变量：小写下划线分隔
robot_name="nav_bot"
sensor_count=5

# 常量和环境变量：大写下划线分隔
readonly MAX_RETRY=3
export ROS_DOMAIN_ID=42

# 函数：小写下划线分隔，使用动词开头
start_navigation() { ... }
check_sensor_status() { ... }
get_robot_ip() { ... }
```


### 最佳实践

```bash
# 1. 始终引用变量
echo "文件：$file"           # 不好（在某些情况下会出错）
echo "文件：${file}"         # 较好
echo "文件：\"${file}\""     # 路径含空格时最安全

# 2. 使用 $() 替代反引号
date=$(date +%Y%m%d)         # 推荐
date=`date +%Y%m%d`          # 不推荐（嵌套困难）

# 3. 使用 [[ ]] 替代 [ ]
if [[ -f "$file" ]]; then    # 推荐（更安全，支持更多特性）
if [ -f "$file" ]; then      # 不推荐

# 4. 算术运算使用 $(())
result=$((a + b * c))        # 推荐
result=$(expr $a + $b)       # 不推荐

# 5. 函数使用 local 声明局部变量
my_func() {
    local input="$1"         # 避免污染全局作用域
    local result
    result=$(process "$input")
    echo "$result"
}

# 6. 提供有意义的退出码
EXIT_SUCCESS=0
EXIT_CONFIG_ERROR=1
EXIT_DEVICE_ERROR=2
EXIT_NETWORK_ERROR=3

# 7. 使用 trap 确保清理
cleanup() {
    rm -f "$TEMP_FILE"
    echo "清理完成"
}
trap cleanup EXIT
```


## 推荐工具与资源

| 类别 | 工具/资源 | 说明 |
|------|-----------|------|
| 静态分析 | [ShellCheck](https://www.shellcheck.net/) | Shell 脚本 lint 工具 |
| 格式化 | [shfmt](https://github.com/mvdan/sh) | Shell 脚本自动格式化 |
| 调试 | `bash -x script.sh` | 逐行打印执行过程 |
| 调试 | `set -x` / `set +x` | 在脚本内部开关调试输出 |
| 在线工具 | [ExplainShell](https://explainshell.com/) | 命令行语法在线解析 |
| 参考手册 | [Bash Reference Manual](https://www.gnu.org/software/bash/manual/) | GNU 官方手册 |
| 教程 | [The Linux Command Line](https://linuxcommand.org/) | 入门教材 |
| 高级教程 | [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/) | 进阶脚本编程 |
| 代码风格 | [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) | Google 编码规范 |
| 速查表 | [devhints.io/bash](https://devhints.io/bash) | Bash 语法速查 |

调试技巧：

```bash
# 方法 1：命令行开启调试
bash -x ./my_script.sh

# 方法 2：在脚本中开关调试
set -x          # 开启调试输出
# ... 需要调试的代码 ...
set +x          # 关闭调试输出

# 方法 3：使用 PS4 自定义调试前缀
export PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
bash -x ./my_script.sh

# 方法 4：使用 trap DEBUG 逐行追踪
trap 'echo "DEBUG: 行 $LINENO: $BASH_COMMAND"' DEBUG
```


## 参考资料

- [GNU Bash Manual](https://www.gnu.org/software/bash/manual/bash.html) —— Bash 官方完整手册
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) —— Google Shell 编码风格指南
- [ShellCheck Wiki](https://github.com/koalaman/shellcheck/wiki) —— ShellCheck 规则详解
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/) —— 高级 Bash 脚本编程指南
- [Bash Hackers Wiki](https://wiki.bash-hackers.org/) —— Bash 社区知识库
- [The Linux Documentation Project](https://tldp.org/) —— Linux 文档项目
