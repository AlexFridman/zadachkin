import datetime

import mongoengine as me
import numpy as np


class Source(me.Document):
    author = me.StringField()
    topic = me.StringField()
    url = me.URLField()
    intervals = me.ListField()
    is_active = me.BooleanField(default=True)

    @property
    def str_id(self):
        return str(self.id)

    def peek_task(self):
        interval_sizes = [r - l + 1 for r, l in self.intervals]
        total_size = sum(interval_sizes)
        interval_probs = [size / total_size for size in interval_sizes]
        interval_idxs = np.arange(len(self.intervals))

        interval_idx = np.random.choice(interval_idxs, p=interval_probs)

        min_, max_ = self.intervals[interval_idx]
        return np.random.randint(min_, max_ + 1)


class TaskList(me.Document):
    user_id = me.StringField()
    timestamp = me.DateTimeField()
    tasks = me.ListField()

    @classmethod
    def get_user_last_timestamp(cls, user_id):
        try:
            return cls.objects(user_id=user_id).order_by('-timestamp').only('timestamp').first().timestamp
        except Exception as e:
            return datetime.datetime.min


def insert_default_sources():
    sources = [
        Source(author='Филипов',
               intervals=[(1, 510)]),
        Source(author='Зубков',
               intervals=[(1001, 1085), (2001, 2089), (3001, 3281),
                          (4001, 4158), (5001, 5095), (6001, 6042)]),
        Source(author='Виноградова', topic='Производные и пределы',
               intervals=[(1001, 1460), (2001, 2174), (3001, 3199)]),
        Source(author='Виноградова', topic='Интегралы',
               intervals=[(21001, 21400), (22001, 22152)]),
        Source(author='Сканави',
               intervals=[(2001, 2360), (3001, 3500), (4036, 4058),
                          (5030, 5090), (6001, 6370), (7001, 7340),
                          (8001, 8500), (9001, 9305)]),
    ]

    Source.objects.insert(sources)
