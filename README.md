# PyStack - RAW图像堆叠工具

PyStack 是一个用于处理和堆叠数码相机RAW格式图像的Python工具。它使用增量平均算法，可以处理大量图像序列而不会占用过多内存。

## 功能特点

- 支持 Sony ARW 格式RAW文件的读取和处理
- 使用增量平均算法，内存占用低
- 支持批量处理大量图像
- 自动保存临时结果，防止处理中断导致数据丢失
- 详细的日志记录

## 安装要求

- Python 3.6+
- rawpy
- numpy
- tifffile
- tqdm

## 安装方法

```bash
# 克隆仓库
git clone https://github.com/你的用户名/PyStack.git
cd PyStack

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

```bash
python pystack/stack.py --input /path/to/raw/files --output result.tiff --start DSC00001.ARW --end DSC00100.ARW
```

### 参数说明

- `--input`, `-i`: RAW文件所在的输入目录
- `--output`, `-o`: 输出文件路径（默认为 ./mean_output.tiff）
- `--start`: 起始文件名
- `--end`: 结束文件名
- `--save-interval`, `-s`: 临时结果保存间隔（默认每10张图像保存一次）

## 示例

```bash
python pystack/stack.py -i ./raw_images -o stacked.tiff --start DSC00001.ARW --end DSC00050.ARW -s 5
```

## 注意事项

1. 确保有足够的磁盘空间存储临时文件和最终结果
2. 处理过程中请勿关闭程序，以免数据丢失
3. 建议先用少量图像测试后再处理大量图像

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。 