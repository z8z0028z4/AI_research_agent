#!/usr/bin/env python3
"""
CUDA 安裝檢查腳本
"""

import torch

print("=" * 50)
print("PyTorch CUDA 安裝檢查")
print("=" * 50)

print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 是否可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA 版本: {torch.version.cuda}")
    print(f"GPU 數量: {torch.cuda.device_count()}")
    
    for i in range(torch.cuda.device_count()):
        gpu_name = torch.cuda.get_device_name(i)
        print(f"GPU {i}: {gpu_name}")
    
    # 測試 CUDA 功能
    try:
        x = torch.randn(3, 3).cuda()
        y = torch.randn(3, 3).cuda()
        z = torch.mm(x, y)
        print("✅ CUDA 計算測試成功")
    except Exception as e:
        print(f"❌ CUDA 計算測試失敗: {e}")
else:
    print("❌ CUDA 不可用")
    print("可能的原因:")
    print("1. 沒有 NVIDIA GPU")
    print("2. 沒有安裝 CUDA 驅動")
    print("3. 安裝的是 CPU 版本的 PyTorch")

print("=" * 50)
