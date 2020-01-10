from datetime import datetime, timedelta
import re

def check_time_in(pubtime:datetime, curtime:datetime, diff=60):   # 60单位分钟
    delta = (curtime - pubtime)
    return delta.days == 0 and delta.seconds // 3600 <= 1


now = datetime.now()
MINUTE = 60 * 1

# format_pattern_list = [(re.compile(x), m, y) for x, m, y in [
#     ('(%s-0*%s-\d{1,2} \d{1,2}:\d{1,2})'%(now.year, now.month), '%s', '%y-%m-%d %H:%M'),   # 年月日 时分秒
#     ('(0*%s-\d{1,2} \d{1,2}:\d{1,2})'%now.month, f'{now.year}-%s', '%Y-%m-%d %H:%M'),    # 月日  时分
#     ('(%s0*%s[0-3]\d)'%(now.year, now.month), '%s', '%Y%m%d'),
#     ('(\d{1,2}:\d{1,2})', f'{now.year}-{now.month}-{now.day} %s', '%Y-%m-%d %H:%M'),  # 时分
#     ('\D(%s-0*%s-\d{1,2})\D'%(now.year, now.month), '%s' ,'%Y-%m-%d'),  # 年月日
#     ('(%s年0*%s月\d{1,2}日)'%(now.year, now.month), '%s', '%y年%m月%d日'),
#     ('(0*%s月\d{1,2}日)'%now.month, f'{now.year}年%s', '%Y年%m月%d日'),
#     ('\D(0*%s-\d{1,2})\D'%now.month, f'{now.year}-%s', '%Y-%m-%d'),   # 月日
# ]]



def get_ymdhm_date(result):  # 年月日 时分
    year, month, day, hour, minute = [int(x) for x in result.groups()]
    if year > now.year or (month > 12 or month < 1) or day > 31 or day < 1:
        return None
    return datetime(year, month, day, hour, minute)


def get_mdhm_date(result):   # 月日 时分
    month, day, hour, minute = [int(x) for x in result.groups()]
    if (month > 12 or month < 1) or day > 31 or day < 1:
        return None
    cur_datetime = datetime(now.year, month, day, hour, minute)
    if cur_datetime > now:
        cur_datetime = datetime(now.year-1, month, day, hour, minute)
    return cur_datetime

def get_ymd_date(result):    # 年月日
    year, month, day = [int(x) for x in result.groups()]
    if year > now.year or (month > 12 or month < 1) or day > 31 or day < 1:
        return None
    return datetime(year, month, day)


def get_hm_date(result):   # 时分
    hour, minute = [int(x) for x in result.groups()]
    cur_datetime = datetime(now.year, now.month, now.day, hour, minute)
    if cur_datetime > now:
        cur_datetime = datetime(now.year-1, now.month, now.day, hour, minute)
    return cur_datetime

def get_md_date(result):   # 月日
    month, day = [int(x) for x in result.groups()]
    if (month > 12 or month < 1) or day > 31 or day < 1:
        return None
    cur_datetime = datetime(now.year, month, day)
    if cur_datetime > now:
        cur_datetime = datetime(now.year-1, month, day)
    return cur_datetime

def get_hour_date(timestr):
    if timestr == '半':
        cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * 30)
    else:
        cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * 60 * int(timestr))
    return cur_datetime

def get_minute_date(timestr):
    return datetime.fromtimestamp(now.timestamp() - 60 * int(timestr))


def get_second_date(timestr):
    return datetime.fromtimestamp(now.timestamp() - int(timestr))

format_pattern_list = [(re.compile(x), format_func) for x, format_func in [
    ('(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日* *(\d{1,2}):(\d{1,2})', get_ymdhm_date),   # 年月日 时分
    ('\D(\d{1,2})[-/月](\d{1,2})日* *(\d{1,2}):(\d{1,2})', get_mdhm_date),    # 月日  时分
    ('(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})日*', get_ymd_date),  # 年月日
    # ('(20\d{2}/*[01]\d[0-3]\d)', get_ymd_date),  # 年月日
    ('(\d{1,2}):(\d{1,2})', get_hm_date),  # 时分
    ('(\d{1,2})[-/月](\d{1,2})日*', get_md_date),    # 月日
]]


hour_pattern = re.compile('([半\d]) *小时前')
minute_pattern = re.compile('(\d{1,2}) *分钟*前')
second_pattern = re.compile('(\d{1,2}) *秒前')

def search_time_in(url):
    result = re.search('(20\d{2})[-/]*([01]\d)[-/]*([0-3]\d)', url)  # 年月日
    if result:
        year = int(result.group(1))
        month = int(result.group(2))
        day = int(result.group(3))
        if month > 12 or month < 1:
            return ''
        elif day > 31 or day < 1:
            return ''
        return datetime(year, month, day).strftime('%Y-%m-%d %H:%M')
    return ''

