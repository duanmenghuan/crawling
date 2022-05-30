import mysql.connector
from conf import *
from decimal import Decimal, ROUND_HALF_UP
import time
from cacheout import Cache

db = mysql.connector.connect(**DB_CONFIG)
cache = Cache(maxsize=256, ttl=60 * 60, timer=time.time, default=None)  # 缓存1小时


class SourceDataDemo:
    cur = None
    profession = ''

    def __init__(self, profession):
        self.profession = profession
        self.cur = db.cursor()

        self.title = '前程无忧职位可视化大屏'
        self.counter = {'name': '总职位数', 'value': self.sum_jobs()}
        self.counter2 = {'name': '最高年薪工资', 'value': self.max_year_salary()}
        self.echart1_data = {
            'title': '行业分布',
            'data': self.sum_work(),
        }
        self.echart2_data = {
            'title': '省份分布',
            'data': self.sum_province(),
        }
        self.echarts3_1_data = {
            'title': '企业性质',
            'data': self.sum_company(),
        }
        self.echarts3_2_data = {
            'title': '行业分布',
            'data': self.sum_industry(),
        }
        self.echarts3_3_data = {
            'title': '学历要求',
            'data': self.sum_education(),
        }
        self.echart4_data = {
            'title': '北京和上海工资对比',
            'data': self.sum_city_compare(),
            'xAxis': ['0.8-1万', '1.5-2万', '1-1.5万', '2-2.5万', '0.8-1.2万'],
        }
        self.echart5_data = {
            'title': '工作经验',
            'data': self.sum_experience(),
        }
        self.echart6_data = {
            'title': '一线城市职位占比情况',
            'data': self.sum_first_city(),
        }
        self.map_1_data = {
            'symbolSize': 100,
            'data': self.avg_salary(),
        }

    @property
    def echart1(self):
        data = self.echart1_data
        echart = {
            'title': data.get('title'),
            'xAxis': [i.get("name") for i in data.get('data')],
            'series': [i.get("value") for i in data.get('data')]
        }
        return echart

    @property
    def echart2(self):
        data = self.echart2_data
        echart = {
            'title': data.get('title'),
            'xAxis': [i.get("name") for i in data.get('data')],
            'series': [i.get("value") for i in data.get('data')]
        }
        return echart

    @property
    def echarts3_1(self):
        data = self.echarts3_1_data
        echart = {
            'title': data.get('title'),
            'xAxis': [i.get("name") for i in data.get('data')],
            'data': data.get('data'),
        }
        return echart

    @property
    def echarts3_2(self):
        data = self.echarts3_2_data
        echart = {
            'title': data.get('title'),
            'xAxis': [i.get("name") for i in data.get('data')],
            'data': data.get('data'),
        }
        return echart

    @property
    def echarts3_3(self):
        data = self.echarts3_3_data
        echart = {
            'title': data.get('title'),
            'xAxis': [i.get("name") for i in data.get('data')],
            'data': data.get('data'),
        }
        return echart

    @property
    def echart4(self):
        data = self.echart4_data
        echart = {
            'title': data.get('title'),
            'names': [i.get("name") for i in data.get('data')],
            'xAxis': data.get('xAxis'),
            'data': data.get('data'),
        }
        return echart

    @property
    def echart5(self):
        data = self.echart5_data
        echart = {
            'title': data.get('title'),
            'xAxis': [i.get("name") for i in data.get('data')],
            'series': [i.get("value") for i in data.get('data')],
            'data': data.get('data'),
        }
        return echart

    @property
    def echart6(self):
        data = self.echart6_data
        echart = {
            'title': data.get('title'),
            'xAxis': [i.get("name") for i in data.get('data')],
            'data': data.get('data'),
        }
        return echart

    @property
    def map_1(self):
        data = self.map_1_data
        echart = {
            'symbolSize': data.get('symbolSize'),
            'data': data.get('data'),
        }
        return echart

    # 统计当前专业职位总数: 招聘人数累计
    def sum_jobs(self):
        ret = cache.get('sum_jobs:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_jobs start")
        sql = "SELECT SUM(`_招聘人数`) FROM `job` WHERE `所属行业` like '%{}%'".format(self.profession)
        self.cur.execute(sql)
        row = self.cur.fetchone()
        if row is None or row[0] is None:
            row = [0]  # 默认值
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_jobs finish")

        cache.set('sum_jobs:' + self.profession, row[0])
        return row[0]

    # 当前专业职位里最高薪*12月=年薪
    def max_year_salary(self):
        ret = cache.get('max_year_salary:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "max_year_salary start")
        sql = "SELECT MAX(`_最高工资`) FROM `job` WHERE `所属行业` like '%{}%'".format(self.profession)
        self.cur.execute(sql)
        row = self.cur.fetchone()
        if row is None or row[0] is None:
            row = [0]  # 默认值
        year_salary = int(Decimal(row[0]) * Decimal("12").quantize(Decimal('0'), rounding=ROUND_HALF_UP))
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "max_year_salary finish")

        cache.set('max_year_salary:' + self.profession, year_salary)
        return year_salary

    # 当前专业职位的行业分布: 前7
    def sum_industry(self):
        ret = cache.get('sum_industry:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_industry start")
        sql = "SELECT SUM(`_招聘人数`) as c,`_行业` FROM job WHERE `所属行业` like '%{}%' GROUP BY `_行业` ORDER BY c DESC LIMIT 7".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        data = []
        for row in rows:
            data.append({"name": row[1], "value": int(row[0])})
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_industry finish")

        cache.set('sum_industry:' + self.profession, data)
        return data

    # 当前专业职位的省份分布: 前7
    def sum_province(self):
        ret = cache.get('sum_province:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_province start")
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` FROM job WHERE `所属行业` like '%{}%' GROUP BY `_城市` ORDER BY c DESC LIMIT 7".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        data = []
        for row in rows:
            data.append({"name": row[1], "value": int(row[0])})
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_province finish")

        cache.set('sum_province:' + self.profession, data)
        return data

    # 当前专业职位的企业性质: 前5
    def sum_company(self):
        ret = cache.get('sum_company:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_company start")
        sql = "SELECT SUM(`_招聘人数`) as c,`公司性质` FROM job WHERE `所属行业` like  '%{}%' AND `公司性质`!='' GROUP BY `公司性质` ORDER BY c DESC LIMIT 5".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        data = []
        count = 0
        for row in rows:
            count = count + row[0]
            data.append({"name": row[1], "value": row[0]})

        for node in data:
            node['value'] = Decimal(node["value"]) / Decimal(count).quantize(Decimal('0.00'),
                                                                             rounding=ROUND_HALF_UP) * Decimal("100")
            node['value'] = int(node['value'])
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_company finish")

        cache.set('sum_company:' + self.profession, data)
        return data

    # 当前专业职位的行业分布: 前7->前5(太多了显示不全)
    def sum_work(self):
        ret = cache.get('sum_work:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_work start")
        sql = "SELECT SUM(`_招聘人数`) as c,`_职位` FROM job WHERE `所属行业` like '%{}%' GROUP BY `_职位` ORDER BY c DESC LIMIT 5".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        data = []
        for row in rows:
            data.append({"name": row[1], "value": int(row[0])})
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_work finish")

        cache.set('sum_work:' + self.profession, data)
        return data

    # 当前专业职位的学历布: 前6
    def sum_education(self):
        ret = cache.get('sum_education:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_education start")
        sql = "SELECT SUM(`_招聘人数`) as c,`学历` FROM job WHERE `所属行业` like  '%{}%' AND `学历` in ('大专','本科','中专','高中','中技','初中及以下','硕士','博士') GROUP BY `学历` ORDER BY c DESC LIMIT 6".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        data = []
        count = 0
        for row in rows:
            count = count + row[0]
            if row[1] == '初中及以下':
                data.append({"name": '初中', "value": int(row[0])})
            else:
                data.append({"name": row[1], "value": int(row[0])})

        for node in data:
            node['value'] = Decimal(node["value"]) / Decimal(count).quantize(Decimal('0.00'),
                                                                             rounding=ROUND_HALF_UP) * Decimal("100")
            node['value'] = int(node['value'])
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_education finish")

        cache.set('sum_education:' + self.profession, data)
        return data

    # 当前专业职位的北京与上海数量对比
    def sum_city_compare(self):
        ret = cache.get('sum_city_compare:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_city_compare start")
        # '0.8-1万', '1.5-2万', '1-1.5万', '2-2.5万', '0.8-1.2万'
        _beijing = []
        _shanghai = []

        # 0.8-1.2
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` from job WHERE `所属行业` like  '%{}%' AND `_城市` IN ('北京','上海') AND (`_最低工资`+`_最高工资`)/2 >= 8000 AND (`_最低工资`+`_最高工资`)/2 < 10000 GROUP BY `_城市`".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            if row[1] == '北京':
                _beijing.append(int(row[0]))
            if row[1] == '上海':
                _beijing.append(int(row[0]))

        # 1.5-2万
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` from job WHERE `所属行业` like  '%{}%' AND `_城市` IN ('北京','上海') AND (`_最低工资`+`_最高工资`)/2 >= 15000 AND (`_最低工资`+`_最高工资`)/2 < 20000 GROUP BY `_城市`".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            if row[1] == '北京':
                _beijing.append(int(row[0]))
            if row[1] == '上海':
                _beijing.append(int(row[0]))

        # 1-1.5万
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` from job WHERE `所属行业` like  '%{}%' AND `_城市` IN ('北京','上海') AND (`_最低工资`+`_最高工资`)/2 >= 10000 AND (`_最低工资`+`_最高工资`)/2 < 15000 GROUP BY `_城市`".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            if row[1] == '北京':
                _beijing.append(int(row[0]))
            if row[1] == '上海':
                _beijing.append(int(row[0]))

        # 2-2.5万
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` from job WHERE `所属行业` like  '%{}%' AND `_城市` IN ('北京','上海') AND (`_最低工资`+`_最高工资`)/2 >= 20000 AND (`_最低工资`+`_最高工资`)/2 < 25000 GROUP BY `_城市`".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            if row[1] == '北京':
                _beijing.append(int(row[0]))
            if row[1] == '上海':
                _beijing.append(int(row[0]))

        # 0.8-1.2万
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` from job WHERE `所属行业` like  '%{}%' AND `_城市` IN ('北京','上海') AND (`_最低工资`+`_最高工资`)/2 >= 8000 AND (`_最低工资`+`_最高工资`)/2 < 12000 GROUP BY `_城市`".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            if row[1] == '北京':
                _beijing.append(int(row[0]))
            if row[1] == '上海':
                _beijing.append(int(row[0]))

        data = [{"name": "北京", "value": _beijing}, {"name": "上海", "value": _shanghai}]
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_city_compare finish")

        cache.set('sum_city_compare:' + self.profession, data)
        return data

    # 当前专业职位的经验要求: 前8->前5(太多了显示不全)
    def sum_experience(self):
        ret = cache.get('sum_experience:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_experience start")
        sql = "SELECT SUM(`_招聘人数`) as c,`工作经验` FROM job WHERE `所属行业` like '%{}%' GROUP BY `工作经验` ORDER BY c DESC LIMIT 5".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        data = []
        for row in rows:
            data.append({"name": row[1], "value": int(row[0])})
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_experience finish")

        cache.set('sum_experience:' + self.profession, data)
        return data

    # 当前专业职位的城市占比: 5个
    def sum_first_city(self):
        ret = cache.get('sum_first_city:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_first_city start")
        exist_map = {'北京': 0, '上海': 0, '广州': 0, '深圳': 0, '成都': 0}
        full_map = {'北京': 1, '上海': 1, '广州': 1, '深圳': 1, '成都': 1}

        # 当前行业数量按城市统计
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` FROM job WHERE `所属行业` like  '%{}%' AND `_城市` in ('北京','上海','广州','深圳','成都') GROUP BY `_城市`".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            exist_map[row[1]] = row[0]

        # 按城市统计职位数量
        sql = "SELECT SUM(`_招聘人数`) as c,`_城市` FROM job WHERE `_城市` in ('北京','上海','广州','深圳','成都') GROUP BY `_城市`"
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            full_map[row[1]] = row[0]

        # 比例
        percent_map = {}
        for _city in ['北京', '上海', '广州', '深圳', '成都']:
            percent_map[_city] = (Decimal(exist_map[_city]) / Decimal(full_map[_city])).quantize(Decimal('0.00'),
                                                                                                 rounding=ROUND_HALF_UP) * Decimal(
                "100")

        data = [
            {"name": "北京", "value": float(percent_map['北京']), "value2": 100 - float(percent_map['北京']), "color": "01",
             "radius": ['59%', '70%']},
            {"name": "上海", "value": float(percent_map['上海']), "value2": 100 - float(percent_map['上海']), "color": "02",
             "radius": ['49%', '60%']},
            {"name": "广州", "value": float(percent_map['广州']), "value2": 100 - float(percent_map['广州']), "color": "03",
             "radius": ['39%', '50%']},
            {"name": "深圳", "value": float(percent_map['深圳']), "value2": 100 - float(percent_map['深圳']), "color": "04",
             "radius": ['29%', '40%']},
            {"name": "成都", "value": float(percent_map['成都']), "value2": 100 - float(percent_map['成都']), "color": "05",
             "radius": ['20%', '30%']},
        ]
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "sum_first_city finish")

        cache.set('sum_first_city:' + self.profession, data)
        return data

    # 当前专业职位的平均工资: 5个
    def avg_salary(self):
        ret = cache.get('avg_salary:' + self.profession, default=None)
        if ret is not None:
            return ret

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "avg_salary start")
        sql = "SELECT AVG(`_最低工资`+`_最高工资`)/2 as c,`_城市` FROM job WHERE `所属行业` like '%{}%' AND `_城市` in ('北京','上海','广州','深圳','成都') GROUP BY `_城市`".format(
            self.profession)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        data = []
        for row in rows:
            data.append({'name': row[1], 'value': int(Decimal(row[0]).quantize(Decimal('0'), rounding=ROUND_HALF_UP))})

        # 数字转换汉字
        for tmp in data:
            # 千: 9千8
            if tmp['value'] < 10000:
                tmp['value'] = (Decimal(tmp['value']) / Decimal('1000')).quantize(Decimal('0.0'),
                                                                                  rounding=ROUND_HALF_UP)
                tmp['value'] = str(tmp['value']).replace(".", "千")

            # 万: 1万2
            elif tmp['value'] >= 10000:
                tmp['value'] = (Decimal(tmp['value']) / Decimal('10000')).quantize(Decimal('0.0'),
                                                                                   rounding=ROUND_HALF_UP)
                tmp['value'] = str(tmp['value']).replace(".", "万")

            # 1万0 改为 1万
            if str(tmp['value']).endswith("万0") or str(tmp['value']).endswith("千0"):
                tmp['value'] = tmp['value'][:-1]

        print(time.strftime("%Y-%m-%d %H:%M:%S"), "avg_salary finish")

        cache.set('avg_salary:' + self.profession, data)
        return data


class SourceData(SourceDataDemo):

    def __init__(self, profession=''):
        super().__init__(profession)
        self.title = '职场状况可视化分析'
