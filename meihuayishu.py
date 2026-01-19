import os
import io
import pytz
import re
import time
from datetime import datetime, timedelta
from lunar_python import Solar, Lunar
from zhdate import ZhDate
from common.log import logger

# 定义八卦对应的五行
BA_GUA_WUXING = {
    1: '金',  # 乾
    2: '金',  # 兑
    3: '火',  # 离
    4: '木',  # 震
    5: '木',  # 巽
    6: '水',  # 坎
    7: '土',  # 艮
    8: '土'   # 坤
}

# 定义五行的生克关系
WU_XING_XIANG_SHENG = {
    '金': '水',
    '水': '木',
    '木': '火',
    '火': '土',
    '土': '金'
}
WU_XING_XIANG_KE = {
    '金': '木',
    '木': '土',
    '土': '水',
    '水': '火',
    '火': '金'
}

# 定义每个月令对应的五行旺相休囚死状态
YUE_LING_WANG_SHUAI = {
    # 当令者旺，令生者相，生令者休，克令者囚，令克者死。
    # 1月2月属木
    1: {'木': '旺', '火': '相', '水': '休', '金': '囚', '土': '死'},
    2: {'木': '旺', '火': '相', '水': '休', '金': '囚', '土': '死'},
    # 3月属土
    3: {'土': '旺', '金': '相', '火': '休', '木': '囚', '水': '死'},
    # 4月5月属火
    4: {'火': '旺', '土': '相', '木': '休', '水': '囚', '金': '死'},
    5: {'火': '旺', '土': '相', '木': '休', '水': '囚', '金': '死'},
    # 6月属土
    6: {'土': '旺', '金': '相', '火': '休', '木': '囚', '水': '死'},
    # 7月8月属金
    7: {'金': '旺', '水': '相', '土': '休', '火': '囚', '木': '死'},
    8: {'金': '旺', '水': '相', '土': '休', '火': '囚', '木': '死'},
    # 9月属土
    9: {'土': '旺', '金': '相', '火': '休', '木': '囚', '水': '死'},
    # 10月11月属水
    10: {'水': '旺', '木': '相', '金': '休', '土': '囚', '火': '死'},
    11: {'水': '旺', '木': '相', '金': '休', '土': '囚', '火': '死'},
    # 12月属土
    12: {'土': '旺', '金': '相', '火': '休', '木': '囚', '水': '死'}
}

# 旺相休囚死对应的气数变化比例
WANG_SHUAI_HUA_QI = {
    '旺': 0.6,
    '相': 0.3,
    '休': 0.0,
    '囚': -0.3,
    '死': -0.6
}

# 八卦映射
MAP_FOR_8_GUA = {
    1: {'name': '乾', 'lines': ['yang', 'yang', 'yang']},
    2: {'name': '兑', 'lines': ['yang', 'yang', 'yin']},
    3: {'name': '离', 'lines': ['yang', 'yin', 'yang']},
    4: {'name': '震', 'lines': ['yang', 'yin', 'yin']},
    5: {'name': '巽', 'lines': ['yin', 'yang', 'yang']},
    6: {'name': '坎', 'lines': ['yin', 'yang', 'yin']},
    7: {'name': '艮', 'lines': ['yin', 'yin', 'yang']},
    8: {'name': '坤', 'lines': ['yin', 'yin', 'yin']}
}

