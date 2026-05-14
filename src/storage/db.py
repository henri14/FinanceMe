import sqlite3

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        self.conn.commit()

    def save_message(self, role, content):
        self.conn.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
        self.conn.commit()

    def get_last_turns(self, n=10):
        cursor = self.conn.execute('SELECT role, content FROM messages ORDER BY id DESC LIMIT ?', (n,))
        rows = cursor.fetchall()
        return list(reversed(rows))  # oldest first