import time
from database import Shader, setup_db
import datetime
import sqlite3 as sql

session = setup_db()

conn = sql.connect('shaderwall.old.db')
cursor = conn.cursor()
session.query(Shader).delete()
session.commit()
for result in cursor.execute("SELECT id,source,authcode FROM shader").fetchall():
    if 1:
        shader = Shader(id=result[0], source=result[1], authcode=result[2])
        session.add(shader)
        session.commit()
    else:
        print("Error on id %d" % result[0])


