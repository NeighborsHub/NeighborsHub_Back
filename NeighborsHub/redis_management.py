from redis import Redis
from django.conf import settings


class VerificationEmailRedis:
    def __init__(self, issued_for: str):
        self.issued_for = issued_for
        self.connection = Redis(host=settings.REDIS_ENGINE['host'], port=settings.REDIS_ENGINE['port'], db=0)
        self.expire_time = 24 * 3600

    def create(self, keyword: str, token: str) -> None:
        self.connection.set(f"{self.issued_for}_{keyword}", token, self.expire_time)

    def get(self, keyword: str) -> None | str:
        return self.connection.get(f"{self.issued_for}_{keyword}")

    def revoke(self, keyword: str) -> None:
        self.connection.delete(f"{self.issued_for}_{keyword}")


class VerificationOTPRedis(VerificationEmailRedis):
    def __init__(self, issued_for: str):
        super().__init__(issued_for)
        self.expire_time = 5 * 60


class AuthenticationTokenRedis(VerificationEmailRedis):
    def __init__(self):
        super().__init__(issued_for="Authorization")
        self.expire_time = settings.JWT_AUTH_TIME_DELTA * 24 * 3600
