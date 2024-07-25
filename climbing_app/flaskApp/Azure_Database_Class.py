import pyodbc

class azureSQLdb:
    def __init__(self, dbms, host, user, password, database):
        self.dbms = dbms
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connect()

    def connect(self):
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.host};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password}"
        )
        self._db = pyodbc.connect(connection_string)
        self._cur = self._db.cursor()

    def sql_do(self, sql, parms=()):
        """Execute an SQL statement"""
        if parms:
            self._cur.execute(sql, parms)
        else:
            self._cur.execute(sql)
        self.commit()
        return self._cur.rowcount

    def sql_query(self, sql, parms=()):
        if parms:
            self._cur.execute(sql, parms)
        else:
            self._cur.execute(sql)
        for row in self._cur:
            yield row

    def commit(self):
        if self.have_db():
            self._db.commit()

    def have_db(self):
        return self._db is not None

    def close(self):
        if self._cur:
            self._cur.close()
        if self._db:
            self._db.close()