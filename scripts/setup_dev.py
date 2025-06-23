#!/usr/bin/env python3
"""
开发环境设置脚本

自动设置开发环境，包括依赖安装、pre-commit钩子等。
"""

import subprocess
import sys
from pathlib import Path


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


def check_uv():
    """检查uv是否安装"""
    print("检查uv包管理器...")
    result = run_command("uv --version", check=False)
    if result.returncode != 0:
        print("错误: uv未安装")
        print("请访问 https://docs.astral.sh/uv/ 安装uv")
        sys.exit(1)
    print("✓ uv已安装")


def install_dependencies():
    """安装依赖"""
    print("安装项目依赖...")
    run_command("uv sync --dev")
    print("✓ 依赖安装完成")


def setup_pre_commit():
    """设置pre-commit钩子"""
    print("设置pre-commit钩子...")
    
    # 创建pre-commit配置文件
    pre_commit_config = """
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        exclude: ^tests/
"""
    
    config_file = Path(".pre-commit-config.yaml")
    if not config_file.exists():
        with open(config_file, "w") as f:
            f.write(pre_commit_config.strip())
        print("✓ 创建pre-commit配置文件")
    
    # 安装pre-commit
    run_command("uv add --dev pre-commit")
    run_command("uv run pre-commit install")
    print("✓ pre-commit钩子设置完成")


def create_vscode_settings():
    """创建VSCode设置"""
    print("创建VSCode设置...")
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # settings.json
    settings = {
        "python.defaultInterpreterPath": "./.venv/bin/python",
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": False,
        "python.linting.flake8Enabled": True,
        "python.linting.mypyEnabled": True,
        "python.formatting.provider": "black",
        "python.sortImports.args": ["--profile", "black"],
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {
            "source.organizeImports": True
        },
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            ".pytest_cache": True,
            ".coverage": True,
            "htmlcov": True,
            "dist": True,
            "build": True,
            "*.egg-info": True
        }
    }
    
    import json
    settings_file = vscode_dir / "settings.json"
    if not settings_file.exists():
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
        print("✓ 创建VSCode设置文件")
    
    # launch.json
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: 当前文件",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal"
            },
            {
                "name": "Python: 测试",
                "type": "python",
                "request": "launch",
                "module": "pytest",
                "args": ["tests/", "-v"],
                "console": "integratedTerminal"
            },
            {
                "name": "CLI: 帮助",
                "type": "python",
                "request": "launch",
                "module": "time_series_analyzer.cli",
                "args": ["--help"],
                "console": "integratedTerminal"
            }
        ]
    }
    
    launch_file = vscode_dir / "launch.json"
    if not launch_file.exists():
        with open(launch_file, "w") as f:
            json.dump(launch_config, f, indent=2)
        print("✓ 创建VSCode调试配置")


def run_initial_tests():
    """运行初始测试"""
    print("运行初始测试...")
    run_command("uv run pytest tests/ -v")
    print("✓ 测试通过")


def create_gitignore():
    """创建.gitignore文件"""
    print("检查.gitignore文件...")
    
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.log
temp/
tmp/
"""
    
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        with open(gitignore_file, "w") as f:
            f.write(gitignore_content.strip())
        print("✓ 创建.gitignore文件")
    else:
        print("✓ .gitignore文件已存在")


def main():
    """主函数"""
    print("=" * 60)
    print("时序模型传递函数分析器 - 开发环境设置")
    print("=" * 60)
    
    try:
        check_uv()
        install_dependencies()
        create_gitignore()
        setup_pre_commit()
        create_vscode_settings()
        run_initial_tests()
        
        print("\n" + "=" * 60)
        print("开发环境设置完成！")
        print("=" * 60)
        print("\n下一步:")
        print("1. 运行测试: uv run pytest")
        print("2. 启动开发: uv run python examples/usage_examples.py")
        print("3. 命令行工具: uv run tsm-analyzer --help")
        print("4. 代码格式化: uv run black src tests")
        print("5. 类型检查: uv run mypy src")
        
    except KeyboardInterrupt:
        print("\n设置被中断")
        sys.exit(1)
    except Exception as e:
        print(f"设置出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
