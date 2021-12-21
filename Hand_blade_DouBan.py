import requests
import re
import csv
from time import sleep
import sqlite3

headers = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
}
obj = re.compile(r'ic_play_web@2x.png"/>(?P<film_name>.*?)</a>.*?rating_nums">(?P<rating>.*?)</span>'
                 r'.*?类型: (?P<kind>.*?)<br />.*?【.*?】(?P<time>.*?)开画.*?累计票房(?P<total_price>.*?)元', re.S)

obj_menu = re.compile(r'<br/>[内內]地票房年度[总總]排行：(?P<year>.*?)年(电影|電影) .*?">(?P<domain_pre>.*?)<wbr/>'
                      r'(?P<domain_suffix>.*?)(<wbr/>|</a>)', re.S)

conn = sqlite3.connect("film_info.db")
c = conn.cursor()

def bug_catch(file_name,url):
    table_name = "film_info_" + file_name
    # 创建数据表
    c.execute('''
                CREATE TABLE if not exists %s (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 film_name TEXT NOT NULL,
                                 rating TEXT,
                                 kind TEXT,
                                 time TEXT,
                                 total_price TEXT)
            ''' % table_name)
    conn.commit()
    f = open(file_name+".csv", "w")
    csvwriter = csv.writer(f)
    for j in range(0, 6):
        new_url = url + "?start=" + str(25 * j)
        print("正在手刃 "+new_url)
        resp = requests.get(new_url, headers=headers)
        page_content = resp.text
        content = obj.finditer(page_content)

        for i in content:
            dic = i.groupdict()
            dic['film_name'] = dic['film_name'].strip()
            dic['rating'] = dic['rating'].strip()
            dic['kind'] = dic['kind'].strip()
            dic['time'] = dic['time'].strip()
            dic['total_price'] = dic['total_price'].strip()
            csvwriter.writerow(dic.values())

            sql = '''INSERT INTO %s (film_name,rating,kind,time,total_price) 
                    values('%s','%s','%s','%s','%s')''' % (table_name,dic['film_name'],dic['rating'],
                                                           dic['kind'],dic['time'],dic['total_price'])
            c.execute(sql)
            conn.commit()

        sleep(2)
        resp.close()
    f.close()
    print(file_name,"年数据手刃完毕,已导出至",file_name,".csv和数据库film_info.db的表",table_name)

def main():
    print("请稍等......")

    resp_content = requests.get("https://www.douban.com/doulist/135651096/",headers=headers).text
    content = obj_menu.finditer(resp_content)
    for it in content:
        print("读取到数据"+it.group("year")+" : "+it.group("domain_pre") + it.group("domain_suffix"))
        bug_catch(it.group("year"),it.group("domain_pre") + it.group("domain_suffix"))
    bug_catch("2021","https://www.douban.com/doulist/135651096/")


    # bug_catch("2021","https://www.douban.com/doulist/135651096/")
    # bug_catch("2020","https://www.douban.com/doulist/123308712/")
    # bug_catch("2019","https://www.douban.com/doulist/111687014/")
    # bug_catch("2018","https://www.douban.com/doulist/46436333/")
    # bug_catch("2017","https://www.douban.com/doulist/45837913/")
    # bug_catch("2016","https://www.douban.com/doulist/42975662/")
    # bug_catch("2015","https://www.douban.com/doulist/37815319/")
    # bug_catch("2014","https://www.douban.com/doulist/3401345/")
    # bug_catch("2013","https://www.douban.com/doulist/1765813/")
    # bug_catch("2012","https://www.douban.com/doulist/943009/")
    # bug_catch("2011","https://www.douban.com/doulist/665041/")
    # bug_catch("2010","https://www.douban.com/doulist/226207/")
    # bug_catch("2009","https://www.douban.com/doulist/226734/")
    conn.close()

if __name__ == "__main__":
    main()
