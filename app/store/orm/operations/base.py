from __future__ import annotations

import abc
from typing import (
    TYPE_CHECKING,
    Any,
    Generator,
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
    def __init__(
        self,
        iterable: Union[
            Generator[InSequenceT, None, None], Optional[Sequence[InSequenceT]]
        ] = None,
    ) -> None:
        ...


ClassT = TypeVar("ClassT")


def _filter(
    klass: Union[Type[SequenceT[InSequenceT]], Type[None]],
    sequence: Optional[SequenceT[InSequenceT]] = None,
    *,
    use_on_default: Tuple[Any],
) -> SequenceT[InSequenceT]:
    return (
        cast(SequenceT[InSequenceT], use_on_default)
        if sequence is None
        else klass(i for i in sequence if i is not None)
    )


class BaseOperation(Generic[ClassT]):
    _USE_DEFAULT: Tuple[Any] = ()  # type: ignore[assignment]

    if TYPE_CHECKING:
        model: Type[ClassT]

    def transform(
        self,
        *sequences: Optional[SequenceT[InSequenceT]],
    ) -> Tuple[SequenceT[InSequenceT]]:
        cls = sequences.__class__
        return cast(
            Tuple[SequenceT[InSequenceT]],
            cls(
                _filter(
                    klass=sequence.__class__,
                    sequence=sequence,
                    use_on_default=self._USE_DEFAULT,
                )
                for sequence in sequences
            ),
        )
