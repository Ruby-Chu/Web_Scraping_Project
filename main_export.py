from utils.MySQLDB import Connect_DB
from datetime import datetime, timedelta, date
import json

if __name__ == "__main__":
    # 選取近7筆
    cmd = "SELECT id, date, fighter, warship, officialship, balloon, missile, \
        enter_fighter, missile_date FROM mnd_data order by date desc limit 7"
    params = {}
    connectDB = Connect_DB()
    connectDB.connection()
    results = connectDB.selectAll(cmd)
    infos = []
    connectDB.disconnect()
    for r in results:
        dt = datetime.strftime(r[1], '%Y-%m-%d')
        fighter = r[2]
        warship = r[3]
        officialship = r[4]
        balloon = r[5]
        missile = r[6]
        enter_fighter = r[7]
        missile_date = r[8]
        infos.append(
            {
                "dt": dt,
                "fighter": fighter,
                "enter_fighter": enter_fighter,
                "warship": warship,
                "officialship": officialship,
                "balloon": balloon,
                "missile": missile,
                "missile_date": missile_date
            }
        )
    with open("mnd_data.json", "w", encoding="utf-8") as f:
        json.dump(
            infos, f, ensure_ascii=False,  # 中文不轉成 \uXXXX
            indent=2,
            default=str          # date / datetime 等物件可轉成字串
            )