GUA_SHENYUN_MAP = {
    # 乾宫八卦 (乾为天为本宫)
    (1, 1): ["䷀ 乾为天", "纯粹创造。神在自强不息，是纯粹的行动与意志，如龙行九天。"],
    (1, 2): ["䷉ 天泽履", "践行天道。神在慎行知礼，以柔履刚，如履薄冰而终吉。"],
    (1, 3): ["䷌ 天火同人", "同心同德。神在天下为公，求同存异，光明普照而志通。"],
    (1, 4): ["䷘ 天雷无妄", "真实不虚。神在顺天而动，不妄为，守正道而元亨利贞。"],
    (1, 5): ["䷫ 天风姤", "遇合之道。神在机遇暗藏，阴遇阳柔，防微杜渐知进退。"],
    (1, 6): ["䷅ 天水讼", "争讼纠纷。神在惕惧中正，天与水违行，谋始戒争可免凶。"],
    (1, 7): ["䷠ 天山遁", "退避守时。神在顺势退藏，君子远小人，与时行不恶而严。"],
    (1, 8): ["䷋ 天地否", "闭塞不通。神在内守修德，天地不交，俭德避难不可荣禄。"],
    
    # 兑宫八卦 (兑为泽为本宫)
    (2, 1): ["䷪ 泽天夬", "决断刚健。神在果断裁决，五阳决一阴，健而悦决而和。"],
    (2, 2): ["䷹ 兑为泽", "欣悦沟通。神在和悦致祥，朋友讲习，顺天应人而民忘劳。"],
    (2, 3): ["䷰ 泽火革", "变革革新。神在顺天应人，革故鼎新，文明以说大亨以正。"],
    (2, 4): ["䷐ 泽雷随", "随从之道。神在随时而动，刚来下柔，动而悦天下随时。"],
    (2, 5): ["䷛ 泽风大过", "过度非常。神在独立不惧，泽灭木，君子以独立不惧。"],
    (2, 6): ["䷮ 泽水困", "困境求通。神在致命遂志，泽无水，君子以致命遂志。"],
    (2, 7): ["䷞ 泽山咸", "感应相通。神在虚怀若谷，山泽通气，以虚受人感人心。"],
    (2, 8): ["䷬ 泽地萃", "汇聚英才。神在聚而正吉，泽上于地，聚以正观其所聚。"],
    
    # 离宫八卦 (离为火为本宫)
    (3, 1): ["䷍ 火天大有", "丰盛保有。神在遏恶扬善，火在天上，顺天休命明辨皙。"],
    (3, 2): ["䷥ 火泽睽", "乖离和合。神在同而异用，上火下泽，小事吉而终合。"],
    (3, 3): ["䷝ 离为火", "光明依附。神在继明照四方，重明以丽，畜牝牛吉柔中正。"],
    (3, 4): ["䷔ 火雷噬嗑", "咬合贯通。神在用狱明罚，雷电合章，明罚敕法亨利用狱。"],
    (3, 5): ["䷱ 火风鼎", "鼎新固基。神在正位凝命，木上有火，君子以正位凝命。"],
    (3, 6): ["䷿ 火水未济", "未成待时。神在慎辨物居，火水未交，君子以慎辨物居方。"],
    (3, 7): ["䷷ 火山旅", "羁旅之道。神在明慎用刑，山上有火，君子以明慎用刑不留狱。"],
    (3, 8): ["䷢ 火地晋", "晋升成长。神在昭明德善，明出地上，君子以自昭明德。"],
    
    # 震宫八卦 (震为雷为本宫)
    (4, 1): ["䷡ 雷天大壮", "壮大守正。神在非礼弗履，雷在天上，君子以非礼弗履。"],
    (4, 2): ["䷵ 雷泽归妹", "婚嫁之道。神在永终知敝，泽上有雷，君子以永终知敝。"],
    (4, 3): ["䷶ 雷火丰", "丰大光明。神在折狱致刑，雷电皆至，君子以折狱致刑。"],
    (4, 4): ["䷲ 震为雷", "震动奋起。神在恐惧修省，洊雷震，君子以恐惧修省。"],
    (4, 5): ["䷟ 雷风恒", "恒久之道。神在立不易方，雷风相与，君子以立不易方。"],
    (4, 6): ["䷧ 雷水解", "解难释困。神在赦过宥罪，雷雨作，君子以赦过宥罪。"],
    (4, 7): ["䷽ 雷山小过", "小有过越。神在行过恭丧哀，山上有雷，君子以行过乎恭。"],
    (4, 8): ["䷏ 雷地豫", "愉乐顺动。神在作乐崇德，雷出地奋，先王以作乐崇德。"],
    
    # 巽宫八卦 (巽为风为本宫)
    (5, 1): ["䷈ 风天小畜", "小有蓄积。神在懿文德，风行天上，君子以懿文德。"],
    (5, 2): ["䷼ 风泽中孚", "诚信感物。神在议狱缓死，泽上有风，君子以议狱缓死。"],
    (5, 3): ["䷤ 风火家人", "家庭伦理。神在言有物行有恒，风自火出，君子以言有物行有恒。"],
    (5, 4): ["䷩ 风雷益", "增益利他。神在见善则迁，风雷益，君子以见善则迁有过则改。"],
    (5, 5): ["䷸ 巽为风", "随顺入微。神在申命行事，随风巽，君子以申命行事。"],
    (5, 6): ["䷺ 风水涣", "涣散凝聚。神在享帝立庙，风行水上，先王以享于帝立庙。"],
    (5, 7): ["䷴ 风山渐", "渐进有序。神在居贤德善俗，山上有木，君子以居贤德善俗。"],
    (5, 8): ["䷓ 风地观", "观省洞察。神在省方观民，风行地上，先王以省方观民设教。"],
    
    # 坎宫八卦 (坎为水为本宫)
    (6, 1): ["䷄ 水天需", "等待时机。神在饮食宴乐，云上于天，君子以饮食宴乐。"],
    (6, 2): ["䷻ 水泽节", "节制有度。神在制数度议德行，泽上有水，君子以制数度议德行。"],
    (6, 3): ["䷾ 水火既济", "事成守成。神在思患预防，水在火上，君子以思患而预防之。"],
    (6, 4): ["䷂ 水雷屯", "初生艰难。神在经纶云雷，君子以经纶。"],
    (6, 5): ["䷯ 水风井", "井养不穷。神在劳民劝相，木上有水，君子以劳民劝相。"],
    (6, 6): ["䷜ 坎为水", "险陷重重。神在常德行习教事，水洊至，君子以常德行习教事。"],
    (6, 7): ["䷦ 水山蹇", "险阻在前。神在反身修德，山上有水，君子以反身修德。"],
    (6, 8): ["䷇ 水地比", "亲附和谐。神在建万国亲诸侯，地上有水，先王以建万国亲诸侯。"],
    
    # 艮宫八卦 (艮为山为本宫)
    (7, 1): ["䷙ 山天大畜", "大畜德智。神在多识前言往行，天在山中，君子以多识前言往行。"],
    (7, 2): ["䷨ 山泽损", "损下益上。神在惩忿窒欲，山下有泽，君子以惩忿窒欲。"],
    (7, 3): ["䷕ 山火贲", "文饰质朴。神在明庶政无敢折狱，山下有火，君子以明庶政无敢折狱。"],
    (7, 4): ["䷚ 山雷颐", "养正之道。神在慎言语节饮食，山下有雷，君子以慎言语节饮食。"],
    (7, 5): ["䷑ 山风蛊", "整治腐败。神在振民育德，山下有风，君子以振民育德。"],
    (7, 6): ["䷃ 山水蒙", "启蒙教育。神在果行育德，山下出泉，君子以果行育德。"],
    (7, 7): ["䷳ 艮为山", "止其所当。神在思不出其位，兼山艮，君子以思不出其位。"],
    (7, 8): ["䷖ 山地剥", "剥落凋零。神在上厚下安宅，山附于地，上以厚下安宅。"],
    
    # 坤宫八卦 (坤为地为本宫)
    (8, 1): ["䷊ 地天泰", "通泰祥和。神在辅相天地，天地交，后以财成天地之道。"],
    (8, 2): ["䷒ 地泽临", "监临督导。神在教思无穷，泽上有地，君子以教思无穷容保民。"],
    (8, 3): ["䷣ 地火明夷", "明德受伤。神在莅众用晦，明入地中，君子以莅众用晦而明。"],
    (8, 4): ["䷗ 地雷复", "回复生机。神在静以修身，雷在地中，先王以至日闭关。"],
    (8, 5): ["䷭ 地风升", "柔顺上升。神在积小高大，地中生木，君子以顺德积小以高大。"],
    (8, 6): ["䷆ 地水师", "行军打仗。神在容民畜众，地中有水，君子以容民畜众。"],
    (8, 7): ["䷎ 地山谦", "谦虚美德。神在裒多益寡，地中有山，君子以裒多益寡称物平施。"],
    (8, 8): ["䷁ 坤为地", "柔顺承载。神在厚德载物，地势坤，君子以厚德载物。"]
}

