from locust import HttpUser, between
from tasks.auth_task import AuthTaskSet
from tasks.bond_task import BondTaskSet
import logging

from tests.load.tasks.user_task import UserTaskSet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChillingBondUser(HttpUser):
    wait_time = between(1, 3)

    tasks = [BondTaskSet, UserTaskSet]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_email = None
        self.bonds_cache = []
        self.created_users = []

    def on_start(self) -> None:
        auth_tasks = AuthTaskSet(self)
        auth_tasks.login()

    def on_stop(self) -> None:
        if self.created_users:
            logger.info(f"🧹 Cleaning up {len(self.created_users)} created users")
            for user_id in self.created_users:
                try:
                    self.client.delete(f"/api/users/{user_id}")
                except Exception as e:
                    logger.error(f"Failed to cleanup user {user_id}: {e}")
