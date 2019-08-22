import os

CONFIG = {
    'Redis': {
        'host': os.getenv('Redis_host', 'redis'),
        'port': os.getenv('Redis_port', 6379),
        'pwd': os.getenv('Redis_pwd', None),
        'db': os.getenv('Redis_db', 0),
        'timeout': os.getenv('Redis_timeout', None),
    },
    'Mysql': {
        'host': os.getenv('Mysql_host', 'mysql'),
        'port': os.getenv('Mysql_port', 3306),
        'user': os.getenv('Mysql_user', 'crm'),
        'pwd': os.getenv('Mysql_pwd', 'crm'),
        'db': os.getenv('Mysql_db', 'campaign'),
    }
}

def get_redis_config():
   return CONFIG['Redis']


def get_config():
    return CONFIG
