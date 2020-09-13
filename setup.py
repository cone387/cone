# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2020-03-04 17:14
# software: PyCharm

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-cone",
    version="0.0.2",
    author="Cone",
    author_email="1183008540@qq.com",
    description="a simple spider framework, and some tools for spider",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cone387/cone",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
