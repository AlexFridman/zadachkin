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
        interval_borders = [(l, r) for l, r, _, _ in self.intervals]
        interval_pages = [(l, r) for _, _, l, r in self.intervals]

        interval_sizes = [np.sqrt(r - l + 1) for l, r in interval_borders]
        total_size = sum(interval_sizes)
        interval_probs = [size / total_size for size in interval_sizes]
        interval_idxs = np.arange(len(self.intervals))

        interval_idx = np.random.choice(interval_idxs, p=interval_probs)

        min_, max_ = interval_borders[interval_idx]
        return np.random.randint(min_, max_ + 1), interval_pages[interval_idx]


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
               intervals=[(1, 510, 7, 49)]),
        Source(author='Зубков',
               intervals=[(1001, 1085, 13, 26), (2001, 2089, 37, 50), (3001, 3281, 66, 106),
                          (4001, 4158, 113, 148), (5001, 5095, 154, 173), (6001, 6042, 178, 185)]),
        Source(author='Виноградова', topic='Производные и пределы',
               intervals=[[(1001, 1460, 34, 47), (2001, 2174, 77, 87), (3001, 3199, 122, 133)]),
        Source(author='Виноградова', topic='Интегралы',
               intervals=[(21001, 21400, 177, 223), (22001, 22152, 276, 283)]),
        Source(author='Сканави',
               intervals=[(2001, 2360, 15, 44), (3001, 3500, 52, 87), (4036, 4085, 91, 94),
                          (5030, 5090, 99, 103), (6001, 6370, 109, 130), (7001, 7340, 138, 156),
                          (8001, 8500, 163, 188), (9001, 9305, 198, 214)]),
    ]

    Source.objects.insert(sources)
