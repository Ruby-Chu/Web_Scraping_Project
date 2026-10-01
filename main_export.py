from utils.MySQLDB import Connect_DB
from datetime import datetime, timedelta, date
import json

if __name__ == "__main__":
    # 選取近365筆
    cmd1 = "SELECT id, date, fighter, warship, officialship, balloon, missile, \
        enter_fighter, missile_date FROM mnd_data order by date desc limit 365"
    # 美金
    cmd2 = "SELECT * FROM exg_data where exg_info_id = 2 order by exg_date desc limit 365"
    # 人民幣
    cmd3 = "SELECT * FROM exg_data where exg_info_id = 3 order by exg_date desc limit 365"
    params = {}
    connectDB = Connect_DB()
    connectDB.connection()
    results1 = connectDB.selectAll(cmd1)
    results2 = connectDB.selectAll(cmd2)
    results3 = connectDB.selectAll(cmd3)
    infos1 = []
    exg_infos = {}
    connectDB.disconnect()
    for r in results1:
        dt = datetime.strftime(r[1], '%Y-%m-%d')
        fighter = r[2]
        warship = r[3]
        officialship = r[4]
        balloon = r[5]
        missile = r[6]
        enter_fighter = r[7]
        missile_date = r[8]
        infos1.append(
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
    exg_infos.update({"exg_2": []})
    for r in results2:
        dt = datetime.strftime(r[1], '%Y-%m-%d')
        exg = r[3]
        exg_infos["exg_2"].append({
            "dt": dt,
            "exg": exg
        })
    exg_infos.update({"exg_3": []})
    for r in results3:
        dt = datetime.strftime(r[1], '%Y-%m-%d')
        exg = r[3]
        exg_infos["exg_3"].append({
            "dt": dt,
            "exg": exg
        })
    with open("C:\\Ruby\\GitHub\\Ruby-Chu.github.io\\data\\mnd_data.json", "w", encoding="utf-8") as f:
        json.dump(
            infos1, f, ensure_ascii=False,  # 中文不轉成 \uXXXX
            indent=2,
            default=str          # date / datetime 等物件可轉成字串
            )
    with open("C:\\Ruby\\GitHub\\Ruby-Chu.github.io\\data\\exg_data.json", "w", encoding="utf-8") as f:
        json.dump(
            exg_infos, f, ensure_ascii=False,  # 中文不轉成 \uXXXX
            indent=2,
            default=str          # date / datetime 等物件可轉成字串
            )
