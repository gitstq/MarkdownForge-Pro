# 🚀 MarkdownForge-Pro

<p align="center">
  <strong>Lightweight Terminal Markdown Document Intelligence Engine</strong><br>
  <strong>轻量级终端Markdown文档智能排版与增强引擎</strong>
</p>

<p align="center">
  <a href="#english">English</a> •
  <a href="#简体中文">简体中文</a> •
  <a href="#繁體中文">繁體中文</a>
</p>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**MarkdownForge-Pro** is a powerful yet lightweight terminal-based Markdown document processing engine. It transforms your Markdown files into beautifully formatted documents with intelligent enhancements - all without leaving your terminal.

Inspired by the trending [quarkdown](https://github.com/iamgio/quarkdown) project, MarkdownForge-Pro brings similar capabilities to the Python ecosystem with zero dependencies and maximum portability.

### ✨ Core Features

- 🚀 **Zero Dependencies** - Pure Python standard library, no external packages required
- 📄 **Multi-Format Export** - Generate HTML, PDF, and Word-compatible documents
- 🎨 **Syntax Highlighting** - Automatic code highlighting for 20+ languages
- 📑 **Smart TOC** - Auto-generated table of contents with anchor links
- 🧮 **Math Support** - LaTeX math rendering via KaTeX/MathJax
- 👁️ **Live Preview** - Watch mode with auto-rebuild on file changes
- 🌐 **Built-in Server** - Local preview server with hot reload
- 🎯 **Extensible** - Plugin architecture for custom enhancers

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/MarkdownForge-Pro.git
cd MarkdownForge-Pro

# Install locally
pip install -e .
```

#### Basic Usage

```bash
# Convert markdown to HTML
markdownforge input.md

# Generate with table of contents
markdownforge input.md --toc

# Export as PDF
markdownforge input.md -f pdf

# Watch for changes
markdownforge input.md --watch

# Start preview server
markdownforge input.md --serve --open
```

### 📖 Detailed Usage

#### Command Line Options

```
markdownforge [OPTIONS] INPUT

Options:
  -o, --output PATH       Output file path
  -f, --format FORMAT     Output format: html, pdf, docx (default: html)
  --toc                   Add table of contents
  --toc-depth INTEGER     Maximum TOC depth (default: 6)
  --no-highlight          Disable syntax highlighting
  --math RENDERER         Math renderer: katex, mathjax, none (default: katex)
  --theme THEME           Theme name (default: default)
  -w, --watch             Watch for file changes
  -s, --serve             Start preview server
  -p, --port INTEGER      Server port (default: 8080)
  --open                  Open browser after starting server
  -v, --version           Show version
  --verbose               Enable verbose output
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📄 License

This project is licensed under the MIT License.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**MarkdownForge-Pro** 是一个功能强大且轻量级的终端Markdown文档处理引擎。它能将您的Markdown文件转换为格式精美的文档，并提供智能增强功能。

### ✨ 核心特性

- 🚀 **零依赖** - 纯Python标准库，无需外部包
- 📄 **多格式导出** - 生成HTML、PDF和Word兼容文档
- 🎨 **语法高亮** - 支持20+种语言的自动代码高亮
- 📑 **智能目录** - 自动生成带锚点链接的目录
- 🧮 **数学公式** - 通过KaTeX/MathJax渲染LaTeX数学公式
- 👁️ **实时预览** - 监视模式，文件变更时自动重建
- 🌐 **内置服务器** - 带热重载的本地预览服务器

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/MarkdownForge-Pro.git
cd MarkdownForge-Pro

# 本地安装
pip install -e .
```

#### 基本用法

```bash
# 将markdown转换为HTML
markdownforge input.md

# 生成带目录的文档
markdownforge input.md --toc

# 导出为PDF
markdownforge input.md -f pdf

# 监视文件变更
markdownforge input.md --watch

# 启动预览服务器
markdownforge input.md --serve --open
```

### 📖 详细使用指南

#### 命令行选项

```
markdownforge [选项] 输入文件

选项:
  -o, --output PATH       输出文件路径
  -f, --format FORMAT     输出格式: html, pdf, docx (默认: html)
  --toc                   添加目录
  --toc-depth INTEGER     目录最大深度 (默认: 6)
  --no-highlight          禁用语法高亮
  --math RENDERER         数学渲染器: katex, mathjax, none (默认: katex)
  --theme THEME           主题名称 (默认: default)
  -w, --watch             监视文件变更
  -s, --serve             启动预览服务器
  -p, --port INTEGER      服务器端口 (默认: 8080)
  --open                  启动服务器后打开浏览器
  -v, --version           显示版本
  --verbose               启用详细输出
```

### 🤝 贡献指南

欢迎贡献！请随时提交Pull Request。

### 📄 开源协议

本项目采用 MIT 协议。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 項目介紹

**MarkdownForge-Pro** 是一個功能強大且輕量級的終端Markdown文檔處理引擎。它能將您的Markdown文件轉換為格式精美的文檔，並提供智能增強功能。

### ✨ 核心特性

- 🚀 **零依賴** - 純Python標準庫，無需外部包
- 📄 **多格式導出** - 生成HTML、PDF和Word兼容文檔
- 🎨 **語法高亮** - 支持20+種語言的自動代碼高亮
- 📑 **智能目錄** - 自動生成帶錨點鏈接的目錄
- 🧮 **數學公式** - 通過KaTeX/MathJax渲染LaTeX數學公式
- 👁️ **實時預覽** - 監視模式，文件變更時自動重建
- 🌐 **內置服務器** - 帶熱重載的本地預覽服務器

### 🚀 快速開始

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/MarkdownForge-Pro.git
cd MarkdownForge-Pro

# 本地安裝
pip install -e .
```

#### 基本用法

```bash
# 將markdown轉換為HTML
markdownforge input.md

# 生成帶目錄的文檔
markdownforge input.md --toc

# 導出為PDF
markdownforge input.md -f pdf

# 監視文件變更
markdownforge input.md --watch

# 啟動預覽服務器
markdownforge input.md --serve --open
```

### 📖 詳細使用指南

#### 命令行選項

```
markdownforge [選項] 輸入文件

選項:
  -o, --output PATH       輸出文件路徑
  -f, --format FORMAT     輸出格式: html, pdf, docx (默認: html)
  --toc                   添加目錄
  --toc-depth INTEGER     目錄最大深度 (默認: 6)
  --no-highlight          禁用語法高亮
  --math RENDERER         數學渲染器: katex, mathjax, none (默認: katex)
  --theme THEME           主題名稱 (默認: default)
  -w, --watch             監視文件變更
  -s, --serve             啟動預覽服務器
  -p, --port INTEGER      服務器端口 (默認: 8080)
  --open                  啟動服務器後打開瀏覽器
  -v, --version           顯示版本
  --verbose               啟用詳細輸出
```

### 🤝 貢獻指南

歡迎貢獻！請隨時提交Pull Request。

### 📄 開源協議

本項目採用 MIT 協議。

---

<p align="center">
  Made with ❤️ by MarkdownForge Team
</p>
