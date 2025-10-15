#!/usr/bin/env python3
"""
Berxel P100R相机功能测试脚本
验证相机连接和SDK封装

作者: Zhuo
日期: 2025-10-15
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from berxel_camera import BerxelCamera
import cv2
import numpy as np
import time


def test_camera_basic():
    """基础相机功能测试"""
    print("="*60)
    print("🧪 P100R相机基础功能测试")
    print("="*60)
    
    camera = BerxelCamera()
    
    # 测试初始化
    print("\n[TEST 1] 相机初始化...")
    if camera.initialize():
        print("✅ 初始化成功")
    else:
        print("❌ 初始化失败")
        return False
    
    # 测试彩色图读取
    print("\n[TEST 2] 彩色图读取...")
    color = camera.get_frame()
    if color is not None:
        print(f"✅ 彩色图读取成功: {color.shape}")
    else:
        print("❌ 彩色图读取失败")
        return False
    
    # 测试深度图读取
    print("\n[TEST 3] 深度图读取(毫米)...")
    depth_mm = camera.get_depth()
    if depth_mm is not None:
        print(f"✅ 深度图读取成功: {depth_mm.shape}")
        print(f"   范围: {depth_mm.min()}mm - {depth_mm.max()}mm")
    else:
        print("❌ 深度图读取失败")
        return False
    
    # 测试深度图读取(米)
    print("\n[TEST 4] 深度图读取(米)...")
    depth_m = camera.get_depth_meters()
    if depth_m is not None:
        print(f"✅ 深度图读取成功: {depth_m.shape}")
        print(f"   范围: {depth_m.min():.3f}m - {depth_m.max():.3f}m")
    else:
        print("❌ 深度图读取失败")
        return False
    
    # 测试帧率
    print("\n[TEST 5] 帧率测试(100帧)...")
    start_time = time.time()
    for i in range(100):
        camera.get_depth()
    elapsed = time.time() - start_time
    fps = 100 / elapsed
    print(f"✅ 平均帧率: {fps:.1f} FPS")
    
    # 释放相机
    print("\n[TEST 6] 资源释放...")
    camera.release()
    print("✅ 资源释放成功")
    
    print("\n" + "="*60)
    print("✅ 所有测试通过！")
    print("="*60)
    
    return True


def test_camera_realtime():
    """实时相机测试"""
    print("\n" + "="*60)
    print("🎥 实时相机测试")
    print("="*60)
    print("\n按 'q' 退出, 's' 截图\n")
    
    camera = BerxelCamera()
    if not camera.initialize():
        return False
    
    frame_count = 0
    start_time = time.time()
    screenshot_count = 0
    
    try:
        while True:
            # 读取数据
            color = camera.get_frame()
            depth = camera.get_depth()
            
            if color is None or depth is None:
                print("\r[WARNING] 数据读取失败", end='', flush=True)
                continue
            
            # 可视化深度
            depth_vis = cv2.applyColorMap(
                cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8),
                cv2.COLORMAP_JET
            )
            
            # 显示
            cv2.imshow('Color', cv2.resize(color, (640, 360)))
            cv2.imshow('Depth', depth_vis)
            
            # 计算FPS
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"\r[Frame {frame_count:05d}] FPS: {fps:5.1f}", end='', flush=True)
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                screenshot_count += 1
                cv2.imwrite(f'test_color_{screenshot_count}.png', color)
                cv2.imwrite(f'test_depth_{screenshot_count}.png', depth_vis)
                print(f"\n📸 截图保存: test_*_{screenshot_count}.png")
    
    except KeyboardInterrupt:
        print("\n\n中断退出")
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"\n\n平均FPS: {avg_fps:.1f}")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="P100R相机测试")
    parser.add_argument(
        '--mode', choices=['basic', 'realtime'], default='basic',
        help='测试模式'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'basic':
            success = test_camera_basic()
        else:
            success = test_camera_realtime()
        
        sys.exit(0 if success else 1)
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
