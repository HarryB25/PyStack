import unittest
import numpy as np
from ..stack import IncrementalMeanCalculator

class TestIncrementalMeanCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = IncrementalMeanCalculator()

    def test_update_mean_first_image(self):
        """测试第一张图片的平均值计算"""
        test_image = np.ones((100, 100, 3), dtype=np.uint16) * 1000
        self.calculator.update_mean(test_image)
        result = self.calculator.get_current_mean()
        
        self.assertEqual(self.calculator.count, 1)
        np.testing.assert_array_equal(result, test_image)

    def test_update_mean_multiple_images(self):
        """测试多张图片的平均值计算"""
        image1 = np.ones((100, 100, 3), dtype=np.uint16) * 1000
        image2 = np.ones((100, 100, 3), dtype=np.uint16) * 2000
        
        self.calculator.update_mean(image1)
        self.calculator.update_mean(image2)
        result = self.calculator.get_current_mean()
        
        expected = np.ones((100, 100, 3), dtype=np.uint16) * 1500
        self.assertEqual(self.calculator.count, 2)
        np.testing.assert_array_equal(result, expected)

if __name__ == '__main__':
    unittest.main() 