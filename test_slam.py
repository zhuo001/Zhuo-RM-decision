#!/usr/bin/env python3
"""
SLAM避障算法测试脚本
使用模拟数据或真实相机数据测试SLAM算法

作者: Zhuo
日期: 2025-10-15
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from depth_slam_obstacle import DepthSLAMObstacleDetector
import cv2
import numpy as np
import time


def test_slam_simulated():
    """使用模拟数据测试SLAM"""
    print("="*60)
    print("🧪 SLAM算法测试(模拟数据)")
    print("="*60)
    
    # 初始化检测器
    slam = DepthSLAMObstacleDetector(
        depth_threshold_near=0.5,
        depth_threshold_far=5.0,
        obstacle_height_min=0.1,
        grid_resolution=0.05
    )
    
    print("\n✅ SLAM检测器初始化完成")
    print("\n按 'q' 退出\n")
    
    frame_count = 0
    
    try:
        while True:
            # 生成模拟深度图
            depth = np.random.rand(400, 640) * 4.0 + 0.5
            
            # 添加模拟障碍物
            depth[150:250, 250:350] = 0.3  # 近距离障碍物
            depth[50:120, 450:550] = 1.5   # 中距离障碍物
            
            # 处理
            obstacle_mask, info = slam.process_depth_frame(depth)
            
            # 可视化
            vis = slam.visualize(depth, obstacle_mask, info)
            
            cv2.imshow('SLAM Test', vis)
            cv2.imshow('Obstacles', obstacle_mask)
            
            # 输出信息
            if frame_count % 30 == 0:
                print(f"Frame {frame_count:05d}: "
                      f"Direction={info['suggested_direction']:8s}, "
                      f"Zones={len(info['navigable_zones']):2d}, "
                      f"FPS={1.0/info['processing_time']:.1f}")
            
            frame_count += 1
            
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n中断退出")
    
    finally:
        cv2.destroyAllWindows()
        
        print("\n" + "="*60)
        print("📊 统计信息:")
        print(f"  - 总帧数: {slam.frame_count}")
        print(f"  - 平均处理时间: {np.mean(slam.processing_times):.3f}秒")
        print(f"  - 平均FPS: {1.0/np.mean(slam.processing_times):.1f}")
        print("="*60)


def test_slam_with_camera():
    """使用真实相机测试SLAM"""
    print("="*60)
    print("🎥 SLAM算法测试(真实相机)")
    print("="*60)
    
    # 导入相机
    try:
        from berxel_camera import BerxelCamera
    except ImportError:
        print("❌ 无法导入berxel_camera模块")
        print("   请先编译: python setup.py build_ext --inplace")
        return
    
    # 初始化相机
    print("\n初始化相机...")
    camera = BerxelCamera()
    if not camera.initialize():
        print("❌ 相机初始化失败")
        return
    
    # 初始化SLAM
    print("初始化SLAM...")
    slam = DepthSLAMObstacleDetector(
        depth_threshold_near=0.5,
        depth_threshold_far=5.0
    )
    
    print("\n✅ 系统就绪")
    print("按 'q' 退出, 's' 截图\n")
    
    frame_count = 0
    screenshot_count = 0
    
    try:
        while True:
            # 获取深度
            depth = camera.get_depth_meters()
            if depth is None:
                print("\r[WARNING] 无法获取深度", end='', flush=True)
                continue
            
            # 获取彩色(可选)
            color = camera.get_frame()
            
            # SLAM处理
            obstacle_mask, info = slam.process_depth_frame(depth, color)
            
            # 可视化
            vis = slam.visualize(depth, obstacle_mask, info, color)
            cv2.imshow('SLAM with Camera', vis)
            if color is not None:
                cv2.imshow('Camera Color', cv2.resize(color, (640, 360)))
            
            # 输出
            if frame_count % 30 == 0:
                print(f"\rFrame {frame_count:05d}: "
                      f"Direction={info['suggested_direction']:8s}, "
                      f"FPS={1.0/info['processing_time']:.1f}",
                      end='', flush=True)
            
            frame_count += 1
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                screenshot_count += 1
                cv2.imwrite(f'slam_test_{screenshot_count}.png', vis)
                print(f"\n📸 截图: slam_test_{screenshot_count}.png")
    
    except KeyboardInterrupt:
        print("\n\n中断退出")
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        
        print("\n" + "="*60)
        print("📊 统计信息:")
        print(f"  - 总帧数: {slam.frame_count}")
        print(f"  - 平均FPS: {1.0/np.mean(slam.processing_times):.1f}")
        print("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SLAM测试")
    parser.add_argument(
        '--mode', choices=['sim', 'camera'], default='sim',
        help='测试模式: sim=模拟数据, camera=真实相机'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'sim':
            test_slam_simulated()
        else:
            test_slam_with_camera()
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
