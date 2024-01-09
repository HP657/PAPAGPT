import psycopg2

class DB:
    def __init__(self, database, user, password):
        self.conn = psycopg2.connect(
        database=database,
        user=user,
        password=password,
    )
        self.cur = self.conn.cursor()

    def execute_query(self, query, params):
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur
    
    def select_user(self, userID):
        return self.execute_query("SELECT * FROM users WHERE user_id = %s;", (userID,)).fetchone()

    def select_user_password(self, userID, password):
        return self.execute_query("SELECT * FROM users WHERE user_id = %s AND user_pw = %s;", (userID, password)).fetchone()

    def insert_user(self, userID, password):
        self.execute_query("INSERT INTO users VALUES (%s, %s);", (userID, password))

    def delete_user(self, userID):
        self.execute_query("DELETE FROM users WHERE user_id = %s;", (userID,))

    def chat(self, userID, input_text, output):
        self.execute_query("INSERT INTO chat_log (user_id, question, answer) VALUES (%s ,%s, %s)",(userID,input_text,output))

    def select_log(self, userID):
        return self.execute_query("SELECT * FROM Chat_Log WHERE user_id = %s ORDER BY timestamp ASC;",(userID,)).fetchall()