import datetime
from typing import Sequence


class DateSequence(Sequence):
    def __init__(self, start_date: datetime.date, end_date: datetime.date, step: int = 1):
        self.start_date = start_date
        self.end_date = end_date
        self.step = step
        self.length = ((end_date - start_date).days + 1) // step

    def __getitem__(self, index: int | slice) -> datetime.date | Sequence[datetime.date]:
        if isinstance(index, slice):
            return [self[i] for i in range(*index.indices(self.length))]
        if not 0 <= index < self.length:
            raise IndexError
        return self.start_date + datetime.timedelta(days=index * self.step)

    def __len__(self) -> int:
        return self.length
