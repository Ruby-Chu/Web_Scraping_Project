import pandas as pd
import os
from utils.MySQLDB import Connect_DB
from decimal import Decimal, ROUND_HALF_UP

if __name__ == "__main__":
    regex = r"(\d{4})(\d{1,2})(\d{1,2})"
    exg_file = {
        "USD": {"EXG_ID": 2, "file": "USDTWD_history.csv"},
        "CNY": {"EXG_ID": 3, "file": "CNYTWD_history.csv"}
    }
    infos = []
    for key, val in exg_file.items():
        exg_info_id = val["EXG_ID"]
        file_path = val["file"]
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df.drop('Open', inplace=True, axis=1)
            df.drop('High', inplace=True, axis=1)
            df.drop('Low', inplace=True, axis=1)
            df.drop('Change', inplace=True, axis=1)
            df.drop('Change%', inplace=True, axis=1)
            for index, row in df.iterrows():
                dt = row['Date']
                rp = dt.replace("/", "")
                rate = round(row['Close'], 2)
                rate = float(Decimal(row['Close']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                # rate = float(row['Close'])
                infos.append({
                    "id": int("{}{}".format(rp, str(exg_info_id).zfill(2))),
                    "exg_date": dt.replace("/", "-"),
                    "exg_info_id": exg_info_id,
                    "exg_rate": rate
                })
    cmd1 = "INSERT INTO exg_data (id, exg_date, exg_info_id, exg_rate) VALUES (%s, %s, %s, %s)"
    cmd2 = "SELECT * FROM exg_data WHERE id = %s"
    connectDB = Connect_DB()
    connectDB.connection()
    for info in infos:
        params1 = (info['id'], info['exg_date'], info['exg_info_id'], info['exg_rate'])
        params2 = (info['id'],)
        result = connectDB.selectOne(cmd2, params2)
        if (result == None or len(result) == 0):
            connectDB.execute(cmd1, params1)
            print('[insert]: ', info)
        else:
            print('[exist]: ', info)
    connectDB.disconnect()
