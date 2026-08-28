import mysql.connector


class Connect_DB():
    def __init__(self):
        try:
            self.host="localhost"
            self.user = "root"
            self.password = "123456"
            self.db = "db"
            self.dt_format = 'yyyy/mm/dd'
            self.connect = None
            self.cursor = None
        except Exception as e:
            print(e)

    def connection(self):
        self.connect = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.db
            )
        self.cursor = self.connect.cursor()

    def disconnect(self):
        if (self.cursor != None):
            self.cursor.close()
        if (self.connect != None):
            self.connect.close()

    def selectOne(self, cmd, params):
        self.cursor.execute(cmd, params)
        result = self.cursor.fetchone()
        return result

    def execute(self, cmd, params):
        self.cursor.execute(cmd, params)
        self.connect.commit()
