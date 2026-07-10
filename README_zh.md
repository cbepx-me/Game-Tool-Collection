# 🎮 游戏工具集合

**一站式 EmulationStation (ES) 前端游戏列表管理工具集。**

![版本](https://img.shields.io/badge/版本-v1.5.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![许可证](https://img.shields.io/badge/许可证-MIT-yellow)

---

## 📖 概述

**游戏工具集合** 是一款基于 Python + Tkinter 的桌面应用程序（支持 Windows / Linux / macOS），专为复古游戏玩家设计，用于高效维护 ES 游戏列表文件 `gamelist.xml`。

它集成了五个核心功能模块：

- **Gamelist 生成器** – 根据 ROM 文件夹自动生成 `gamelist.xml`，并自动匹配预览图/视频。
- **Gamelist 编辑器** – 提供友好的图形界面，打开、编辑、保存和校验 `gamelist.xml`。
- **Gamelist 拼音处理器** – 自动为游戏名称添加/删除拼音首字母（前缀或后缀），例如 `超级玛丽` → `C-超级玛丽` 或 `超级玛丽 [CJML]`。
- **ROM 文件名修改器** – 批量重命名 ROM 文件，支持添加序号前缀、字母前缀、混合前缀，并可应用拼音处理。
- **天马转换器** – 将 Pegasus 前端导出的 `metadata.pegasus.txt` 转换为 ES 兼容的 `gamelist.xml`，同时复制或移动媒体资源。

---

## ✨ 主要功能

- ✅ **打开并编辑** `gamelist.xml`，支持增删改查
- ✅ **自动检测缺失文件**（ROM、图片、视频），并提供一键修复
- ✅ **从 ROM 文件夹生成**全新 `gamelist.xml`，根据文件名自动匹配媒体
- ✅ **拼音处理**（为游戏名添加或删除拼音首字母前缀/后缀）
- ✅ **批量重命名 ROM 文件**（数字序号、字母序号、混合序号）
- ✅ **将 Pegasus 元数据**转换为 ES 格式（支持复制或移动模式）
- ✅ **多语言支持**（英文、简体/繁体中文、日文、韩文、法文、俄文、德文、葡萄牙文、西班牙文）
- ✅ **Windows 注册表**保存语言偏好设置
- ✅ **轻量级** – 除 Python 标准库和 `pypinyin` 外无额外依赖

---

## 🖥️ 安装与使用

### 环境要求

- Python 3.8 或更高版本
- `pypinyin` 库（用于拼音功能）

安装依赖：

```bash
pip install pypinyin
```

### 从源码运行

克隆仓库：
```
bash
git clone https://github.com/yourusername/game-tool-collection.git
cd game-tool-collection
```

启动应用：
```
bash
python gamelist.py
```

### 打包为独立可执行文件（Windows）

使用 PyInstaller 打包成单个 .exe：
```
bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon/icon.ico gamelist.py
```
生成的 exe 文件位于 dist/ 目录下。

## 📸 截图

<img width="899" height="1027" alt="屏幕截图 2026-07-10 122208" src="https://github.com/user-attachments/assets/4818bad2-f451-4474-a309-3e8876da1fa4" />

## 🧩 模块速览
模块|功能说明
|----|----|
|生成器|扫描 ROM 文件夹，匹配图片/视频，导出 gamelist.xml
|编辑器|编辑游戏条目，检测完整性，修复缺失文件
|拼音处理器|为游戏名添加或删除拼音首字母（前缀或后缀）
|ROM 文件名修改器|批量重命名 ROM 文件，支持序号前缀和拼音处理
|天马转换器|将 Pegasus 元数据转换为 ES 格式

## 🌐 多语言支持
界面语言会根据系统语言自动适配（也可在菜单中手动切换）。
支持语言：English、简体中文、繁體中文、日本語、한국어、Français、Русский、Deutsch、Português‑BR、Español。

## 🤝 参与贡献
欢迎任何形式的贡献！请随时提交 Issue 或 Pull Request。
- Fork 本仓库
- 创建新分支 (git checkout -b feature/你的功能)
- 提交更改 (git commit -am '添加新功能')
- 推送分支 (git push origin feature/你的功能)
- 发起 Pull Request

## 📄 许可证
本项目采用 MIT 许可证 – 详见 LICENSE 文件。

## 👨‍💻 作者
上帝之右手 (G.R.H)

## 🙏 致谢
- pypinyin – 提供中文拼音转换支持
- Tkinter – 图形界面框架

## 祝游戏愉快！ 🕹️
