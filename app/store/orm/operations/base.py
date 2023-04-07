from __future__ import annotations

import abc
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    cast,
)

InSequenceT = TypeVar("InSequenceT", bound=Any)


class SequenceT(abc.ABC, Sequence[InSequenceT]):  # type: ignore
    def __init__(self, iterable: Optional[Sequence[InSequenceT]] = None) -> None:
        ...


ClassT = TypeVar("ClassT")


def _filter(
    klass: Type[SequenceT[InSequenceT]],
    sequence: Optional[SequenceT[Optional[InSequenceT]]] = None,
    *,
    use_on_default: SequenceT[InSequenceT],
) -> SequenceT[InSequenceT]:
    return use_on_default if sequence is None else klass(filter(None, sequence))  # type: ignore


class BaseOperation(Generic[ClassT]):
    if TYPE_CHECKING:
        model: Type[ClassT]

    @staticmethod
    def transform(
        *sequences: Optional[SequenceT[Optional[InSequenceT]]],
    ) -> Tuple[SequenceT[InSequenceT], ...]:
        cls = sequences.__class__
        return cast(
            Tuple[SequenceT[InSequenceT]],
            cls(
                _filter(
                    klass=sequence.__class__,  # type: ignore
                    sequence=sequence,
                    use_on_default=sequences.__class__(),  # type: ignore
                )
                for sequence in sequences
            ),
        )