# 定义时辰对应的值和名称
SHI_CHEN = {
    1: '子时',
    2: '丑时',
    3: '寅时',
    4: '卯时',
    5: '辰时',
    6: '巳时',
    7: '午时',
    8: '未时',
    9: '申时',
    10: '酉时',
    11: '戌时',
    12: '亥时'
}

def get_gua_info(shang_gua, xia_gua):
    """根据上下卦数字获取卦的完整信息"""
    return GUA_SHENYUN_MAP.get((shang_gua, xia_gua), ["未知卦", "未找到相关信息"])


def WuXingCalculator(shanggua_num, xiagua_num, ti_flag, month):
    """
    五行计算函数。

    参数：
    - shanggua_num: 上卦数（1-8）
    - xiagua_num: 下卦数（1-8）
    - ti_flag: 体卦标志（0或1），0表示下卦为体卦，1表示上卦为体卦
    - month: 月令（1-12）

    返回：
    - dict，包含旺相休囚死、生克关系、吉凶判断
    """
    try:
        # 验证输入参数
        if shanggua_num not in range(1, 9) or xiagua_num not in range(1, 9):
            logger.error("[sakuraTools] 错误：上卦数和下卦数必须在1到8之间。")
            return None
        if ti_flag not in [0, 1]:
            logger.error("[sakuraTools] 错误：体卦标志必须为0或1。")
            return None
        if month not in range(1, 13):
            logger.error("[sakuraTools] 错误：月令必须在1到12之间。")
            return None

        # 五行的旺相休囚死
        wuxing_sequence = ['木', '火', '土', '金', '水']

        # 确定旺相休囚死
        wangxiangxiuqiusi_dict = YUE_LING_WANG_SHUAI[month]

        # 获取体卦和用卦的五行
        ti_gua_num = shanggua_num if ti_flag == 1 else xiagua_num
        yong_gua_num = xiagua_num if ti_flag == 1 else shanggua_num

        ti_wuxing = BA_GUA_WUXING[ti_gua_num]
        yong_wuxing = BA_GUA_WUXING[yong_gua_num]

        logger.debug(f"[sakuraTools] 体卦五行：{ti_wuxing}")
        logger.debug(f"[sakuraTools] 用卦五行：{yong_wuxing}")

        # 初始化气数
        ti_qi = 10
        yong_qi = 10

        # 第一轮：按照旺相休囚死调整气数
        ti_state = wangxiangxiuqiusi_dict[ti_wuxing]
        yong_state = wangxiangxiuqiusi_dict[yong_wuxing]

        ti_qi += ti_qi * WANG_SHUAI_HUA_QI[ti_state]
        yong_qi += yong_qi * WANG_SHUAI_HUA_QI[yong_state]

        logger.debug(f"[sakuraTools] 第一轮修正：")
        logger.debug(f"[sakuraTools] 体卦气数: {ti_qi}")
        logger.debug(f"[sakuraTools] 用卦气数: {yong_qi}")

        # 第二轮：按照生克关系调整气数
        if ti_wuxing == yong_wuxing:
            relation = '体用比和'
            # 比和情况下，气数不变
        elif yong_wuxing == WU_XING_XIANG_SHENG[ti_wuxing]:
            # 体生用：检查用卦的五行是否是体卦五行所生
            relation = '体生用'
            transfer_qi = ti_qi * 0.25
            ti_qi -= transfer_qi
            yong_qi += transfer_qi
        elif ti_wuxing == WU_XING_XIANG_SHENG[yong_wuxing]:
            # 用生体：检查体卦的五行是否是用卦五行所生
            relation = '用生体'
            transfer_qi = yong_qi * 0.25
            yong_qi -= transfer_qi
            ti_qi += transfer_qi
        elif yong_wuxing == WU_XING_XIANG_KE[ti_wuxing]:
            # 体克用：检查用卦的五行是否是体卦五行所克
            relation = '体克用'
            yong_qi *= 0.5
        elif ti_wuxing == WU_XING_XIANG_KE[yong_wuxing]:
            # 用克体：检查体卦的五行是否是用卦五行所克
            relation = '用克体'
            ti_qi *= 0.5
        else:
            relation = '无生克关系'
            # 无生克关系，气数不变

        logger.debug(f"[sakuraTools] 第二轮修正：")
        logger.debug(f"[sakuraTools] 体卦气数: {ti_qi}")
        logger.debug(f"[sakuraTools] 用卦气数: {yong_qi}")

        # 判断吉凶
        if ti_wuxing == yong_wuxing:
            # 比和情况下，仅考虑体卦气数与初始值比较
            if ti_qi > 10:
                result = '小吉'
            else:
                result = '小凶'
        else:
            if relation in ['体生用', '体克用', '体用比和']:
                if ti_qi > yong_qi:
                    if yong_qi * 2 < ti_qi:
                        result = '大吉'
                    else:
                        result = '小吉'
                else:
                    if ti_qi * 2 < yong_qi:
                        result = '大凶'
                    else:
                        result = '小凶'
            else:
                # 用生体、用克体的情况
                if ti_qi > yong_qi:
                    if yong_qi * 2 < ti_qi:
                        result = '大吉'
                    else:
                        result = '小吉'
                else:
                    if ti_qi * 2 < yong_qi:
                        result = '大凶'
                    else:
                        result = '小凶'

        logger.debug(f"[sakuraTools] 比较完毕，结果为：{result}")

        # 构建旺相休囚死的字符串
        wangxiangxiuqiusi_str = '，'.join([
            f"{wx}{wangxiangxiuqiusi_dict[wx]}" for wx in wuxing_sequence
        ])

        return {
            'wang_shuai': wangxiangxiuqiusi_str,
            'sheng_ke': relation,
            'ji_xiong': result
        }

    except Exception as e:
        logger.error(f"[sakuraTools] 发生错误：{e}")
        return None


