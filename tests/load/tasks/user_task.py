from locust import TaskSet, task
import random
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class UserTaskSet(TaskSet):
    @task(1)
    def create_user(self) -> None:
        random_suffix = str(uuid4())[:4]
        payload = {
            "email": f"test_{random_suffix}@example.com",
            "name": f"Test User {random_suffix}",
            "password": "TestPassword123!",
        }
        with self.client.post(
            "/api/users",
            json=payload,
            catch_response=True,
            name="POST /api/users",
        ) as r:
            if r.status_code == 201:
                try:
                    created_user = r.json()
                    user_id = created_user.get("id")
                    email = created_user.get("email")

                    # logger.info(f"✅ Created user: {user_id} ({email})")

                    if not hasattr(self.user, "created_users"):
                        self.user.created_users = []
                    self.user.created_users.append(user_id)

                    r.success()

                except Exception as e:
                    r.failure(f"Failed to parse response: {e}")

            elif r.status_code == 400:
                r.failure(f"Bad request: {r.text}")
            elif r.status_code == 409:
                r.failure("User already exists")
            else:
                r.failure(f"Failed with status {r.status_code}")

    @task(1)
    def delete_created_user(self) -> None:
        if not hasattr(self.user, "created_users") or not self.user.created_users:
            return

        user_id = random.choice(self.user.created_users)

        with self.client.delete(
            f"/api/users/{user_id}",
            catch_response=True,
            name="DELETE /api/users/{id}",
        ) as r:
            if r.status_code == 204:
                self.user.created_users.remove(user_id)
                # logger.info(f"🗑️ Deleted user: {user_id}")
                r.success()

            elif r.status_code == 404:
                r.failure("User not found")
                if user_id in self.user.created_users:
                    self.user.created_users.remove(user_id)

            elif r.status_code == 401:
                r.failure("Authentication failed")
            else:
                r.failure(f"Unexpected status: {r.status_code}")
