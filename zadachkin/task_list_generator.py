import copy

from prwlock import RWLock


class TaskListGenerator:
    def __init__(self, sources=None):
        self._sources = sources
        self._sources_mutex = RWLock()

    def replace_sources(self, sources):
        with self._sources_mutex.writer_lock():
            self._sources = copy.deepcopy(sources)

    @staticmethod
    def format_task_number(task_i):
        task_i = str(task_i)

        if len(task_i) < 4:
            return task_i

        if len(task_i) == 4:
            return '.'.join((task_i[0], task_i[1:]))

        if len(task_i) == 5:
            return '.'.join((task_i[0], task_i[1], task_i[2:]))

        logger.error('Encouraged with very long task number {}'.format(task_i))

        return task_i

    def generate_task_list(self):
        with self._sources_mutex.reader_lock():
            assert self._sources
            # TODO: generate task list

            task_list = []

            for source in self._sources:
                task_list.append((source, self.format_task_number(source.peek_task())))

            return task_list
