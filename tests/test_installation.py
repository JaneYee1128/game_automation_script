"""
安装测试脚本

用于验证游戏自动化脚本工具的安装是否正确
检查所有依赖项是否已正确安装，以及核心功能是否可用
"""

import os
import sys
import importlib
import platform

# 添加父目录到系统路径，以便导入src包
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_dependency(module_name, min_version=None):
    """检查依赖项是否已安装"""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, '__version__'):
            version = module.__version__
        elif hasattr(module, 'version'):
            version = module.version
        else:
            version = "未知"
        
        if min_version and version != "未知":
            if version < min_version:
                return False, f"{module_name} 版本 {version} 低于最低要求 {min_version}"
        
        return True, f"{module_name} 已安装 (版本: {version})"
    except ImportError:
        return False, f"{module_name} 未安装"

def check_core_modules():
    """检查核心模块是否可用"""
    core_modules = [
        "src.screen_capture",
        "src.event_recorder",
        "src.event_player",
        "src.image_recognition",
        "src.gui"
    ]
    
    results = []
    for module_name in core_modules:
        try:
            importlib.import_module(module_name)
            results.append((True, f"{module_name} 可用"))
        except ImportError as e:
            results.append((False, f"{module_name} 导入失败: {str(e)}"))
    
    return results

def check_tesseract():
    """检查Tesseract OCR是否已安装"""
    try:
        import pytesseract
        try:
            version = pytesseract.get_tesseract_version()
            return True, f"Tesseract OCR 已安装 (版本: {version})"
        except Exception:
            return False, "Tesseract OCR 未正确安装或未添加到PATH"
    except ImportError:
        return False, "pytesseract 模块未安装"

def main():
    """主函数"""
    print("=" * 50)
    print("游戏自动化脚本工具 - 安装测试")
    print("=" * 50)
    
    # 检查系统信息
    print("\n系统信息:")
    print(f"操作系统: {platform.system()} {platform.release()} ({platform.architecture()[0]})")
    print(f"Python版本: {platform.python_version()}")
    
    # 检查依赖项
    print("\n检查依赖项:")
    dependencies = [
        ("opencv-python", "4.5.0"),
        ("numpy", "1.19.0"),
        ("Pillow", "8.0.0"),
        ("pyautogui", "0.9.50"),
        ("pynput", "1.7.0"),
        ("pytesseract", "0.3.0"),
    ]
    
    all_deps_installed = True
    for dep, min_version in dependencies:
        success, message = check_dependency(dep, min_version)
        print(f"{'✓' if success else '✗'} {message}")
        if not success:
            all_deps_installed = False
    
    # 检查Tesseract OCR
    print("\n检查Tesseract OCR:")
    success, message = check_tesseract()
    print(f"{'✓' if success else '✗'} {message}")
    
    # 检查核心模块
    print("\n检查核心模块:")
    all_modules_available = True
    for success, message in check_core_modules():
        print(f"{'✓' if success else '✗'} {message}")
        if not success:
            all_modules_available = False
    
    # 总结
    print("\n" + "=" * 50)
    if all_deps_installed and all_modules_available:
        print("✓ 所有检查通过！游戏自动化脚本工具已正确安装。")
    else:
        print("✗ 检查未通过。请解决上述问题后再使用游戏自动化脚本工具。")
    print("=" * 50)

if __name__ == "__main__":
    main()