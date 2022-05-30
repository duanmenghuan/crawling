import mysql.connector
import time
from conf import *
from decimal import Decimal, ROUND_HALF_UP

db = mysql.connector.connect(**DB_CONFIG)


def update_database():
    print(time.strftime("%Y-%m-%d %H:%M:%S"), "开始生成SQL文件")

    # 写入SQL
    file = open("update.sql", mode="w", encoding="utf-8")

    # 修正数据
    cur = db.cursor()
    # sql= "SELECT _ID,`招聘人数`,`工资`,`所属行业`,`工作地点` from job WHERE `_招聘人数`=-1 OR `_平均工资`=-1 OR `_城市` is NULL OR `_行业` is NULL"
    sql = "SELECT _ID,`招聘人数`,`工资`,`所属行业`,`工作地点`,`职位名称` from job"
    cur.execute(sql)
    rows = cur.fetchall()
    count = 0
    for row in rows:
        _ID = row[0]
        招聘人数 = row[1]
        工资 = row[2]
        所属行业 = row[3]
        工作地点 = row[4]
        职位名称 = row[5]

        # 提取招聘人数
        users = 1  # 3-26发布 这种默认就是1人吧
        if "招" in 招聘人数:
            users = 招聘人数.replace("招", "").replace("人", "").replace("若干", "2")
        _招聘人数 = int(users)
        # print(_招聘人数)

        # 提取工资: 万/月，千/月，万/年
        _最低工资 = Decimal("0")
        _最高工资 = Decimal("0")
        if "万/月" in 工资:  # 1.2-1.6万/月 -> 14000
            _工资 = 工资.replace("万/月", "")
            _最低工资 = Decimal(_工资.split("-")[0]) * Decimal("10000").quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            _最高工资 = Decimal(_工资.split("-")[1]) * Decimal("10000").quantize(Decimal('0'), rounding=ROUND_HALF_UP)
        if "千/月" in 工资:  # 7-9千/月 -> 8000
            _工资 = 工资.replace("千/月", "")
            _最低工资 = Decimal(_工资.split("-")[0]) * Decimal("1000").quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            _最高工资 = Decimal(_工资.split("-")[1]) * Decimal("1000").quantize(Decimal('0'), rounding=ROUND_HALF_UP)
        if "万/年" in 工资:  # 8-20万/年 -> 14万/年 -> 14/12万/月
            _工资 = 工资.replace("万/年", "")
            _最低工资 = Decimal(_工资.split("-")[0]) * Decimal("10000") / Decimal("12").quantize(Decimal('0'),
                                                                                           rounding=ROUND_HALF_UP)
            _最高工资 = Decimal(_工资.split("-")[1]) * Decimal("10000") / Decimal("12").quantize(Decimal('0'),
                                                                                           rounding=ROUND_HALF_UP)
        # print(float(_最低工资))
        # print(float(_最高工资))

        # 提取行业: 房地产,物业管理/商业中心
        _行业 = 所属行业
        if "," in _行业:
            array = _行业.split(",")
            first = array[0]
            _行业 = first
            if "/" in first:
                _行业 = first.split('/')[0]
        if "/" in _行业:
            _行业 = _行业.split('/')[0]
        if "(" in _行业:
            _行业 = _行业.split('(')[0]
        # print(_行业)

        # 提取城市: 上海-金山区
        _城市 = 工作地点
        if '-' in 工作地点:
            _城市 = 工作地点.split("-")[0]
        # print(_城市)

        # 提取职位
        _职位 = 职位名称
        if ' ' in _职位:
            _职位 = _职位.split(" ")[0]
        if '（' in _职位:
            _职位 = _职位.split("（")[0]
        if '(' in _职位:
            _职位 = _职位.split("(")[0]
        if '/' in _职位:
            _职位 = _职位.split("/")[0]
        if '-' in _职位:
            _职位 = _职位.split("-")[0]
        if '.' in _职位:
            _职位 = _职位.split(".")[0]
        if '+' in _职位:
            _职位 = _职位.split("+")[0]
        # print(_职位)

        update = "UPDATE job SET `_最低工资`='{}',`_最高工资`='{}',`_招聘人数`='{}',`_行业`='{}',`_城市`='{}',`_职位`='{}' where _ID='{}';".format(
            _最低工资, _最高工资, _招聘人数, _行业, _城市, _职位, _ID)
        print("数据升级:" + update)

        file.write(update + "\n")
        count = count + 1

    cur.close()
    db.close()
    file.close()
    print(time.strftime("%Y-%m-%d %H:%M:%S"), "总计生成SQL:{}条".format(count))


if __name__ == "__main__":
    update_database()
    print("SQL修复脚本已生成,请在数据库中执行SQL")
