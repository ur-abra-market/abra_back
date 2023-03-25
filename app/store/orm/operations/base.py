from typing import Any, Final, List, Optional, Sequence

EMPTY_RESULT: Final[List[Any]] = []


class BaseOperation:
    def generate_value(self, sequence: Optional[Sequence[Any]] = None) -> List[Any]:
        return EMPTY_RESULT if sequence is None else list(sequence)

    def transform(self, *sequences: Optional[Sequence[Any]]) -> List[List[Any]]:
        return [self.generate_value(sequence) for sequence in sequences]
