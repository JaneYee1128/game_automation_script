from setuptools import setup, find_packages

setup(
    name="game_automation_script",
    version="0.1.0",
    description="游戏自动化脚本工具",
    author="AI Assistant",
    packages=find_packages(),
    package_dir={"": "src"},
    install_requires=[
        "opencv-python>=4.5.0",
        "numpy>=1.19.0",
        "Pillow>=8.0.0",
        "pyautogui>=0.9.50",
        "pynput>=1.7.0",
        "pytesseract>=0.3.0",
    ],
    entry_points={
        "console_scripts": [
            "game-automation=main:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment",
    ],
)