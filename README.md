# PyStack - RAW图像堆栈工具

PyStack是一个用于处理RAW格式图像的堆栈工具，支持多种堆栈模式。特别适合天文摄影、长曝光和高动态范围(HDR)图像的处理。

## 特点

- 支持多种堆栈模式：
  - 平均值堆栈：适合降噪和提高信噪比
  - 最大值堆栈：适合星轨和光绘摄影
  - 最小值堆栈：适合去除移动物体

- 其他功能：
  - 支持批量处理
  - 定期保存临时结果
  - 详细的处理日志
  - 低内存占用的增量处理

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/PyStack.git
cd PyStack
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用

基本用法：
```bash
python -m pystack.stack --input /path/to/raw/files --output output.tiff --start first.ARW --end last.ARW
```

完整参数说明：
```bash
python -m pystack.stack \
    --input /path/to/raw/files \  # 输入目录
    --output output.tiff \        # 输出文件
    --start first.ARW \          # 起始文件名
    --end last.ARW \             # 结束文件名
    --mode mean \                # 堆栈模式(mean/max/min)
    --save-interval 10           # 临时保存间隔
```

### 作为Python模块使用

```python
from pystack.stack import create_calculator, StackMode

# 创建计算器实例
calculator = create_calculator(StackMode.MEAN)

# 处理图像目录
calculator.process_directory(
    input_dir="raw_images",
    output_path="output.tiff",
    start_file="IMG_0001.ARW",
    end_file="IMG_0100.ARW",
    save_interval=10
)
```

## 堆栈模式说明

1. 平均值堆栈 (mean)
   - 使用增量平均算法
   - 内存占用最小
   - 适合大量图像的降噪
   - 最适合：夜空摄影、长曝光降噪

2. 最大值堆栈 (max)
   - 保留每个像素位置的最大值
   - 适合星轨摄影
   - 适合光绘创作
   - 最适合：星轨摄影、光绘摄影

3. 最小值堆栈 (min)
   - 保留每个像素位置的最小值
   - 适合去除移动物体
   - 适合暗场处理
   - 最适合：建筑摄影中去除游客、交通摄影去除车辆

## 性能优化建议

1. 堆栈模式选择：
   - 星空摄影降噪：平均值堆栈
   - 长曝光降噪：平均值堆栈
   - 星轨摄影：最大值堆栈
   - 移动物体去除：最小值堆栈

2. 内存管理：
   - 所有模式都使用增量处理算法
   - 只需存储一张图片的内存空间
   - 适合处理大量图像

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。 