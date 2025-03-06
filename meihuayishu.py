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

# 六十四卦映射
MAP_FOR_64_GUA = {
    (1, 1): '乾为天',   (1, 2): '天泽履',   (1, 3): '天火同人', (1, 4): '天雷无妄',
    (1, 5): '天风姤',   (1, 6): '天水讼',   (1, 7): '天山遁',   (1, 8): '天地否',
    (2, 1): '泽天夬',   (2, 2): '兑为泽',   (2, 3): '泽火革',   (2, 4): '泽雷随',
    (2, 5): '泽风大过', (2, 6): '泽水困',   (2, 7): '泽山咸',   (2, 8): '泽地萃',
    (3, 1): '火天大有', (3, 2): '火泽睽',   (3, 3): '离为火',   (3, 4): '火雷噬嗑',
    (3, 5): '火风鼎',   (3, 6): '火水未济', (3, 7): '火山旅',   (3, 8): '火地晋',
    (4, 1): '雷天大壮', (4, 2): '雷泽归妹', (4, 3): '雷火丰',   (4, 4): '震为雷',
    (4, 5): '雷风恒',   (4, 6): '雷水解',   (4, 7): '雷山小过', (4, 8): '雷地豫',
    (5, 1): '风天小畜', (5, 2): '风泽中孚', (5, 3): '风火家人', (5, 4): '风雷益',
    (5, 5): '巽为风',   (5, 6): '风水涣',   (5, 7): '风山渐',   (5, 8): '风地观',
    (6, 1): '水天需',   (6, 2): '水泽节',   (6, 3): '水火既济', (6, 4): '水雷屯',
    (6, 5): '水风井',   (6, 6): '坎为水',   (6, 7): '水山蹇',   (6, 8): '水地比',
    (7, 1): '山天大畜', (7, 2): '山泽损',   (7, 3): '山火贲',   (7, 4): '山雷颐',
    (7, 5): '山风蛊',   (7, 6): '山水蒙',   (7, 7): '艮为山',   (7, 8): '山地剥',
    (8, 1): '地天泰',   (8, 2): '地泽临',   (8, 3): '地火明夷', (8, 4): '地雷复',
    (8, 5): '地风升',   (8, 6): '地水师',   (8, 7): '地山谦',   (8, 8): '坤为地'
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
        prompt = f"""{gen_random_num_str}占卜结果出来啦~😸🔮\n问题：{question}\n{result['shichen_info']}\n{result['gan_zhi_info']}\n{result['wang_shuai']}\n数字：{number}\n[主卦] {result['ben_gua']}({result['ben_gua_sheng_ke']})\n[互卦] {result['hu_gua']}\n[动爻] {result['dong_yao']}爻动\n[变卦] {result['bian_gua']}({result['bian_gua_sheng_ke']})\n解析：\n{reply_content}\n(解读仅供参考哦，我们还是要活在当下嘛~🐾)"""

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
以上为排盘结果。请结合《梅花易数》的断卦方法，先根据卦象本身判断吉凶，再辅以“三要十应”取象（即通过捕捉文字中隐藏的声音、形象和内在理）来辅助断局。分析时注意：
1. 旺相休囚死：当令者旺，令生者相，生令者休，克令者囚，令克者死。令就是这个月的地支，生克是指这个月的地支生克的五行。
2. 梅花易数不参照易经对于64卦的解释，更注重卦本身的生克制化（参见《梅花易数》的体用之说：体卦为我，用卦为事，即根据本、互、变三个重卦本身的五行生克推测吉凶和事物的发展）。记住，万事万物皆是五行生克。
3. “三要十应”作为辅助依据，勿逐项列举；
4. 断局需结合卦和问题描述中涉及的天气、地理、人事、时令、方位、动静、方向、器物、声音及文字等信息，将提取到的信息结合八卦万物类象进行取象；
5. 最终请结合你的推测、取象，给我你的预测结果，300字以内给。
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
    bengua_name = MAP_FOR_64_GUA.get((upper_num, lower_num), '未知卦')

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

    hugua_name_pro = MAP_FOR_64_GUA.get((hugua_upper_num, hugua_lower_num), '未知卦')

    # 修改此处，互卦名称直接输出上卦和下卦名称
    hugua_name = f"互见{hugua_upper_name}{hugua_lower_name}"

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

    bian_gua_name = MAP_FOR_64_GUA.get((bian_gua_upper_num, bian_gua_lower_num), '未知卦')

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
        "wang_shuai": bengua_wuxing_result['wang_shuai'],
        "ben_gua_sheng_ke": bengua_wuxing_result['sheng_ke'],
        "hu_gua": hugua_name,
        "bian_gua": bian_gua_name,
        "bian_gua_sheng_ke": bian_gua_wuxing_result['sheng_ke'],
        "dong_yao": dong_yao_full
    }
    logger.info(f"[sakuraTools] 占卜结果：\n时间：{datetime_str}\n干支：{ganzhi_info}\n旺衰：{bengua_wuxing_result['wang_shuai']}\n本卦：{bengua_name}  {bengua_wuxing_result['sheng_ke']}\n互卦：{hugua_name}\n动爻：{dong_yao_full}\n变卦：{bian_gua_name}  {bian_gua_wuxing_result['sheng_ke']}\n")
    return result