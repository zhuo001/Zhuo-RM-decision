#!/usr/bin/env python3
"""
卓越RM机器人决策系统主程序
实时SLAM避障与路径规划

使用方法:
    python main_decision.py [--depth-threshold DEPTH] [--fps FPS]

作者: Zhuo
日期: 2025-10-15
"""

import sys
import os
import argparse
import time
import cv2
import numpy as np

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from depth_slam_obstacle import DepthSLAMObstacleDetector
from berxel_camera import BerxelCamera


class DecisionSystem:
    """决策系统主类"""
    
    def __init__(self, depth_threshold=1.5, fps=30, enable_visualization=True):
        """
        初始化决策系统
        
        Args:
            depth_threshold: 障碍物检测阈值(米)
            fps: 目标帧率
            enable_visualization: 是否启用可视化
        """
        self.depth_threshold = depth_threshold
        self.target_fps = fps
        self.enable_visualization = enable_visualization
        
        # 初始化相机
        self.camera = None
        
        # 初始化SLAM检测器
        self.slam = None
        
        # 统计信息
        self.frame_count = 0
        self.start_time = None
        
    def initialize(self):
        """初始化所有组件"""
        print("="*60)
        print("🤖 卓越RM决策系统初始化")
        print("="*60)
        
        # 1. 初始化相机
        print("\n[1/2] 初始化P100R相机...")
        self.camera = BerxelCamera()
        if not self.camera.initialize():
            raise RuntimeError("相机初始化失败")
        print("✅ 相机初始化成功")
        
        # 2. 初始化SLAM
        print("\n[2/2] 初始化SLAM避障系统...")
        self.slam = DepthSLAMObstacleDetector(
            depth_threshold_near=0.5,
            depth_threshold_far=5.0,
            obstacle_height_min=0.1,
            grid_resolution=0.05
        )
        print("✅ SLAM系统初始化成功")
        
        print("\n"  + "="*60)
        print("🎯 系统就绪！")
        print("="*60)
        print(f"\n配置参数:")
        print(f"  - 深度阈值: {self.depth_threshold}m")
        print(f"  - 目标FPS: {self.target_fps}")
        print(f"  - 可视化: {'开启' if self.enable_visualization else '关闭'}")
        print("\n控制:")
        print("  - 按 'q' 退出")
        print("  - 按 's' 截图")
        print("  - 按 'p' 暂停/继续")
        print("="*60 + "\n")
        
    def run(self):
        """主循环"""
        self.start_time = time.time()
        paused = False
        screenshot_count = 0
        
        try:
            while True:
                loop_start = time.time()
                
                if not paused:
                    # 1. 获取深度图
                    depth_meters = self.camera.get_depth_meters()
                    if depth_meters is None:
                        print("[WARNING] 无法获取深度数据")
                        continue
                    
                    # 2. 获取彩色图(可选)
                    color = self.camera.get_frame() if self.enable_visualization else None
                    
                    # 3. SLAM处理
                    obstacle_mask, info = self.slam.process_depth_frame(depth_meters, color)
                    
                    # 4. 获取决策
                    direction = info['suggested_direction']
                    navigable_zones = info['navigable_zones']
                    
                    # 5. 输出决策
                    self._output_decision(direction, navigable_zones, info)
                    
                    # 6. 可视化
                    if self.enable_visualization:
                        self._visualize(depth_meters, obstacle_mask, info, color)
                    
                    self.frame_count += 1
                
                # 键盘控制
                key = cv2.waitKey(1) & 0xFF if self.enable_visualization else -1
                if key == ord('q'):
                    print("\n用户退出")
                    break
                elif key == ord('p'):
                    paused = not paused
                    print(f"\n{'⏸️ 暂停' if paused else '▶️ 继续'}")
                elif key == ord('s') and self.enable_visualization:
                    screenshot_count += 1
                    self._save_screenshot(depth_meters, obstacle_mask, color, screenshot_count)
                
                # 帧率控制
                loop_time = time.time() - loop_start
                sleep_time = max(0, 1.0/self.target_fps - loop_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n⚠️ 中断退出")
        
        finally:
            self._cleanup()
    
    def _output_decision(self, direction, zones, info):
        """输出决策信息"""
        if self.frame_count % 30 == 0:  # 每30帧输出一次
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed
            
            print(f"\r[Frame {self.frame_count:06d}] "
                  f"FPS: {fps:5.1f} | "
                  f"方向: {direction:8s} | "
                  f"障碍物: {info['obstacle_count']:6d} | "
                  f"可导航区: {len(zones):2d} | "
                  f"最近: {info['min_depth']:.2f}m",
                  end='', flush=True)
    
    def _visualize(self, depth, obstacle_mask, info, color):
        """可视化结果"""
        # 深度图可视化
        depth_normalized = np.clip(depth / 5.0, 0, 1)
        depth_vis = cv2.applyColorMap(
            (depth_normalized * 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        
        # 障碍物掩码可视化
        obstacle_vis = cv2.cvtColor(obstacle_mask, cv2.COLOR_GRAY2BGR)
        obstacle_vis[obstacle_mask > 0] = [0, 0, 255]  # 红色障碍物
        
        # 绘制可导航区域
        for zone in info['navigable_zones'][:3]:
            cx, cy = int(zone['centroid'][0]), int(zone['centroid'][1])
            cv2.circle(obstacle_vis, (cx, cy), 10, (0, 255, 0), -1)
        
        # 添加信息叠加
        direction = info['suggested_direction']
        cv2.putText(depth_vis, f"Direction: {direction}",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(depth_vis, f"FPS: {1.0/info['processing_time']:.1f}",
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示
        cv2.imshow('Decision - Depth', depth_vis)
        cv2.imshow('Decision - Obstacles', obstacle_vis)
        if color is not None:
            cv2.imshow('Decision - Color', cv2.resize(color, (640, 360)))
    
    def _save_screenshot(self, depth, obstacle_mask, color, count):
        """保存截图"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # 保存深度图
        depth_vis = cv2.applyColorMap(
            np.clip((depth / 5.0) * 255, 0, 255).astype(np.uint8),
            cv2.COLORMAP_JET
        )
        cv2.imwrite(f"depth_{timestamp}_{count}.png", depth_vis)
        
        # 保存障碍物掩码
        cv2.imwrite(f"obstacles_{timestamp}_{count}.png", obstacle_mask)
        
        # 保存彩色图
        if color is not None:
            cv2.imwrite(f"color_{timestamp}_{count}.png", color)
        
        print(f"\n📸 截图已保存: *_{timestamp}_{count}.png")
    
    def _cleanup(self):
        """清理资源"""
        print("\n\n" + "="*60)
        print("🧹 清理资源...")
        print("="*60)
        
        if self.camera:
            self.camera.release()
        
        if self.enable_visualization:
            cv2.destroyAllWindows()
        
        # 统计信息
        if self.start_time:
            elapsed = time.time() - self.start_time
            avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
            
            print(f"\n📊 运行统计:")
            print(f"  - 总帧数: {self.frame_count}")
            print(f"  - 运行时间: {elapsed:.1f}秒")
            print(f"  - 平均FPS: {avg_fps:.1f}")
            print(f"  - 平均处理时间: {np.mean(self.slam.processing_times):.3f}秒")
        
        print("\n✅ 决策系统已关闭")
        print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="卓越RM机器人决策系统",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--depth-threshold', type=float, default=1.5,
        help='障碍物深度阈值(米)'
    )
    parser.add_argument(
        '--fps', type=int, default=30,
        help='目标帧率'
    )
    parser.add_argument(
        '--no-viz', action='store_true',
        help='禁用可视化(提升性能)'
    )
    
    args = parser.parse_args()
    
    # 创建决策系统
    system = DecisionSystem(
        depth_threshold=args.depth_threshold,
        fps=args.fps,
        enable_visualization=not args.no_viz
    )
    
    try:
        # 初始化
        system.initialize()
        
        # 运行
        system.run()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
