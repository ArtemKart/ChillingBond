from locust import TaskSet, task
import random
import logging

from tests.load.tasks.auth_task import AuthTaskSet

logger = logging.getLogger(__name__)


class BondTaskSet(TaskSet):
    @task(10)
    def get_all_bonds(self) -> None:
        with self.client.get(
            "/api/bonds",
            catch_response=True,
            name="GET /api/bonds",
        ) as r:
            if r.status_code == 200:
                try:
                    data = r.json()
                    assert isinstance(data, list)

                    bondholder_count = len(data)
                    response_time_ms = r.elapsed.total_seconds() * 1000

                    if random.random() < 0.1:
                        logger.info(
                            f"📊 GET /api/bonds |||| {bondholder_count} bondholders, "
                            f"{response_time_ms:.0f}ms"
                        )
                    r.success()

                except Exception as e:
                    r.failure(f"Failed to parse response: {e}")
                    logger.error(f"❌ GET /api/bonds failed: {e}")

            elif r.status_code == 401:
                r.failure("Authentication failed")
                logger.error("❌ GET /api/bonds: Auth failed, re-logging in")

                auth_tasks = AuthTaskSet(self.user)
                auth_tasks.login()
            else:
                r.failure(f"Unexpected status code: {r.status_code}")

    @task(3)
    def create_bond(self) -> None:
        payload = {
            "series": "ROR1111",
            "nominal_value": float(100),
            "maturity_period": 12,
            "initial_interest_rate": float(4.75),
            "first_interest_period": 1,
            "reference_rate_margin": float(0.1),
            "quantity": random.randint(1, 100),
            "purchase_date": "2024-01-15",
        }

        with self.client.post(
            "/api/bonds",
            json=payload,
            catch_response=True,
            name="POST /api/bonds",
        ) as r:
            if r.status_code == 201:
                data = r.json()
                bh_id = data["id"]
                self.user.bonds_cache.append(bh_id)
                r.success()

            elif r.status_code == 401:
                r.failure("Authentication failed")
            else:
                r.failure(f"Failed with status {r.status_code}")

    @task(2)
    def get_single_bond(self) -> None:
        if not self.user.bonds_cache:
            return

        bh_id = random.choice(self.user.bonds_cache)
        if not bh_id:
            return
        with self.client.get(
            f"/api/bonds/{bh_id}",
            catch_response=True,
            name="GET /api/bonds/{id}",
        ) as r:
            if r.status_code == 200:
                r.success()
            elif r.status_code == 404:
                r.failure("BondHolder not found")
            elif r.status_code == 401:
                r.failure("Authentication failed")
            else:
                r.failure(f"Unexpected status: {r.status_code}")

    @task(1)
    def delete_bond(self) -> None:
        if not self.user.bonds_cache:
            return
        bh_id = random.choice(self.user.bonds_cache)
        if not bh_id:
            return
        with self.client.delete(
            f"/api/bonds/{bh_id}",
            catch_response=True,
            name="DELETE /api/bonds/{id}",
        ) as r:
            if r.status_code == 204:
                self.user.bonds_cache = [b for b in self.user.bonds_cache if b != bh_id]
                r.success()
            elif r.status_code == 404:
                r.failure("BondHolder not found")
            elif r.status_code == 401:
                r.failure("Authentication failed")
            else:
                r.failure(f"Unexpected status: {r.status_code}")
