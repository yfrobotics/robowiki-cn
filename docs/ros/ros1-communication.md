# ROS 1 通信机制

!!! note "引言"
    ROS 1 提供了三种核心通信模式：话题 (Topics)、服务 (Services) 和动作 (Actions)，分别适用于异步数据流、同步请求-响应和长时间异步任务。本文通过完整的代码示例，深入讲解每种通信机制的原理与使用方法，并介绍参数服务器、自定义消息、Nodelet 零拷贝传输等进阶主题。


## 话题通信 (Topics)

话题是 ROS 1 中最常用的通信方式，采用发布-订阅 (publish-subscribe) 模式。发布者和订阅者之间是多对多的松耦合关系，通信完全异步。


### C++ 发布者示例

```cpp
// src/talker.cpp
#include <ros/ros.h>
#include <std_msgs/String.h>
#include <sstream>

int main(int argc, char **argv)
{
    ros::init(argc, argv, "talker");
    ros::NodeHandle nh;

    // 创建发布者：话题名 "chatter"，消息队列长度 10
    ros::Publisher pub = nh.advertise<std_msgs::String>("chatter", 10);

    ros::Rate loop_rate(10);  // 10 Hz

    int count = 0;
    while (ros::ok())
    {
        std_msgs::String msg;
        std::stringstream ss;
        ss << "Hello ROS " << count++;
        msg.data = ss.str();

        ROS_INFO("发布: %s", msg.data.c_str());
        pub.publish(msg);

        ros::spinOnce();
        loop_rate.sleep();
    }
    return 0;
}
```


### C++ 订阅者示例

```cpp
// src/listener.cpp
#include <ros/ros.h>
#include <std_msgs/String.h>

void chatterCallback(const std_msgs::String::ConstPtr &msg)
{
    ROS_INFO("收到: %s", msg->data.c_str());
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "listener");
    ros::NodeHandle nh;

    // 创建订阅者：话题名 "chatter"，消息队列长度 10
    ros::Subscriber sub = nh.subscribe("chatter", 10, chatterCallback);

    ros::spin();  // 阻塞等待回调
    return 0;
}
```


### Python 发布者与订阅者

```python
#!/usr/bin/env python
# scripts/talker.py
import rospy
from std_msgs.msg import String

def talker():
    rospy.init_node('talker', anonymous=True)
    pub = rospy.Publisher('chatter', String, queue_size=10)
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        msg = String()
        msg.data = f"Hello ROS {rospy.get_time():.2f}"
        rospy.loginfo(f"发布: {msg.data}")
        pub.publish(msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
```

```python
#!/usr/bin/env python
# scripts/listener.py
import rospy
from std_msgs.msg import String

def callback(msg):
    rospy.loginfo(f"收到: {msg.data}")

def listener():
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber('chatter', String, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()
```


### 消息队列与丢失

`queue_size` 参数控制消息缓冲区大小。当订阅者处理速度慢于发布速度时：

- 队列满后，旧消息会被丢弃
- 传感器数据通常设为 `1`（只保留最新值）
- 命令数据通常设为 `10` 或更大（避免丢失）


## 服务通信 (Services)

服务提供同步的请求-响应模式，适用于需要即时返回结果的场景，如查询机器人状态、触发特定动作等。


### 定义服务类型

首先创建 `.srv` 文件，`---` 分隔请求和响应：

```
# srv/AddTwoInts.srv
int64 a
int64 b
---
int64 sum
```


### C++ 服务端

```cpp
// src/add_server.cpp
#include <ros/ros.h>
#include <my_robot_pkg/AddTwoInts.h>

bool add(my_robot_pkg::AddTwoInts::Request &req,
         my_robot_pkg::AddTwoInts::Response &res)
{
    res.sum = req.a + req.b;
    ROS_INFO("请求: %ld + %ld = %ld", req.a, req.b, res.sum);
    return true;
}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "add_server");
    ros::NodeHandle nh;

    ros::ServiceServer service = nh.advertiseService("add_two_ints", add);
    ROS_INFO("服务就绪");
    ros::spin();

    return 0;
}
```


### C++ 客户端

