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
        #self._init_schema()


    def get_user_role(self, user_id: int) -> Optional[str]:
        c = self.conn.cursor()
        c.execute("SELECT role FROM Employees WHERE id = %s", (user_id,))
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
    
    def get_fields_for_table(self, table_name: str) -> List[str]:
        query = f"DESCRIBE {table_name};"
        with self.conn.cursor() as cursor:  # ← fix: use self.conn instead of self.connection
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]

    def close(self):
        self.conn.close()