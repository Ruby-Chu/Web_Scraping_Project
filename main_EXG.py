import requests
import re
from utils.MySQLDB import Connect_DB

def get_exchange_rate():
    # 年月日格式
    regex = r"(\d{4})(\d{1,2})(\d{1,2})"
    try:
        get_info = requests.get('https://openapi.taifex.com.tw/v1/DailyForeignExchangeRates')
        json_data = get_info.json()
        infos = []
        # 取得最後一筆(最新)
        for info in json_data:
            # print(info)
            DT = info['Date']
            t = re.search(regex, DT)
            if t:
                y = t.group(1)
                m = t.group(2).zfill(2)
                d = t.group(3).zfill(2)
                rmb_rate = round(float(info['RMB/NTD']), 2)
                usd_rate = round(float(info['USD/NTD']), 2)
                # 台幣 default 1
                # infos.append({
                #     "id": "{}{}{}{}".format(y, m, d, str(1).zfill(2)),
                #     "exg_date": "{}/{}/{}".format(y, m, d),
                #     "exg_id": 1,
                #     "exg_number": 1
                # })
                # 美金
                infos.append({
                    "id": int("{}{}{}{}".format(y, m, d, str(2).zfill(2))),
                    "exg_date": "{}-{}-{}".format(y, m, d),
                    "exg_id": 2,
                    "exg_number": usd_rate
                })
                # 人民幣
                infos.append({
                    "id": int("{}{}{}{}".format(y, m, d, str(3).zfill(2))),
                    "exg_date": "{}-{}-{}".format(y, m, d),
                    "exg_id": 3,
                    "exg_number": rmb_rate
                })
        return infos  # DT, usd_rate, rmb_rate
    except Exception as e:
        return []

if __name__ == "__main__":
    infos = get_exchange_rate()
    cmd1 = "INSERT INTO exg_data (id, exg_date, exg_id, exg_number) VALUES (%s, %s, %s, %s)"
    cmd2 = "SELECT * FROM exg_data WHERE id = %s"
    connectDB = Connect_DB()
    connectDB.connection()
    for info in infos:
        params1 = (info['id'], info['exg_date'], info['exg_id'], info['exg_number'])
        params2 = (info['id'],)
        result = connectDB.selectOne(cmd2, params2)
        if (result == None or len(result) == 0):
            connectDB.execute(cmd1, params1)
            print('[insert]: ', info)
        else:
            print('[exist]: ', info)

    connectDB.disconnect()