import pickle

occlusion_profile = [1.5, 20., -10., 10.]


class LogReader():
    def __init__(self, log_path):
        self.log_path = log_path
        self.log_gen = self.make_log_gen(log_path)
        self.msg_count = -1
        self.first = next(self.log_gen)
        self.prev = next(self.log_gen)
        self.curr = next(self.log_gen)
        self.deltas = []

    def get_by_timestamp(self, timestamp):
        """
        returns msg with timestamp <= timestamp
        """
        if self.curr is None:
            raise StopIteration

        curr_t, _ = self.curr

        while curr_t <= timestamp:
            next(self)

            if self.curr is None:
                return self.prev

            curr_t, _ = self.curr

        return self.prev

    def __next__(self):
        ret = self.prev

        if self.curr is not None:
            self.deltas.append((self.curr[0], self.curr[0] - self.prev[0]))

        self.prev = self.curr

        try:
            self.curr = next(self.log_gen)
        except StopIteration:
            self.curr = None

        if ret is None:
            raise StopIteration

        self.msg_count += 1

        return ret

    def __iter__(self):
        return self

    def make_log_gen(self, log_path):
        with open(log_path, 'rb') as f:
            while True:
                try:
                    yield pickle.load(f)
                except EOFError:
                    break
                except pickle.UnpicklingError:
                    break

    def reset_gen(self):
        self.log_gen = self.make_log_gen(self.log_path)
        # -1 to compensate for first message
        self.msg_count = -1
        self.first = next(self.log_gen)
        self.prev = next(self.log_gen)
        self.curr = next(self.log_gen)
        self.deltas = []
