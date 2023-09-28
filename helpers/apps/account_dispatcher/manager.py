from dataclasses import dataclass, field

from .dispatcher import Dispatcher


@dataclass
class DispatcherManager:
    dispatchers: dict[int, Dispatcher] = field(default_factory=dict)
