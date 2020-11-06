# 如何贡献这个维基？

[项目GitHub地址](https://github.com/yfrobotics/robowiki)

## 贡献方法

你可以通过以下两种方式贡献这个维基：

1. 通过提交代码PR：git clone -> make change -> push & pull request
2. 通过创建issues：[Create a new issue](https://github.com/yfrobotics/robowiki/issues)


## 环境配置与运行

```bash
# 安装依赖
> sudo python3 -m pip install -r "requirements.txt"

# 确认mkdocs安装成功并显示版本
> mkdocs --version

# 运行mkdocs
> mkdocs serve
```

运行成功之后，打开浏览器，访问：`localhost:8000`


## 开发细节

- [Materials for Mkdocs文档](https://squidfunk.github.io/mkdocs-material/reference/abbreviations/)
- 创建新条目: 如果你的修改涉及新增条目，你需要同时在`mkdocs.yml`中修改导航目录。


## 排版与文档管理约束

- 文本格式: 本维基所有内容全部使用Markdown格式进行书写。
- 图片的保存: 图片保存在对应子目录下的`assets`目录中，使用Github作为图床。如果有与之对应的原始文件 (.vsx, .drawio, .ps等)，也以同样名称保存在相同目录。
