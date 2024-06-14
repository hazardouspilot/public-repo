#this code was written by Bill Weinman and procured via the exercise files for LinkedIn Learning course 'Using SQL With Python'

try:
    import mysql.connector as mysql
    have_mysql = True
except ImportError:
    mysql = None
    have_mysql = False

class BWErr(Exception):
    """Simple Error class"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class BWDB:
    def __init__(self, **kwargs):
        self._db = None
        self._cur = None
        self._dbms = None
        self._database = None
        self._table = None
        self._column_names = None

        # populate simple parameters first
        if "user" in kwargs:
            self._user = kwargs["user"]
        else:
            self._user = None

        if "password" in kwargs:
            self._password = kwargs["password"]
        else:
            self._password = None

        if "host" in kwargs:
            self._host = kwargs["host"]
        else:
            self._host = None

        # populate properties
        if "dbms" in kwargs:
            self.dbms = kwargs["dbms"]

        if "database" in kwargs:
            self.database = kwargs["database"]

        if "table" in kwargs:
            self.table = kwargs["table"]

    # property setters/getters
    def get_dbms(self):
        return self._dbms

    def set_dbms(self, dbms_str):
        if dbms_str == "mysql":
            if have_mysql:
                self._dbms = dbms_str
            else:
                raise BWErr("mysql not available.. ?")
        else:
            raise BWErr("set_dbms: invalid dbms_str specified")

    def get_database(self):
        return self._database

    def set_database(self, database):
        self._database = database
        if self._cur:
            self._cur.close()
        if self._db:
            self._db.close()

        self._database = database
        if self._dbms == "mysql":
            self._db = mysql.connect(
                user=self._user,
                password=self._password,
                host=self._host,
                database=self._database,
            )
            if self._db is None:
                raise BWErr("set_database: failed to connect to mysql")
            else:
                self._cur = self._db.cursor(prepared=True)
        else:
            raise BWErr("set_database: unknown _dbms")

    def get_cursor(self):
        return self._cur

    def set_table(self, table):
        self._table = self.sanitize_string(table)
        self.column_names()

    def get_table(self):
        return self._table

    # properties
    dbms = property(fget=get_dbms, fset=set_dbms)
    database = property(fget=get_database, fset=set_database)
    table = property(fget=get_table, fset=set_table)
    cursor = property(fget=get_cursor)

    # sql methods =====
    def sql_do_nocommit(self, sql, parms=()):
        """Execute an SQL statement"""
        self._cur.execute(sql, parms)
        return self._cur.rowcount

    def sql_do(self, sql, parms=()):
        """Execute an SQL statement"""
        self._cur.execute(sql, parms)
        self.commit()
        return self._cur.rowcount

    def sql_do_many_nocommit(self, sql, parms=()):
        """Execute an SQL statement over set of data"""
        self._cur.executemany(sql, parms)
        return self._cur.rowcount

    def sql_do_many(self, sql, parms=()):
        """Execute an SQL statement over set of data"""
        self._cur.executemany(sql, parms)
        self.commit()
        return self._cur.rowcount

    def sql_query(self, sql, parms=()):
        self._cur.execute(sql, parms)
        for row in self._cur:
            yield row

    def sql_query_row(self, sql, parms=()):
        self._cur.execute(sql, parms)
        row = self._cur.fetchone()
        self._cur.fetchall()
        return row

    def sql_query_value(self, sql, parms=()):
        return self.sql_query_row(sql, parms)[0]

    # crud methods =====
    def column_names(self):
        """Get column names"""
        if self._column_names is not None:
            return self._column_names

        if self._dbms == "mysql":
            self._cur.execute(f"SELECT * FROM {self._table} LIMIT 1")
            self._cur.fetchall()
            self._column_names = self._cur.column_names
        else:
            raise BWErr("column_names: unknown _dbms")

        if len(self._column_names) < 1:
            self._column_names = None
            raise BWErr("colum_names: empty list")
        else:
            return self._column_names

    def add_row_nocommit(self, parms=()):
        colnames = self.column_names()
        numnames = len(colnames)
        if "id" in colnames:
            numnames -= 1
        names_str = self.sql_colnames_string(colnames)
        values_str = self.sql_values_string(numnames)
        sql = f"INSERT INTO {self._table} ({names_str}) VALUES ({values_str})"
        return self.sql_do_nocommit(sql, parms)

    def add_row(self, parms=()):
        r = self.add_row_nocommit(parms)
        self.commit()
        return r

    def update_row_nocommit(self, row_id, dict_rec):
        """Update row id with data in dict"""
        if "id" in dict_rec.keys():  # don't update id column
            del dict_rec["id"]

        keys = sorted(dict_rec.keys())  # get keys and values
        values = [dict_rec[v] for v in keys]
        update_string = self.sql_update_string(keys)
        sql = f"UPDATE {self._table} SET {update_string} WHERE id = ?"
        values.append(row_id)
        return self.sql_do_nocommit(sql, values)

    def update_row(self, row_id, dict_rec):
        r = self.update_row_nocommit(row_id, dict_rec)
        self.commit()
        return r

    def find_row(self, colname, value):
        """Find the first match and returns id or None"""
        colname = self.sanitize_string(colname)  # sanitize params
        sql = f"SELECT * FROM {self._table} WHERE {colname} LIKE ?"
        row = self.sql_query_row(sql, (value,))
        if row:
            return row[0]
        else:
            return None

    def find_rows(self, colname, value):
        """Find the first match and returns id or empty list"""
        colname = self.sanitize_string(colname)  # sanitize params
        sql = f"SELECT * FROM {self._table} WHERE {colname} LIKE ?"
        row_ids = []
        for row in self.sql_query(sql, (value,)):
            row_ids.append(row[0])
        return row_ids

    # Utilities =====

    @staticmethod
    def version():
        return __version__

    @staticmethod
    def sanitize_string(s):
        """Remove nefarious characters from a string"""
        charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-.% "
        san_string = ""
        for i in range(0, len(s)):
            if s[i] in charset:
                san_string += s[i]
            else:
                san_string += "_"
        return san_string

    @staticmethod
    def sql_colnames_string(colnames):
        names_str = ","
        if colnames[0] == "id":
            colnames = colnames[1:]
        return names_str.join(colnames)

    @staticmethod
    def sql_values_string(num):
        s = "?," * num
        return s[0:-1]

    @staticmethod
    def sql_update_string(colnames):
        update_string = ","
        for i in range(len(colnames)):
            colnames[i] += "=?"
        return update_string.join(colnames)

    def have_db(self):
        if self._db is None:
            return False
        else:
            return True

    def lastrowid(self):
        return self._cur.lastrowid

    def begin_transaction(self):
        if self.have_db():
            if self._database == "mysql":
                self.sql_do("START TRANSACTION")

    def commit(self):
        if self.have_db():
            self._db.commit()

    def disconnect(self):
        if self.have_cursor():
            self._cur.close()
        if self.have_db():
            self._db.close()
        self._cur = None
        self._db = None
        self._column_names = None

    # destructor
    def __del__(self):
        try:
            self.disconnect()
        except:
            # above code causing "ReferenceError: weakly-referenced object no longer exists"
            pass
