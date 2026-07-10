# 🎮 Game Tool Collection

**A comprehensive toolkit for managing game lists (gamelist.xml) of EmulationStation (ES) frontends.**

![Version](https://img.shields.io/badge/version-v1.5.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 📖 Overview

**Game Tool Collection** is a cross‑platform desktop application (Windows/Linux/macOS) built with Python and Tkinter. It helps retro‑gaming enthusiasts maintain and polish their ES game collections with ease.

It provides five core modules:

- **Gamelist Generator** – Create a `gamelist.xml` from a folder of ROM files, automatically matching preview images/videos.
- **Gamelist Editor** – Open, edit, save, and validate `gamelist.xml` entries with a clean GUI.
- **Gamelist Pinyin Processor** – Automatically add/remove Chinese Pinyin initials to game names (e.g., `Super Mario Bros` → `S-Super Mario Bros` or `Super Mario Bros [SMB]`).
- **ROM Name Editor** – Batch rename ROM files with serial numbers, remove prefixes, and apply Pinyin transformations.
- **Pegasus Converter** – Convert a Pegasus front‑end `metadata.pegasus.txt` game library to ES‑compatible `gamelist.xml`, copying/moving media files.

---

## ✨ Features

- ✅ **Open & edit** `gamelist.xml` with full CRUD operations
- ✅ **Auto‑detect missing files** (ROM, image, video) and **fix** them with a few clicks
- ✅ **Generate new gamelist** from a ROM folder, auto‑match media by filename
- ✅ **Pinyin processing** (add/remove initials as prefix or suffix)
- ✅ **Batch rename ROM files** with sequential numbers, letter prefixes, or mixed styles
- ✅ **Convert Pegasus metadata** to ES `gamelist.xml` (copy or move mode)
- ✅ **Multi‑language support** (English, Simplified/Traditional Chinese, Japanese, Korean, French, Russian, German, Portuguese, Spanish)
- ✅ **Windows registry** for persistent language settings
- ✅ **Lightweight** – no external dependencies beyond Python standard library and `pypinyin`

---

## 🖥️ Installation & Usage

### Prerequisites

- Python 3.8 or higher
- `pypinyin` library (for Pinyin features)

Install the dependency:

```bash
pip install pypinyin
```

### Running from source

Clone the repository:

```bash
git clone https://github.com/yourusername/game-tool-collection.git
cd game-tool-collection
```

Run the application:
```
bash
python gamelist.py
```
You can package the app into a single .exe using PyInstaller:
```
bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon/icon.ico gamelist.py
```
The executable will be created in the dist/ folder.

## 📸 Screenshots

<img width="899" height="1027" alt="Screenshots" src="https://github.com/user-attachments/assets/ef426ad1-a617-4513-b531-aeea9493e108" />


## 🧩 Modules at a Glance
|Module|Description
|----|----|
|Generator|Scan ROM folder, match images/videos, export gamelist.xml
|Editor|Edit game entries, check integrity, fix missing files
|Pinyin Processor|Add/remove Pinyin initials (prefix or suffix) to game names
|ROM Name Editor|Batch rename ROM files with prefixes (numbers/letters) and Pinyin
|Pegasus Converter|Convert Pegasus metadata to ES format

## 🌐 Language Support
The interface automatically adapts to the system language (or you can select it from the menu).
Available languages: English, 简体中文, 繁體中文, 日本語, 한국어, Français, Русский, Deutsch, Português‑BR, Español.

## 🤝 Contributing
Contributions are welcome! Feel free to open issues or pull requests.

- Fork the repository
- Create a new branch (git checkout -b feature/your-feature)
- Commit your changes (git commit -am 'Add some feature')
- Push to the branch (git push origin feature/your-feature)
- Open a Pull Request

## 📄 License
This project is licensed under the MIT License – see the LICENSE file for details.

## 👨‍💻 Author
G.R.H – God's Right Hand

## 🙏 Acknowledgements
- pypinyin – for Chinese Pinyin conversion
- Tkinter – for the GUI framework

## Happy gaming! 🕹️
