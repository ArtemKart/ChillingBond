from dataclasses import dataclass
from datetime import datetime
from abc import ABC


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events"""
    occurred_at: datetime
