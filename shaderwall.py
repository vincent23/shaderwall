import bottle
import sqlite3 as sql

def main():
    global conn
    conn = sql.connect('shaderwall.db')
    setup_db()
    bottle.run(host='localhost', port=8080)

@bottle.get('/shaders')
def get_shader_list():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shader')
    shaders = cursor.fetchall()
    return '<br>'.join(str(shader) for shader in shaders)

@bottle.post('/shaders')
def create_shader():
    source = bottle.request.params.getunicode('source')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO shader (source) VALUES (?)', (source,))
    conn.commit()
    return 'Created new shader ' + str(cursor.lastrowid)

@bottle.get('/shaders/<shader_id:int>')
def get_shader(shader_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shader WHERE id = ?', (shader_id,))
    result = cursor.fetchone()
    if result:
        return str(result)
    else:
        bottle.abort(404, 'Shader not found')

@bottle.post('/shaders/<shader_id:int>')
def edit_shader(shader_id):
    source = bottle.request.params.getunicode('source')
    cursor = conn.cursor()
    cursor.execute('UPDATE shader SET source = ? WHERE id = ?' , (source, shader_id))
    conn.commit()
    if cursor.rowcount == 1:
        return 'Updated shader'
    else:
        bottle.abort(403, 'Update failed')

def setup_db():
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS shader (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT,
                        created TEXT DEFAULT CURRENT_TIMESTAMP
                      )''')
    conn.commit()

main()