```cpp
// src/add_client.cpp
#include <ros/ros.h>
#include <my_robot_pkg/AddTwoInts.h>

int main(int argc, char **argv)
{
    ros::init(argc, argv, "add_client");
    ros::NodeHandle nh;

    // 等待服务可用
    ros::service::waitForService("add_two_ints");

    ros::ServiceClient client =
        nh.serviceClient<my_robot_pkg::AddTwoInts>("add_two_ints");

    my_robot_pkg::AddTwoInts srv;
    srv.request.a = 3;
    srv.request.b = 5;

    if (client.call(srv))
    {
        ROS_INFO("结果: %ld", srv.response.sum);
    }
    else
    {
        ROS_ERROR("服务调用失败");
        return 1;
    }
    return 0;
}
```


### Python 服务端与客户端

```python
#!/usr/bin/env python
# scripts/add_server.py
import rospy
from my_robot_pkg.srv import AddTwoInts, AddTwoIntsResponse

def handle_add(req):
    result = req.a + req.b
    rospy.loginfo(f"请求: {req.a} + {req.b} = {result}")
    return AddTwoIntsResponse(result)

def server():
    rospy.init_node('add_server')
    rospy.Service('add_two_ints', AddTwoInts, handle_add)
    rospy.loginfo("服务就绪")
    rospy.spin()

if __name__ == '__main__':
    server()
```

```python
#!/usr/bin/env python
# scripts/add_client.py
import rospy
from my_robot_pkg.srv import AddTwoInts

def client():
    rospy.init_node('add_client')
    rospy.wait_for_service('add_two_ints')

    try:
        add = rospy.ServiceProxy('add_two_ints', AddTwoInts)
        resp = add(3, 5)
        rospy.loginfo(f"结果: {resp.sum}")
    except rospy.ServiceException as e:
        rospy.logerr(f"服务调用失败: {e}")

if __name__ == '__main__':
    client()
```


## 动作通信 (Actions)

动作 (actionlib) 用于执行需要较长时间的任务，支持目标发送、进度反馈和取消操作，是对服务模式的扩展。


### 定义动作类型

创建 `.action` 文件，由目标、结果和反馈三部分组成：

```
# action/CountTo.action
# Goal（目标）
int32 target_number
---
# Result（结果）
int32 final_count
string message
---
# Feedback（反馈）
int32 current_count
float32 percent_complete
```


### Python 动作服务端

```python
#!/usr/bin/env python
# scripts/count_server.py
import rospy
import actionlib
from my_robot_pkg.msg import CountToAction, CountToFeedback, CountToResult

class CountServer:
    def __init__(self):
        self.server = actionlib.SimpleActionServer(
            'count_to',
            CountToAction,
            execute_cb=self.execute,
            auto_start=False
        )
        self.server.start()
        rospy.loginfo("计数动作服务器已启动")

    def execute(self, goal):
        feedback = CountToFeedback()
        result = CountToResult()
        rate = rospy.Rate(2)  # 2 Hz

        for i in range(1, goal.target_number + 1):
            # 检查是否被取消
            if self.server.is_preempt_requested():
                rospy.loginfo("动作被取消")
                self.server.set_preempted()
                return

            # 发送反馈
            feedback.current_count = i
            feedback.percent_complete = (i / goal.target_number) * 100.0
            self.server.publish_feedback(feedback)
            rospy.loginfo(f"进度: {feedback.percent_complete:.0f}%")
            rate.sleep()

        # 发送结果
        result.final_count = goal.target_number
        result.message = "计数完成"
        self.server.set_succeeded(result)

if __name__ == '__main__':
    rospy.init_node('count_server')
    server = CountServer()
    rospy.spin()
```


### Python 动作客户端