def GetGuaShu(query):
    """
    提取用户输入中头部或尾部的三位数字和问题文本

    Args:
        query: 用户输入的字符串

    Returns:
        tuple: (数字, 问题文本, 是否使用随机数)
    """
    # 移除所有空格
    query_no_space = ''.join(query.split())

    # 是否使用随机数标志
    gen_random_flag = False
    number = None

    # 匹配开头或结尾的三位数字（排除中间的三位数字）
    # (?:^|[^\d])表示字符串开头或非数字字符
    # (?=$|[^\d])表示字符串结尾或非数字字符
    start_pattern = r'(?:^|[^\d])(\d{3})(?=$|[^\d])'

    matches = re.finditer(start_pattern, query_no_space)
    matches = list(matches)

    if matches:
        # 获取所有匹配结果
        potential_numbers = []
        for match in matches:
            num = int(match.group(1))
            # 检查数字范围
            if 100 <= num <= 999:
                # 检查是否在开头或结尾
                start_pos = match.start(1)
                end_pos = match.end(1)

                # 判断是否在开头或结尾（允许最多一个符号的偏移）
                is_at_start = start_pos <= 1
                is_at_end = end_pos >= len(query_no_space) - 1

                if is_at_start or is_at_end:
                    potential_numbers.append(num)

        if potential_numbers:
            number = potential_numbers[0]  # 使用第一个有效的数字
        else:
            gen_random_flag = True
    else:
        gen_random_flag = True

    if gen_random_flag:
        # 获取当前时间戳（微秒级）生成随机数
        current_time = time.time()
        microseconds = int(str(current_time).split('.')[1][:6])
        number = microseconds % 900 + 100

    # 去除问题中的数字（只替换找到的那个三位数）
    if number is not None:
        question = re.sub(rf'\b{number}\b', '', query)
    else:
        question = query

    return number, question.strip(), gen_random_flag


