def query(sql, args=(), one=False, commit=False):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, args)
    if commit:
        db.commit()
        return cur.lastrowid
    rv = cur.fetchone() if one else cur.fetchall()
    cur.close()
    return rv