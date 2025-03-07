import os
import re
import io
import time
import json
import random
import plugins
import requests
from plugins import *
import concurrent.futures
from common.log import logger
from datetime import datetime
from PIL import Image, ImageDraw
from bridge.bridge import Bridge
from bridge.context import ContextType, Context
from bridge.reply import Reply, ReplyType
from plugins.sakuraTools.meihuayishu import MeiHuaXinYi
from plugins.sakuraTools.meihuayishu import GetGuaShu
from plugins.sakuraTools.meihuayishu import FormatZhanBuReply
from plugins.sakuraTools.meihuayishu import GenZhanBuCueWord


@plugins.register(
    name="sakuraTools",  # 插件名称
    desire_priority=99,  # 插件优先级
    hidden=False,  # 是否隐藏
    desc="有趣的小功能合集",  # 插件描述
    version="1.0.2",  # 插件版本
    author="sakura7301",  # 作者
)
class sakuraTools(Plugin):
    def __init__(self):
        # 调用父类的初始化
        super().__init__()
        # 获取协议类型
        self.channel_type = conf().get("channel_type")
        # 定义目标URL
        self.DOG_URL = "https://api.vvhan.com/api/text/dog?type=json"
        self.JOKE_URL = "https://api.pearktrue.cn/api/jdyl/xiaohua.php"
        self.MOYU_URL = "https://api.vvhan.com/api/moyu?type=json"
        self.ACG_URL = "https://api.vvhan.com/api/wallpaper/acg?type=json"
        self.PIXIV_URL = "https://xiaobapi.top/api/xb/api/pixiv.php"
        self.YOUNG_GIRL_URL = ["https://api.317ak.com/API/sp/hssp.php",
                            "https://api.317ak.com/API/sp/xjxl.php",
                            "https://api.317ak.com/API/sp/ldxl.php",
                            "https://api.317ak.com/API/sp/zycx.php",
                            "https://api.317ak.com/API/sp/slxl.php",
                            "https://api.317ak.com/API/sp/ndxl.php"
        ]
        self.BEAUTIFUL_URL = "https://api.317ak.com/API/sp/hssp.php"
        self.CONSTELLATION_URL = "https://api.vvhan.com/api/horoscope"
        self.CONSTELLATION_URL_BACKUP = "https://xiaobapi.top/api/xb/api/xingzuo.php"
        self.CBL_URL = "https://api.vvhan.com/api/hotlist/chongBluo"
        self.KFC_URL = "https://api.pearktrue.cn/api/kfc"
        self.WYY_URL = "https://zj.v.api.aa1.cn/api/wenan-wy/?type=json"
        self.NEWSPAPER_URL = "https://api.03c3.cn/api/zb?type=jsonImg"
        self.HUANG_LI_URL = "https://www.36jxs.com/api/Commonweal/almanac"
        self.HOT_SEARCH_URL = "https://api.pearktrue.cn/api/60s/image/hot"
        self.AI_FIND_URL = "https://api.pearktrue.cn/api/aisearch/"
        self.AI_DRAW_URL = "https://api.pearktrue.cn/api/stablediffusion/"
        self.DRAW_CARD_URL = "https://www.hhlqilongzhu.cn/api/tu_tlp.php"
        self.FORTUNE_URL = "https://www.hhlqilongzhu.cn/api/tu_yunshi.php"

        # 初始化配置
        self.config = super().load_config()
        # 加载配置模板
        if not self.config:
            self.config = self._load_config_template()

        # 加载图片临时目录
        self.image_tmp_path = "./plugins/sakuraTools/tmp"
        # 加载塔罗牌目录
        self.tarot_cards_path = "plugins/sakuraTools/images/TarotCards"
        # 加载真武灵签目录
        self.zwlq_image_path = "plugins/sakuraTools/images/ZWLQ"
        # 加载断易天机64卦卦图目录
        self.dytj_image_path = "plugins/sakuraTools/images/DYTJ"
        # 加载舔狗日记关键字
        self.dog_keyword = self.config.get("dog_diary_keyword", [])
        # 加载笑话关键字
        self.joke_keyword = self.config.get("joke_keyword", [])
        # 加载摸鱼关键字
        self.moyu_keyword = self.config.get("moyu_keyword", [])
        # 加载二次元关键字
        self.acg_keyword = self.config.get("acg_keyword", [])
        # 加载二次元关键字
        self.pixiv_keyword = self.config.get("pixiv_keyword", [])
        # 加载小姐姐视频关键字
        self.young_girl_keyword = self.config.get("young_girl_keyword", [])
        # 加载美女视频关键字
        self.beautiful_keyword = self.config.get("beautiful_keyword", [])
        # 加载虫部落热搜关键字
        self.chongbuluo_keyword = self.config.get("chongbuluo_keyword", [])
        # 加载疯狂星期四关键字
        self.kfc_keyword = self.config.get("kfc_keyword", [])
        # 加载网抑云关键字
        self.wyy_keyword = self.config.get("wyy_keyword", [])
        # 加载早报关键字
        self.newspaper_keyword = self.config.get("newspaper_keyword", [])
        # 加载随机表情包关键字(可能这样子更人性化一些？)
        self.meme_keyword = self.config.get("meme_keyword", [])
        # 加载抽卡关键字
        self.draw_card_keyword = self.config.get("draw_card_keyword", [])
        # 加载运势关键字
        self.fortune_keyword = self.config.get("fortune_keyword", [])
        # 加载塔罗牌单抽牌关键字
        self.tarot_single_keyword = self.config.get("tarot_single_keyword", [])
        # 加载塔罗牌三牌阵关键字
        self.tarot_three_keyword = self.config.get("tarot_three_keyword", [])
        # 加载塔罗牌十字牌阵关键字
        self.tarot_cross_keyword = self.config.get("tarot_cross_keyword", [])
        # 加载黄历关键字
        self.huang_li_keyword = self.config.get("huang_li_keyword", [])
        # 加载真武灵签抽签关键字
        self.zwlq_chou_qian_keyword = self.config.get("zwlq_chou_qian_keyword", [])
        # 加载真武灵签解签关键字
        self.zwlq_jie_qian_keyword = self.config.get("zwlq_jie_qian_keyword", [])
        # 加载断易天机指定卦图关键字
        self.dytj_gua_tu_keyword = self.config.get("dytj_gua_tu_keyword", [])
        # 加载每日一卦关键字
        self.dytj_daily_gua_tu_keyword = self.config.get("dytj_daily_gua_tu_keyword", [])
        # 加载热搜关键字
        self.hot_search_keyword = self.config.get("hot_search_keyword", [])
        self.hot_search_baidu_keyword = self.config.get("hot_search_baidu_keyword", [])
        self.hot_search_weibo_keyword = self.config.get("hot_search_weibo_keyword", [])
        # 加载AI搜索关键字
        self.ai_find_keyword = self.config.get("ai_find_keyword", [])
        # 加载AI画图关键字
        self.ai_draw_keyword = self.config.get("ai_draw_keyword", [])
        # 加载梅花易数开关
        self.mei_hua_yi_shu = self.config.get("mei_hua_yi_shu")
        # 加载梅花易数关键字
        self.mei_hua_yi_shu_keyword = self.config.get("mei_hua_yi_shu_keyword", [])
        # 存储上一次清理日期
        self.last_cleanup_date = None
        # 星座名映射
        self.ZODIAC_MAPPING = {
            '白羊座': 'aries',
            '金牛座': 'taurus',
            '双子座': 'gemini',
            '巨蟹座': 'cancer',
            '狮子座': 'leo',
            '处女座': 'virgo',
            '天秤座': 'libra',
            '天蝎座': 'scorpio',
            '射手座': 'sagittarius',
            '摩羯座': 'capricorn',
            '水瓶座': 'aquarius',
            '双鱼座': 'pisces'
        }
        # 六十四卦映射
        self.sixty_four_gua_mapping = {
            "乾": "乾为天",
            "坤": "坤为地",
            "震": "震为雷",
            "巽": "巽为风",
            "坎": "坎为水",
            "离": "离为火",
            "艮": "艮为山",
            "兑": "兑为泽",
            "天风": "天风姤",
            "天山": "天山遁",
            "天地": "天地否",
            "天雷": "天雷无妄",
            "天火": "天火同人",
            "天水": "天水讼",
            "天泽": "天泽履",
            "地风": "地风升",
            "地山": "地山谦",
            "地天": "地天泰",
            "地雷": "地雷复",
            "地火": "地火明夷",
            "地水": "地水师",
            "地泽": "地泽临",
            "雷风": "雷风恒",
            "雷山": "雷山小过",
            "雷天": "雷天大壮",
            "雷地": "雷地豫",
            "雷火": "雷火丰",
            "雷水": "雷水解",
            "雷泽": "雷泽归妹",
            "风山": "风山渐",
            "风天": "风天小畜",
            "风地": "风地观",
            "风雷": "风雷益",
            "风火": "风火家人",
            "风水": "风水涣",
            "风泽": "风泽中孚",
            "水风": "水风井",
            "水山": "水山蹇",
            "水天": "水天需",
            "水地": "水地比",
            "水雷": "水雷屯",
            "水火": "水火既济",
            "水泽": "水泽节",
            "火风": "火风鼎",
            "火山": "火山旅",
            "火天": "火天大有",
            "火地": "火地晋",
            "火雷": "火雷噬嗑",
            "火水": "火水未济",
            "火泽": "火泽睽",
            "山风": "山风蛊",
            "山天": "山天大畜",
            "山地": "山地剥",
            "山雷": "山雷颐",
            "山火": "山火贲",
            "山水": "山水蒙",
            "山泽": "山泽损",
            "泽风": "泽风大过",
            "泽山": "泽山咸",
            "泽天": "泽天夬",
            "泽地": "泽地萃",
            "泽雷": "泽雷随",
            "泽火": "泽火革",
            "泽水": "泽水困"
        }
        # 注册处理上下文的事件
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[sakuraTools] 插件初始化完毕")

    def get_reply(self, session_id, prompt):
        """
            定义一个用于获取 AI 回复的函数
        """
        # 创建字典
        content_dict = {
            "session_id": session_id,
        }
        context = Context(ContextType.TEXT, prompt, content_dict)
        reply : Reply = Bridge().fetch_reply_content(prompt, context)
        return reply.content

    def shuffle_tarot_cards(self):
        """
            随机洗牌并返回卡牌列表
        """
        try:
            logger.debug("开始洗牌...")
            # 获取卡牌列表
            card_files = os.listdir(self.tarot_cards_path)
            # 随机打乱文件名列表
            random.shuffle(card_files)
            logger.debug("洗牌完成！")
            # 返回卡牌列表
            return card_files
        except Exception as e:
            logger.error(f"发生错误: {e}")

    def generate_draw_flag(self):
        """
            生成随机的抽牌标志 (0: 逆位, 1: 正位)
        """
        # 随机种子为当前时间戳
        random.seed(time.time())
        return random.randint(0, 1)

    def get_card_name(self, card_file):
        """
            根据文件名获取塔罗牌名称
        """
        # 从文件名中提取牌名
        return card_file.split('_', 1)[1].replace('.jpg', '')

    def tarot_single_card_check_keyword(self, query):
        return any(keyword in query for keyword in self.tarot_single_keyword)

    def tarot_three_cards_check_keyword(self, query):
        return any(keyword in query for keyword in self.tarot_three_keyword)

    def tarot_cross_cards_check_keyword(self, query):
        return any(keyword in query for keyword in self.tarot_cross_keyword)

    def tarot_get_single_card(self, num=None):
        """
            塔罗牌 单抽牌
        """
        card_files = self.shuffle_tarot_cards()
        draw_flag = self.generate_draw_flag()  # 生成抽牌标志

        output_filename = "Single"

        # 如果指定了牌位
        if num is not None:
            if 0 <= num < len(card_files):
                # 按指定位置抽牌
                selected_card = card_files[num]
                card_name = self.get_card_name(selected_card)
                logger.debug(f"抽取的牌为: {card_name} (标志: {draw_flag})")
            else:
                # 随机抽取牌位
                logger.info("参数m超出范围，使用随机数抽取牌")
                selected_card = card_files[random.randint(0, len(card_files) - 1)]
                card_name = self.get_card_name(selected_card)
                logger.debug(f"抽取的牌为: {card_name} (标志: {draw_flag})")
        else:
            # 随机抽取牌位
            selected_card = card_files[random.randint(0, len(card_files) - 1)]
            card_name = self.get_card_name(selected_card)
            logger.info(f"抽取的牌为: {card_name} (标志: {draw_flag})")

        # 根据抽牌标志处理图像
        if draw_flag == 0:  # 逆位处理
            logger.debug(f"抽到：{card_name}(逆位)")
            output_filename += f"_{card_name}逆"
        else:
            logger.debug(f"抽到：{card_name}(正位)")
            output_filename += f"_{card_name}正"

        # 生成路径
        output_filename += ".png"
        # 检查目录是否存在
        self.ensure_directory_exists(self.image_tmp_path)
        # 生成路径
        output_path = os.path.join(self.image_tmp_path, output_filename)

        # 检查文件是否已存在
        if os.path.exists(output_path):
            #存在就直接返回
            logger.debug(f"找到已存在的图片：{output_path}")
        else:
            # 生成合成图像逻辑
            card_path = os.path.join(self.tarot_cards_path, selected_card)
            # 打开图像
            card_image = Image.open(card_path).convert("RGBA")

            if draw_flag == 0:
                # 逆位处理(旋转图像)
                card_image = card_image.rotate(180)

            # 压缩图像
            card_image = card_image.resize((card_image.width//3, card_image.height//3), Image.LANCZOS)

            # 保存合成的图片
            card_image.save(output_path)

        return open(output_path, 'rb')

    def tarot_get_three_cards(self, query=None):
        """
            塔罗牌 三牌阵
        """
        # 洗牌
        card_files = self.shuffle_tarot_cards()
        selected_cards = []  # 用于保存选中的卡牌信息
        output_filename = "Three"

        for i in range(3):
            # 生成抽牌标志
            draw_flag = self.generate_draw_flag()
            #按顺序抽
            selected_card = card_files[i]
            card_name = self.get_card_name(selected_card)
            # 保存完整信息
            selected_cards.append((selected_card, card_name, draw_flag))

            if draw_flag == 0:
                # 逆位处理
                logger.debug(f"抽到：{card_name}(逆位)")
                output_filename += f"_{card_name}逆"
            else:
                # 正位处理
                logger.debug(f"抽到：{card_name}(正位)")
                output_filename += f"_{card_name}正"

        logger.info("抽取的三张牌为: " + ", ".join([f"{name}({'正位' if flag == 1 else '逆位'})" for _, name, flag in selected_cards]))

        # 生成路径
        output_filename += ".png"
        # 检查目录是否存在
        self.ensure_directory_exists(self.image_tmp_path)
        # 生成路径
        output_path = os.path.join(self.image_tmp_path, output_filename)

        # 检查文件是否已存在
        if os.path.exists(output_path):
            #存在就直接返回
            logger.debug(f"找到已存在的图片：{output_path}")
        else:
            # 生成合成图像逻辑
            card_images = []

            for selected_card, card_name, draw_flag in selected_cards:
                card_path = os.path.join(self.tarot_cards_path, selected_card)
                card_image = Image.open(card_path).convert("RGBA")

                # 根据抽牌标志处理图像
                if draw_flag == 0:
                    # 逆位处理(旋转图像)
                    card_image = card_image.rotate(180)

                # 添加处理后的图像
                card_images.append(card_image)
            # 3张牌的宽度加上间隔
            total_width = sum(img.width for img in card_images) + 100
            # 适当增加高度
            total_height = max(img.height for img in card_images) + 20
            # 背景颜色
            background_color = (200, 220, 255)
            # 创建新图像
            new_image = Image.new('RGBA', (total_width, total_height), background_color)
            # 创建绘图对象
            draw = ImageDraw.Draw(new_image)
            # 边框颜色
            border_color = (0, 0, 0)
            border_thickness = 3

            # 将三张牌放入新图片
            x_offset = 20
            for img in card_images:
                new_image.paste(img, (x_offset, 10))
                draw.rectangle([x_offset, 10, x_offset + img.width, 10 + img.height], outline=border_color, width=border_thickness)
                x_offset += img.width + 30

            # 压缩图像
            new_image = new_image.resize((total_width//5, total_height//5), Image.LANCZOS)

            # 保存合成的图片
            new_image.save(output_path)

            logger.debug(f"合成的三张牌图片已保存: {output_path}")
        return open(output_path, 'rb')

    def tarot_get_cross_cards(self, query=None):
        """
            塔罗牌 十字牌阵
        """
        # 洗牌
        card_files = self.shuffle_tarot_cards()
        selected_cards = []

        output_filename = "Cross"

        for i in range(5):
            # 生成抽牌标志
            draw_flag = self.generate_draw_flag()
            #按顺序抽
            selected_card = card_files[i]
            # 牌名
            card_name = self.get_card_name(selected_card)
            # 保存完整信息
            selected_cards.append((selected_card, card_name, draw_flag))

            if draw_flag == 0:
                # 逆位处理
                logger.debug(f"抽到：{card_name}(逆位)")
                output_filename += f"_{card_name}逆"
            else:
                # 正位处理
                logger.debug(f"抽到：{card_name}(正位)")
                output_filename += f"_{card_name}正"

        logger.info("抽取的五张牌为: " + ", ".join([f"{name}({'正位' if flag == 1 else '逆位'})" for _, name, flag in selected_cards]))

        # 生成路径
        output_filename += ".png"
        # 检查目录是否存在
        self.ensure_directory_exists(self.image_tmp_path)
        # 生成路径
        output_path = os.path.join(self.image_tmp_path, output_filename)

        # 检查文件是否已存在
        if os.path.exists(output_path):
            #存在就直接返回
            logger.debug(f"找到已存在的图片：{output_path}")
        else:
            # 生成合成图像逻辑
            card_images = []
            for selected_card, card_name, draw_flag in selected_cards:
                # 牌路径
                card_path = os.path.join(self.tarot_cards_path, selected_card)
                # 打开图像
                card_image = Image.open(card_path).convert("RGBA")
                # 根据抽牌标志处理图像
                if draw_flag == 0:
                    # 逆位处理(旋转图像)
                    card_image = card_image.rotate(180)

                # 添加处理后的图像
                card_images.append(card_image)

            # 计算合成图像的尺寸
            card_width, card_height = card_images[0].size
            total_width = card_width * 3 + 120
            total_height = card_height * 3 + 120

            # 创建新图像
            background_color = (200, 220, 255)
            new_image = Image.new('RGBA', (total_width, total_height), background_color)
            draw = ImageDraw.Draw(new_image)

            # 边框颜色
            border_color = (0, 0, 0)
            border_thickness = 3

            # 计算中心位置
            center_x = (total_width - card_width) // 2
            center_y = (total_height - card_height) // 2

            # 中心
            new_image.paste(card_images[0], (center_x, center_y))
            draw.rectangle([center_x, center_y, center_x + card_width, center_y + card_height], outline=border_color, width=border_thickness)

            # 上方
            new_image.paste(card_images[1], (center_x, center_y - card_height - 30))
            draw.rectangle([center_x, center_y - card_height - 30, center_x + card_width, center_y - 30], outline=border_color, width=border_thickness)

            # 下方
            new_image.paste(card_images[2], (center_x, center_y + card_height + 30))
            draw.rectangle([center_x, center_y + card_height + 30, center_x + card_width, center_y + card_height * 2 + 30], outline=border_color, width=border_thickness)

            # 左侧
            new_image.paste(card_images[3], (center_x - card_width - 30, center_y))
            draw.rectangle([center_x - card_width - 30, center_y, center_x - 30, center_y + card_height], outline=border_color, width=border_thickness)

            # 右侧
            new_image.paste(card_images[4], (center_x + card_width + 30, center_y))
            draw.rectangle([center_x + card_width + 30, center_y, center_x + card_width * 2 + 30, center_y + card_height], outline=border_color, width=border_thickness)

            # 压缩图像
            new_image = new_image.resize((total_width//5, total_height//5), Image.LANCZOS)

            # 保存合成的图片
            new_image.save(output_path)

            logger.debug(f"合成的五张牌图片已保存: {output_path}")
        return open(output_path, 'rb')

    def get_local_image(self, number):
        """
            在指定目录下查找指定数字前缀的图片
        """
        try:
            if not isinstance(number, int) or number < 1 or number > 49:
                logger.error(f"数字必须在1-49之间，当前数字：{number}")
                return None

            # 获取目标目录的完整路径
            target_dir = self.zwlq_image_path

            # 确保目录存在
            if not os.path.exists(target_dir):
                logger.error(f"目录不存在：{target_dir}")
                return None

            # 生成匹配的文件名模式
            patterns = [
                f"{number:02d}_",
                f"{number}_"
            ]

            for filename in os.listdir(target_dir):
                if filename.endswith('.png'):
                    for pattern in patterns:
                        if filename.startswith(pattern):
                            full_path = os.path.join(target_dir, filename)
                            logger.debug(f"找到匹配图片：{filename}")
                            return full_path

            logger.error(f"未找到数字{number}对应的签文图片")
            return None
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def check_and_delete_files(self):
        """
            检查并删除文件的主函数
        """
        # 获取当前时间
        now = datetime.now()
        today = now.date()

        if self.last_cleanup_date is None:
            # 第一次调用
            # 清空目录下的所有文件
            self.delete_all_files_in_directory(self.image_tmp_path)
            logger.info(f"已清空{self.image_tmp_path}目录下的所有文件")
            self.last_cleanup_date = today
        elif self.last_cleanup_date < today:
            # 检查是否过了一天
            # 清空目录下的所有文件
            self.delete_all_files_in_directory(self.image_tmp_path)
            logger.info(f"已清空{self.image_tmp_path}目录下的所有文件")
            self.last_cleanup_date = today

    def delete_all_files_in_directory(self, directory):
        """
            删除指定目录下的所有文件
        """
        if not os.path.exists(directory):
            logger.warning(f"目录不存在: {directory}")
            return "目录不存在"  # 返回特定消息

        try:
            # 遍历目录中的所有文件和子目录
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                # 检查是否是文件
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)  # 删除文件
                        logger.debug(f"已清除文件: {file_path}")
                    except PermissionError:
                        logger.error(f"无法删除文件 (文件可能被占用): {file_path}")
                    except Exception as e:
                        logger.error(f"发生错误: {e}")
        except Exception as e:
            logger.error(f"发生错误: {e}")

    def parse_huang_li_data(self, data):
        try:
            result = []

            # 干支纪年
            if 'TianGanDiZhiYear' in data and data['TianGanDiZhiYear'] and 'TianGanDiZhiMonth' in data and data['TianGanDiZhiMonth'] and 'TianGanDiZhiDay' in data and data['TianGanDiZhiDay']:
                result.append(f"{data['TianGanDiZhiYear']}年 {data['TianGanDiZhiMonth']}月 {data['TianGanDiZhiDay']}日")

            # 农历日期
            if 'LYear' in data and data['LYear'] and 'LMonth' in data and data['LMonth'] and 'LDay' in data and data['LDay'] and 'LMonthName' in data and data['LMonthName']:
                result.append(f"{data['LYear']}年 {data['LMonth']}{data['LDay']}  {data['LMonthName']}")

            # 公历日期
            if 'GregorianDateTime' in data and data['GregorianDateTime']:
                result.append(f"公历: {data['GregorianDateTime']}")

            # 节气
            if 'SolarTermName' in data and data['SolarTermName']:
                result.append(f"节气: {data['SolarTermName']}")

            # 宜
            if 'Yi' in data and data['Yi']:
                result.append(f"宜: {data['Yi']}")

            # 忌
            if 'Ji' in data and data['Ji']:
                result.append(f"忌: {data['Ji']}")

            # 神位
            shenwei = data.get('ShenWei', '')
            if shenwei:
                # 在"阳贵"前加一个空格
                shenwei = shenwei.replace("阳贵", " 阳贵")
                shenwei_list = shenwei.split()
                shenwei_result = ["[神位]:"]
                for item in shenwei_list:
                    shenwei_result.append(f"    {item}")
                result.append('\n'.join(shenwei_result))

            # 胎神
            if 'Taishen' in data and data['Taishen']:
                result.append(f"胎神: {data['Taishen']}")

            # 冲日
            if 'Chong' in data and data['Chong']:
                result.append(f"冲日: {data['Chong']}")

            # 岁煞
            if 'SuiSha' in data and data['SuiSha']:
                result.append(f"岁煞: {data['SuiSha']}")

            # 公历节日
            if 'GJie' in data and data['GJie']:
                result.append(f"公历节日: {data['GJie']}")

            # 农历节日
            if 'LJie' in data and data['LJie']:
                result.append(f"农历节日: {data['LJie']}")

            # 星宿
            if 'XingEast' in data and data['XingEast']:
                result.append(f"星宿: {data['XingEast']}")

            # 星座
            if 'XingWest' in data and data['XingWest']:
                result.append(f"星座: {data['XingWest']}")

            # 彭祖百忌
            if 'PengZu' in data and data['PengZu']:
                result.append(f"彭祖百忌: {data['PengZu']}")

            # 五行纳音
            if 'WuxingNaYear' in data and data['WuxingNaYear'] and 'WuxingNaMonth' in data and data['WuxingNaMonth'] and 'WuxingNaDay' in data and data['WuxingNaDay']:
                result.append(f"五行纳音: {data['WuxingNaYear']} {data['WuxingNaMonth']} {data['WuxingNaDay']}")

            # 组合结果为多行字符串
            return '\n'.join(result)

        except json.JSONDecodeError:
            return "无效的 JSON 数据"
        except Exception as e:
            return f"发生错误: {str(e)}"

    def ensure_directory_exists(self, directory):
        """
            检查指定目录是否存在，如果不存在则创建该目录
        """
        try:
            if not os.path.exists(directory):
                # 创建目录
                os.makedirs(directory, exist_ok=True)
                logger.info(f"目录已创建: {directory}")
            else:
                logger.debug(f"目录已存在: {directory}")
        except Exception as e:
            logger.error(f"发生错误: {e}")

    # 下载图片
    def download_image(self, image_url: str, name: str, image_raw=None) -> io.BytesIO:
        """
            下载图片的通用函数
        """
        try:
            if image_raw:
                write_text = image_raw
            else:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
                    "Referer": "https://i.yuki.sh/"
                }

                # 下载图片
                response = requests.get(image_url, headers=headers)
                # 检查请求是否成功
                response.raise_for_status()
                # 待写入文件内容
                write_text = response.content

            # 确定保存路径
            save_dir = self.image_tmp_path
            # 创建目录（如果不存在的话）
            self.ensure_directory_exists(save_dir)
            # 获取当前日期
            current_date = datetime.now()
            date_str = current_date.strftime("%Y-%m-%d")
            # 构建文件名
            filename = f"{name}_{date_str}.png"
            file_path = os.path.join(save_dir, filename)

            # 保存图片
            with open(file_path, 'wb') as f:
                # 写入文件
                f.write(write_text)

            logger.info(f"成功下载图片: {file_path}")
            # 关闭文件
            f.close()

            # 创建 io.BytesIO 对象并返回
            img_io = io.BytesIO(write_text)
            img_io.seek(0)  # 将指针移动到开头

            return img_io
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP错误: {http_err}")
            return None
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    # 读取图片
    def get_image_by_name(self, name: str) -> io.BytesIO:
        """
            读取图片的通用函数
        """
        try:
            # 获取当前时间并格式化为字符串
            datetime_str = datetime.now().strftime("%Y-%m-%d")  # 根据需要调整格式
            # 构建文件名
            filename = f"{name}_{datetime_str}.png"
            file_path = os.path.join(self.image_tmp_path, filename)
            logger.debug(f"查找路径：{file_path}")
            # 检查文件是否存在
            if os.path.exists(file_path):
                # 如果文件存在，读取并返回 io 对象
                image = Image.open(file_path)
                img_io = io.BytesIO()
                image.save(img_io, format='PNG')
                img_io.seek(0)  # 将指针移动到开头
                return img_io
            else:
                # 文件不存在，返回 None
                return None
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    # http通用请求接口
    def http_request_data(self, url, response_type=None, user_headers=None, user_params=None, verify_flag=None):
        """
            通用的HTTP请求函数
        """
        try:
            # 发起GET请求
            if verify_flag:
                response = requests.get(url, headers=user_headers, params=user_params, verify=False)
            else:
                response = requests.get(url, headers=user_headers, params=user_params)

            # 打印请求信息
            logger.debug(f"发送的HTTP请求:\nGET {response.url}\n{response.request.headers}\n{response.request.body}")

            # 检查响应状态码
            # 如果响应状态码不是200，将会抛出HTTPError异常
            response.raise_for_status()

            # 打印响应信息
            logger.debug(f"收到的HTTP响应:\n{response.status_code}\n{response.headers}")

            # 解析响应体
            if "raw" == response_type:
                # 直接返回二进制流
                response_data = response.content
            elif "text" == response_type:
                # 返回文本
                response_data = response.text
            elif "url" == response_type:
                response_data = response.url
            else :
                # 默认按json处理
                response_data = response.json()

            return response_data
        except requests.exceptions.HTTPError as http_err:
            err_str = f"HTTP错误: {http_err}"
            logger.error(err_str)
            return err_str
        except ValueError as json_err:
            err_str = f"JSON解析错误: {json_err}"
            logger.error(err_str)
            return err_str
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def get_first_video_url(self, response):
        """
            从响应数据中提取第一个视频的 URL
        """
        # 确保 response 有效并包含结果
        if response and 'result' in response and 'list' in response['result'] and len(response['result']['list']) > 0:
            # 返回第一个视频的 URL
            return response['result']['list'][0]['playurl']
        else:
            # 如果没有找到视频，返回 None
            return None

    def chongbuluo_five_posts(self, response):
        """
            从response中提取前五条内容
        """
        # 确保 response 有效并包含数据
        if response and response.get("success") and "data" in response:
            # 获取热门帖子并按热度排序，取前 5 条
            top_posts = sorted(response["data"], key=lambda x: float(x["hot"]), reverse=True)[:5]

            # 构造输出字符串
            output = []
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output.append(current_time)
            output.append("虫部落今日热门：")

            for index, post in enumerate(top_posts, start=1):
                output.append(f"{index}. [{post['title']}]: {post['url']}")

            return "\n".join(output)  # 将列表转换为字符串，使用换行符连接
        else:
            return "没有找到热门帖子，稍后再试试叭~🐾"

    def dog_check_keyword(self, content):
        """
            检查舔狗日记关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.dog_keyword)

    def dog_request(self, url):
        """
            舔狗日记请求函数
        """
        try:
            # http请求
            response_data = self.http_request_data(url)

            # 返回舔狗日记
            if response_data["success"]:
                # 获取舔狗日记内容
                dog_str = response_data['data']['content']
                logger.debug(f"get dog diary:{dog_str}")
                return dog_str
            else:
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)
                return err_str
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def joke_check_keyword(self, content):
        """
            检查笑话关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.joke_keyword)

    def joke_request(self, url):
        """
            笑话请求函数
        """
        try:
            # http请求
            response_data = self.http_request_data(url, "text")

            # 返回笑话
            # 获取笑话内容
            joke_str = f"""{response_data}\n(希望这则笑话能带给你快乐~🐾)"""
            logger.debug(f"get joke text:{joke_str}")
            return joke_str
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def moyu_check_keyword(self, content):
        """
            检查摸鱼日历关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.moyu_keyword)

    def moyu_request(self, url):
        """
            摸鱼日历请求函数
        """
        try:
            # 从本地获取摸鱼日历
            moyu_image_io = self.get_image_by_name("mo_yu")
            if moyu_image_io:
                # 本地存在就直接返回
                logger.debug("[sakuraTools] 本地存在摸鱼日历，直接返回。")
                return moyu_image_io
            else:
                #本地不存在，从网络获取
                logger.debug("[sakuraTools] 本地不存在摸鱼日历，从网络获取")
                # http请求
                response_data = self.http_request_data(url)

                # 返回响应的数据内容
                if response_data["success"]:
                    # 获取摸鱼日历
                    mo_yu_url = response_data['url']
                    logger.debug(f"get mo_yu image url:{mo_yu_url}")
                    return self.download_image(mo_yu_url, "mo_yu")
                else:
                    err_str = f"错误信息: {response_data['message']}"
                    logger.error(err_str)
                    return err_str
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def acg_check_keyword(self, content):
        """
            检查ACG图片关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.acg_keyword)

    def acg_request(self, url):
        """
            ACG图片请求函数
        """
        try:
            # http请求
            response_data = self.http_request_data(url)

            # 返回响应的数据内容
            if response_data["success"]:
                # 获取acg内容
                acg_image_url = response_data['url']
                logger.debug(f"get acg image url:{acg_image_url}")
                return acg_image_url
            else:
                logger.error(f"错误信息: {response_data['message']}")
                return None
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def pixiv_check_keyword(self, content):
        """
            检查pixiv图片关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.pixiv_keyword)

    def pixiv_request(self, url):
        """
            pixiv图片请求函数
        """
        try:
            # http请求
            response_data = self.http_request_data(url)

            # 返回响应的数据内容
            # 获取pixiv内容
            pixiv_image_url = response_data['data'][0]['urls']['original']
            logger.debug(f"get pixiv image url:{pixiv_image_url}")
            return self.download_image(pixiv_image_url, "pixiv")
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def draw_card_check_keyword(self, content):
        """
            检查抽卡关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.draw_card_keyword)

    def draw_card_request(self, url):
        """
            抽卡请求函数
        """
        try:

            # http请求
            response_data = self.http_request_data(url, "raw")

            # 获取抽卡内容
            logger.debug(f"get draw card image")
            return self.download_image(None, "draw_card", response_data)
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def fortune_check_keyword(self, content):
        """
            检查运势关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.fortune_keyword)

    def fortune_request(self, url):
        """
            运势请求函数
        """
        try:

            # http请求
            response_data = self.http_request_data(url, "raw")

            # 获取运势内容
            logger.debug(f"get fortune image")
            return self.download_image(None, "fortune", response_data)
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def young_girl_check_keyword(self, content):
        """
            检查小姐姐视频关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.young_girl_keyword)

    def young_girl_request(self, url):
        """
            小姐姐视频请求函数
        """
        try:
            # http请求
            if self.channel_type == "gewechat":
                headers = {"User-Agent": "Mozilla/5.0"}
                young_girl_video_url = self.http_request_data(url, "url", headers)
            else:
                response_data = self.http_request_data(url)
                young_girl_video_url = self.get_first_video_url(response_data)
            logger.debug(f"get young_girl video url:{young_girl_video_url}")
            return young_girl_video_url
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def constellation_check_keyword(self, content):
        """
            检查星座关键字
        """
        horoscope_match = re.match(r'^([\u4e00-\u9fa5]{2}座)$', content)
        return horoscope_match

    def constellation_request(self, zodiac_english, url, backup_url):
        """
            星座请求函数
        """
        try:

            # 设置请求的参数
            params = {
                "type": zodiac_english,
                "time": "today"
            }

            # http请求
            response_data = self.http_request_data(url, None, None, params)

            # 返回星座
            if response_data["success"]:
                # 获取星座运势
                data = response_data['data']
                constellation_text = (
                    f"😸{data['title']}今日运势\n"
                    f"📅 日期：{data['time']}\n"
                    f"💡【每日建议】\n宜：{data['todo']['yi']}\n忌：{data['todo']['ji']}\n"
                    f"📊【运势指数】\n"
                    f"总运势：{data['fortune']['all']}\n"
                    f"爱情：{data['fortune']['love']}\n"
                    f"工作：{data['fortune']['work']}\n"
                    f"财运：{data['fortune']['money']}\n"
                    f"健康：{data['fortune']['health']}\n"
                    f"🍀【幸运提示】\n"
                    f"数字：{data['luckynumber']}\n"
                    f"颜色：{data['luckycolor']}\n"
                    f"星座：{data['luckyconstellation']}\n"
                    f"🔔【简评】：{data['shortcomment']}"
                )
                logger.debug(f"get Constellation text:{constellation_text}")
                return constellation_text
            else:
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)
                return err_str
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str
    def chongbuluo_check_keyword(self, content):
        """
            检查虫部落热搜关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.chongbuluo_keyword)

    def chongbuluo_request(self, url):
        """
            虫部落热搜请求函数
        """
        try:
            # http请求
            response_data = self.http_request_data(url)

            # 返回虫部落热门
            if response_data["success"]:
                # 获取虫部落热门
                chongbuluo_text = self.chongbuluo_five_posts(response_data)
                logger.debug(f"get chongbuluo text:{chongbuluo_text}")
                return chongbuluo_text
            else:
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)
                return err_str
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def kfc_check_keyword(self, content):
        """
            检查疯狂星期四文案关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.kfc_keyword)

    def extract_sentences(self, text, max_length=128):
        # 按照句号分割文本，获取前面的句子
        sentences = text.split('。')
        extracted_sentences = []

        for sentence in sentences:
            if len(''.join(extracted_sentences)) + len(sentence) + 1 <= max_length:
                extracted_sentences.append(sentence.strip())
                # 只取前三个句子
            if len(extracted_sentences) >= 3:
                break

        return ''.join(extracted_sentences) + ('' if extracted_sentences else '')

    def format_ai_find_result(self, data):
        try:
            # 提取相关问题
            # related_questions = data["data"]["related_questions"]

            # 提取sources并检查是否有百度百科
            sources = data["data"]["sources"]
            baidu_baike_snippet = ""

            for source in sources:
                if "百度百科" in source["title"]:
                    # 如果找到百度百科，限制输出的snippet长度为100个汉字
                    full_snippet = source["snippet"].strip()
                    baidu_baike_snippet = self.extract_sentences(full_snippet)
                    baidu_baike_snippet += "..."

            # 创建输出字符串
            output = f"搜索[{data['keyword']}]为您找到以下内容：\n\n"

            # 添加百度百科
            if baidu_baike_snippet:
                output += f"{baidu_baike_snippet}\n\n"

            # 添加来源
            output += "\n".join(
                f"[{source['title']}] : {source['link']}\n" for source in sources[:5]
            ) + ""

            # 打印相关问题
            # output += "\n相关问题：\n" + "\n".join(f"- {question}" for question in related_questions)

            return output
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def kfc_request(self, url):
        """
            疯狂星期四文案请求函数
        """
        try:
            # http请求
            response_data = self.http_request_data(url)

            # 返回疯狂星期四文案
            if "text" in response_data:
                # 获取疯狂星期四文案
                kfc_text = response_data['text']
            logger.debug(f"get kfc text:{kfc_text}")
            return kfc_text
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def wyy_check_keyword(self, content):
        """
            检查网抑云评论关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.wyy_keyword)

    def wyy_request(self, url):
        """
            网抑云评论请求函数
        """
        try:
            # http请求
            response_data = self.http_request_data(url)

            # 返回网易云热评
            if "msg" in response_data:
                # 获取网易云热评
                wyy_text = response_data['msg']
            logger.debug(f"get wyy text:{wyy_text}")
            return wyy_text
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str
    def newspaper_check_keyword(self, content):
        """
            检查早报关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.newspaper_keyword)

    def newspaper_request(self, url):
        """
            早报请求函数
        """
        try:
            # 从本地获取早报图片
            feature_newspaper_io = self.get_image_by_name("zao_bao")
            if feature_newspaper_io:
                # 本地存在就直接返回
                logger.info("[sakuraTools] 本地存在早报图片，直接返回")
                return feature_newspaper_io
            else:
                #本地不存在，从网络获取
                # http请求
                logger.info("[sakuraTools] 本地不存在早报图片，从网络获取")
                response_data = self.http_request_data(url)

                # 获取早报内容
                newspaper_image_url = response_data['data']['imageurl']
                logger.debug(f"get zao_bao image url:{newspaper_image_url}")
                return self.download_image(newspaper_image_url, "zao_bao")
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def ai_draw_check_keyword(self, content):
        """
            检查画图关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.ai_draw_keyword)

    def ai_draw_request(self, url, content):
        """
            画图请求函数
        """
        try:
            call_word = ""
            # 遍历短语，检查是否在输入字符串中
            for phrase in self.ai_draw_keyword:
                index = content.find(phrase)
                if index != -1:
                    # 如果找到短语，提取后面的内容
                    call_word = content[index + len(phrase):].strip()
            # 默认为方形作画
            direction = "normal"

            if "横" in content:
                direction = "horizontal"
            elif "竖" in content:
                direction = "vertical"

            params = {
                "prompt" : call_word,
                "model"  : direction
            }

            logger.info(f"AI 画图：{call_word}")

            #本地不存在，从网络获取
            # http请求
            response_data = self.http_request_data(url, None, None, params)

            # 获取绘图url
            ai_draw_image_url = response_data['imgurl']
            logger.debug(f"get AI draw image url:{ai_draw_image_url}")
            return self.download_image(ai_draw_image_url, "ai_draw")
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def tarot_check_keyword(self, content):
        """
            检查塔罗牌关键字
        """
        # 检查关键词
        if self.tarot_single_card_check_keyword(content):
            return 1
        elif self.tarot_three_cards_check_keyword(content):
            return 3
        elif self.tarot_cross_cards_check_keyword(content):
            return 5
        else:
            return 0

    def tarot_request(self, num=int):
        """
            塔罗牌请求函数
        """
        try:
            # 检查抽牌分类
            if num == 1:
                # 请求单张牌
                return self.tarot_get_single_card()
            elif num == 3:
                # 请求三牌阵
                return self.tarot_get_three_cards()
            elif num == 5:
                # 请求十字牌阵
                return self.tarot_get_cross_cards()
            else:
                return None
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def huang_li_check_keyword(self, content):
        """
            检查黄历关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.huang_li_keyword)

    def huang_li_request(self, url):
        """
            黄历请求函数
        """
        try:
            # 获取当前日期
            current_date = datetime.now().strftime("%Y-%m-%d")

            # 构造请求头
            headers = {
                # 使用 Firefox 的 User-Agent
                'User-Agent': 'Mozilla/5.0 (Linux; Ubuntu; rv:94.0) Gecko/20100101 Firefox/94.0',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Host': 'www.36jxs.com',
            }

            # 设置请求的参数
            params = {
                "sun": current_date,
            }

            # http请求
            response_data = self.http_request_data(url, None, headers, params)

            # 获取黄历
            huang_li_text = self.parse_huang_li_data(response_data['data'])
            return huang_li_text
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def ai_find_check_keyword(self, content):
        """
            检查AI搜索关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.ai_find_keyword)

    def ai_find_request(self, url, content):
        """
            AI搜索函数
        """
        try:
            # 使用正则表达式提取 question
            pattern = r'(?i)搜索\s*(.*)'
            # 使用 re.search 查找第一个匹配
            match = re.search(pattern, content)
            # 返回匹配结果并去除前后空格
            question = match.group(1).strip() if match else None

            params = {
                "keyword" : question,
            }

            logger.info(f"AI 搜索：{question}")

            # http请求
            response_data = self.http_request_data(url, None, None, params)

            # 获取结果
            ai_find_text = self.format_ai_find_result(response_data)
            return ai_find_text
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def mei_hua_yi_shu_check_keyword(self, content):
        """
            检查梅花易数关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.mei_hua_yi_shu_keyword)

    def mei_hua_yi_shu_request(self, session_id, content):
        """
            梅花易数
        """
        try:
            # 获取起卦数
            qi_gua_num_result = GetGuaShu(content)
            if qi_gua_num_result and qi_gua_num_result[2] is True:
                # 使用了随机数，需要进行说明
                gen_random_num_str = f"卜卦要准确提供3个数字哦，不然会影响准确率哒,下次别忘咯~\n这次我就先用随机数{qi_gua_num_result[0]}帮你起卦叭~\n"
            else:
                gen_random_num_str = ""
            # 数字
            number = qi_gua_num_result[0]
            # 问题
            question = qi_gua_num_result[1]
            # 调用 MeiHuaXinYi 函数获取结果
            result = MeiHuaXinYi(number)
            if result:
                # 生成占卜提示词
                prompt = GenZhanBuCueWord(result, question)
                try:
                    # 使用 ThreadPoolExecutor 来设置超时
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        # 使用 lambda 函数延迟调用 get_reply 并传递 prompt 参数
                        future = executor.submit(self.get_reply, session_id, prompt)
                        # 设置超时时间为10秒
                        reply_content = future.result(timeout=30)
                except concurrent.futures.TimeoutError:
                    # 如果超时，返回超时提示
                    reply_content = "大模型超时啦~😕等一下再问叭~🐱"
                    logger.warning("[sakuraTools] [ZHIPU_AI] session_id={}, reply_content={}, 处理超时".format(session_id, reply_content))
                # 按照指定格式回复用户
                return FormatZhanBuReply(gen_random_num_str, question, number, result, reply_content)
            else:
                # MeiHuaXinYi 函数返回 None，说明数字不在范围内
                mei_hua_reply_text = "输入的数字不在指定范围内，请提供一个介于100到999之间的数字。"
                return mei_hua_reply_text
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def zwlq_chou_qian_check_keyword(self, query):
        # 定义抽签关键词列表
        return any(keyword in query for keyword in self.zwlq_chou_qian_keyword)

    def zwlq_jie_qian_check_keyword(self, query):
        # 定义解签关键词列表
        return any(keyword in query for keyword in self.zwlq_jie_qian_keyword)

    def zwlq_chou_qian_request(self):
        """
        读取本地图片并返回BytesIO对象
        """
        try:
            # 用当前时间戳作为种子
            seed = int(time.time())
            random.seed(seed)
            # 生成一个范围在1到49的随机整数
            random_number = random.randint(1, 49)
            # 获取图片路径
            image_path = self.get_local_image(random_number)

            # 检查图片是否存在
            if image_path and os.path.exists(image_path):
                # 返回图片的BytesIO对象
                return open(image_path, 'rb')
            else:
                logger.error(f"图片不存在：{image_path}")
                return None
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def dytj_gua_tu_check_keyword(self, query):
        """
            检查卦图关键词
        """
        return any(keyword in query for keyword in self.dytj_gua_tu_keyword)

    def dytj_daily_gua_tu_check_keyword(self, query):
        """
            检查每日一卦关键字
        """
        return any(keyword in query for keyword in self.dytj_daily_gua_tu_keyword)

    def dytj_gua_tu_request(self, input_text):
        """
            根据输入文本读取对应的卦图
        """
        try:
            # 去除输入文本中的空格和全角空格
            input_text = input_text.replace('　', ' ').strip()
            # 卦图目录路径
            gua_dir = self.dytj_image_path
            # 检查当前工作目录
            current_directory = os.getcwd()
            logger.debug(f"current_directory: {current_directory}")
            logger.debug(f"[DuanYiTianJi] 查找卦图目录: {gua_dir}")
            # 列出卦图目录中的所有文件
            files = os.listdir(gua_dir)
            # 去掉"卦图"关键词
            input_text = input_text.replace('卦图', '').strip()
            target_file = None
            gua_name = None

            # 通过卦名匹配卦图
            search_text = input_text.replace(' ', '')
            # 获取卦名
            if len(search_text) >= 1 and search_text[0] in self.sixty_four_gua_mapping:
                gua_name = self.sixty_four_gua_mapping[search_text[0]]
            elif len(search_text) >= 2 and search_text[:2] in self.sixty_four_gua_mapping:
                gua_name = self.sixty_four_gua_mapping[search_text[:2]]

            # 根据卦名匹配卦图文件名
            if gua_name:
                for file in files:
                    # 检查文件名是否包含目标卦名
                    file_gua_name = file.split('_')[1].replace('.jpg', '')
                    if file_gua_name == gua_name:
                        target_file = file
                        break
            # 检查是否找到了匹配的卦图
            if target_file is None:
                logger.warning(f"找不到与 '{input_text}' 匹配的卦图")
                raise None
            # 构建完整的文件路径
            image_path = os.path.join(gua_dir, target_file)
            logger.info(f"image_path:{image_path}")
            return open(image_path, "rb")

        except Exception as e:
            logger.error(f"获取卦图时出现错误：{str(e)}")
            return None

    def dytj_daily_gua_tu_request(self):
        """
            根据生成的随机数字（1-64）读取对应的卦图
        """
        try:
            # 用当前时间戳作为种子
            seed = int(time.time())
            random.seed(seed)
            # 生成一个范围在1到64的随机整数
            random_number = random.randint(1, 64)
            # 获取目录
            gua_dir = self.dytj_image_path
            # 检查当前工作目录
            current_directory = os.getcwd()
            logger.debug(f"current_directory: {current_directory}")
            logger.debug(f"[DuanYiTianJi] 查找卦图目录: {gua_dir}")
            # 列出目录中的所有文件
            files = os.listdir(gua_dir)
            # 构建文件名的前缀
            prefix = f"{random_number:02d}_"
            target_file = None
            # 遍历文件列表，查找匹配的文件名
            for file in files:
                if file.startswith(prefix):
                    target_file = file
                    break
            # 检查是否找到了匹配的卦图
            if target_file is None:
                logger.warning(f"找不到序号为 {random_number} 的卦图")
                raise None
            # 构建完整的文件路径
            image_path = os.path.join(gua_dir, target_file)
            return open(image_path, "rb")

        except Exception as e:
            logger.error(f"获取随机卦图时出现错误：{str(e)}")
            return None

    def hot_search_check_keyword(self, content):
        """
            检查热搜关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.hot_search_keyword)

    def hot_search_baidu_check_keyword(self, content):
        """
            检查百度热搜关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.hot_search_baidu_keyword)

    def hot_search_weibo_check_keyword(self, content):
        """
            检查微博热搜关键字
        """
        # 检查关键词
        return any(keyword in content for keyword in self.hot_search_weibo_keyword)

    def hot_search_request(self, context):
        """
            热搜请求函数
        """
        try:
            hot_search_type = ""
            url = self.HOT_SEARCH_URL
            # 检查热搜类型
            if self.hot_search_baidu_check_keyword(context):
                hot_search_type = "baidu"
            elif self.hot_search_weibo_check_keyword(context):
                hot_search_type = "weibo"
            else:
                # 不支持的热搜类型
                return None

            # 设置请求的参数
            params = {
                "type": hot_search_type
            }

            #本地不存在，从网络获取
            # http请求
            logger.info(f"[sakuraTools] 从网络获取 {hot_search_type} 热搜")
            response_data = self.http_request_data(url, "raw", None, params, None)

            # 获取早报内容
            logger.debug(f"get {hot_search_type} image text")
            return self.download_image(None, hot_search_type, response_data)
        except Exception as err:
            logger.error(f"其他错误: {err}")
            return None

    def on_handle_context(self, e_context: EventContext):
        """处理上下文事件"""
        # 检查上下文类型是否为文本
        if e_context["context"].type not in [ContextType.TEXT]:
            logger.debug("[sakuraTools] 上下文类型不是文本，无需处理")
            return

        # 获取消息内容并去除首尾空格
        content = e_context["context"].content.strip()
        # 预定义塔罗牌选择类型
        tarot_num = 0
        # 检查缓存文件是否需要清除，默认每天00:00清除
        self.check_and_delete_files()

        if self.dog_check_keyword(content):
            logger.debug("[sakuraTools] 舔狗日记")
            reply = Reply()
            # 获取舔狗日记
            reply.type = ReplyType.TEXT
            reply.content = self.dog_request(self.DOG_URL)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.ai_draw_check_keyword(content):
            logger.debug("[sakuraTools] AI 画图")
            reply = Reply()
            # AI 画图
            ai_draw_image_io = self.ai_draw_request(self.AI_DRAW_URL, content)
            reply.type = ReplyType.IMAGE if ai_draw_image_io else ReplyType.TEXT
            reply.content = ai_draw_image_io if ai_draw_image_io else "画图失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.joke_check_keyword(content):
            logger.debug("[sakuraTools] 笑话")
            reply = Reply()
            # 获取笑话
            reply.type = ReplyType.TEXT
            reply.content = self.joke_request(self.JOKE_URL)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.moyu_check_keyword(content):
            logger.debug("[sakuraTools] 摸鱼日历")
            reply = Reply()
            # 获取摸鱼日历
            moyu_image_io = self.moyu_request(self.MOYU_URL)
            reply.type = ReplyType.IMAGE if moyu_image_io else ReplyType.TEXT
            reply.content = moyu_image_io if moyu_image_io else "获取摸鱼日历失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.acg_check_keyword(content):
            logger.debug("[sakuraTools] 二次元")
            reply = Reply()
            # 获取二次元小姐姐
            acg_image_url = self.acg_request(self.ACG_URL)
            reply.type = ReplyType.IMAGE_URL if acg_image_url else ReplyType.TEXT
            reply.content = acg_image_url if acg_image_url else "获取二次元小姐姐失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.pixiv_check_keyword(content):
            logger.debug("[sakuraTools] pixiv")
            reply = Reply()
            # 获取pixiv图片
            pixiv_image_io = self.pixiv_request(self.PIXIV_URL)
            reply.type = ReplyType.IMAGE if pixiv_image_io else ReplyType.TEXT
            reply.content = pixiv_image_io if pixiv_image_io else "获取pixiv图片失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.young_girl_check_keyword(content):
            logger.debug("[sakuraTools] 小姐姐")
            reply = Reply()
            # 获取小姐姐视频
            young_girl_video_url = self.young_girl_request(random.choice(self.YOUNG_GIRL_URL))
            reply.type = ReplyType.VIDEO_URL if young_girl_video_url else ReplyType.TEXT
            reply.content = young_girl_video_url if young_girl_video_url else "获取小姐姐视频失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.constellation_check_keyword(content):
            logger.debug(f"[sakuraTools] {content}")
            reply = Reply()
            reply.type = ReplyType.TEXT
            # 获取今日星座运势
            if content in self.ZODIAC_MAPPING:
                zodiac_english = self.ZODIAC_MAPPING[content]
                reply.content = self.constellation_request(zodiac_english, self.CONSTELLATION_URL, self.CONSTELLATION_URL_BACKUP)
            else:
                reply.content = "输入有问题哦，请重新输入星座名称~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.chongbuluo_check_keyword(content):
            logger.debug("[sakuraTools] 虫部落热门")
            reply = Reply()
            # 获取虫部落热门
            reply.type = ReplyType.TEXT
            reply.content = self.chongbuluo_request(self.CBL_URL)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.kfc_check_keyword(content):
            logger.debug("[sakuraTools] 疯狂星期四")
            reply = Reply()
            # 获取疯狂星期四文案
            reply.type = ReplyType.TEXT
            reply.content = self.kfc_request(self.KFC_URL)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.wyy_check_keyword(content):
            logger.debug("[sakuraTools] 网抑云")
            reply = Reply()
            # 获取网抑云评论
            reply.type = ReplyType.TEXT
            reply.content = self.wyy_request(self.WYY_URL)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.newspaper_check_keyword(content):
            logger.debug("[sakuraTools] 60s早报")
            reply = Reply()
            # 获取早报
            newspaper_image_io = self.newspaper_request(self.NEWSPAPER_URL)
            reply.type = ReplyType.IMAGE if newspaper_image_io else ReplyType.TEXT
            reply.content = newspaper_image_io if newspaper_image_io else "获取早报失败，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif (tarot_num := self.tarot_check_keyword(content)) > 0:
            logger.debug("[sakuraTools] 塔罗牌")
            reply = Reply()
            # 获取塔罗牌图片
            tarot_image_io = self.tarot_request(tarot_num)
            reply.type = ReplyType.IMAGE if tarot_image_io else ReplyType.TEXT
            reply.content = tarot_image_io if tarot_image_io else "获取塔罗牌失败，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.huang_li_check_keyword(content):
            logger.debug("[sakuraTools] 黄历")
            reply = Reply()
            # 获取黄历
            reply.type = ReplyType.TEXT
            reply.content = self.huang_li_request(self.HUANG_LI_URL)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.zwlq_chou_qian_check_keyword(content):
            logger.debug("[sakuraTools] 抽签")
            reply = Reply()
            # 获取真武灵签
            zwlq_image_io = self.zwlq_chou_qian_request()
            reply.type = ReplyType.IMAGE if zwlq_image_io else ReplyType.TEXT
            reply.content = zwlq_image_io if zwlq_image_io else "抽签失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.zwlq_jie_qian_check_keyword(content):
            logger.debug("[sakuraTools] 解签")
            reply = Reply()
            # 暂未实现解签功能
            reply.type = ReplyType.TEXT
            reply.content = "签文都给你啦😾！你自己看看嘛~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.dytj_gua_tu_check_keyword(content):
            logger.debug("[sakuraTools] 指定卦图")
            reply = Reply()
            # 获取指定卦图
            dytj_image_io = self.dytj_gua_tu_request(content)
            reply.type = ReplyType.IMAGE if dytj_image_io else ReplyType.TEXT
            reply.content = dytj_image_io if dytj_image_io else "获取卦图失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.dytj_daily_gua_tu_check_keyword(content):
            logger.debug("[sakuraTools] 随机卦图")
            reply = Reply()
            # 获取随机卦图
            dytj_image_io = self.dytj_daily_gua_tu_request()
            reply.type = ReplyType.IMAGE if dytj_image_io else ReplyType.TEXT
            reply.content = dytj_image_io if dytj_image_io else "获取卦图失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.hot_search_check_keyword(content):
            logger.debug("[sakuraTools] 热搜")
            reply = Reply()
            # 获取热搜
            hot_search_image_io = self.hot_search_request(content)
            reply.type = ReplyType.IMAGE if hot_search_image_io else ReplyType.TEXT
            reply.content = hot_search_image_io if hot_search_image_io else "获取热搜失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.ai_find_check_keyword(content):
            logger.debug("[sakuraTools] AI 搜索")
            reply = Reply()
            # AI 搜索
            reply.type = ReplyType.TEXT
            reply.content = self.ai_find_request(self.AI_FIND_URL, content)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.draw_card_check_keyword(content):
            logger.debug("[sakuraTools] 抽卡")
            reply = Reply()
            # 获取抽卡结果
            draw_card_image_io = self.draw_card_request(self.DRAW_CARD_URL)
            reply.type = ReplyType.IMAGE if draw_card_image_io else ReplyType.TEXT
            reply.content = draw_card_image_io if draw_card_image_io else "抽卡失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.fortune_check_keyword(content):
            logger.debug("[sakuraTools] 运势")
            reply = Reply()
            # 获取抽卡结果
            fortune_image_io = self.fortune_request(self.FORTUNE_URL)
            reply.type = ReplyType.IMAGE if fortune_image_io else ReplyType.TEXT
            reply.content = fortune_image_io if fortune_image_io else "获取运势失败啦，待会再来吧~🐾"
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS
        elif self.mei_hua_yi_shu_check_keyword(content):
            logger.debug("[sakuraTools] 梅花易数")
            # 获取session_id
            session_id = e_context["context"]["session_id"]
            reply = Reply()
            # 梅花易数
            reply.type = ReplyType.TEXT
            reply.content = self.mei_hua_yi_shu_request(session_id, content)
            e_context['reply'] = reply
            # 事件结束，并跳过处理context的默认逻辑
            e_context.action = EventAction.BREAK_PASS

    def get_help_text(self, **kwargs):
        """获取帮助文本"""
        help_text = "\n- [早报]：获取今日早报\n- [舔狗日记]：获取一则舔狗日记\n- [笑话]：获得一则笑话\n- [摸鱼日历]：获取摸鱼日历\n- [纸片人老婆]：获取一张纸片人老婆图片\n- [小姐姐]：获取一条小姐姐视频\n- [星座名]：获取今日运势\n- [虫部落]：获取虫部落今日热门\n- [kfc]：获取一条一条随机疯四文案\n- [网抑云]：获取一条网易云评论\n -[黄历]：获取今日黄历\n- [抽牌]：抽取单张塔罗牌\n- [三牌阵]：抽取塔罗牌三牌阵\n- [十字牌阵]：抽取塔罗牌十字牌阵\n- [每日一卦]：获取随机卦图\n- [卦图+卦名]：获取对应卦图\n- [微博热搜]：获取微博热搜\n- [百度热搜]：获取百度热搜\n- [AI搜索]：输入 `搜索 + 关键词`可以获取整合信息\n- [AI画图]：输入`画一个 + 关键字`可以生成ai图片\n- [梅花易数] 输入`算算` + `你想问的问题` + `三位数字`即可获得占卜结果\n- [抽卡]：获取带有解释的塔罗牌。\n- [运势]：获取你的运势。\n"
        return help_text
