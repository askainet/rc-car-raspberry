class Motor:
    def __init__(self, min_duty_cycle=20, reverse_polarity=False):
        self.reverse_polarity = reverse_polarity
        self.min_duty_cycle = min_duty_cycle