def FormatZhanBuReply(gen_random_num_str: str, question: str, number: str, result: dict, reply_content: str) -> str:
    """
    格式化占卜结果回复
    """

    try:
        # 验证必需的键是否存在
        required_keys = [
            'shichen_info', 'wang_shuai',
            'ben_gua',  'ben_gua_sheng_ke',
            'hu_gua',
            'bian_gua', 'bian_gua_sheng_ke',
        ]

        if not all(key in result for key in required_keys):
            missing_keys = [key for key in required_keys if key not in result]
            raise ValueError(f"结果字典缺少必需的键: {missing_keys}")

        # 保持占卜结果模板
        prompt = f"""{gen_random_num_str}占卜结果出来啦~😸🔮\n问题：{question}\n{result['shichen_info']}\n{result['gan_zhi_info']}\n{result['wang_shuai']}\n数字：{number}\n[主卦] {result['ben_gua']}({result['ben_gua_sheng_ke']})\n        {result['ben_gua_shuo_ming']}\n[互卦] {result['hu_gua']}\n[变卦] {result['bian_gua']}({result['bian_gua_sheng_ke']})\n        {result['bian_gua_shuo_ming']}\n[动爻] {result['dong_yao']}爻动\n解析：\n{reply_content}\n(解读仅供参考哦，我们还是要活在当下嘛~🐾)"""

        return prompt

    except Exception as e:
        logger.error(f"获取占卜结果出错：{e}")
        raise


