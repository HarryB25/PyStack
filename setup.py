from setuptools import setup, find_packages

setup(
    name="pystack",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "rawpy>=0.17.0",
        "tifffile>=2021.8.30",
        "tqdm>=4.62.0",
    ],
    author="Huang Yibo",
    author_email="huangyibo25@163.com",
    description="RAW图像堆栈工具",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HarryB25/PyStack",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 