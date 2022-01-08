import sys

class ProgressBar():
    def __init__(self, total, suffix='',every=1):
        self.total = total
        self.suffix = suffix
        self.every = every

    def draw(self, count):
        if count % self.every or count == self.total-1 or count == 0:             
            bar_len = 60
            filled_len = int(round(bar_len * count / float(self.total)))

            percents = round(100.0 * count / float(self.total), 1)
            bar = '=' * filled_len + '-' * (bar_len - filled_len)

            sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', self.suffix))
            sys.stdout.flush()

    def __del__(self):
        print('\r')