```python
#!/usr/bin/env python
# scripts/count_client.py
import rospy
import actionlib
from my_robot_pkg.msg import CountToAction, CountToGoal

def feedback_cb(feedback):
    rospy.loginfo(f"当前进度: {feedback.percent_complete:.0f}%")

def client():
    rospy.init_node('count_client')
    client = actionlib.SimpleActionClient('count_to', CountToAction)
    client.wait_for_server()

    goal = CountToGoal()
    goal.target_number = 10

    # 发送目标并注册反馈回调
    client.send_goal(goal, feedback_cb=feedback_cb)

    # 等待结果，超时 30 秒
    finished = client.wait_for_result(rospy.Duration(30.0))

    if finished:
        result = client.get_result()
        rospy.loginfo(f"结果: {result.message}，最终计数: {result.final_count}")
    else:
        rospy.logwarn("动作超时，正在取消")
        client.cancel_goal()

if __name__ == '__main__':
    client()
```


## 参数服务器 (Parameter Server)

参数服务器是一个集中式的键值存储系统，由 ROS Master 维护，适用于存储配置参数。

```python
#!/usr/bin/env python
import rospy

rospy.init_node('param_demo')

# 设置参数
rospy.set_param('/robot/max_speed', 1.5)
rospy.set_param('/robot/name', 'my_bot')
rospy.set_param('/robot/sensors', ['lidar', 'camera', 'imu'])

# 获取参数（带默认值）
max_speed = rospy.get_param('/robot/max_speed', 1.0)
name = rospy.get_param('/robot/name', 'default_bot')

# 检查参数是否存在
if rospy.has_param('/robot/max_speed'):
    rospy.loginfo(f"最大速度: {max_speed}")

# 删除参数
rospy.delete_param('/robot/name')
```

使用 YAML 文件批量加载参数：

```yaml
# config/robot_params.yaml
robot:
  max_speed: 1.5
  max_angular_speed: 0.8
  base_frame: "base_link"
  sensors:
    lidar:
      topic: "/scan"
      range_max: 30.0
    camera:
      topic: "/camera/image_raw"
      resolution: [640, 480]
```

```xml
<!-- 在 launch 文件中加载参数 -->
<launch>
  <rosparam file="$(find my_robot_pkg)/config/robot_params.yaml" command="load"/>
  <node pkg="my_robot_pkg" type="robot_node" name="robot" output="screen"/>
</launch>
```


## 常用消息类型

ROS 1 提供了丰富的标准消息类型，覆盖大多数机器人应用场景：

| 包名 | 常用消息 | 用途 |
|------|----------|------|
| `std_msgs` | `String`, `Int32`, `Float64`, `Bool`, `Header` | 基础数据类型 |
| `geometry_msgs` | `Twist`, `Pose`, `PoseStamped`, `Transform`, `Wrench` | 几何和运动学 |
| `sensor_msgs` | `Image`, `LaserScan`, `PointCloud2`, `Imu`, `JointState` | 传感器数据 |
| `nav_msgs` | `Odometry`, `Path`, `OccupancyGrid`, `MapMetaData` | 导航数据 |
| `visualization_msgs` | `Marker`, `MarkerArray` | RViz 可视化 |
| `trajectory_msgs` | `JointTrajectory`, `MultiDOFJointTrajectory` | 轨迹规划 |
| `actionlib_msgs` | `GoalStatus`, `GoalID` | 动作状态 |


## 自定义消息创建

### 定义消息文件

```
# msg/RobotStatus.msg
Header header
string robot_name
float64 battery_level        # 电池电量百分比
geometry_msgs/Twist velocity # 当前速度
bool is_emergency_stop       # 是否急停
uint8 operating_mode         # 0: 手动, 1: 自动, 2: 遥控

uint8 MODE_MANUAL = 0
uint8 MODE_AUTO = 1
uint8 MODE_TELEOP = 2
```


### 配置编译

在 `package.xml` 中添加依赖：

```xml
<build_depend>message_generation</build_depend>
<exec_depend>message_runtime</exec_depend>
```

在 `CMakeLists.txt` 中配置：

```cmake
find_package(catkin REQUIRED COMPONENTS
  std_msgs
  geometry_msgs
  message_generation
)

add_message_files(FILES RobotStatus.msg)

generate_messages(DEPENDENCIES std_msgs geometry_msgs)

catkin_package(CATKIN_DEPENDS message_runtime std_msgs geometry_msgs)
```

编译后，可以在 C++ 中通过 `#include <my_robot_pkg/RobotStatus.h>` 使用，在 Python 中通过 `from my_robot_pkg.msg import RobotStatus` 使用。


