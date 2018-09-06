class ctx:
    def __init__(self):
        self.m_reqs_count = {}
        self.m_reqs_in_flight = 0
        self.m_reqs_duration = []