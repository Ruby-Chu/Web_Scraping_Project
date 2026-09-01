from datetime import datetime, date, timedelta, timezone
import requests
from utils.MySQLDB import Connect_DB
from decimal import Decimal, ROUND_HALF_UP

def process_forex_data(exg_id, api_response):
    infos = []
    infos.clear()
    inner_data = api_response['data']
    currency_name = inner_data['quote']['200009']

    timestamps = inner_data['t']
    closes = inner_data['c']

    # print(f"=== {currency_name} 歷史收盤價 ===")

    # 使用 zip 將時間戳與收盤價一一對應結合
    for ts, close in zip(timestamps, closes):
        # 轉換為 UTC 時間，並格式化為 年-月-日
        dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d')
        y, m, d = dt.split('-')
        price = float(Decimal(close).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) # close
        infos.append({
            "id": int("{}{}{}{}".format(y, m, d, str(exg_id).zfill(2))),
            "exg_date": "{}-{}-{}".format(y, m, d),
            "exg_id": exg_id,
            "exg_number": price # close
        })
        # print(f"日期: {date_str} | 收盤價 'c': {close}")
    return infos

if __name__ == "__main__":
    cmd1 = "INSERT INTO exg_data (id, exg_date, exg_id, exg_number) VALUES (%s, %s, %s, %s)"
    cmd2 = "SELECT * FROM exg_data WHERE id = %s"
    cmd3 = "UPDATE exg_data SET exg_number = %s WHERE id = %s"

    # start
    today_date = date.today()
    today_utc_timestamp = datetime.combine(today_date, datetime.min.time().replace(tzinfo=timezone.utc)).timestamp()

    # end
    days_ago_7 = date.today() - timedelta(days=7)
    timestamp_7_days_ago_local = datetime.combine(days_ago_7, datetime.min.time()).timestamp()

    usd_url = 'https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=D&symbol=FX:USDTWD:FOREX&from={}&to={}&quote=1'.format(str(int(today_utc_timestamp)), str(int(timestamp_7_days_ago_local)))
    rmb_url = 'https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=D&symbol=FX:CNYTWD:FOREX&from={}&to={}&quote=1'.format(str(int(today_utc_timestamp)), str(int(timestamp_7_days_ago_local)))

    exg_info = {
        2: usd_url,
        3: rmb_url
    }

    connectDB = Connect_DB()
    connectDB.connection()

    for exg_id, exg_api in exg_info.items():
        get_info = requests.get(exg_api)
        json_data = get_info.json()
        infos = process_forex_data(exg_id, json_data)
        for info in infos:
            params1 = (info['id'], info['exg_date'], info['exg_id'], info['exg_number'])
            params2 = (info['id'],)
            params3 = (info['exg_number'], info['id'],)
            result = connectDB.selectOne(cmd2, params2)
            if (result == None or len(result) == 0):
                connectDB.execute(cmd1, params1)
                print('[insert]: ', info)
            else:
                if (info['exg_number'] == result[3]):
                    print('[exist]: ', info)
                else:
                    connectDB.execute(cmd3, params3)
                    print('[update]: ', info, '->',result[3])
    connectDB.disconnect()

# import requests
# import re
# from utils.MySQLDB import Connect_DB
# from decimal import Decimal, ROUND_HALF_UP
#
# def get_exchange_rate():
#     # 年月日格式
#     regex = r"(\d{4})(\d{1,2})(\d{1,2})"
#     try:
#         get_info = requests.get('https://openapi.taifex.com.tw/v1/DailyForeignExchangeRates')
#         json_data = get_info.json()
#         infos = []
#         # 取得最後一筆(最新)
#         for info in json_data:
#             # print(info)
#             DT = info['Date']
#             t = re.search(regex, DT)
#             if t:
#                 y = t.group(1)
#                 m = t.group(2).zfill(2)
#                 d = t.group(3).zfill(2)
#                 rmb_rate = float(Decimal(info['RMB/NTD']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) # round(float(info['RMB/NTD']), 2)
#                 usd_rate = float(Decimal(info['USD/NTD']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) # round(float(info['USD/NTD']), 2)
#                 # 台幣 default 1
#                 # infos.append({
#                 #     "id": "{}{}{}{}".format(y, m, d, str(1).zfill(2)),
#                 #     "exg_date": "{}/{}/{}".format(y, m, d),
#                 #     "exg_id": 1,
#                 #     "exg_number": 1
#                 # })
#                 # 美金
#                 infos.append({
#                     "id": int("{}{}{}{}".format(y, m, d, str(2).zfill(2))),
#                     "exg_date": "{}-{}-{}".format(y, m, d),
#                     "exg_id": 2,
#                     "exg_number": usd_rate
#                 })
#                 # 人民幣
#                 infos.append({
#                     "id": int("{}{}{}{}".format(y, m, d, str(3).zfill(2))),
#                     "exg_date": "{}-{}-{}".format(y, m, d),
#                     "exg_id": 3,
#                     "exg_number": rmb_rate
#                 })
#         return infos  # DT, usd_rate, rmb_rate
#     except Exception as e:
#         return []
#
#
# if __name__ == "__main__":
#     # https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=D&symbol=FX:USDTWD:FOREX&from=1788278400&to=1787711635&quote=1
#
#     infos = get_exchange_rate()
#     cmd1 = "INSERT INTO exg_data (id, exg_date, exg_id, exg_number) VALUES (%s, %s, %s, %s)"
#     cmd2 = "SELECT * FROM exg_data WHERE id = %s"
#     connectDB = Connect_DB()
#     connectDB.connection()
#     for info in infos:
#         params1 = (info['id'], info['exg_date'], info['exg_id'], info['exg_number'])
#         params2 = (info['id'],)
#         result = connectDB.selectOne(cmd2, params2)
#         if (result == None or len(result) == 0):
#             connectDB.execute(cmd1, params1)
#             print('[insert]: ', info)
#         else:
#             if (info['exg_number'] == result[3]):
#                 print('[exist]: ', info)
#             else:
#                 print('[update]: ', info, result[3])
#
#     connectDB.disconnect()
