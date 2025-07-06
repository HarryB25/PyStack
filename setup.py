from setuptools import setup, find_packages

setup(
    name="pystack",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "rawpy>=0.17.0",
        "tifffile>=2021.8.30",
        "tqdm>=4.62.0",
    ],
    author="Huang Yibo",
    author_email="huangyibo25@163.com",
    description="RAW图像堆栈工具 - 支持多种相机品牌RAW格式的图像堆叠处理",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HarryB25/PyStack",
    project_urls={
        "Bug Tracker": "https://github.com/HarryB25/PyStack/issues",
        "Documentation": "https://github.com/HarryB25/PyStack#readme",
        "Source Code": "https://github.com/HarryB25/PyStack",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    keywords="raw image stacking astrophotography photography sony nikon canon fujifilm",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "pystack=pystack.stack:main",
        ],
    },
) 