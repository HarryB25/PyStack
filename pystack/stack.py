#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import rawpy
import tifffile
import argparse
import logging
from pathlib import Path
from tqdm import tqdm
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 支持的RAW格式
RAW_EXTENSIONS = {
    'SONY': ['.arw', '.srf', '.sr2'],
    'NIKON': ['.nef', '.nrw'],
    'CANON': ['.cr2', '.cr3', '.crw'],
    'FUJI': ['.raf'],
    'OLYMPUS': ['.orf'],
    'PENTAX': ['.pef', '.dng'],
    'PANASONIC': ['.rw2'],
    'LEICA': ['.dng'],
    'RICOH': ['.dng'],
    'SIGMA': ['.x3f'],
}

# 所有支持的扩展名
SUPPORTED_EXTENSIONS = [ext.lower() for exts in RAW_EXTENSIONS.values() for ext in exts]

class StackMode(Enum):
    """堆栈模式枚举"""
    MEAN = "mean"  # 平均值堆栈
    MAX = "max"  # 最大值堆栈
    MIN = "min"  # 最小值堆栈

class BaseStackCalculator(ABC):
    """堆栈计算器基类"""
    def __init__(self):
        self.count = 0
        self.result = None

    def read_raw_image(self, image_path: str) -> np.ndarray:
        """读取RAW图像，支持多种格式"""
        try:
            with rawpy.imread(image_path) as raw:
                # 根据不同相机品牌调整参数
                ext = Path(image_path).suffix.lower()
                brand = next((brand for brand, exts in RAW_EXTENSIONS.items() 
                            if ext in [e.lower() for e in exts]), None)
                
                if brand == 'FUJI':
                    # Fuji的X-Trans传感器需要特殊处理
                    return raw.postprocess(
                        use_camera_wb=True,
                        half_size=False,
                        no_auto_bright=True,  # Fuji已经做了亮度调整
                        output_bps=16,
                        user_flip=0,  # 保持原始方向
                        demosaic_algorithm=rawpy.DemosaicAlgorithm.AAHD  # 更适合X-Trans
                    )
                elif brand == 'SONY':
                    # Sony相机通常需要更强的锐化
                    return raw.postprocess(
                        use_camera_wb=True,
                        half_size=False,
                        no_auto_bright=False,
                        output_bps=16,
                        user_flip=0,
                        bright=1.0,
                        exp_shift=1.0
                    )
                else:
                    # 其他品牌使用标准处理
                    return raw.postprocess(
                        use_camera_wb=True,
                        half_size=False,
                        no_auto_bright=False,
                        output_bps=16,
                        user_flip=0
                    )
        except Exception as e:
            logger.error(f"无法读取图像 {image_path}: {str(e)}")
            raise

    @abstractmethod
    def update(self, new_image: np.ndarray) -> None:
        """更新堆栈结果"""
        pass

    def get_result(self) -> np.ndarray:
        """获取当前结果"""
        if self.result is None:
            return None
        return np.clip(self.result, 0, 65535).astype(np.uint16)

    def process_directory(self, input_dir: str, output_path: str, start_file: str, end_file: str, save_interval: int = 10) -> None:
        """处理目录中的指定范围的RAW图像"""
        input_path = Path(input_dir)
        if not input_path.exists():
            raise ValueError(f"输入目录不存在: {input_dir}")

        # 获取所有支持格式的RAW文件
        raw_files = []
        for ext in SUPPORTED_EXTENSIONS:
            raw_files.extend(input_path.glob(f'*{ext}'))
            raw_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        if not raw_files:
            supported_formats = ', '.join(SUPPORTED_EXTENSIONS)
            raise ValueError(f"未找到支持的RAW格式文件。支持的格式: {supported_formats}")
            
        # 按文件名排序
        raw_files = sorted(raw_files, key=lambda x: x.name)
        
        # 找到起始和结束文件的索引
        start_idx = next((i for i, f in enumerate(raw_files) if f.name == start_file), None)
        end_idx = next((i for i, f in enumerate(raw_files) if f.name == end_file), None)
        
        if start_idx is None:
            raise ValueError(f"未找到起始文件: {start_file}")
        if end_idx is None:
            raise ValueError(f"未找到结束文件: {end_file}")
            
        # 获取需要处理的文件列表
        files_to_process = raw_files[start_idx:end_idx + 1]
        logger.info(f"将处理从 {start_file} 到 {end_file} 的 {len(files_to_process)} 个文件")

        # 处理每张图片
        for idx, file_path in enumerate(tqdm(files_to_process, desc="处理图像")):
            try:
                # 读取并处理图像
                image = self.read_raw_image(str(file_path))
                self.update(image)
                
                # 定期保存结果
                if (idx + 1) % save_interval == 0:
                    result = self.get_result()
                    temp_output = output_path.replace('.tiff', f'_temp_{idx+1}.tiff')
                    tifffile.imwrite(temp_output, result)
                    logger.info(f"已保存临时结果到: {temp_output}")
                
            except Exception as e:
                logger.error(f"处理图像 {file_path.name} 时出错: {str(e)}")
                continue

        # 保存最终结果
        final_result = self.get_result()
        if final_result is not None:
            tifffile.imwrite(output_path, final_result)
            logger.info(f"已保存最终结果到: {output_path}")

class MeanStackCalculator(BaseStackCalculator):
    """平均值堆栈计算器"""
    def __init__(self):
        super().__init__()
        self.result = None

    def update(self, new_image: np.ndarray) -> None:
        self.count += 1
        if self.result is None:
            self.result = new_image.astype(np.float64)
        else:
            # 使用增量更新公式：new_mean = old_mean + (new_value - old_mean) / n
            self.result += (new_image.astype(np.float64) - self.result) / self.count

class MaxStackCalculator(BaseStackCalculator):
    """最大值堆栈计算器"""
    def __init__(self):
        super().__init__()
        self.result = None

    def update(self, new_image: np.ndarray) -> None:
        if self.result is None:
            self.result = new_image.astype(np.float64)
        else:
            self.result = np.maximum(self.result, new_image)

class MinStackCalculator(BaseStackCalculator):
    """最小值堆栈计算器"""
    def __init__(self):
        super().__init__()
        self.result = None

    def update(self, new_image: np.ndarray) -> None:
        if self.result is None:
            self.result = new_image.astype(np.float64)
        else:
            self.result = np.minimum(self.result, new_image)

def create_calculator(mode: StackMode) -> BaseStackCalculator:
    """创建堆栈计算器实例"""
    calculators = {
        StackMode.MEAN: MeanStackCalculator,
        StackMode.MAX: MaxStackCalculator,
        StackMode.MIN: MinStackCalculator,
    }
    return calculators[mode]()

def main():
    parser = argparse.ArgumentParser(description='RAW图像堆栈工具')
    parser.add_argument('--input', '-i', help='输入目录路径', required=True)
    parser.add_argument('--output', '-o', help='输出文件路径', default='./stacked_output.tiff')
    parser.add_argument('--start', help='起始文件名', required=True)
    parser.add_argument('--end', help='结束文件名', required=True)
    parser.add_argument('--save-interval', '-s', type=int, default=10, 
                        help='每处理多少张图片保存一次临时结果')
    parser.add_argument('--mode', '-m', type=str, choices=[m.value for m in StackMode],
                        default=StackMode.MEAN.value, help='堆栈模式')
    
    args = parser.parse_args()
    
    try:
        mode = StackMode(args.mode)
        calculator = create_calculator(mode)
        calculator.process_directory(args.input, args.output, args.start, args.end, args.save_interval)
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 