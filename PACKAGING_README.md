# MockBoost 打包说明

本文档提供了如何将 MockBoost 项目打包成可执行文件的说明。

## 准备工作

在开始打包之前，请确保已安装所有必要的依赖：

```bash
pip install -r requirements.txt
pip install cx_Freeze PyInstaller
```

## 打包方法

### 方法一：使用 cx_Freeze 打包

cx_Freeze 是一个将 Python 脚本转换为可执行文件的工具，适用于较复杂的应用程序。

1. 在命令行中，切换到项目根目录
2. 运行以下命令：

```bash
python setup.py build
```

打包完成后，可执行文件将位于 `build` 目录下。

### 方法二：使用 PyInstaller 打包

PyInstaller 是另一个流行的 Python 打包工具，通常生成单个可执行文件或单个目录。

1. 在命令行中，切换到项目根目录
2. 运行以下命令：

```bash
python build_with_pyinstaller.py
```

打包完成后，可执行文件将位于 `dist/MockBoost` 目录下。

## 注意事项

1. 打包过程可能需要几分钟到几十分钟不等，取决于您的计算机性能和项目大小。
2. 如果打包过程中遇到问题，请检查是否所有依赖都已正确安装。
3. 打包后的应用程序可能比源代码大很多，这是正常的，因为它包含了运行所需的所有依赖。
4. 对于使用 GPU 的功能（如深度学习模型），可能需要在目标机器上安装相应的驱动程序。

## 自定义打包选项

如果需要自定义打包选项，可以编辑 `setup.py`（cx_Freeze）或 `build_with_pyinstaller.py`（PyInstaller）文件。

### cx_Freeze 常用选项

- `packages`：需要包含的 Python 包
- `include_files`：需要包含的文件和目录
- `excludes`：需要排除的模块

### PyInstaller 常用选项

- `--onefile`：创建单个可执行文件（替代 `--onedir`）
- `--noconsole`：不显示控制台窗口（与 `--windowed` 相同）
- `--add-data`：添加数据文件
- `--hidden-import`：添加隐式导入的模块