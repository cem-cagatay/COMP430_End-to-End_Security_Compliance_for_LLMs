import mysql.connector
from typing import Any, List, Tuple, Optional

class MySQLDatabase:
    """
    Single MySQL DB for both your RBAC user store and your toy banking data.
    """
    def __init__(
        self,
        host: str = "localhost",
        user: str = "root",
        password: str = "",
        database: str = "llmsec"
    ):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self._init_schema()

    def _init_schema(self):
        c = self.conn.cursor()
        # users table for RBAC
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            role VARCHAR(50)
        )""")
        # Employees table
        c.execute("""
        CREATE TABLE IF NOT EXISTS Employees (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            salary DECIMAL(10,2),
            ssn VARCHAR(20),
            role VARCHAR(50)
        )""")
        # Clients table
        c.execute("""
        CREATE TABLE IF NOT EXISTS Clients (
            id INT PRIMARY KEY,
            credit_score INT,
            transactions TEXT
        )""")
        self.conn.commit()

    def seed_sample_data(self):
        c = self.conn.cursor()
        # seed Employees
        c.execute("SELECT COUNT(*) FROM Employees")
        if c.fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO Employees (id, name, salary, ssn, role) VALUES (%s,%s,%s,%s,%s)",
                [
                    (1, "Alice", 90000.00, "123-45-6789", "Manager"),
                    (2, "Bob",   50000.00, "987-65-4321", "Teller"),
                ]
            )
        # seed Clients
        c.execute("SELECT COUNT(*) FROM Clients")
        if c.fetchone()[0] == 0:
            c.executemany(
                "INSERT INTO Clients (id, credit_score, transactions) VALUES (%s,%s,%s)",
                [
                    (1, 720, "['txn1','txn2']"),
                    (2, 580, "['txnA','txnB']"),
                ]
            )
        self.conn.commit()

    def get_user_role(self, user_id: int) -> Optional[str]:
        c = self.conn.cursor()
        c.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        row = c.fetchone()
        return row[0] if row else None

    def query(
        self,
        table: str,
        fields: List[str],
        where: str = "",
        params: Tuple[Any, ...] = ()
    ) -> List[Tuple[Any,...]]:
        cols = ", ".join(fields)
        sql = f"SELECT {cols} FROM {table}"
        if where:
            sql += " WHERE " + where
        c = self.conn.cursor()
        c.execute(sql, params)
        return c.fetchall()

    def close(self):
        self.conn.close()