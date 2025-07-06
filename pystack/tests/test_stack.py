import pytest
import numpy as np
from pystack.stack import (
    MeanStackCalculator,
    MaxStackCalculator,
    MinStackCalculator,
    create_calculator,
    StackMode
)

def test_mean_stack():
    """测试平均值堆栈"""
    calculator = MeanStackCalculator()
    
    # 测试单张图像
    image1 = np.array([[1, 2], [3, 4]], dtype=np.uint16)
    calculator.update(image1)
    result = calculator.get_result()
    assert np.array_equal(result, image1)
    
    # 测试多张图像
    image2 = np.array([[2, 3], [4, 5]], dtype=np.uint16)
    calculator.update(image2)
    expected = np.array([[1.5, 2.5], [3.5, 4.5]], dtype=np.uint16)
    result = calculator.get_result()
    assert np.array_equal(result, expected)

def test_max_stack():
    """测试最大值堆栈"""
    calculator = MaxStackCalculator()
    
    # 测试单张图像
    image1 = np.array([[1, 2], [3, 4]], dtype=np.uint16)
    calculator.update(image1)
    result = calculator.get_result()
    assert np.array_equal(result, image1)
    
    # 测试多张图像
    image2 = np.array([[2, 1], [2, 5]], dtype=np.uint16)
    calculator.update(image2)
    expected = np.array([[2, 2], [3, 5]], dtype=np.uint16)
    result = calculator.get_result()
    assert np.array_equal(result, expected)

def test_min_stack():
    """测试最小值堆栈"""
    calculator = MinStackCalculator()
    
    # 测试单张图像
    image1 = np.array([[1, 2], [3, 4]], dtype=np.uint16)
    calculator.update(image1)
    result = calculator.get_result()
    assert np.array_equal(result, image1)
    
    # 测试多张图像
    image2 = np.array([[2, 1], [2, 5]], dtype=np.uint16)
    calculator.update(image2)
    expected = np.array([[1, 1], [2, 4]], dtype=np.uint16)
    result = calculator.get_result()
    assert np.array_equal(result, expected)

def test_create_calculator():
    """测试计算器工厂函数"""
    mean_calc = create_calculator(StackMode.MEAN)
    assert isinstance(mean_calc, MeanStackCalculator)
    
    max_calc = create_calculator(StackMode.MAX)
    assert isinstance(max_calc, MaxStackCalculator)
    
    min_calc = create_calculator(StackMode.MIN)
    assert isinstance(min_calc, MinStackCalculator)

def test_value_clipping():
    """测试值裁剪功能"""
    calculator = MeanStackCalculator()
    
    # 测试超出范围的值
    image = np.array([[0, 65536], [-1, 70000]], dtype=np.float64)
    calculator.update(image)
    result = calculator.get_result()
    
    # 确保结果在有效范围内
    assert np.all(result >= 0)
    assert np.all(result <= 65535)
    assert result.dtype == np.uint16 