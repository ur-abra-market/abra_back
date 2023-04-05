from __future__ import annotations

from typing import Any, Optional, Sequence, Tuple, Type, TypeVar

SequenceT = TypeVar("SequenceT", bound=Sequence)
InSequenceT = TypeVar("InSequenceT", bound=Any)


def _filter(
    klass: Type[SequenceT[InSequenceT]],
    sequence: Optional[SequenceT[InSequenceT]] = None,
    *,
    use_on_default: SequenceT[InSequenceT],
) -> SequenceT[InSequenceT]:
    return use_on_default if sequence is None else klass(filter(None, sequence))


class BaseOperation:
    def transform(
        self, *sequences: Optional[SequenceT[InSequenceT]]
    ) -> Tuple[SequenceT[InSequenceT]]:
        cls = sequences.__class__
        return cls(
            _filter(
                klass=sequence.__class__,
                sequence=sequence,
                use_on_default=sequences.__class__(),
            )
            for sequence in sequences
        )
