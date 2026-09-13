# 介绍

![](logo.png)

云飞机器人中文维基 (RoboWiki-cn) 是由 [云飞机器人实验室](https://space.bilibili.com/493264461) 发起的机器人公共领域知识编辑项目。目前该项目在 [GitHub](https://github.com/yfrobotics/robowiki) 管理和维护。

本维基旨在涵盖机器人设计、建模、仿真、编程、视觉、算法、行业应用等各个方面的内容。

我们采用公共知识编辑的方式并提倡**知识自由** --- 所有人都被鼓励、并可以亲自参与到编辑的过程中，并在该过程中不断改进内容的质量。

机器人正在不断的进入到我们的生活里。我们相信通过整个社区的努力，可以最终做成覆盖全面的机器人知识库，为机器人开发者、研究者和爱好者提供便利。


## 写在前面

本维基的目的在于提供机器人开发的基础知识，方便机器人研究者、开发人员及爱好者。

机器人涉及的知识甚广，不可能通过一本书或者一个网站彻底介绍。本维基的目的是将一些常用的、通用的知识进行归纳整理，供机器人入门者学习或作为参考，并方便日后深入的学习。


## 搜索引擎与页面摘要

`mkdocs.yml` 中的 `site_url` 必须与部署地址一致（包含 `/robowiki-cn/`），用于生成规范链接和 `sitemap.xml`。
部署后，可在 Google Search Console 中提交 `https://yfrobotics.github.io/robowiki-cn/sitemap.xml`。
GitHub Pages 项目目录下的 `robots.txt` 不控制爬虫；如需声明站点地图，应在域名根目录所属的网站中配置。

每篇文章可以使用 YAML front matter 编写标题和摘要：

```yaml
---
title: PID 控制器原理与实现
description: 介绍 PID 控制器的连续与离散公式，以及 C 语言实现中的积分和微分处理。
---
```

没有显式摘要时，`scripts/seo.py` 从正文段落生成摘要。页面模板复用摘要生成 Open Graph、Twitter 卡片和 WebPage 结构化数据。
修改后运行 `mkdocs build`，检查生成页面的标题、摘要、规范链接和 `site/sitemap.xml`。


## 致谢

本维基在设计过程中受到了 [OI-wiki](https://oi-wiki.org/) 和 [CTF-Wiki](https://ctf-wiki.github.io/ctf-wiki/) 的设计理念启发。

本项目基于MkDocs静态文档架构以及Materials主题。

如果没有这些开放的知识和开源工具，我们无法做到现在的程度。在此一并表示感谢。


## 版权声明

本维基遵循"知识共享署名-相同方式共享4.0 国际协议 (CC 4.0-BY-SA)" ，详见 [条款](https://creativecommons.org/licenses/by-sa/4.0/deed.zh-Hans)。

![cc-by-sa-4.0](https://i.creativecommons.org/l/by-sa/4.0/88x31.png)
