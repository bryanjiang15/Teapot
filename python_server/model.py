import flask
import sqlite3

def get_db():
    if 'sqlite_db' not in flask.g:
        flask.g.sqlite_db = sqlite3.connect(flask.current_app.config['DATABASE_FILENAME'])
        flask.g.sqlite_db.execute('PRAGMA foreign_keys = ON')
    
    return flask.g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()
