import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from common.tools import is_datatime, is_number
from utils.MySQLDB import Connect_DB
from decimal import Decimal, ROUND_HALF_UP

if __name__ == "__main__":
    infos = {
        1: "https://fubon-ebrokerdj.fbs.com.tw/Z/ZH/ZHG/CZHG.djbcd?A=120280",  # 倫敦金價 前日現貨價 (美金)
        2: "https://fubon-ebrokerdj.fbs.com.tw/Z/ZH/ZHG/CZHG.djbcd?A=120270",  # 紐約金價 前日收盤價 (美金)
        3: "https://fubon-ebrokerdj.fbs.com.tw/Z/ZH/ZHG/CZHG.djbcd?A=120250",  # 黃金現貨 中信局售出 (台幣)
    }
    connectDB = Connect_DB()
    connectDB.connection()
    cmd1 = "INSERT INTO kind_data (id, kind_id, kind_date, kind_price) VALUES (%s, %s, %s, %s)"
    cmd2 = "SELECT * FROM kind_data WHERE id = %s"
    for kind_id, url in infos.items():
        user_agent = UserAgent().random
        headers = {'User-Agent': user_agent}
        req = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(req.text, 'lxml')
        element = soup.find('p')
        if element != None:
            text = element.text
            sp = text.split(' ')
            dt = sp[0].split(',')
            price = sp[1].split(',')
            for d, p in zip(dt, price):
                id = d.replace("/", "") + str(kind_id).zfill(2)
                s_p = p.replace('.00', '')
                # i_p = float(s_p)
                i_p = float(Decimal(s_p).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                if is_datatime(d, '%Y/%m/%d') and is_number(p) and is_number(id):
                    params1 = (int(id), kind_id, d, i_p)
                    params2 = (int(id),)
                    result = connectDB.selectOne(cmd2, params2)
                    if (result == None or len(result) == 0):
                        connectDB.execute(cmd1, params1)
                        print('[insert]: ', params1)
                    else:
                        print('[exist]: ', params2)
    connectDB.disconnect()