def GenZhanBuCueWord(result: dict, question: str) -> str:
    """
    生成占卜解读的提示词，保持原有格式和换行

    Args:
        result (dict): 占卜结果字典，包含以下键：
            - wang_shuai: 旺衰信息
            - ben_gua: 本卦
            - ben_gua_sheng_ke: 本卦生克
            - ben_gua_ji_xiong: 本卦吉凶
            - hu_gua: 互卦
            - bian_gua: 变卦
            - bian_gua_sheng_ke: 变卦生克
            - bian_gua_ji_xiong: 变卦吉凶
            - dong_yao: 动爻
        question (str): 用户的问题

    Returns:
        str: 格式化后的提示词
    """
    try:
        # 验证必需的键是否存在
        required_keys = [
            'wang_shuai',
            'ben_gua', 'ben_gua_sheng_ke',
            'hu_gua',
            'bian_gua',  'bian_gua_sheng_ke',
            'dong_yao'
        ]

        if not all(key in result for key in required_keys):
            missing_keys = [key for key in required_keys if key not in result]
            raise ValueError(f"[sakuraTools] 结果字典缺少必需的键: {missing_keys}")

        # 保持原有格式的提示词模板
        prompt = f"""问题：{question}。\n时间：{result['gan_zhi_info']}\n五行旺衰为：{result['wang_shuai']}\n本卦:{result['ben_gua']}({result['ben_gua_sheng_ke']})\n互卦:{result['hu_gua']}\n{result['dong_yao']}爻动\n变卦:{result['bian_gua']}({result['bian_gua_sheng_ke']})\n：
------------------------分割线----------------------
以上为排盘结果。请结合《梅花易数》的断卦方法来预测分析，请注意：
1. 八卦五行：乾为金，兑为金，离为火，震为木，巽为木，坎为水，艮为土，坤为土。
2. 什么是重卦？重卦由两个普通卦(乾坎艮震巽离坤兑)堆叠而成，因此重卦有六个爻，八卦两两组合，因此共有64个，例如水火既济，天山遁等。
3. 什么是动爻？动爻是指在卦象中有变化的爻，排盘结果中的X爻动就是在为你指明动爻，梅花易数中只会有一个动爻，比如乾为天卦，三爻动(这个爻阴阳互变以产生新的卦)，则变卦为天泽履。
3. 什么是体用？体卦就是我自己，用卦代表我要预测的事物。我现在给了你三个重卦，即本卦，互卦，变卦。这三个卦又分别有上下两卦，一共六个爻，自下而上分别为初爻、二爻、三爻、四爻、五爻、上爻。此时你需要看动爻，如果是[初爻、二爻、三爻]动，则这个重卦的下卦就是用卦，上卦就是本卦；如果是[四爻、五爻、上爻]动，则这个重卦的上卦就是用卦，下卦就是本卦；也就是说，哪个卦动了，哪个卦就是用卦。[体克用、体用比和]为吉，[用克体，体升用]为凶。
4. 五行生克关系：金生水，水生木，木生火，火生土，土生金；金克木，木克土，土克水，水克火，火克金。生代表帮扶，克代表制约。如果体卦和用卦的五行相同，则为比和，比和意味着互相帮扶，互有助力。你需要额外注意，五行生克只推演一层，也就是说，比方说本卦是乾金，那么金克木，金生水，土生金，火克金。不会再做任何额外的推演。否则按照五行不断推演就无穷无尽了，所以只推演一层。
5. 旺相休囚死：当令者旺，令生者相，生令者休，克令者囚，令克者死。令就是这个月的地支，生克是指这个月的地支生克的五行。举例：现在是庚辰月，那么月令就是辰，辰在十二地支属土，因此，土当令，土旺；土生金，因为土非常的旺，所以被它所生的金也有比较不错的力量，仅次于月令(辰土)；火生土，火的一部分力量用来生土了，因此火的的力量较弱；木克土，但是土是月令，土太旺了，克不动，木反而被土囚，因而木较为衰弱；土克水，土太旺了，水直接被死，水非常非常衰弱。
6. 你在推断预测时，需要着重参考卦与卦之间的五行生克，根据体用、生克来判断事情的吉凶，难易程度，成败，顺逆等。同时，断局也需要根据[八卦万物类象]来对卦进行取象，从而获取当前事件中卦的象征含义；
9. 最终请结合你的推测、取象，给我你的预测结果，300字以内即可。
"""

        return prompt

    except Exception as e:
        logger.error(f"[sakuraTools] 生成占卜提示词时出错：{e}")
        raise


# 修改时辰计算方式
def get_shichen(hour):
    if hour == 23 or hour == 0:
        shichen = 1  # 子时
    elif hour >= 1 and hour < 3:
        shichen = 2  # 丑时
    elif hour >= 3 and hour < 5:
        shichen = 3  # 寅时
    elif hour >= 5 and hour < 7:
        shichen = 4  # 卯时
    elif hour >= 7 and hour < 9:
        shichen = 5  # 辰时
    elif hour >= 9 and hour < 11:
        shichen = 6  # 巳时
    elif hour >= 11 and hour < 13:
        shichen = 7  # 午时
    elif hour >= 13 and hour < 15:
        shichen = 8  # 未时
    elif hour >= 15 and hour < 17:
        shichen = 9  # 申时
    elif hour >= 17 and hour < 19:
        shichen = 10  # 酉时
    elif hour >= 19 and hour < 21:
        shichen = 11  # 戌时
    else:  # hour >= 21 and hour < 23
        shichen = 12  # 亥时

    return shichen


