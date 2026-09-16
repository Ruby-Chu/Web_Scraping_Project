from common.chrome_driver import slider_window, sleep_random_time, get_chrome_driver
from selenium.webdriver.common.by import By
import re
from datetime import datetime, timedelta, date
from utils.MySQLDB import Connect_DB

if __name__ == "__main__":
    main_url = "https://www.mnd.gov.tw/news/plaactlist"
    log_message, driver = get_chrome_driver(show=False)
    cmd1 = "INSERT INTO mnd_data (id, date, url, fighter, warship, officialship, \
        balloon, missile, enter_fighter, missile_date, content) VALUES (%s, %s, %s, %s, \
            %s, %s, %s, %s, %s, %s, %s)"
    cmd2 = "SELECT * FROM mnd_data WHERE id = %s"
    # cmd3 = "UPDATE mnd_data SET exg_rate = %s WHERE id = %s"
    connectDB = Connect_DB()
    connectDB.connection()
    for page in range(1, 6):
        if page != 1:
            page_url = "{}/{}".format(main_url, page)
        else:
            page_url = main_url
        print(page_url)
        driver.get(page_url)
        driver.implicitly_wait(10)
        sleep_random_time(t1=1, t2=2)
        slider_window(driver)
        class_elements = driver.find_elements(By.CLASS_NAME, 'news_list')
        urls = []
        for class_element in class_elements:
            try:
                url = class_element.get_attribute('href')
                urls.append(url)
            except:
                pass
        for url in urls:
            driver.delete_all_cookies()
            driver.get(url)
            driver.implicitly_wait(10)
            sleep_random_time(t1=1, t2=2)
            slider_window(driver)
            content = driver.find_element(By.CLASS_NAME, 'pagewrap1')
            text = content.text
            match = re.search(r"(\d{1,3}).(\d{1,2}).(\d{1,2})", text)
            if match:
                year, month, day = match.groups()
                year = int(year) + 1911
                date_string = f"{year}-{month}-{day}"
                # date_object = datetime.strptime(date_string, "%Y-%m-%d")
                # id
                id = "{}{}{}".format(year, month.zfill(2), day.zfill(2))
                # 共機
                fighter_pattern = re.findall(r'共機(\d+)架次', text)
                fighter_number = 0
                if fighter_pattern:
                    fighter_number = fighter_pattern[0]
                # 逾越共機架次
                enter_fighter_pattern = re.findall(r'(?:逾越|進入).*?(\d+)架', text)
                enter_fighter_number = 0
                if enter_fighter_pattern:
                    enter_fighter_number = enter_fighter_pattern[0]
                # 共艦
                warship_pattern = re.findall(r'共艦(\d+)艘', text)
                warship_number = 0
                if warship_pattern:
                    warship_number = warship_pattern[0]
                # 公務船
                officialship_pattern = re.findall(r'公務船(\d+)艘', text)
                officialship_number = 0
                if officialship_pattern:
                    officialship_number = officialship_pattern[0]
                # 氣球
                balloon_pattern = re.findall(r'中共空飄氣球計偵獲(\d+)顆', text)
                balloon_number = 0
                if balloon_pattern:
                    balloon_number = balloon_pattern[0]
                # 預告飛彈
                note_pattern = r'臺海周邊海、空域活動_?([2-9]\d*)'
                missile_number = 0
                for number in re.findall(note_pattern, text):
                    missile_number = 1
                    print("~~~ Note: {} ~~~".format(id))
                params1 = (id, date_string, url, fighter_number, warship_number, officialship_number, \
                           balloon_number, missile_number, enter_fighter_number, " ", text, )
                params2 = (id, )
                result = connectDB.selectOne(cmd2, params2)
                if (result == None or len(result) == 0):
                    connectDB.execute(cmd1, params1)
                    print(f'[insert] {id} new')
                    print("{}\n共機{}架次(逾越共{}架次)\n共艦{}艘\n公務船{}艘\n氣球{}顆\n飛彈{}顆\n====END====".format(\
                                        id, fighter_number, enter_fighter_number, \
                                        warship_number, officialship_number, balloon_number, missile_number))
                else:
                    print(f'[exist] {id}')
                    print("{}\n共機{}架次(逾越共{}架次)\n共艦{}艘\n公務船{}艘\n氣球{}顆\n飛彈{}顆\n====END====".format(\
                                                            id, fighter_number, enter_fighter_number, \
                                                            warship_number, officialship_number, balloon_number, missile_number))
    connectDB.disconnect()
    driver.quit()