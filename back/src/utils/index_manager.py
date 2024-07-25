class IndexManager:
    index_shifts: list[int]
    removed_indexes: list[int]

    def __init__(self) -> None:
        self.index_shifts = [0]
        self.removed_indexes = []

    def _ensure_size(self, size: int) -> None:
        while len(self.index_shifts) < size:
            self.index_shifts.append(self.index_shifts[-1])

    def add_from_index(self, index: int) -> None:
        self._ensure_size(index + 2)
        self.index_shifts = [
            x + 1 if i >= index else x for i, x in enumerate(self.index_shifts)
        ]

    def remove_from_index(self, index: int) -> None:
        self._ensure_size(index + 2)
        self.index_shifts = [
            x - 1 if i >= index else x for i, x in enumerate(self.index_shifts)
        ]
        self.removed_indexes.append(index)

    def get_updated_index(self, index: int) -> int:
        self._ensure_size(index + 2)
        if index in self.removed_indexes:
            return -1
        return index + self.index_shifts[index]