def ChangeYao(bengua_lines, move_line):
    bian_gua_lines = bengua_lines.copy()
    index = move_line - 1
    # 变动指定的爻
    if bian_gua_lines[index] == 'yin':
        bian_gua_lines[index] = 'yang'
    elif bian_gua_lines[index] == 'yang':
        bian_gua_lines[index] = 'yin'

    return bian_gua_lines


def GanZhi():
    # 获取当前时间的干支
    solar = Solar.fromDate(datetime.utcnow() + timedelta(hours=8))
    lunar = solar.getLunar()

    # 获取年月日时的干支
    year_ganzhi = lunar.getYearInGanZhi()  # 年干支
    month_ganzhi = lunar.getMonthInGanZhi()  # 月干支
    day_ganzhi = lunar.getDayInGanZhi()  # 日干支
    hour_ganzhi = lunar.getTimeInGanZhi()  # 时辰干支

    return [year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi]


def GetNongLiMonth(input_str):
    logger.debug(type(input_str))
    month = 1
    # 定义地支与月份的对应关系字典
    branch_to_month = {
        '寅': 1,  # 正月
        '卯': 2,  # 二月
        '辰': 3,  # 三月
        '巳': 4,  # 四月
        '午': 5,  # 五月
        '未': 6,  # 六月
        '申': 7,  # 七月
        '酉': 8,  # 八月
        '戌': 9,  # 九月
        '亥': 10, # 十月
        '子': 11, # 十一月
        '丑': 12  # 十二月
    }

    # 检查输入是否为空
    if not input_str:
        logger.debug("[sakuraTools] Invalid Input: Empty string")
        return month

    # 获取地支（如果输入是两个字符，取第二个；如果是一个字符，直接使用）
    earthly_branch = input_str[-1]  # 取最后一个字符作为地支

    # 检查提取的地支是否有效
    if earthly_branch not in branch_to_month:
        logger.debug("[sakuraTools] Invalid Earthly Branch")
        return month

    # 返回对应的月份
    month = branch_to_month[earthly_branch]
    return  month


