import requests
from requests.exceptions import RequestException
import re
from lxml import etree
import chardet
import csv
import pymysql
from time import sleep
def get_data(url):
    def get_html(url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                response.encoding = chardet.detect(response.content).get('encoding')
                html = response.text
                return html
        except RequestException:
            return None


    def main(url):
        db=pymysql.connect(host="localhost",user="root",password="root",db="food") #链接数据库
        cursor = db.cursor()
        items = []
        html = get_html(url)
        url_lists = re.findall('<script type="text/javascript">.*?engine_search_result":(.*),.*?"jobid_count"', html, re.S)
        url_lists = url_lists[0]
        url_lists = eval(url_lists)
        for url in url_lists:
            url = url.get('job_href')
            url = re.sub(r'\\', '', url)
            html = get_html(url)
            item = parse_html(html)
            items.append(item)
        for item in items:
            if isinstance(item,list):
                sql="insert into job(职位名称, 公司名称, 工作地点, 工作经验, 学历, 招聘人数, 发布时间, 公司性质, 公司规模,所属行业, 工资) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8],item[9],item[10])
                cursor.execute(sql)
                db.commit()
            else:
                continue
        db.close()

    def parse_html(html):
        try:
            # 返回xpath对象
            html_xpath = etree.HTML(html)
            # 职位名称
            job_title = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/h1/text()")
            job_title = job_title[0]
            # 公司名称
            company_name = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/p[@class='cname']/a/@title")
            company_name = company_name[0]
            # 工作地点
            info = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/p[contains(@class, 'msg')]/@title")
            info = re.sub('[(xa0)(|)]', '', info[0])
            info = info.split()
            work_place = info[0]
            # 工作经验
            work_year = info[1]
            # 学历
            education = info[2]
            # 招聘人数
            recruit_number = info[3]
            # 发布时间
            release_time = info[4]
            # 公司性质
            company_nature = html_xpath.xpath("//div[@class='tCompany_sidebar']//div[@class='com_tag']/p[1]/@title")
            company_nature = company_nature[0]
            # 公司规模
            company_size = html_xpath.xpath("//div[@class='tCompany_sidebar']//div[@class='com_tag']/p[2]/@title")
            company_size = company_size[0]
            # 所属行业
            industry = html_xpath.xpath("//div[@class='tCompany_sidebar']//div[@class='com_tag']/p[3]/@title")
            industry = industry[0]
            # 工资
            salary = html_xpath.xpath("//div[contains(@class, 'tHeader')]/div[@class='in']/div[@class='cn']/strong/text()")
            salary = salary[0]
            item = [job_title, company_name, work_place, work_year, education, recruit_number, release_time,
                    company_nature, company_size, industry, salary]
            return item
        except:
            pass
    main(url)
for i in range(346,2000):
    url="https://search.51job.com/list/000000,000000,0000,32,9,99,+,2,{}.html".format(i)
    get_data(url)
    print(i,"ok",end=" ")
print("ok")