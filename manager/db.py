import sqlite3
from . import const 


class db_instance():

    __instance = None 

    @staticmethod
    def get_instance():

        if db_instance.__instance:

            return db_instance.__instance

        db_instance.__instance = db_instance()

        return db_instance.__instance

    def __init__(self) -> None:
        
        if self.__instance:
            raise Exception("this class is a singleton")

        self.connection = get_connection(const.DATABASE_PATH)
        self.cursor = self.connection.cursor()

        create_tables(self.cursor, self.connection)

    def close(self):

        self.connection.commit()
        self.cursor.close()
        self.connection.close()



def get_connection(database_path : str, foreign_key_checks=True):
    
    conn = sqlite3.connect(database_path)

    if foreign_key_checks:
    
        conn.execute('pragma foreign_keys = ON')

    return conn


def create_tables(cursor, connection=None):

    cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_hash" (
        "hash_id" INTEGER PRIMARY KEY NOT NULL,
        "SHA256" BLOB UNIQUE,
        "arg_id" INTEGER, 
        "MIME" VARCHAR,
        FOREIGN KEY(arg_id) REFERENCES tbl_args(arg_id) ON DELETE CASCADE
    );
    """)
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_url" (
        "url_id" INTEGER PRIMARY KEY NOT NULL,
        "url" VARCHAR UNIQUE,
        "downloaded" INTEGER
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_hash_url" (
        "hash_id" INTEGER,
        "url_id" INTEGER,
        FOREIGN KEY(hash_id) REFERENCES tbl_hash(hash_id) ON DELETE CASCADE
        FOREIGN KEY(url_id) REFERENCES tbl_url(url_id) ON DELETE CASCADE
        PRIMARY KEY(hash_id, url_id)
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_hash_filename" (
        "hash_id" INTEGER,
        "filename" VARCHAR,
        FOREIGN KEY(hash_id) REFERENCES tbl_hash(hash_id) ON DELETE CASCADE
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS "tbl_args" (
        "arg_id" INTEGER PRIMARY KEY NOT NULL,
        "args" VARCHAR UNIQUE
    );""")

    if connection:
        connection.commit()
    

def add_args(args):

    inst = db_instance.get_instance()

    try:

        inst.cursor.execute("INSERT INTO tbl_args VALUES (NULL, ?)", (args,))

        inst.connection.commit()
        
        return inst.cursor.lastrowid

    except sqlite3.IntegrityError as e: 

        inst.cursor.execute("SELECT arg_id FROM tbl_args WHERE args=?", (args,))
        row = inst.cursor.fetchone()

        if row:

            return row[0]

        raise e

def add_hash(sha256, ARGS, mime):

    inst = db_instance.get_instance()

    arg_id = add_args(ARGS)

    try:

        inst.cursor.execute("INSERT INTO tbl_hash VALUES (NULL, ?, ?, ?)", (sha256, arg_id, mime))

        inst.connection.commit()

        return inst.cursor.lastrowid

    except sqlite3.IntegrityError as e: 

        inst.cursor.execute("SELECT hash_id FROM tbl_hash WHERE sha256=?", (sha256,))
        row = inst.cursor.fetchone()

        if row:

            return row[0]

        raise e

def add_url(url):

    inst = db_instance.get_instance()

    try:

        inst.cursor.execute("INSERT INTO tbl_url VALUES (NULL, ?, 0)", (url,))

        inst.connection.commit()
        
        return inst.cursor.lastrowid

    except sqlite3.IntegrityError as e: 

        inst.cursor.execute("SELECT url_id FROM tbl_url WHERE url=?", (url,))
        row = inst.cursor.fetchone()

        if row:

            return row[0]

        raise e




def add_url_hash(hash_id, url_id):

    inst = db_instance.get_instance()

    inst.cursor.execute("INSERT OR IGNORE INTO tbl_hash_url VALUES (? , ?)", (hash_id, url_id))

    inst.connection.commit()


def add_hash_filename(hash_id, filename):

    inst = db_instance.get_instance()

    inst.cursor.execute("INSERT INTO tbl_hash_filename VALUES (? , ?)", (hash_id, filename))

    inst.connection.commit()



def get_url(url):

    inst = db_instance.get_instance()

    inst.cursor.execute("SELECT url_id FROM tbl_url WHERE url=?", (url,))
    row = inst.cursor.fetchone()

    if row:

        return row[0]

    return -1 


def get_files_from_url_id(url_id):

    inst = db_instance.get_instance()
    inst.cursor.execute("SELECT * FROM tbl_hash_url JOIN tbl_hash USING(hash_id) WHERE url_id=?", (url_id,))
    
    for row in inst.cursor.fetchall():

        yield row 


def get_filename(hash_id):

    inst = db_instance.get_instance()
    inst.cursor.execute("SELECT filename FROM tbl_hash_filename WHERE hash_id=?", (hash_id,))
    
    row = inst.cursor.fetchone()

    if row:

        return row[0]

    return None 