def MeiHuaXinYi(value):
    """
    梅花易数卜卦函数
    """
    if not isinstance(value, int):
        raise ValueError("[sakuraTools] 输入必须是整数。")
    if value < 100 or value > 999:
        return None

    # 1. 计算上卦数
    hundreds_digit = value // 100
    upper_num = hundreds_digit % 8
    upper_num = upper_num if upper_num != 0 else 8

    # 2. 计算下卦数
    tens_digit = (value // 10) % 10
    units_digit = value % 10
    lower_sum = tens_digit + units_digit
    lower_num = lower_sum % 8
    lower_num = lower_num if lower_num != 0 else 8

    # 3. 计算动爻数
    digit_sum = hundreds_digit + tens_digit + units_digit
    logger.debug(f"{hundreds_digit} + {tens_digit} + {units_digit} = {digit_sum}")

    # 获取当前时间
    now = datetime.now()

    hour = now.hour

    # 获取时辰数
    shichen = get_shichen(hour)
    shichen_name = SHI_CHEN[shichen]

    total = digit_sum + shichen
    moving_line = total % 6
    logger.debug(f"{total} = {digit_sum} + {shichen}")
    logger.debug(f"{moving_line} = {total} % 6 ")
    if moving_line == 0:
        moving_line = 6

    # 4. 得到本卦
    try:
        lower_trigram = MAP_FOR_8_GUA[lower_num]['lines']
        lower_name = MAP_FOR_8_GUA[lower_num]['name']
        upper_trigram = MAP_FOR_8_GUA[upper_num]['lines']
        upper_name = MAP_FOR_8_GUA[upper_num]['name']
    except KeyError:
        raise ValueError("上卦数或下卦数无效。")

    bengua_lines = lower_trigram + upper_trigram  # 自下而上六爻
    bengua_info = get_gua_info(upper_num, lower_num)
    bengua_name = bengua_info[0]
    bengua_shuoming = f"「{bengua_info[1]}」"

    # 5. 得到互卦
    hugua_lines = bengua_lines[1:5]
    hugua_lower_lines = hugua_lines[:3]
    hugua_upper_lines = hugua_lines[1:]

    def get_trigram_from_lines(lines):
        for num, trigram in MAP_FOR_8_GUA.items():
            if trigram['lines'] == lines:
                return num, trigram['name']
        return None, '未知'

    hugua_lower_num, hugua_lower_name = get_trigram_from_lines(hugua_lower_lines)
    hugua_upper_num, hugua_upper_name = get_trigram_from_lines(hugua_upper_lines)

    huua_info = get_gua_info(hugua_upper_num, hugua_lower_num)

    # 修改此处，互卦名称直接输出上卦和下卦名称
    hugua_name = f"{huua_info[0][0]} 互见{hugua_upper_name}{hugua_lower_name}"

    # 6. 得到变卦
    bian_gua_lines = ChangeYao(bengua_lines, moving_line)
    logger.debug("bengua_lines:", bengua_lines)
    logger.debug("bian_gua_lines:", bian_gua_lines)
    bian_gua_lower_lines = bian_gua_lines[:3]
    logger.debug("bian_gua_lower_lines:", bian_gua_lower_lines)
    bian_gua_upper_lines = bian_gua_lines[3:]
    logger.debug("bian_gua_upper_lines:", bian_gua_upper_lines)

    bian_gua_lower_num, bian_gua_lower_name = get_trigram_from_lines(bian_gua_lower_lines)
    bian_gua_upper_num, bian_gua_upper_name = get_trigram_from_lines(bian_gua_upper_lines)

    biangua_info = get_gua_info(bian_gua_upper_num, bian_gua_lower_num)
    bian_gua_name = biangua_info[0]
    biangua_shuoming = f"「{biangua_info[1]}」"

    # 7. 获取动爻，六爻顺序为自下而上，索引为0表示初爻，动爻是 moving_line
    dong_yao = ['初', '二', '三', '四', '五', '上'][moving_line - 1]
    dong_yao_full = f"{dong_yao}"

    logger.debug(f"上卦数:{upper_num}   下卦数:{lower_sum}")
    logger.debug(f"时  辰:{shichen_name}   时辰数:{shichen}")
    logger.debug(f"动爻数:{moving_line}   动  爻:{dong_yao}")

    # 8. 获取时辰信息
    datetime_str = f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second}"

    # 整合信息，准备获取五行生克结果
    if 1 <= moving_line < 3:
        # 动爻在下卦，上卦为体
        dong_yao_flag = 1
    else:
        # 动爻在上卦，下卦为体
        dong_yao_flag = 0

    # 获取干支
    gan_zhi = GanZhi()
    ganzhi_info = f"{gan_zhi[0]}年 {gan_zhi[1]}月 {gan_zhi[2]}日 {gan_zhi[3]}时"

    # 获取农历月份数
    nongli_month = GetNongLiMonth(gan_zhi[1])

    # 调用 WuXingCalculator 函数获取体用生克信息以及吉凶结果
    bengua_wuxing_result = WuXingCalculator(upper_num, lower_num, dong_yao_flag, nongli_month)
    bian_gua_wuxing_result = WuXingCalculator(bian_gua_upper_num, bian_gua_lower_num, dong_yao_flag, nongli_month)

    # 构造结果字典
    result = {
        "shichen_info": datetime_str,
        "gan_zhi_info": ganzhi_info,
        "ben_gua": bengua_name,
        "ben_gua_shuo_ming": bengua_shuoming,
        "wang_shuai": bengua_wuxing_result['wang_shuai'],
        "ben_gua_sheng_ke": bengua_wuxing_result['sheng_ke'],
        "hu_gua": hugua_name,
        "bian_gua": bian_gua_name,
        "bian_gua_shuo_ming": biangua_shuoming,
        "bian_gua_sheng_ke": bian_gua_wuxing_result['sheng_ke'],
        "dong_yao": dong_yao_full
    }
    logger.info(f"[sakuraTools] 占卜结果：\n时间：{datetime_str}\n干支：{ganzhi_info}\n旺衰：{bengua_wuxing_result['wang_shuai']}\n本卦：{bengua_name}  {bengua_wuxing_result['sheng_ke']}\n互卦：{hugua_name}\n动爻：{dong_yao_full}\n变卦：{bian_gua_name}  {bian_gua_wuxing_result['sheng_ke']}\n")
    return result