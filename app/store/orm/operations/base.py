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
    Union,
    cast,
)

InSequenceT = TypeVar("InSequenceT", bound=Any)


class SequenceT(abc.ABC, Sequence[InSequenceT]):
    def __init__(self, iterable: Optional[Sequence[InSequenceT]] = None) -> None:
        ...


ClassT = TypeVar("ClassT")


def _filter(
    klass: Union[Type[SequenceT[InSequenceT]], Type[None]],
    sequence: Optional[SequenceT[InSequenceT]] = None,
    *,
    use_on_default: SequenceT[InSequenceT],
) -> SequenceT[InSequenceT]:
    return use_on_default if sequence is None else klass(filter(None, sequence))  # type: ignore


class BaseOperation(Generic[ClassT]):
    if TYPE_CHECKING:
        model: Type[ClassT]

    @staticmethod
    def transform(
        *sequences: Optional[SequenceT[InSequenceT]],
    ) -> Tuple[SequenceT[InSequenceT]]:
        cls = sequences.__class__
        return cast(
            Tuple[SequenceT[InSequenceT]],
            cls(
                _filter(
                    klass=sequence.__class__,
                    sequence=sequence,
                    use_on_default=sequence.__class__(),  # type: ignore[misc]
                )
                for sequence in sequences
            ),
        )
