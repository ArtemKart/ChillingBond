from locust import TaskSet, task
import random
import logging

logger = logging.getLogger(__name__)


class AuthTaskSet(TaskSet):
    def login(self) -> bool:
        user_num = random.randint(0, 9)
        self.user.user_email = f"loadtest{user_num}@example.com"
        password = "LoadTest123!"

        with self.client.post(
            "/api/login/token",
            data={"username": self.user.user_email, "password": password},
            catch_response=True,
            name="POST /api/login/token",
        ) as r:
            if r.status_code == 200:
                if "access_token" in r.cookies:
                    r.success()
                    return True
                else:
                    r.failure("No access_token cookie in response")
                    return False
            else:
                r.failure(f"Login failed with status {r.status_code}")
                return False

    @task(1)
    def relogin(self) -> None:
        self.login()
