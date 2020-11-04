# Nvidia Jetson

Jetson是英伟达推出的面向嵌入式计算的硬件平台，包括：

- Jetson Nano
- Jetson TX1
- Jetson TX2
- Jetson Xaiver
- Jetson Xavier Nx



Jetson各个型号的对比如下：

| Hardware feature \ Jetson module | Jetson Nano                                        | Jetson TX1                                         | Jetson TX2/TX2i                                       | Jetson Xavier                         | Jetson Xavier Nx                                             |
| -------------------------------- | -------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| CPU (ARM)                        | 4-core ARM A57 @ 1.43 GHz                          | 4-core ARM Cortex A57 @ 1.73 GHz                   | 4-core ARM Cortex-A57 @ 2 GHz, 2-core Denver2 @ 2 GHz | 8-core ARM Carmel v.8.2 @ 2.26 GHz    | 6-core NVIDIA Carmel ARM®v8.2 64-bit CPU                     |
| GPU                              | 128-core Maxwell @ 921 MHz                         | 256-core Maxwell @ 998 MHz                         | 256-core Pascal @ 1.3 GHz                             | 512-core Volta @ 1.37 GHz             | 384-core NVIDIA Volta™ GPU                                   |
| Memory                           | 4 GB LPDDR4, 25.6 GB/s                             | 4 GB LPDDR4, 25.6 GB/s                             | 8 GB 128-bit LPDDR4, 58.3 GB/s                        | 16 GB 256-bit LPDDR4, 137 GB/s        | 8 GB 128-bit LPDDR4x @ 1600 MHz51.2GB/s                      |
| Storage                          | MicroSD                                            | 16 GB eMMC 5.1                                     | 32 GB eMMC 5.1                                        | 32 GB eMMC 5.1                        | 16 GB eMMC 5.1                                               |
| Tensor cores                     | --                                                 | --                                                 | --                                                    | 64                                    | 48                                                           |
| Video encoding                   | (1x) 4Kp30, (2x) 1080p60, (4x) 1080p30             | (1x) 4Kp30, (2x) 1080p60, (4x) 1080p30             | (1x) 4Kp60, (3x) 4Kp30, (4x) 1080p60, (8x) 1080p30    | (4x) 4Kp60, (8x) 4Kp30, (32x) 1080p30 | 2x464MP/sec (HEVC)2x 4K @ 30 (HEVC)6x 1080p @ 60 (HEVC)14x 1080p @ 30 (HEVC) |
| Video decoding                   | (1x) 4Kp60, (2x) 4Kp30, (4x) 1080p60, (8x) 1080p30 | (1x) 4Kp60, (2x) 4Kp30, (4x) 1080p60, (8x) 1080p30 | (2x) 4Kp60, (4x) 4Kp30, (7x) 1080p60                  | (2x) 8Kp30, (6x) 4Kp60, (12x) 4Kp30   | 2x690MP/sec (HEVC)2x 4K @ 60 (HEVC)4x 4K @ 30 (HEVC)12x 1080p @ 60 (HEVC)32x 1080p @ 30 (HEVC)16x 1080p @ 30 (H.264) |
| USB                              | (4x) USB 3.0 + Micro-USB 2.0                       | (1x) USB 3.0 + (1x) USB 2.0                        | (1x) USB 3.0 + (1x) USB 2.0                           | (3x) USB 3.1 + (4x) USB 2.0           |                                                              |
| PCI-Express lanes                | 4 lanes PCIe Gen 2                                 | 5 lanes PCIe Gen 2                                 | 5 lanes PCIe Gen 2                                    | 16 lanes PCIe Gen 4                   | 1 x1 + 1x4(PCIe Gen3, Root Port & Endpoint)                  |
| Power                            | 5W / 10W                                           | 10W                                                | 7.5W / 15W                                            | 10W / 15W / 30W                       | 10W / 15W                                                    |




---

**参考资料：**

1. Benchmark comparison for Jetson Nano, TX1, TX2 and AGX Xavier, https://www.fastcompression.com/blog/jetson-benchmark-comparison.htm
2. Jetson Xavier NX, https://developer.nvidia.com/embedded/jetson-xavier-nx

---

**本条目贡献者**：

- automaticdai

---

(本条目需要完善，[立刻参与知识公共编辑](/how-to-contribute/))