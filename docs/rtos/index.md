# RTOS

目前市场上常见的商用实时操作系统有：

- uCosII / uCosIII | Micrium
- FreeRTOS
- Nucleus RTOS | Mentor Graphics
- RTLinux (需要MMU支持)
- QNX (需要MMU支持)
- VxWorks | WindRiver
- eCos
- RTEMS

(国产的另有：RT-Thread和DJYOS.)

其中除了FreeRTOS, RTEMS和RTLinux是免费的之外，其余RTOS都是需要商业授权的。uCos II和FreeRTOS是平时接触比较多的RTOS，相关资料比较多。而VxWorks是安全性公认最佳的，用于航空航天、轨道交通和卫星的应用。如果系统中需要使用复杂的文件、数据库、网络等功能，那么以Linux为基础的RTLinux是比较好的选择；但是如果系统对实时性和确定性的要求非常高，那么可以使用较为简单的RTOS（如 uCosII），再根据需要开发通信协议或者软件包。总体上来说，操作系统的复杂性是与应用软件的复杂性一致的。同时，功能上更复杂的RTOS对硬件系统资源的需求也会更高。


## 参考资料
1. 戴晓天, [RTOS操作系统杂谈](https://www.yfworld.com/?p=2911)，云飞机器人实验室
