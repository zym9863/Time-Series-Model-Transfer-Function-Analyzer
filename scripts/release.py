#!/usr/bin/env python3
"""
发布脚本

自动化版本发布流程，包括测试、构建和发布到PyPI。
"""

import subprocess
import sys
from pathlib import Path
import argparse


def run_command(cmd, check=True):
    """运行命令并打印输出"""
    print(f"运行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        print(f"命令失败，退出码: {result.returncode}")
        sys.exit(1)
    
    return result


def check_environment():
    """检查发布环境"""
    print("检查发布环境...")
    
    # 检查是否在git仓库中
    result = run_command("git status", check=False)
    if result.returncode != 0:
        print("错误: 不在git仓库中")
        sys.exit(1)
    
    # 检查是否有未提交的更改
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("警告: 有未提交的更改")
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # 检查是否在主分支
    result = run_command("git branch --show-current")
    current_branch = result.stdout.strip()
    if current_branch not in ['main', 'master']:
        print(f"警告: 当前分支是 '{current_branch}'，不是主分支")
        response = input("是否继续? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)


def run_tests():
    """运行测试套件"""
    print("运行测试套件...")
    run_command("uv run pytest tests/ -v --cov=time_series_analyzer")


def run_linting():
    """运行代码检查"""
    print("运行代码检查...")
    
    # 代码格式化检查
    print("检查代码格式...")
    run_command("uv run black --check src tests")
    run_command("uv run isort --check-only src tests")
    
    # 类型检查
    print("运行类型检查...")
    run_command("uv run mypy src", check=False)  # mypy可能有警告，不强制退出


def build_package():
    """构建包"""
    print("构建包...")
    
    # 清理之前的构建
    dist_dir = Path("dist")
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
    
    # 构建
    run_command("uv build")


def test_installation():
    """测试安装"""
    print("测试本地安装...")
    
    # 在临时环境中测试安装
    run_command("uv run pip install dist/*.whl --force-reinstall")
    
    # 测试命令行工具
    run_command("uv run tsm-analyzer --help")
    
    # 测试Python导入
    run_command('uv run python -c "import time_series_analyzer; print(time_series_analyzer.__version__)"')


def publish_to_pypi(test=True):
    """发布到PyPI"""
    if test:
        print("发布到TestPyPI...")
        run_command("uv publish --repository testpypi")
    else:
        print("发布到PyPI...")
        response = input("确认发布到正式PyPI? (y/N): ")
        if response.lower() != 'y':
            print("取消发布")
            return
        run_command("uv publish")


def create_git_tag(version):
    """创建Git标签"""
    print(f"创建Git标签 v{version}...")
    run_command(f"git tag v{version}")
    run_command("git push origin --tags")


def main():
    parser = argparse.ArgumentParser(description="发布脚本")
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    parser.add_argument("--skip-lint", action="store_true", help="跳过代码检查")
    parser.add_argument("--test-pypi", action="store_true", help="发布到TestPyPI")
    parser.add_argument("--production", action="store_true", help="发布到正式PyPI")
    parser.add_argument("--version", help="版本号（用于创建标签）")
    
    args = parser.parse_args()
    
    try:
        # 检查环境
        check_environment()
        
        # 运行测试
        if not args.skip_tests:
            run_tests()
        
        # 代码检查
        if not args.skip_lint:
            run_linting()
        
        # 构建包
        build_package()
        
        # 测试安装
        test_installation()
        
        # 发布
        if args.test_pypi:
            publish_to_pypi(test=True)
        elif args.production:
            publish_to_pypi(test=False)
            
            # 创建Git标签
            if args.version:
                create_git_tag(args.version)
        
        print("发布流程完成！")
        
    except KeyboardInterrupt:
        print("\n发布流程被中断")
        sys.exit(1)
    except Exception as e:
        print(f"发布流程出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