def search_time(timestr:str, target_format='%Y-%m-%d %H:%M'):
    # 如果origin_match为True, 则返回原始匹配到的字符
    now = datetime.now()
    cur_datetime = ''
    for format_pattern, format_func in format_pattern_list:
        result = format_pattern.search(timestr)
        if result:
            # (format_func, result.group())
            cur_datetime = format_func(result)
            if cur_datetime:
                return cur_datetime.strftime(target_format)
    hour = hour_pattern.search(timestr)
    if hour:
        if hour.group(1) == '半':
            cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * 30)
        else:
            cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * 60 * int(hour.group(1)))
        # return cur_datetime.strftime(target_format)
    else:
        minute = minute_pattern.search(timestr)
        if minute:
            cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * int(minute.group(1)))
            # return cur_datetime.strftime(target_format)
        else:
            second = second_pattern.search(timestr)
            if second:
                cur_datetime = datetime.fromtimestamp(now.timestamp() - int(second.group(1)))
                # return cur_datetime.strftime(target_format)
    if target_format:
        return cur_datetime.strftime(target_format) if cur_datetime else ''
    else:
        return cur_datetime




def search_time_ex(timestr:str, target_format='%Y-%m-%d %H:%M'):
    # 如果origin_match为True, 则返回原始匹配到的字符
    now = datetime.now()
    timestr = timestr.replace("/", '-')
    cur_datetime = ''
    origin_datetime = ''
    for format_pattern, format_middle, format_value in format_pattern_list:
        result = format_pattern.search(timestr)
        if result:
            origin_datetime = result.group(),
            cur_datetime = datetime.strptime(format_middle % result.group(), format_value)
            break
    if not cur_datetime:
        hour = hour_pattern.search(timestr)
        if hour:
            origin_datetime = hour.group()
            if hour.group(1) == '半':
                cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * 30)
            else:
                cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * 60 * int(hour.group(1)))
        else:
            minute = minute_pattern.search(timestr)
            if minute:
                origin_datetime = minute.group()
                cur_datetime = datetime.fromtimestamp(now.timestamp() - 60 * int(minute.group(1)))
            else:
                second = second_pattern.search(timestr)
                if second:
                    origin_datetime = minute.group()
                    cur_datetime = datetime.fromtimestamp(now.timestamp() - int(second.group(1)))
                    # return cur_datetime.strftime(target_format)
    if not cur_datetime:
        return '', ''
    if cur_datetime.timestamp() - MINUTE > now.timestamp():
        cur_datetime = cur_datetime - timedelta(days=365)
    if target_format is None:
        return origin_datetime, cur_datetime
    else:
        return origin_datetime, cur_datetime.strftime(target_format)



def search_all(timestr:str, target_format='%Y-%m-%d %H:%M'):
    # 如果origin_match为True, 则返回原始匹配到的字符
    now = datetime.now()
    timestr = timestr.replace("/", '-')
    time_list = []
    for format_pattern, format_func in format_pattern_list:
        result_list = format_pattern.findall(timestr)
        for result in result_list:
            try:
                cur_datetime = format_func(result)
                time_list.append((result, cur_datetime))
            except Exception as e:
                ("strptime error", str(e), result, format_func)
                return []
    hour_list = hour_pattern.findall(timestr)
    for result in hour_list:
        cur_datetime = get_hour_date(result)
        time_list.append((result, cur_datetime))
    minute_list = minute_pattern.findall(timestr)
    for result in minute_list:
        cur_datetime = get_minute_date(result)
        time_list.append((result, cur_datetime))
    second_list = second_pattern.findall(timestr)
    for result in second_list:
        cur_datetime = get_second_date(result)
        time_list.append((result, cur_datetime))
    return [(result, x.strftime(target_format)) for result, x in time_list]


def test_all():
    ('年月日 时分\n--------------------------------------------------')
    (search_time(' 2019年12月1日 11:1'))
    (search_time(' 2019-12-1 11:1'))
    print(search_time(' 2019/12/1 11:1'))
    print('月日 时分\n--------------------------------------------------')
    print(search_time(' sfsdf12月1日 11:1'))
    print(search_time(' asdasd12-1 11:01'))
    print(search_time(' asdasd12/1 1:1'))
    print('年月日\n--------------------------------------------------')
    print(search_time(' 2019年12月1日'))
    print(search_time(' 2019-12-1'))
    print(search_time(' asd2019/12/1dfafa'))
    print(search_time(' 20190301dasd'))
    print('时分\n--------------------------------------------------')
    print(search_time(' 2019asda12:1'))
    print(search_time(' 212:13'))
    print('月日\n--------------------------------------------------')
    print(search_time(' 12月1日'))
    print(search_time(' asdasd12-1'))
    print(search_time(' asdasd12/1asda'))
    print('n小时前\n--------------------------------------------------')
    print(search_time('半小时前'))
    print(search_time('半 小时前'))
    print(search_time('11小时前'))
    print(search_time('1小时前'))
    print(search_time('1 小时前'))
    print(search_time('11 小时前'))
    print('n分钟前\n--------------------------------------------------')
    print(search_time(' 20分钟前'))
    print(search_time(' 20分钟前-1'))
    print(search_time(' 20 分前'))
    print(search_time(' 20 分钟前'))
    print('n天前\n--------------------------------------------------')
    print(search_time(' 20天前'))
    print(search_time(' 20 天-1'))
    print(search_time(' 20 天前'))
    print(search_time(' 0 天钟前'))
