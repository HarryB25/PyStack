#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import rawpy
import tifffile
import argparse
import logging
from pathlib import Path
from tqdm import tqdm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IncrementalMeanCalculator:
    def __init__(self):
        self.count = 0
        self.mean_image = None
        
    def read_raw_image(self, image_path: str) -> np.ndarray:
        """读取RAW图像"""
        try:
            with rawpy.imread(image_path) as raw:
                return raw.postprocess(
                    use_camera_wb=True,
                    half_size=False,
                    no_auto_bright=False,
                    output_bps=16
                )
        except Exception as e:
            logger.error(f"无法读取图像 {image_path}: {str(e)}")
            raise

    def update_mean(self, new_image: np.ndarray) -> None:
        """增量更新平均值图像"""
        self.count += 1
        if self.mean_image is None:
            self.mean_image = new_image.astype(np.float64)
        else:
            # 使用增量更新公式：new_mean = old_mean + (new_value - old_mean) / n
            self.mean_image += (new_image.astype(np.float64) - self.mean_image) / self.count

    def get_current_mean(self) -> np.ndarray:
        """获取当前的平均值图像"""
        if self.mean_image is None:
            return None
        return np.clip(self.mean_image, 0, 65535).astype(np.uint16)

    def process_directory(self, input_dir: str, output_path: str, start_file: str, end_file: str, save_interval: int = 10) -> None:
        """处理目录中的指定范围的RAW图像"""
        input_path = Path(input_dir)
        if not input_path.exists():
            raise ValueError(f"输入目录不存在: {input_dir}")

        # 获取所有RAW文件
        raw_files = list(input_path.glob('*.ARW'))
        raw_files.extend(input_path.glob('*.arw'))
        
        if not raw_files:
            raise ValueError("未找到ARW格式图像文件")
            
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
                self.update_mean(image)
                
                # 定期保存结果
                if (idx + 1) % save_interval == 0:
                    mean_image = self.get_current_mean()
                    temp_output = output_path.replace('.tiff', f'_temp_{idx+1}.tiff')
                    tifffile.imwrite(temp_output, mean_image)
                    logger.info(f"已保存临时结果到: {temp_output}")
                
            except Exception as e:
                logger.error(f"处理图像 {file_path.name} 时出错: {str(e)}")
                continue

        # 保存最终结果
        final_mean = self.get_current_mean()
        if final_mean is not None:
            tifffile.imwrite(output_path, final_mean)
            logger.info(f"已保存最终结果到: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='增量计算RAW图像序列的平均值')
    parser.add_argument('--input', '-i', help='输入目录路径', required=True)
    parser.add_argument('--output', '-o', help='输出文件路径', default='./mean_output.tiff')
    parser.add_argument('--start', help='起始文件名', required=True)
    parser.add_argument('--end', help='结束文件名', required=True)
    parser.add_argument('--save-interval', '-s', type=int, default=10, 
                        help='每处理多少张图片保存一次临时结果')
    
    args = parser.parse_args()
    
    try:
        calculator = IncrementalMeanCalculator()
        calculator.process_directory(args.input, args.output, args.start, args.end, args.save_interval)
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 