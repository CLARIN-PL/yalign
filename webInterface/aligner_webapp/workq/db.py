import sqlite3

schema = """
create table tasks(
    id integer primary key autoincrement,
    user text not null,
    status text not null,
    data text,
    result text,
    created_time integer not null
)
"""

STATUS_PREPARE = 'prepare'
STATUS_ENQUEUED = 'enqueued'
STATUS_INPROGRESS = 'inprogress'
STATUS_READY = 'ready'
STATUS_FAILED = 'failed'

statuses = {
    STATUS_PREPARE,
    STATUS_ENQUEUED,
    STATUS_INPROGRESS,
    STATUS_READY,
    STATUS_FAILED,
}

def init_db(path):
    """TODO: Docstring for init_db.

    :path: TODO
    :returns: TODO

    """
    con = sqlite3.connect(path)
    with con:
        con.execute(schema)
