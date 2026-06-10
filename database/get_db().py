def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(**DB_CONFIG)
        g.db.autocommit = True
    else:
        try:
            g.db.ping(reconnect=True, attempts=3, delay=1)
        except mysql.connector.Error:
            g.db = mysql.connector.connect(**DB_CONFIG)
            g.db.autocommit = True
    return g.db