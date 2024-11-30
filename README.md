# sakuraTools 插件

## 简介
**sakuraTools** 是一个基于 chatgpt-on-wechat 的插件，集成了一系列有趣的小功能，包括获取舔狗日记、笑话、摸鱼日历、二次元图片、小姐姐视频、星座运势、虫部落热门帖子、疯狂星期四文案、以及赛博算卦等功能。

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
- **抽卡**: 获取带有解读的单张塔罗牌。
- **抽牌**: 抽取单张塔罗牌。
- **三牌阵**: 抽取塔罗牌三牌阵。
- **十字牌阵**: 抽取塔罗牌十字牌阵。
- **黄历**: 获取黄历。
- **抽签**: 抽取真武灵签。
- **卦图+卦名**: 获取指定卦图。
- **每日一卦**: 随机获取一张卦图。
- **百度热搜**: 获取微博热搜图片。
- **微博热搜**: 获取百度热搜图片。
- **AI搜索**: 根据提示词获取AI整合搜索结果。
- **AI绘图**: 根据提示词生成AI绘图(效果一般、但是免费啊)。
- **梅花易数**: 根据你的问题使用梅花易数为你占卜。
- **运势**: 获取运势。
- **表情**: 获取一张随机表情包，实在是没什么用的功能(笑)。


## 配置
该插件支持关键字配置，例如舔狗日记、笑话、摸鱼等关键字，这些可以在配置文件中自定义，星座无需定义。

示例配置：
```json
{
    "dog_diary_keyword": ["舔狗日记","舔狗日常"],
    "joke_keyword": ["笑话","讲个笑话","来个笑话","来点笑话"],
    "moyu_keyword": ["摸鱼","摸鱼日历"],
    "acg_keyword": ["二次元老婆","ACG美图","acg美图","纸片人老婆","动漫图"],
    "young_girl_keyword": ["小姐姐"],
    "beautiful_keyword": ["美女"],
    "chongbuluo_keyword": ["虫部落"],
    "kfc_keyword":["肯德基","kfc","KFC","疯狂星期四"],
    "wyy_keyword":["网抑云", "wyy"],
    "draw_card_keyword":["抽卡"],
    "newspaper_keyword": ["日报","早报","速读报","快报"],
    "tarot_single_keyword":["抽牌", "抽一张牌"],
    "tarot_three_keyword":["三牌阵","三张牌阵","过去-现在-未来阵"],
    "tarot_cross_keyword":["凯尔特十字","凯尔特十字牌阵","十字牌阵","十字阵"],
    "huang_li_keyword":["黄历","老黄历","今日黄历","黄历查询"],
    "zwlq_chou_qian_keyword": ["抽签","抽签查询","抽签结果", "每日一签"],
    "zwlq_jie_qian_keyword":["解签","解签查询","解签结果"],
    "dytj_gua_tu_keyword":["卦图"],
    "dytj_daily_gua_tu_keyword":["每日一卦"],
    "hot_search_keyword":["热搜"],
    "hot_search_baidu_keyword":["百度热搜"],
    "hot_search_weibo_keyword":["微博热搜"],
    "ai_find_keyword":["搜索", "搜一下", "查一下", "AI搜索", "ai搜索"],
    "ai_draw_keyword":["画一个","画个", "画一下", "画一张", "画一张", "画一幅", "画一只", "画一头"],
    "mei_hua_yi_shu_keyword":["算算", "算一算","算一卦","卜卦","算一下","来一卦", "开一卦"],
    "mei_hua_yi_shu": false
}
```

梅花易数功能目前依赖 `智谱AI` 实现，暂未适配其他AI，默认关闭该功能，如需使用，请将 config.json 中的 `mei_hua_yi_shu` 设置为 `true`。

## 功能展示
#### 梅花易数卜卦
![image](https://github.com/user-attachments/assets/f78e62f0-5170-4dc5-b721-03c304bfe95d)
#### 舔狗日记
![image](https://github.com/user-attachments/assets/a42d1eab-5030-4dae-993b-6f5be6c81aef)
#### 笑话
![image](https://github.com/user-attachments/assets/20b6264c-3530-40c1-80cc-e686e118d30c)
#### 摸鱼日历
![image](https://github.com/user-attachments/assets/80620175-6d50-474a-b370-ac837781e8e2)
#### 二次元美图
![image](https://github.com/user-attachments/assets/e5db198d-3190-450e-955d-93ffec93fbe9)
#### 小姐姐视频
![image](https://github.com/user-attachments/assets/92bbf9d6-4b00-44b1-9402-550f9ce13c8f)
#### 美女视频
![image](https://github.com/user-attachments/assets/969ec749-981b-40e9-8fbd-9d442f4dbd91)
#### 虫部落热搜
![image](https://github.com/user-attachments/assets/bc6d4650-fe42-45d5-b521-bac741f14baa)
#### 疯狂星期四文案
![image](https://github.com/user-attachments/assets/8e23893c-7bbc-41f4-bc92-dafbc4b54a0c)
#### 网易云热论
![image](https://github.com/user-attachments/assets/0559f870-ef3f-41c1-8ed0-6795694b2aac)
#### 早报
![image](https://github.com/user-attachments/assets/30094629-e5b6-41d7-8957-0d6ae41fe5c9)
#### 星座运势
![image](https://github.com/user-attachments/assets/e5500c07-8761-49d4-ad4b-0bdb1cd78453)
#### 塔罗牌
![image](https://github.com/user-attachments/assets/f495c476-cc99-407c-89f9-d9828651ae5a)
![image](https://github.com/user-attachments/assets/a7cd8eb8-e801-4fac-ab54-b1810ab99ca5)
#### 黄历
![image](https://github.com/user-attachments/assets/28b3c75a-41b1-48ea-b40c-2b21ec3e90f0)
#### 真武灵签
![image](https://github.com/user-attachments/assets/6510985b-8425-4505-9944-34734078d31c)
#### 断易天机卦图
![image](https://github.com/user-attachments/assets/b1fba9ae-e345-4cfd-beb1-eb49d7d03f78)
![image](https://github.com/user-attachments/assets/176d86b4-1b55-473b-a127-0b64ed53361f)
#### 热搜
![image](https://github.com/user-attachments/assets/9b5ad541-2e1e-43ab-beb1-d3e6bb10c885)
#### AI搜索
![image](https://github.com/user-attachments/assets/c1720148-8032-47d0-a862-02fc63305a6a)
#### AI绘图
![image](https://github.com/user-attachments/assets/9c7144d8-b818-4fcc-b5e0-ad697646c646)


## 记录日志
本插件支持日志记录，所有请求和响应将被记录，方便调试和优化。日志信息将输出到指定的日志文件中，确保可以追踪插件的使用情况。

## 贡献
欢迎任何形式的贡献，包括报告问题、请求新功能或提交代码。你可以通过以下方式与我们联系：

- 提交 issues 到项目的 GitHub 页面。
- 发送邮件至 [sakuraduck@foxmail.com]。

## 赞助
开发不易，我的朋友，如果你想请我喝杯咖啡的话(笑)

<img src="https://github.com/user-attachments/assets/db273642-1787-4195-af52-7b14c8733405" alt="image" width="300"/> 


## 许可
此项目采用 Apache License 版本 2.0，详细信息请查看 [LICENSE](LICENSE)。

---
