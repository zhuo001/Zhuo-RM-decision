# 🚀 Zhuo-RM-decision 部署指南

完整的Ubuntu车载系统部署流程

## 📋 目录

1. [系统要求](#系统要求)
2. [SDK安装](#sdk安装)
3. [项目部署](#项目部署)
4. [编译与测试](#编译与测试)
5. [故障排查](#故障排查)
6. [性能优化](#性能优化)

---

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|---------|----------|
| CPU | 4核 @ 2.0GHz | 6核 @ 2.5GHz+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 16GB可用空间 | 32GB+ SSD |
| USB | USB 3.0 | USB 3.0/3.1 |
| 相机 | Berxel P100R | - |

### 软件要求

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| Ubuntu | 20.04 / 22.04 LTS | 推荐22.04 |
| Python | 3.8+ | 推荐3.10+ |
| GCC | 7.0+ | C++编译器 |
| CMake | 3.10+ | (如果需要) |
| Git | 2.0+ | 版本控制 |

---

## SDK安装

### 方法1: 从官方包安装

```bash
# 1. 下载Berxel SDK for Linux
# 访问: https://www.berxel.com/downloads
# 或联系供应商获取SDK

# 2. 解压SDK
mkdir -p ~/berxel_sdk
tar -xzf BerxelSDK_Linux_v*.tar.gz -C ~/berxel_sdk

# 3. 安装库文件
sudo cp ~/berxel_sdk/libs/libBerxelHawk.so /usr/local/lib/
sudo ldconfig

# 4. 安装头文件
sudo mkdir -p /usr/local/include/berxel
sudo cp ~/berxel_sdk/include/*.h /usr/local/include/berxel/

# 5. 验证安装
ldconfig -p | grep BerxelHawk
# 应该看到: libBerxelHawk.so ...
```

### 方法2: 从仓库复制

如果SDK文件已包含在项目中:

```bash
cd Zhuo-RM-decision

# 确认文件存在
ls include/  # 应该看到 BerxelHawk*.h
ls libs/     # 应该看到 libBerxelHawk.so

# 设置库路径
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/libs

# 添加到 ~/.bashrc 使其永久生效
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$(pwd)/libs" >> ~/.bashrc
```

### 配置USB权限

```bash
# 创建udev规则
sudo nano /etc/udev/rules.d/99-berxel.rules

# 添加以下内容:
# Berxel P100R Camera
SUBSYSTEM=="usb", ATTRS{idVendor}=="2bc5", ATTRS{idProduct}=="*", MODE="0666"

# 重新加载规则
sudo udevadm control --reload-rules
sudo udevadm trigger

# 或临时修改权限(重启后失效)
sudo chmod 666 /dev/bus/usb/*/*
```

---

## 项目部署

### 1. 克隆仓库

```bash
cd ~/
git clone https://github.com/zhuo001/Zhuo-RM-decision.git
cd Zhuo-RM-decision
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### 3. 安装Python依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 如果有网络问题,使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 安装系统依赖

```bash
# OpenCV依赖
sudo apt update
sudo apt install -y \
    python3-dev \
    libopencv-dev \
    python3-opencv \
    libusb-1.0-0-dev \
    build-essential
```

---

## 编译与测试

### 1. 编译Berxel扩展

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 编译C++扩展
python setup.py build_ext --inplace

# 验证编译结果
ls berxel_wrapper*.so
# 应该看到: berxel_wrapper.cpython-*.so

# 测试导入
python -c "import berxel_wrapper; print('✅ 编译成功')"
```

### 2. 测试相机

```bash
# 基础功能测试
python test_camera.py --mode basic

# 实时测试
python test_camera.py --mode realtime
```

预期输出:
```
✅ 相机初始化成功
✅ 彩色图读取成功: (1080, 1920, 3)
✅ 深度图读取成功: (400, 640)
✅ 平均帧率: 28.5 FPS
```

### 3. 测试SLAM算法

```bash
# 模拟数据测试
python test_slam.py --mode sim

# 真实相机测试
python test_slam.py --mode camera
```

### 4. 运行主程序

```bash
# 基础运行
python main_decision.py

# 自定义参数
python main_decision.py --depth-threshold 2.0 --fps 25

# 无可视化运行(提升性能)
python main_decision.py --no-viz
```

---

## 故障排查

### 问题1: 找不到相机

**症状**: `No Berxel camera found`

**解决**:
```bash
# 1. 检查USB连接
lsusb | grep -i berxel
# 或
lsusb | grep 2bc5

# 2. 检查设备权限
ls -l /dev/bus/usb/*/*
# 所有设备应该是 crw-rw-rw-

# 3. 重新插拔USB

# 4. 检查是否被占用
sudo lsof | grep video
```

### 问题2: 编译失败

**症状**: `error: 'BerxelHawkContext.h' file not found`

**解决**:
```bash
# 1. 检查头文件
find /usr -name "BerxelHawkContext.h" 2>/dev/null

# 2. 如果没找到,复制本地头文件
export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:$(pwd)/include

# 3. 重新编译
python setup.py clean
python setup.py build_ext --inplace
```

### 问题3: ImportError

**症状**: `ImportError: cannot import name 'berxel_wrapper'`

**解决**:
```bash
# 1. 检查.so文件
ls -l berxel_wrapper*.so

# 2. 检查库依赖
ldd berxel_wrapper*.so
# 确认 libBerxelHawk.so 被找到

# 3. 设置库路径
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/libs:/usr/local/lib

# 4. 测试导入
python -c "import sys; sys.path.insert(0, '.'); import berxel_wrapper"
```

### 问题4: 深度数据全是0

**症状**: 深度图全黑或全0

**解决**:
```bash
# 1. 检查相机模式
# P100R需要并行模式才能同时输出彩色和深度

# 2. 检查环境光
# P100R红外深度相机在强光下可能失效

# 3. 检查遮挡
# 确保红外发射器和接收器没有被遮挡
```

### 问题5: 性能低

**症状**: FPS低于20

**解决**:
```bash
# 1. 禁用可视化
python main_decision.py --no-viz

# 2. 降低分辨率
# 在 berxel_wrapper.cpp 中修改:
# depthMode.resolutionX = 320;
# depthMode.resolutionY = 200;

# 3. 检查CPU占用
top
# 确保CPU不是瓶颈

# 4. 使用CPU亲和性
taskset -c 0-3 python main_decision.py
```

---

## 性能优化

### 1. 系统级优化

```bash
# 关闭不必要的服务
sudo systemctl disable bluetooth
sudo systemctl disable cups

# 设置CPU性能模式
sudo apt install -y cpufrequtils
sudo cpufreq-set -g performance

# 增加USB缓冲
sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'
```

### 2. 代码级优化

```python
# 在 main_decision.py 中:

# 降低可视化分辨率
color_small = cv2.resize(color, (320, 180))  # 更小

# 减少处理频率
if self.frame_count % 2 == 0:  # 每2帧处理一次
    obstacle_mask, info = self.slam.process_depth_frame(depth_meters)
```

### 3. 自动启动配置

```bash
# 创建systemd服务
sudo nano /etc/systemd/system/zhuo-decision.service

# 添加以下内容:
[Unit]
Description=Zhuo RM Decision System
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Zhuo-RM-decision
Environment="PATH=/home/YOUR_USERNAME/Zhuo-RM-decision/venv/bin"
Environment="LD_LIBRARY_PATH=/home/YOUR_USERNAME/Zhuo-RM-decision/libs"
ExecStart=/home/YOUR_USERNAME/Zhuo-RM-decision/venv/bin/python main_decision.py --no-viz
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable zhuo-decision.service
sudo systemctl start zhuo-decision.service

# 查看状态
sudo systemctl status zhuo-decision.service
```

---

## 验收检查清单

部署完成后,请确认:

- [ ] 相机可以正常检测 (`lsusb` 能看到设备)
- [ ] SDK库可以正常加载 (`ldconfig -p | grep BerxelHawk` 有输出)
- [ ] Python扩展编译成功 (`ls berxel_wrapper*.so` 存在)
- [ ] 相机测试通过 (`python test_camera.py` 正常)
- [ ] SLAM测试通过 (`python test_slam.py` 正常)
- [ ] 主程序可以运行 (`python main_decision.py` 正常)
- [ ] 帧率达标 (FPS >= 25)
- [ ] 深度数据正常 (不全是0)
- [ ] 决策输出正确 (方向建议合理)

---

## 支持

遇到问题?

1. 查看本文档的[故障排查](#故障排查)部分
2. 提交Issue: https://github.com/zhuo001/Zhuo-RM-decision/issues
3. 联系团队技术支持

---

**最后更新**: 2025-10-15  
**版本**: v1.0  
**作者**: Zhuo RM Team
