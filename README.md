# sakuraTools 插件

## 简介
**sakuraTools** 是一个基于 chatgpt-on-wechat 的插件，集成了一系列有趣的小功能，包括获取舔狗日记、笑话、摸鱼日历、二次元图片、小姐姐视频、星座运势、虫部落热门帖子，以及疯狂星期四文案等。

## 安装
- 方法一：
  - 载的插件文件都解压到`plugins`文件夹的一个单独的文件夹，最终插件的代码都位于`plugins/PLUGIN_NAME/*`中。启动程序后，如果插件的目录结构正确，插件会自动被扫描加载。除此以外，注意你还需要安装文件夹中`requirements.txt`中的依赖。

- 方法二：
  - 借助`Godcmd`插件，它是预置的管理员插件，能够让程序在运行时就能安装插件，它能够自动安装依赖。
    - 使用 `#installp git@github.com:Sakura7301/sakuraTools.git` 命令自动安装插件
    - 在安装之后，需要执行`#scanp`命令来扫描加载新安装的插件。
    - 创建`config.json`文件定义你需要的内容，可以参照`config.json.template`。
    - 插件扫描成功之后需要手动使用`#enablep sakuraTools`命令来启用插件。

## 使用方法
在微信聊天界面输入关键词触发插件的功能：
- **早报**: 获取今日早报。
- **舔狗日记**: 获取一则舔狗日记。
- **笑话**: 获得一则笑话。
- **摸鱼日历**: 获取摸鱼日历。
- **二次元老婆**: 获取一张纸片人老婆图片。
- **小姐姐**: 获取一条小姐姐视频。
- **美女**: 获取一条美女视频。
- **星座名**: 获取今日运势。
- **虫部落**:获取虫部落今日热门。
- **疯狂星期四**: 获取一条一条随机疯四文案。
- **网抑云**: 获取网抑云热评。
- **抽牌**: 抽取单张塔罗牌。
- **三牌阵**: 抽取塔罗牌三牌阵。
- **十字牌阵**: 抽取塔罗牌十字牌阵。
- **黄历**: 获取黄历。
- **抽签**: 抽取真武灵签。
- **卦图+卦名**: 获取指定卦图。
- **每日一卦**: 随机获取一张卦图。


## 配置
该插件支持关键字配置，例如舔狗日记、笑话、摸鱼等关键字，这些可以在配置文件中自定义，星座无需定义。

示例配置：
```json
{
    "image_tmp_path":"./plugins/sakuraTools/tmp",
    "dog_diary_keyword": ["舔狗","舔狗日记","舔狗日常"],
    "joke_keyword": ["笑话","讲个笑话","来个笑话","来点笑话"],
    "moyu_keyword": ["摸鱼","摸鱼日历"],
    "acg_keyword": ["二次元老婆","ACG美图","acg美图","纸片人老婆","动漫图"],
    "young_girl_keyword": ["小姐姐", "老婆"],
    "beautiful_keyword": ["美女"],
    "chongbuluo_keyword": ["虫部落"],
    "kfc_keyword":["肯德基","kfc","KFC","疯狂星期四"],
    "wyy_keyword":["网抑云"],
    "newspaper_keyword": ["日报","早报","速读报","快报"],
    "tarot_cards_path": "plugins/sakuraTools/images/TarotCards",
    "tarot_single_keyword":["抽牌", "抽一张牌"],
    "tarot_three_keyword":["三牌阵","三张牌阵","过去-现在-未来阵"],
    "tarot_cross_keyword":["凯尔特十字","凯尔特十字牌阵","十字牌阵","十字阵"],
    "huang_li_keyword":["黄历","老黄历","今日黄历","黄历查询"],
    "zwlq_image_path": "plugins/sakuraTools/images/ZWLQ",
    "zwlq_chou_qian_keyword": ["抽签","抽签查询","抽签结果", "每日一签"],
    "zwlq_jie_qian_keyword":["解签","解签查询","解签结果"],
    "dytj_image_path": "plugins/sakuraTools/images/DYTJ",
    "dytj_gua_tu_keyword":["卦图"],
    "dytj_daily_gua_tu_keyword":["每日一卦"],
    "delete_files_time_interval":86400
}
```

## 记录日志
本插件支持日志记录，所有请求和响应将被记录，方便调试和优化。日志信息将输出到指定的日志文件中，确保可以追踪插件的使用情况。

## 贡献
欢迎任何形式的贡献，包括报告问题、请求新功能或提交代码。你可以通过以下方式与我们联系：

- 提交 issues 到项目的 GitHub 页面。
- 发送邮件至 [你的邮箱]。

## 许可
此项目采用 Apache License 版本 2.0，详细信息请查看 [LICENSE](LICENSE)。

---
