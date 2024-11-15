import os  
import re
import io  
import plugins  
import requests  
from config import conf  
from datetime import datetime  
from bridge.context import ContextType  
from bridge.reply import Reply, ReplyType  
from common.log import logger  
from plugins import *  


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
        self.dog_url = "https://api.vvhan.com/api/text/dog?type=json"
        self.joke_url = "https://api.vvhan.com/api/text/joke?type=json"
        self.moyu_url = "https://api.vvhan.com/api/moyu?type=json"
        self.acg_url = "https://api.vvhan.com/api/wallpaper/acg?type=json"
        self.young_girl_url = "https://api.apiopen.top/api/getMiniVideo?page=0&size=1"
        self.beautiful_url = "https://api.kuleu.com/api/MP4_xiaojiejie?type=json"
        self.xingzuo_url = "https://api.vvhan.com/api/horoscope"
        self.chongbuluo_url = "https://api.vvhan.com/api/hotlist/chongBluo"
        self.kfc_url = "https://api.pearktrue.cn/api/kfc"
        self.wyy_url = "https://zj.v.api.aa1.cn/api/wenan-wy/?type=json"

        # 初始化配置
        self.config = super().load_config()
        # 加载配置模板
        if not self.config:
            self.config = self._load_config_template()
        
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

        # 注册处理上下文的事件  
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context  
        logger.info("[sakuraTools] 插件初始化完毕")  

    # http通用请求接口
    def http_request_data(self, url, params_json=None, verify_flag=None):
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
        # 确保 response 有效并包含结果  
        if response and 'result' in response and 'list' in response['result'] and len(response['result']['list']) > 0:  
            # 返回第一个视频的 URL  
            return response['result']['list'][0]['playurl']  
        else:  
            # 如果没有找到视频，返回 None  
            return None  

    def chongbuluo_five_posts(self, response):  
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
        # 检查关键词    
        return any(keyword in content for keyword in self.dog_keyword)  
    
    def dog_request(self, url):  
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回舔狗日记  
            if response_data["success"]:  
                # 获取舔狗日记内容
                dog_str = response_data['data']['content']
                logger.info(f"get dog diary:{dog_str}")
                return dog_str
            else:  
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def joke_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.joke_keyword)  
    
    def joke_request(self, url):  
        try:
            # http请求
            response_data = self.http_request_data(url)

            # 返回笑话 
            if response_data["success"]:  
                # 获取笑话内容
                joke_str = f"""[{response_data['data']['title']}]\n{response_data['data']['content']}\n(希望这则笑话能带给你快乐~🐾)"""
                logger.info(f"get joke text:{joke_str}")
                return joke_str
            else:  
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def moyu_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.moyu_keyword) 

    def moyu_request(self, url):
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回响应的数据内容  
            if response_data["success"]:  
                # 获取摸鱼内容
                moyu_image_url = response_data['url']
                logger.info(f"get moyu image url:{moyu_image_url}")
                return moyu_image_url
            else:  
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def acg_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.acg_keyword) 

    def acg_request(self, url):
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回响应的数据内容  
            if response_data["success"]:  
                # 获取acg内容
                acg_image_url = response_data['url']
                logger.info(f"get acg image url:{acg_image_url}")
                return acg_image_url
            else:  
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str 

    def young_girl_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.young_girl_keyword) 

    def young_girl_request(self, url):
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回响应的数据内容  
            young_girl_video_url = self.get_first_video_url(response_data)
            logger.info(f"get young_girl video url:{young_girl_video_url}")
            return young_girl_video_url
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def beautiful_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.beautiful_keyword) 

    def beautiful_request(self, url):
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回响应的数据内容  
            beautiful_video_url = response_data['mp4_video']
            logger.info(f"get beautiful video url:{beautiful_video_url}")
            return beautiful_video_url
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str 

    def xingzuo_check_keyword(self, content):
        horoscope_match = re.match(r'^([\u4e00-\u9fa5]{2}座)$', content)
        return horoscope_match

    def xingzuo_request(self, zodiac_english, url):
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
                xingzuo_text = (
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
                logger.info(f"get XingZuo text:{xingzuo_text}")
                return xingzuo_text
            else:  
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
        except Exception as err:  
            err_str = f"其他错误: {err}"
            logger.error(err_str)  
            return err_str  
    def chongbuluo_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.chongbuluo_keyword) 

    def chongbuluo_request(self, url):
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回虫部落热门  
            if response_data["success"]:  
                # 获取虫部落热门
                chongbuluo_text = self.chongbuluo_five_posts(response_data)
                logger.info(f"get chongbuluo text:{chongbuluo_text}")
                return chongbuluo_text
            else:  
                err_str = f"错误信息: {response_data['message']}"
                logger.error(err_str)  
                return err_str  
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str

    def kfc_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.kfc_keyword)  
    
    def kfc_request(self, url):  
        try:  
            # http请求
            response_data = self.http_request_data(url)

            # 返回疯狂星期四文案 
            if "text" in response_data:
                # 获取疯狂星期四文案
                kfc_text = response_data['text']
            logger.info(f"get kfc text:{kfc_text}")
            return kfc_text
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str 

    def wyy_check_keyword(self, content):
        # 检查关键词   
        return any(keyword in content for keyword in self.wyy_keyword)  
    
    def wyy_request(self, url):  
        try:  
            # http请求
            response_data = self.http_request_data(url, None,True)

            # 返回网易云热评
            if "msg" in response_data:
                # 获取网易云热评
                wyy_text = response_data['msg']
            logger.info(f"get wyy text:{wyy_text}")
            return wyy_text
        except Exception as e:
            err_str = f"其他错误: {err}"
            logger.error(err_str)
            return err_str
    
    def on_handle_context(self, e_context: EventContext):  
        """处理上下文事件"""  
        if e_context["context"].type not in [ContextType.TEXT]:  
            logger.debug("[sakuraTools] 上下文类型不是文本，无需处理")  
            return  
        
        content = e_context["context"].content.strip()  

        if self.dog_check_keyword(content):  
            logger.info("[sakuraTools] 舔狗日记")  
            reply = Reply()  
            # 获取舔狗日记
            dog_text = self.dog_request(self.dog_url)  
            reply.type = ReplyType.TEXT  
            reply.content = dog_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.joke_check_keyword(content):
            logger.info("[sakuraTools] 笑话")  
            reply = Reply()  
            # 获取笑话
            dog_text = self.joke_request(self.joke_url) 
            reply.type = ReplyType.TEXT  
            reply.content = dog_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.moyu_check_keyword(content):
            logger.info("[sakuraTools] 摸鱼日历")  
            reply = Reply()  
            # 获取摸鱼日历
            moyu_url = self.moyu_request(self.moyu_url) 
            reply.type = ReplyType.IMAGE_URL if moyu_url else ReplyType.TEXT  
            reply.content = moyu_url if moyu_url else "获取摸鱼日历失败啦，待会再来吧~🐾"  
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.acg_check_keyword(content):
            logger.info("[sakuraTools] 二次元")  
            reply = Reply()  
            # 获取摸鱼日历
            moyu_url = self.acg_request(self.acg_url) 
            reply.type = ReplyType.IMAGE_URL if moyu_url else ReplyType.TEXT  
            reply.content = moyu_url if moyu_url else "获取二次元小姐姐失败啦，待会再来吧~🐾"  
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 

        elif self.young_girl_check_keyword(content):
            logger.info("[sakuraTools] 小姐姐")  
            reply = Reply()  
            # 获取小姐姐视频
            young_girl_video_url = self.young_girl_request(self.young_girl_url) 
            reply.type = ReplyType.VIDEO_URL if young_girl_video_url else ReplyType.TEXT  
            reply.content = young_girl_video_url if young_girl_video_url else "获取小姐姐视频失败啦，待会再来吧~🐾"  
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 
        elif self.beautiful_check_keyword(content):
            logger.info("[sakuraTools] 小姐姐")  
            reply = Reply()  
            # 获取美女视频
            beautiful_video_url = self.beautiful_request(self.beautiful_url) 
            reply.type = ReplyType.VIDEO_URL if beautiful_video_url else ReplyType.TEXT  
            reply.content = beautiful_video_url if beautiful_video_url else "获取美女视频失败啦，待会再来吧~🐾"  
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.xingzuo_check_keyword(content):
            logger.info(f"[sakuraTools] {content}")  
            reply = Reply()  
            reply.type = ReplyType.TEXT 
            # 获取今日星座运势 
            if content in ZODIAC_MAPPING:
                zodiac_english = ZODIAC_MAPPING[content]
                reply.content = self.xingzuo_request(zodiac_english, self.xingzuo_url)
            else:
                reply.content = "输入有问题哦，请重新输入星座名称~🐾"
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 
        elif self.chongbuluo_check_keyword(content):
            logger.info("[sakuraTools] 虫部落热门")  
            reply = Reply()  
            # 获取虫部落热门
            chongbuluo_text = self.chongbuluo_request(self.chongbuluo_url) 
            reply.type = ReplyType.TEXT  
            reply.content = chongbuluo_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS  
        elif self.kfc_check_keyword(content):
            logger.info("[sakuraTools] 疯狂星期四")  
            reply = Reply()  
            # 获取疯狂星期四文案
            kfc_text = self.kfc_request(self.kfc_url) 
            reply.type = ReplyType.TEXT  
            reply.content = kfc_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 
        elif self.wyy_check_keyword(content):
            logger.info("[sakuraTools] 网抑云")  
            reply = Reply()  
            # 获取网抑云评论
            wyy_text = self.wyy_request(self.wyy_url) 
            reply.type = ReplyType.TEXT  
            reply.content = wyy_text 
            e_context['reply'] = reply  
            # 事件结束，并跳过处理context的默认逻辑   
            e_context.action = EventAction.BREAK_PASS 

    def get_help_text(self, **kwargs):  
        """获取帮助文本"""  
        help_text = "[sakuraTools v1.0]\n输入'舔狗日记'将会得到一则舔狗日记~🐾\n输入'笑话'将会得到一则笑话~🐾\n输入'摸鱼日历'将会获得一份摸鱼日历~🐾\n输入'纸片人老婆'将会获得一张纸片人老婆美照~🐾\n输入'小姐姐'会收到一条小姐姐视频~🐾\n输入'美女'会收到一条美女视频~🐾\n输入'对应星座'会收到今日运势~🐾\n输入'虫部落'将会收到虫部落今日热门~🐾\n输入'kfc'将会收到一条随机疯四文案~🐾\n输入'网抑云'将会获得一条网易云评论~🐾"  
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
