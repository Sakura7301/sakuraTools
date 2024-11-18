import os  
import re
import io  
import time
import random 
import plugins  
import requests  
from plugins import *  
from PIL import Image, ImageDraw 
from config import conf  
from datetime import datetime  
from bridge.context import ContextType  
from bridge.reply import Reply, ReplyType  
from common.log import logger  
from selenium import webdriver  
from selenium.webdriver.common.by import By  
from selenium.webdriver.common.keys import Keys


@plugins.register(  
    name="sakuraTools",  # 插件名称  
    desire_priority=99,  # 插件优先级  
    hidden=False,  # 是否隐藏  
    desc="有趣的小功能合集",  # 插件描述  
    version="1.0",  # 插件版本  
    author="sakura7301",  # 作者  
)  
class sakuraTools(Plugin):  
    def __init__(self):  
        # 调用父类的初始化
        super().__init__()
        # 定义目标URL  
        self.DOG_URL = "https://api.vvhan.com/api/text/dog?type=json"
        self.JOKE_URL = "https://api.vvhan.com/api/text/joke?type=json"
        self.MOYU_URL = "https://api.vvhan.com/api/moyu?type=json"
        self.ACG_URL = "https://api.vvhan.com/api/wallpaper/acg?type=json"
        self.YOUNG_GIRL_URL = "https://api.apiopen.top/api/getMiniVideo?page=0&size=1"
        self.BEAUTIFUL_URL = "https://api.kuleu.com/api/MP4_xiaojiejie?type=json"
        self.CONSTELLATION_URL = "https://api.vvhan.com/api/horoscope"
        self.CBL_URL = "https://api.vvhan.com/api/hotlist/chongBluo"
        self.KFC_URL = "https://api.pearktrue.cn/api/kfc"
        self.WYY_URL = "https://zj.v.api.aa1.cn/api/wenan-wy/?type=json"
        self.NEWSPAPER_URL = "https://api.03c3.cn/api/zb?type=jsonImg"

        # 初始化配置
        self.config = super().load_config()
        # 加载配置模板
        if not self.config:
            self.config = self._load_config_template()
        
        # 加载图片临时目录
        self.image_tmp_path = self.config.get("image_tmp_path")
        # 加载塔罗牌目录
        self.tarot_cards_path = self.config.get("tarot_cards_path")
        # 加载舔狗日记关键字
        self.dog_keyword = self.config.get("dog_diary_keyword", [])
        # 加载笑话关键字
        self.joke_keyword = self.config.get("joke_keyword", [])
        # 加载摸鱼关键字
        self.moyu_keyword = self.config.get("moyu_keyword", [])
        # 加载二次元关键字
        self.acg_keyword = self.config.get("acg_keyword", [])
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
        # 加载塔罗牌单抽牌关键字
        self.tarot_single_keyword = self.config.get("tarot_single_keyword", [])
        # 加载塔罗牌三牌阵关键字
        self.tarot_three_keyword = self.config.get("tarot_three_keyword", [])
        # 加载塔罗牌十字牌阵关键字
        self.tarot_cross_keyword = self.config.get("tarot_cross_keyword", [])
        # 加载文件清除时间间隔
        self.delete_files_time_interval = self.config.get("delete_files_time_interval")
        # 存储最后一次删除文件的时间戳  
        self.last_delete_files_time = None 

        # 注册处理上下文的事件  
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context  
        logger.info("[sakuraTools] 插件初始化完毕")  

    def get_local_file(self, path):
        """
            从插件目录中加载文件
        """
        # 检查文件是否存在  
        if os.path.exists(file_path):  
            # 如果文件存在，读取并返回 io 对象  
            image = Image.open(file_path)  
            img_io = io.BytesIO()  
            image.save(img_io, format='PNG')  
            # 将指针移动到开头 
            img_io.seek(0)   
            return img_io  
        else:  
            # 文件不存在，返回 None  
            return None  

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
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def check_and_delete_files(self):  
        """
            检查并删除文件的主函数  
        """
        # 获取当前秒级时间戳
        timestamp = time.time()
        # 第一次调用时，设置删除时间  
        if self.last_delete_files_time is None:  
            # 初始化时间戳
            self.last_delete_files_time = timestamp  
            # 清空目录下的所有文件
            self.delete_all_files_in_directory(self.image_tmp_path)  
            logger.info(f"已清空{self.image_tmp_path}目录下的所有文件")
            return  

        # 检查时间差  
        if (timestamp - self.last_delete_files_time) >= self.delete_files_time_interval:  
            # 清空目录下的所有文件
            self.delete_all_files_in_directory()  
            logger.info(f"已清空{self.image_tmp_path}目录下的所有文件")
            # 更新最后删除时间  
            self.last_delete_files_time = timestamp  

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
    def ensure_directory_exists(self, directory):  
        """
            检查指定目录是否存在，如果不存在则创建该目录
        """  
        try:  
            if not os.path.exists(directory):  
                os.makedirs(directory, exist_ok=True)  # 创建目录  
                logger.info(f"目录已创建: {directory}")  
            else:  
                logger.debug(f"目录已存在: {directory}")  
        except Exception as e:  
            logger.error(f"发生错误: {e}") 

    # 下载图片
    def download_image(self, image_url: str, name: str) -> io.BytesIO:  
        """
            下载图片的通用函数
        """
        try:
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
            # 下载图片  
            response = requests.get(image_url)  
            response.raise_for_status()  # 检查请求是否成功  

            # 保存图片  
            with open(file_path, 'wb') as f:  
                # 写入文件
                f.write(response.content)
            logger.info(f"成功下载图片: {file_path}")
            # 关闭文件
            f.close() 

            # 创建 io.BytesIO 对象并返回  
            img_io = io.BytesIO(response.content)  
            img_io.seek(0)  # 将指针移动到开头  
            
            return img_io
        except requests.exceptions.HTTPError as http_err:
            err_str = f"HTTP错误: {http_err}"
            logger.error(err_str)
            return err_str
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str 
    
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
    def http_request_data(self, url, params_json=None, verify_flag=None):
        """
            通用的HTTP请求函数
        """
        try:  
            # 发起GET请求  
            if verify_flag:
                response = requests.get(url, params=params_json, verify=False)
            else:
                response = requests.get(url, params=params_json)

            # 打印请求信息  
            logger.debug("发送的HTTP请求:")  
            logger.debug("请求方法: GET")  
            logger.debug(f"请求URL: {url}")  
            logger.debug(f"请求头: {response.request.headers}")
            logger.debug(f"请求体: {response.request.body}") 

            # 检查响应状态码  
            # 如果响应状态码不是200，将会抛出HTTPError异常
            response.raise_for_status()  

            # 打印响应信息  
            logger.debug("收到的HTTP响应:")  
            logger.debug(f"响应状态码: {response.status_code}")  
            logger.debug(f"响应头: {response.headers}") 

            # 解析响应体  
            response_data = response.json()  
            # 打印响应体  
            logger.debug(f"响应体: {response_data}")

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
            response_data = self.http_request_data(url)

            # 返回笑话 
            if response_data["success"]:  
                # 获取笑话内容
                joke_str = f"""[{response_data['data']['title']}]\n{response_data['data']['content']}\n(希望这则笑话能带给你快乐~🐾)"""
                logger.debug(f"get joke text:{joke_str}")
                return joke_str
            else:  
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
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
            摸鱼日记请求函数
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
                logger.info("[sakuraTools] 本地不存在摸鱼日历，从网络获取")
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
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

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
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str 

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
            response_data = self.http_request_data(url)

            # 返回响应的数据内容  
            young_girl_video_url = self.get_first_video_url(response_data)
            logger.debug(f"get young_girl video url:{young_girl_video_url}")
            return young_girl_video_url
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def beautiful_check_keyword(self, content):
        """
            检查美女视频关键字
        """
        # 检查关键词   
        return any(keyword in content for keyword in self.beautiful_keyword) 

    def beautiful_request(self, url):
        """
            美女视频请求函数 
        """
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回响应的数据内容  
            beautiful_video_url = response_data['mp4_video']
            logger.debug(f"get beautiful video url:{beautiful_video_url}")
            return beautiful_video_url
        except Exception as err:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str 

    def constellation_check_keyword(self, content):
        """
            检查星座关键字
        """
        horoscope_match = re.match(r'^([\u4e00-\u9fa5]{2}座)$', content)
        return horoscope_match

    def constellation_request(self, zodiac_english, url):
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
            response_data = self.http_request_data(url, params, None)

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
                logger.debug(f"get XingZuo text:{constellation_text}")
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
            response_data = self.http_request_data(url, None,True)

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
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str 
    
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

        if self.dog_check_keyword(content):  
            logger.debug("[sakuraTools] 舔狗日记")  
            reply = Reply()  
            # 获取舔狗日记
            dog_text = self.dog_request(self.DOG_URL)  
            reply.type = ReplyType.TEXT  
            reply.content = dog_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.joke_check_keyword(content):
            logger.debug("[sakuraTools] 笑话")  
            reply = Reply()  
            # 获取笑话
            dog_text = self.joke_request(self.JOKE_URL) 
            reply.type = ReplyType.TEXT  
            reply.content = dog_text 
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
            ACG_URL = self.acg_request(self.ACG_URL) 
            reply.type = ReplyType.IMAGE_URL if ACG_URL else ReplyType.TEXT  
            reply.content = ACG_URL if ACG_URL else "获取二次元小姐姐失败啦，待会再来吧~🐾"  
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 

        elif self.young_girl_check_keyword(content):
            logger.debug("[sakuraTools] 小姐姐")  
            reply = Reply()  
            # 获取小姐姐视频
            young_girl_video_url = self.young_girl_request(self.YOUNG_GIRL_URL) 
            reply.type = ReplyType.VIDEO_URL if young_girl_video_url else ReplyType.TEXT  
            reply.content = young_girl_video_url if young_girl_video_url else "获取小姐姐视频失败啦，待会再来吧~🐾"  
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 
        elif self.beautiful_check_keyword(content):
            logger.debug("[sakuraTools] 美女")  
            reply = Reply()  
            # 获取美女视频
            beautiful_video_url = self.beautiful_request(self.BEAUTIFUL_URL) 
            reply.type = ReplyType.VIDEO_URL if beautiful_video_url else ReplyType.TEXT  
            reply.content = beautiful_video_url if beautiful_video_url else "获取美女视频失败啦，待会再来吧~🐾"  
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.constellation_check_keyword(content):
            logger.debug(f"[sakuraTools] {content}")  
            reply = Reply()  
            reply.type = ReplyType.TEXT 
            # 获取今日星座运势 
            if content in ZODIAC_MAPPING:
                zodiac_english = ZODIAC_MAPPING[content]
                reply.content = self.constellation_request(zodiac_english, self.CONSTELLATION_URL)
            else:
                reply.content = "输入有问题哦，请重新输入星座名称~🐾"
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 
        elif self.chongbuluo_check_keyword(content):
            logger.debug("[sakuraTools] 虫部落热门")  
            reply = Reply()  
            # 获取虫部落热门
            chongbuluo_text = self.chongbuluo_request(self.CBL_URL) 
            reply.type = ReplyType.TEXT  
            reply.content = chongbuluo_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.kfc_check_keyword(content):
            logger.debug("[sakuraTools] 疯狂星期四")  
            reply = Reply()  
            # 获取疯狂星期四文案
            kfc_text = self.kfc_request(self.KFC_URL) 
            reply.type = ReplyType.TEXT  
            reply.content = kfc_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 
        elif self.wyy_check_keyword(content):
            logger.debug("[sakuraTools] 网抑云")  
            reply = Reply()  
            # 获取网抑云评论
            wyy_text = self.wyy_request(self.WYY_URL) 
            reply.type = ReplyType.TEXT  
            reply.content = wyy_text 
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
        else:
            # 检查文件缓存是否需要清除，默认一天清除一次
            self.check_and_delete_files()

    def get_help_text(self, **kwargs):  
        """获取帮助文本"""  
        help_text = "[sakuraTools v1.0]\n- [早报]：获取今日早报\n- [舔狗日记]：获取一则舔狗日记\n- [笑话]：获得一则笑话\n- [摸鱼日历]：获取摸鱼日历\n- [纸片人老婆]：获取一张纸片人老婆图片\n- [小姐姐]：获取一条小姐姐视频\n- [美女]：获取一条美女视频\n- [星座名]：获取今日运势\n- [虫部落]：获取虫部落今日热门\n- [kfc]：获取一条一条随机疯四文案\n- [网抑云]：获取一条网易云评论\n[抽牌]：抽取单张塔罗牌\n[三牌阵]：抽取塔罗牌三牌阵\n[十字牌阵]：抽取塔罗牌十字牌阵"  
        return help_text



ZODIAC_MAPPING = {
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
