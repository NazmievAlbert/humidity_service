import time
from collections import defaultdict
from config import Config


class RateLimiter:
    def __init__(self, config):
        self.config = config
        self.request_log = defaultdict(list)

    def check_rate_limit(self, ip):
        """Проверяет, не превышен ли лимит запросов"""
        now = time.time()
        window_start = now - self.config.RATE_LIMIT_WINDOW

        self.request_log[ip] = [t for t in self.request_log[ip] if t > window_start]

        if len(self.request_log[ip]) >= self.config.RATE_LIMIT:
            return False

        self.request_log[ip].append(now)
        return True