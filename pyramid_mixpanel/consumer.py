"""Consumers send events/profiles messages to Mixpanel's HTTP API."""

from dataclasses import dataclass
from dataclasses import field
from mixpanel import BufferedConsumer
from urllib.error import URLError

import json
import structlog
import typing as t

logger = structlog.get_logger(__name__)


@dataclass(frozen=True)
class MockedMessage:
    """A single Mixpanel message stored by MockedConsumer."""

    endpoint: str
    msg: t.Dict["str", object]


@dataclass(frozen=True)
class MockedConsumer:
    """Save messages in an internal list, useful in unit testing."""

    # Internal storage of mocked message
    mocked_messages: t.List = field(default_factory=lambda: [])

    def send(self, endpoint: str, json_message: str) -> None:
        """Append message to the mocked_messages list."""
        msg = MockedMessage(endpoint=endpoint, msg=json.loads(json_message))
        self.mocked_messages.append(msg)


class PoliteBufferedConsumer(BufferedConsumer):
    """Subclass of BufferedConsumer that logs network errors instead of failing.

    Inspired by:
    https://github.com/mixpanel/mixpanel-python/issues/36#issuecomment-72063207
    """

    def flush(self, *args, **kwargs) -> None:
        """Try to send updates to Mixpanel."""
        try:
            super(PoliteBufferedConsumer, self).flush(*args, **kwargs)
        except URLError:
            logger.exception("It seems like Mixpanel is down.", exc_info=True)


@dataclass(frozen=True)
class QueuedConsumer:
    """Queue sending Mixpanel messages in a separate background queue processor."""

    def send(self, endpoint: str, json_message: str) -> None:
        """Queue sending of Mixpanel message in a background task."""
        # send_api.delay(endpoint, json_message)
        raise NotImplementedError  # pragma: no cover
