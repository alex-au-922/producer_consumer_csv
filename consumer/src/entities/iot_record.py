from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class IOTRecord:
    record_time: datetime
    sensor_id: str
    value: Decimal
