import time


class FunctionTime:
    def __init__(self, name, max_times=10000):
        self.name = name
        self.max_times = max_times
        self.times = []

    def add(self, func_time):
        self.times.append(func_time)
        if len(self.times) > self.max_times:
            self.times = self.times[len(self.times) - self.max_times:]

    def count(self):
        return len(self.times)

    def mean(self, round_to=5):
        return round(sum(self.times) / len(self.times), round_to)

    def median(self, round_to=5):
        return round(sorted(self.times)[len(self.times) // 2], round_to)

    def last(self, round_to=5):
        return round(self.times[-1], round_to)


class Timer:
    def __init__(self):
        self.f_timers = dict()

    def start(self, func_name):
        timer = self.f_timers.setdefault(func_name, {'class': FunctionTime(func_name), 'act_timer': time.time()})
        timer['act_timer'] = time.time()

    def time_stamp(self, func_name):
        timer = self.f_timers.get(func_name, {'class': FunctionTime(func_name), 'act_timer': time.time()})
        timer['class'].add(time.time() - timer['act_timer'])

    def output(self):
        text = '{:^5}|{:^30}|{:^15}|{:^15}|{:^15}\n'.format('count', 'name', 'mean', 'median', 'last')
        timers = list()
        for t in self.f_timers:
            timer = self.f_timers[t]['class']
            timers.append((timer.count(), timer.name, timer.mean(), timer.median(), timer.last()))
        timers.sort(key=lambda x: x[0], reverse=True)
        timers = ['{:>5}|{:<30}|{:>15}|{:>15}|{:>15}'.format(*i) for i in timers]
        print(text + '\n'.join(timers))
