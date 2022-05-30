from flask import Flask, render_template, request, current_app
from data import *
import json
import uuid
import mysql.connector
from conf import *
from flask import jsonify
import time

db = mysql.connector.connect(**DB_CONFIG)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 支持JSON中文返回

# 全部专业词汇
words = []


@app.route('/')
def index():
    return current_app.send_static_file('login.html')


@app.route('/register')
def register_page():
    return current_app.send_static_file('register.html')


@app.route('/home')
def home():
    # 读取HTTP消息头获取token
    token = request.args.get("token", default="")
    if len(token) == 0:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "缺少token令牌")
        return index()

    # 查询专业
    cur = db.cursor()
    cur.execute("select `专业` from user where `令牌`='{}' limit 1".format(token))
    row = cur.fetchone()
    if row is None or row[0] is None or len(row[0]) == 0:
        print(time.strftime("%Y-%m-%d %H:%M:%S"), "令牌token无效")
        return index()

    profession = row[0]
    data = SourceData(profession)
    return render_template('index.html', form=data, title=data.title)


@app.route('/api/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    profession = request.form['profession']  # 专业
    if len(profession) == 0:
        return jsonify({"code": 1, "msg": "必须填写专业"})

    # 用户认证
    sql = "select count(1) from user where 账号='{}' and 密码='{}'".format(username, password)
    cur = db.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    if row[0] == 0:
        return jsonify({"code": 1, "msg": "账号或密码错误"})

    # 存储令牌
    token = str(uuid.uuid4()).replace("-", "")[:6]
    cur.execute("update user set 令牌='{}',专业='{}' where 账号='{}'".format(token, profession, username))
    db.commit()

    return jsonify({"code": 0, "msg": "登录成功", "token": token})


@app.route('/api/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    if password is None or len(username) == 0 or password is None or len(password) < 6:
        return jsonify({"code": 1, "msg": "账号不能为空,密码至少6位"})

    # 账号校验
    sql = "select count(1) from user where 账号='{}'".format(username)
    cur = db.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    if row[0] > 0:
        return jsonify({"code": 1, "msg": "账号已存在,请重新输入"})

    # 存储账号
    sql = "INSERT INTO user VALUES ('{}','{}','','')".format(username, password)
    cur.execute(sql)
    db.commit()

    return jsonify({"code": 0, "msg": "注册成功"})


@app.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('images/favicon.ico')


@app.route('/api/complete', methods=['GET'])
def complete():
    # profession = request.args.get('keywords', default='') # 搜索参数
    global words  # 直接返回全量数据给前端组件自己筛选
    return jsonify({"code": 200, "msg": "success", "data": words})


# 初始化自动补全词汇: 2s
def init_words():
    print(time.strftime("%Y-%m-%d %H:%M:%S"), "init_words start")

    global words
    if len(words) > 0:
        return
    cur = db.cursor()
    cur.execute("SELECT DISTINCT `所属行业` from job")
    rows = cur.fetchall()
    word_set = set()
    for row in rows:
        # / , ，、（ ） ( )
        row = str(row).replace(",", "/").replace("，", "/").replace("、", "/").replace("（", "/") \
            .replace("）", "/").replace("(", "/").replace(")", "/").replace("'", "/")
        if '/' in row:
            array = row.split("/")
            for word in array:
                if len(word) == 0:
                    continue
                word_set.add(word)
        else:
            if len(word) == 0:
                continue
            word_set.add(row)

    print(time.strftime("%Y-%m-%d %H:%M:%S"), "init_words finish")
    words = list(word_set)
    words.sort()  # 排序


if __name__ == "__main__":
    # 自动补全词汇
    init_words()

    # 启动服务器
    print("启动成功: http://127.0.0.1:5000/")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
