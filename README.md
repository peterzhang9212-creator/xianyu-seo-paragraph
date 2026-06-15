# 闲鱼教师SEO项目_段落版

一个用于闲鱼教师类商品素材整理、组装、水印、上传表生成和发布预检的本地工具。

## 功能

- 文件组装
- 批量加水印
- 正文模板导入
- 上传表生成
- 子文件夹导出
- 发布预检和发布

## 环境要求

- Python 3.12 或更高
- 已安装依赖
- 发布功能需要本机打开 `BitBrowser` 并登录闲鱼

## 安装

```powershell
python -m pip install -r requirements.txt
```

## 启动

```powershell
python app.py
```

## 主要文件

- `app.py` 程序入口
- `config/defaults.json` 默认参数和上次输入
- `core/` 核心逻辑
- `ui/` 图形界面
- `vendor/` 迁入的水印和发布核心
- `templates/content_template.xlsx` 正文模板
- `docs/` 使用和维护说明

## 运行顺序

1. 文件组装
2. 加水印
3. 生成上传表
4. 预检
5. 发布

## 常见问题

- 如果发布失败，先检查 `BitBrowser` 是否已打开。
- 正文模板里的 `导出商品名` 必须和素材文件夹名一致。
- 图片缓存和运行结果不需要上传到 GitHub。
