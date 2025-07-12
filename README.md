# 俄罗斯方块（Tetris）

本项目是一个基于 PyQt5 实现的俄罗斯方块游戏，支持图形化界面、分数统计、暂停/重启等功能。

## 目录结构

```
Tetris.py         # 主程序入口
Tetris.spec       # PyInstaller 打包配置
img/              # 游戏相关图片资源
ui/               # Qt Designer 设计的界面文件
```

## 运行环境

- Python 3.x
- PyQt5

## 安装依赖

```powershell
pip install PyQt5
```

## 运行方法

在项目根目录下执行：

```powershell
python Tetris.py
```

## 游戏玩法

- **方向键**：控制方块移动和旋转
  - ← →：左右移动
  - ↑：顺时针旋转
  - ↓：加速下落
- **空格键**：方块直接落到底部
- **P**：暂停/恢复游戏
- **R**：重启游戏

## 文件说明

- Tetris.py：主程序，包含游戏逻辑和界面
- ui/menu.ui：主菜单界面
- ui/help.ui：帮助界面
- ui/over.ui：游戏结束界面
- img/：存放游戏用到的图片资源

## 打包说明

如需打包为可执行文件，可使用 PyInstaller：
```powershell
pyinstaller Tetris.spec
```


