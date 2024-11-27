"""Abstract types."""

from typing import TypeVar, Protocol, Any

T_contra = TypeVar("T_contra", contravariant=True)


class SupportsDunderLT(Protocol[T_contra]):
    """Abstract class for __lt__ types."""

    def __lt__(self, __other):
        # type: (T_contra) -> bool
        ...


ComparableT = TypeVar('ComparableT', bound=SupportsDunderLT[Any])
