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


## 推荐工具

- Git版本控制: SourceTree / GitKraken
- Markdown编辑工具: Typora / Visual Studi Code 
