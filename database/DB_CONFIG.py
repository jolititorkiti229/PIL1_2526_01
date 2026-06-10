DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DB', 'mentorlink'),
    'charset': 'utf8mb4',
    'port': int(os.environ.get('MYSQL_PORT', 3306))
}