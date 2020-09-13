from datetime import datetime, timedelta
import re


def check_time_in(pubtime: datetime, curtime: datetime, diff=60):   # 60单位分钟
    delta = (curtime - pubtime)
    return delta.days == 0 and delta.seconds // 3600 <= 1


now = datetime.now()
MINUTE = 60 * 1
HOUR = MINUTE * 60
DAY = HOUR * 24

timestamp_pattern = re.compile(r'\D(1[5-9]\d{8})(\d{3}\D|\D)')
hour_pattern = re.compile(r'([半\d]) ?小时前')
minute_pattern = re.compile(r'(\d{1,2}) ?分钟*前')
second_pattern = re.compile(r'(\d{1,2}) ?秒前')


def is_time_before(cur_time, minute=0, hour=0, day=0, format='%Y-%m-%d %H:%M'):
    if isinstance(cur_time, str):
        cur_time = datetime.strptime(cur_time, format)
    elif isinstance(cur_time, datetime):
        print("unsupport time format ", cur_time)
        return False
    timestamp = minute * MINUTE + hour * HOUR + day * DAY
    return now.timestamp() - cur_time.timestamp() <= timestamp


def get_ymdhm_date(result):  # 年月日 时分
    result_list = [int(x) for x in result.groups()]
    result_list[0] = 2000 + result_list[0]
    return result_list


def get_mdhm_date(result):   # 月日 时分
    result_list = [int(x) for x in result.groups()]
    result_list.insert(0, now.year)
    return result_list


def get_ymd_date(result):    # 年月日
    result_list = [int(x) for x in result.groups()]
    result_list[0] = 2000 + result_list[0]
    return result_list


def get_hm_date(result):   # 时分
    yestoday, hour, minute = result.groups()
    hour = int(hour)
    minute = int(minute)
    if yestoday:
        date = datetime(now.year, now.month, now.day, hour, minute) - timedelta(days=1)
        return date.year, date.month, date.day, hour, minute
    return now.year, now.month, now.day, hour, minute


def get_md_date(result):   # 月日
    result_list = [int(x) for x in result.groups()]
    result_list.insert(0, now.year)
    return result_list


def get_date_by(year, month, day, hour=0, minute=0):
    # if year > now.year or (month > 12 or month < 1) or (day > 31 or day < 1):
    #     return ''
    try:
        cur_date = datetime(year, month, day, hour=hour, minute=minute)
        if cur_date > now:
            cur_date = datetime(now.year-1, month, day, hour=hour, minute=minute)
        return cur_date
    except Exception as e:
        print("[%s]", str(e))
        return ''


def get_date_from(timestamp: int):
    return datetime.fromtimestamp(timestamp)


def get_int_timestamp(result):
    return int(result.group(1))


def get_day_timestamp(result):
    result = result.group(1)
    if result == '昨':
        return now.timestamp() - DAY
    else:
        return now.timestamp() - DAY * int(result)


def get_hour_timestamp(result):
    result = result.group(1)
    if result == '半':
        return now.timestamp() - MINUTE * 30
    else:
        return now.timestamp() - HOUR * int(result)


def get_minute_timestamp(result):
    return now.timestamp() - 60 * int(result.group(1))


def get_second_timestamp(result):
    return now.timestamp()


date_pattern_list = [(re.compile(x), format_func) for x, format_func in [
    (r'(\d{2})[-/年\.](\d{1,2})[-/月\.](\d{1,2})日?[\sT]?(\d{1,2}):(\d{1,2})', get_ymdhm_date),   # 年月日 时分
    (r'\D(\d{1,2})[-/月](\d{1,2})日* *(\d{1,2}):(\d{1,2})', get_mdhm_date),    # 月日  时分
    (r'(\d{2})[-/年](\d{1,2})[-/月](\d{1,2})日?', get_ymd_date),  # 年月日
    (r'(昨天)?\s?(\d{1,2}):(\d{1,2})', get_hm_date),  # 时分
    (r'(\d{1,2})[-/月](\d{1,2})日?', get_md_date),    # 月日
]]

time_pattern_list = [(re.compile(x), format_func) for x, format_func in [
    (r'(半|\d{1,2})\s?小时前', get_hour_timestamp),  # n小时前
    (r'(\d{1,2})\s?分钟*前', get_minute_timestamp),    # n分钟前
    (r'(刚刚|\d{1,2})\s?秒前', get_second_timestamp),
    (r'\D(1[5-9]\d{8})(\d{3}\D|\D)', get_int_timestamp),
    (r'(昨|\d)\s?天前', get_day_timestamp) # n天前
]]


def search_time(timestr: str, overseas=False, target_format='%Y-%m-%d %H:%M'):
    # 如果origin_match为True, 则返回原始匹配到的字符
    global now
    now = datetime.now()
    for format_pattern, format_func in date_pattern_list:
        result = format_pattern.search(timestr)
        if result:
            date_list = format_func(result)
            if date_list:
                cur_datetime = get_date_by(*date_list)
                break
    else:
        for format_pattern, format_func in time_pattern_list:
            result = format_pattern.search(timestr)
            if result:
                timestamp = format_func(result)
                if timestamp:
                    cur_datetime = get_date_from(timestamp)
                    break
        else:
            return ''
    if cur_datetime and target_format:
        return cur_datetime.strftime(target_format)
    else:
        return cur_datetime


def test_all():
    print('年月日 时分(3)\n--------------------------------------------------')
    print(search_time(' 12月1日 11:1'))
    print(search_time(' 2019年12月1日 11:1'))
    print(search_time(' 2019-12-1 11:1'))
    print(search_time(' 2019/12/1 11:1'))
    print('月日 时分(3)\n--------------------------------------------------')
    print(search_time(' sfsdf12月1日 11:1'))
    print(search_time(' asdasd12-1 11:01'))
    print(search_time(' asdasd12/1 1:1'))
    print('年月日(3)\n--------------------------------------------------')
    print(search_time(' 2019年12月11日'))
    print(search_time(' 2019-12-12'))
    print(search_time(' asd2019/12/13dfafa'))
    print('时分(2)\n--------------------------------------------------')
    print(search_time(' 2019asda12:1'))
    print(search_time(' 212:13'))
    print('月日(3)\n--------------------------------------------------')
    print(search_time(' 12月1日'))
    print(search_time(' asdasd12-1'))
    print(search_time(' asdasd12/1asda'))
    print('n小时前(6)\n--------------------------------------------------')
    print(search_time('半小时前'))
    print(search_time('半 小时前'))
    print(search_time('11小时前'))
    print(search_time('1小时前'))
    print(search_time('1 小时前'))
    print(search_time('11 小时前'))
    print('n分钟前(4)\n--------------------------------------------------')
    print(search_time(' 20分钟前'))
    print(search_time(' 20分钟前-1'))
    print(search_time(' 20 分前'))
    print(search_time(' 20 分钟前'))
    print('n天前(4)\n--------------------------------------------------')
    print(search_time(' 20天前'))
    print(search_time(' 20 天-1'))
    print(search_time(' 20 天前'))
    print(search_time(' 0 天钟前'))


if __name__ == '__main__':
    test_all()

"""
海外可能有的时间格式
2019 七月 01
May 22, 2019
2019年 7月 23日
应该增加url匹配/2019/01/dasd.html该种url
"""
