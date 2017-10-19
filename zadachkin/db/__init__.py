import pymongo
from mongoengine import connect


def init_mongodb(connection):
    # WARN: Do not delete this
    return connect(**connection, connect=False)


class Mongo:
    read_preference = pymongo.ReadPreference.PRIMARY

    def __init__(self, db, hosts, username=None, password=None, rs=None):
        self.db = db
        self.username = username
        self.password = password

        if not isinstance(hosts, str):
            hosts = ','.join(hosts)

        if rs is not None:
            self.host = 'mongodb://{}:{}@{}/{}?replicaSet={}'.format(username, password, hosts, db, rs)
        elif username is None:
            self.host = 'mongodb://{}/{}'.format(hosts, db)
        else:
            self.host = 'mongodb://{}:{}@{}/{}'.format(username, password, hosts, db)

        self.celery_broker_db = db
        self.celery_backend_db = db

        self.connection = {
            'host': self.host,
            'read_preference': self.read_preference,
        }
