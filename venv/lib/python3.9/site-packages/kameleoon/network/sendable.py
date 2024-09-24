"""Network"""
from enum import Enum
from typing import Optional
from kameleoon.helpers import nonce
from kameleoon.network.query_encodable import QueryEncodable
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class Sendable(QueryEncodable):
    """Abstract sendable type"""
    def __init__(self) -> None:
        super().__init__()
        self._nonce: Optional[str] = None
        self._state = Sendable.State.UNSENT

    @property
    def nonce(self) -> str:
        """The nonce associated with the sendable object."""
        raise NotImplementedError

    @property
    def unsent(self) -> bool:
        """Indicates if the sendable object is in the `UNSENT` state."""
        return self._state == Sendable.State.UNSENT

    @property
    def transmitting(self) -> bool:
        """Indicates if the sendable object is in the `TRANSMITTING` state."""
        return self._state == Sendable.State.TRANSMITTING

    @property
    def sent(self) -> bool:
        """Indicates if the sendable object is in the `SENT` state."""
        return self._state == Sendable.State.SENT

    def mark_as_unsent(self) -> None:
        """Marks the sendable object as `UNSENT` if it is currently in the `TRANSMITTING` state."""
        if self.transmitting:
            self._state = Sendable.State.UNSENT

    def mark_as_transmitting(self) -> None:
        """Marks the sendable object as `TRANSMITTING` if it is currently in the `UNSENT` state."""
        if self.unsent:
            self._state = Sendable.State.TRANSMITTING

    def mark_as_sent(self) -> None:
        """Marks the sendable object as `SENT` and clears the nonce."""
        self._state = Sendable.State.SENT
        self._nonce = None

    def encode_query(self) -> str:
        query_builder = QueryBuilder(QueryParam(QueryParams.NONCE, self.nonce))
        self._add_query_params(query_builder)
        return str(query_builder)

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        """Adds query parameters to the given QueryBuilder."""

    class State(Enum):
        """Represents the different states of a sendable object"""
        UNSENT = 0
        TRANSMITTING = 1
        SENT = 2


class DuplicationSafeSendableBase(Sendable):
    """Duplication safe sendable base"""
    def __init__(self) -> None:
        super().__init__()
        self._nonce = nonce.get_nonce()

    @property
    def nonce(self) -> str:
        return self._nonce or ""


class DuplicationUnsafeSendableBase(Sendable):
    """Duplication unsafe sendable base"""
    @property
    def nonce(self) -> str:
        if (self._nonce is None) and not self.sent:
            self._nonce = nonce.get_nonce()
        return self._nonce or ""