## Nodelet：零拷贝传输

Nodelet 是 ROS 1 提供的零拷贝 (zero-copy) 通信机制。普通节点之间的话题通信需要序列化和反序列化消息数据，而 Nodelet 通过在同一进程中运行多个算法模块，使用共享指针传递数据，避免了不必要的拷贝开销。

Nodelet 特别适用于高带宽数据处理管线，如图像处理和点云处理。


### Nodelet 类实现

```cpp
// src/image_filter_nodelet.cpp
#include <nodelet/nodelet.h>
#include <pluginlib/class_list_macros.h>
#include <ros/ros.h>
#include <sensor_msgs/Image.h>

namespace my_robot_pkg
{
class ImageFilterNodelet : public nodelet::Nodelet
{
public:
    virtual void onInit()
    {
        ros::NodeHandle &nh = getNodeHandle();
        ros::NodeHandle &pnh = getPrivateNodeHandle();

        // 使用共享指针，实现零拷贝
        sub_ = nh.subscribe("camera/image_raw", 1,
                            &ImageFilterNodelet::imageCb, this);
        pub_ = nh.advertise<sensor_msgs::Image>("camera/image_filtered", 1);

        NODELET_INFO("图像滤波 Nodelet 已初始化");
    }

private:
    void imageCb(const sensor_msgs::Image::ConstPtr &msg)
    {
        // 处理图像（零拷贝接收）
        sensor_msgs::Image::Ptr output(new sensor_msgs::Image(*msg));
        // ... 滤波处理 ...
        pub_.publish(output);
    }

    ros::Subscriber sub_;
    ros::Publisher pub_;
};
}  // namespace my_robot_pkg

PLUGINLIB_EXPORT_CLASS(my_robot_pkg::ImageFilterNodelet, nodelet::Nodelet)
```


### Nodelet launch 配置

```xml
<launch>
  <!-- 创建 Nodelet Manager -->
  <node pkg="nodelet" type="nodelet" name="manager"
        args="manager" output="screen"/>

  <!-- 加载 Nodelet 到 Manager -->
  <node pkg="nodelet" type="nodelet" name="image_filter"
        args="load my_robot_pkg/ImageFilterNodelet manager"
        output="screen"/>
</launch>
```


## 通信模式对比

| 特性 | 话题 (Topics) | 服务 (Services) | 动作 (Actions) |
|------|---------------|-----------------|----------------|
| 通信模式 | 发布-订阅 | 请求-响应 | 目标-反馈-结果 |
| 同步性 | 异步 | 同步（阻塞） | 异步（非阻塞） |
| 关系 | 多对多 | 一对一 | 一对一 |
| 实时反馈 | 不适用 | 无 | 有（Feedback） |
| 可取消 | 不适用 | 否 | 是 |
| 适用场景 | 传感器数据流、状态广播 | 查询、短耗时操作 | 导航、抓取等长耗时任务 |
| 典型频率 | 1 Hz ~ 1000 Hz | 按需调用 | 按任务触发 |
| 数据定义 | `.msg` 文件 | `.srv` 文件 | `.action` 文件 |

选择通信模式的经验法则：

- **持续的数据流**（传感器读数、机器人状态）：使用话题
- **一次性查询或触发**（获取地图、切换模式）：使用服务
- **需要监控进度的长时间任务**（导航到目标点、执行抓取）：使用动作


## 参考资料

- [ROS Wiki: Topics](http://wiki.ros.org/Topics)
- [ROS Wiki: Services](http://wiki.ros.org/Services)
- [ROS Wiki: actionlib](http://wiki.ros.org/actionlib)
- [ROS Wiki: Parameter Server](http://wiki.ros.org/Parameter%20Server)
- [ROS Wiki: msg](http://wiki.ros.org/msg)
- [ROS Wiki: Nodelet](http://wiki.ros.org/nodelet)
- [ROS Tutorials: Writing a Publisher/Subscriber](http://wiki.ros.org/ROS/Tutorials/WritingPublisherSubscriber%28c%2B%2B%29)
