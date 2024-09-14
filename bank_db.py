import sqlite3
import random

class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            balance REAL,
            FOREIGN KEY (id) REFERENCES users(id)
        )
        """)
        self.conn.commit()

    def generate_unique_id(self):
        while True:
            new_id = f"{random.randint(100000000, 999999999)}"
            self.cur.execute("SELECT 1 FROM users WHERE id = ?", (new_id,))
            if self.cur.fetchone() is None:
                return new_id

    def register(self, username, password):
        try:
            user_id = self.generate_unique_id()
            self.cur.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (user_id, username, password))
            self.cur.execute("INSERT INTO accounts (id, balance) VALUES (?, ?)", (user_id, 0))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists.")

    def login(self, username, password):
        self.cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        row = self.cur.fetchone()
        if row and row[1] == password:
            return row[0]

    def get_balance(self, user_id):
        self.cur.execute("SELECT balance FROM accounts WHERE id = ?", (user_id,))
        row = self.cur.fetchone()
        return row[0]

    def withdraw(self, user_id, amount):
        try:
            # Check that the account has enough funds
            self.cur.execute("SELECT balance FROM accounts WHERE id = ?", (user_id,))
            row = self.cur.fetchone()
            if row[0] < amount:
                raise ValueError("Insufficient funds.")
            
            # Perform the withdrawal
            self.cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, user_id))
            self.conn.commit()

            # Return the updated balance
            self.cur.execute("SELECT balance FROM accounts WHERE id = ?", (user_id,))
            updated_row = self.cur.fetchone()
            return updated_row[0] if updated_row else None
        
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def deposit(self, user_id, amount):
        self.cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, user_id))
        self.conn.commit()

    def transfer(self, sender_id, receiver_id, amount):
        try:
            # Check that the sending account has enough funds
            self.cur.execute("SELECT balance FROM accounts WHERE id = ?", (sender_id,))
            row = self.cur.fetchone()
            if row[0] < amount:
                raise ValueError("Insufficient funds.")

            # Check that the receiving account exists
            self.cur.execute("SELECT 1 FROM accounts WHERE id = ?", (receiver_id,))
            if not self.cur.fetchone():
                raise ValueError("Receiving account not found.")

            # Perform the transfer
            self.cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, sender_id))
            self.cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, receiver_id))
            self.conn.commit()

            # Return the receiver's username
            self.cur.execute("SELECT username FROM users WHERE id = ?", (receiver_id,))
            receiver_username = self.cur.fetchone()
            return receiver_username[0] if receiver_username else None
        
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def __del__(self):
        self.conn.close()