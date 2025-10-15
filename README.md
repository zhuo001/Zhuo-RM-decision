# 🤖 Zhuo-RM-decision

卓越RM机器人决策系统 - 基于P100R深度SLAM的实时避障与路径规划

## 📋 项目概述

本项目是卓越RM机器人的**决策系统核心**，运行在车载Ubuntu电脑上，负责：

- 🎥 实时获取Berxel P100R深度相机数据
- 🚧 基于深度图的障碍物检测
- 🗺️ SLAM地图构建与更新
- 🧭 路径规划与导航决策
- 📡 与控制系统的通信接口

## ✨ 主要功能

### 1. 深度SLAM避障
- ✅ 实时深度图处理 (640x400 @ 30fps)
- ✅ 自适应障碍物检测
- ✅ 可导航区域分析
- ✅ 动态路径规划建议

### 2. P100R相机集成
- ✅ 彩色流 (1920x1080)
- ✅ 深度流 (640x400)
- ✅ 毫米级深度精度
- ✅ 并行模式流处理

### 3. 决策输出
- 导航方向建议 (forward/left/right/stop)
- 障碍物位置与距离
- 占据栅格地图
- 实时性能统计

## 🖥️ 系统要求

### 硬件
- **计算平台**: 车载Ubuntu电脑 (推荐 4核CPU + 4GB RAM)
- **深度相机**: Berxel P100R 3D Camera
- **接口**: USB 3.0 或更高

### 软件
- **操作系统**: Ubuntu 20.04 / 22.04 LTS
- **Python**: 3.8+
- **Berxel SDK**: 已安装 (libBerxelHawk.so + 头文件)

## 🚀 快速开始

### 1. 克隆仓库

```bash
# 在车载Ubuntu电脑上
git clone https://github.com/zhuo001/Zhuo-RM-decision.git
cd Zhuo-RM-decision
```

### 2. 配置环境

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 编译Berxel封装

```bash
# 编译C++扩展 (需要SDK已安装)
python setup.py build_ext --inplace

# 验证编译
ls berxel_wrapper*.so  # 应该看到编译好的.so文件
```

### 4. 运行决策系统

```bash
# 启动主程序
python main_decision.py

# 或带参数启动
python main_decision.py --depth-threshold 1.5 --fps 30
```

## 📁 项目结构

```
Zhuo-RM-decision/
├── README.md                      # 本文件
├── DEPLOYMENT.md                  # 部署指南
├── requirements.txt               # Python依赖
├── setup.py                       # C++扩展编译配置
│
├── src/                           # 源代码
│   ├── depth_slam_obstacle.py    # 核心SLAM算法
│   ├── berxel_camera.py          # 相机Python接口
│   └── berxel_wrapper.cpp        # 相机C++封装
│
├── include/                       # SDK头文件 (需复制)
│   ├── BerxelHawkContext.h
│   ├── BerxelHawkDevice.h
│   ├── BerxelHawkFrame.h
│   └── BerxelHawkDefines.h
│
├── libs/                          # SDK库文件 (需复制)
│   └── libBerxelHawk.so          # Linux动态库
│
├── main_decision.py               # 主程序入口
├── test_camera.py                 # 相机测试脚本
└── test_slam.py                   # SLAM测试脚本
```

## 🔧 配置说明

### SDK路径配置

如果Berxel SDK安装在自定义路径，修改 `setup.py`:

```python
include_dirs = [
    np.get_include(),
    '/usr/local/include/berxel',  # SDK头文件路径
]
library_dirs = [
    '/usr/local/lib',              # SDK库文件路径
]
```

### 相机参数调整

在 `main_decision.py` 中调整:

```python
slam = DepthSLAMObstacleDetector(
    depth_threshold_near=0.5,      # 近距离阈值 (米)
    depth_threshold_far=5.0,       # 远距离阈值 (米)
    obstacle_height_min=0.1,       # 最小障碍物高度 (米)
    grid_resolution=0.05           # 网格分辨率 (米)
)
```

## 📊 性能指标

在标准车载电脑上的实测性能：

| 指标 | 数值 |
|------|------|
| 处理帧率 | 25-30 FPS |
| 单帧处理时间 | 30-40 ms |
| 深度精度 | ±2mm @ 1m |
| 检测距离 | 0.5m - 5.0m |
| CPU占用 | ~30% (4核) |
| 内存占用 | ~300 MB |

## 🐛 故障排查

### 1. 找不到相机

```bash
# 检查USB连接
lsusb | grep Berxel

# 检查设备权限
sudo chmod 666 /dev/bus/usb/*/*
```

### 2. 编译失败

```bash
# 检查SDK是否安装
ldconfig -p | grep BerxelHawk

# 检查头文件
find /usr -name "BerxelHawkContext.h"
```

### 3. ImportError: berxel_wrapper

```bash
# 确认.so文件存在
ls -l berxel_wrapper*.so

# 检查Python路径
python -c "import sys; print(sys.path)"

# 重新编译
python setup.py build_ext --inplace --force
```

## 📡 与其他系统集成

### 与控制系统通信

```python
# 在 main_decision.py 中
from control_interface import ControlClient

client = ControlClient('tcp://192.168.1.100:5555')

# 发送决策
client.send_decision({
    'direction': 'forward',
    'speed': 0.5,
    'obstacles': obstacle_list
})
```

### ROS2集成 (可选)

```bash
# 安装ROS2桥接
pip install rclpy

# 运行ROS2节点
python ros2_decision_node.py
```

## 📝 开发路线图

- [x] 基础深度SLAM算法
- [x] P100R相机SDK封装
- [x] 实时障碍物检测
- [ ] 高级路径规划 (A*, DWA)
- [ ] 占据栅格地图持久化
- [ ] 多传感器融合
- [ ] ROS2完整支持
- [ ] 性能优化 (GPU加速)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 👥 团队

卓越RM机器人团队 - 2025

---

**部署前必读**: 请参考 [DEPLOYMENT.md](DEPLOYMENT.md) 了解完整部署流程！
