"""Module for managing asynchronous request queues with parallel processing limits.

This module provides a RequestQueue class that helps control the number of
concurrent requests and manages a queue for processing requests.
"""

import asyncio
import logging
import time
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class RequestQueue:
    """A queue management system for controlling parallel request processing.

    This class provides mechanisms to limit the number of concurrent requests
    and manage a queue of pending requests.
    """

    def __init__(self, max_parallel_requests: int) -> None:
        """Initialize the RequestQueue with a maximum number of parallel requests.

        Args:
            max_parallel_requests (int): Maximum number of requests that can
                                         be processed simultaneously.
        """
        self.max_parallel_requests: int = max_parallel_requests
        self.current_requests: int = 0
        self.queue: asyncio.Queue = asyncio.Queue()
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(max_parallel_requests)

    async def _process_request(
        self,
        request_id: str,
        handler: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Process a single request with logging and error handling.

        Args:
            request_id (str): Unique identifier for the request.
            handler (Callable): Async function to process the request.
            *args: Positional arguments for the handler.
            **kwargs: Keyword arguments for the handler.

        Returns:
            Any: Result of the request handler.

        Raises:
            Exception: Re-raises any exception that occurs during request processing.
        """
        try:
            async with self.semaphore:
                self.current_requests += 1
                logger.info(
                    "Processing request %s. Current requests: %s",
                    request_id,
                    self.current_requests,
                )
                try:
                    return await handler(*args, **kwargs)
                finally:
                    self.current_requests -= 1
                    logger.info(
                        "Completed request %s. Current requests: %s",
                        request_id,
                        self.current_requests,
                    )
        except Exception as e:
            logger.error("Error processing request %s: %s", request_id, str(e))
            raise

    @asynccontextmanager
    async def request(self, handler: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any) -> Any:
        """Manage a request by queuing or processing immediately based on current load.

        Args:
            handler (Callable): Async function to process the request.
            *args: Positional arguments for the handler.
            **kwargs: Keyword arguments for the handler.

        Yields:
            Any: Result of the request handler.
        """
        request_id: str = str(time.time())

        if self.current_requests >= self.max_parallel_requests:
            logger.info(
                "Request %s queued. Current queue size: %s",
                request_id,
                self.queue.qsize(),
            )
            await self.queue.put((request_id, handler, args, kwargs))
            while True:
                current_id, _, _, _ = await self.queue.get()
                if current_id == request_id:
                    break
                await self.queue.put((current_id, handler, args, kwargs))
                await asyncio.sleep(0.1)  # Prevent busy waiting

        try:
            result = await self._process_request(request_id, handler, *args, **kwargs)
            yield result
        finally:
            if not self.queue.empty():
                next_request: tuple[
                    str, Callable[..., Awaitable[Any]], tuple[Any, ...], dict[str, Any]
                ] = await self.queue.get()
                asyncio.create_task(self._process_request(*next_request))


# Global queue instance
_queue: Optional[RequestQueue] = None


def init_queue(max_parallel_requests: int) -> None:
    """Initialize the global request queue with a specified max parallel requests.

    Args:
        max_parallel_requests (int): Maximum number of requests that can
                                     be processed simultaneously.
    """
    global _queue
    _queue = RequestQueue(max_parallel_requests)


def get_queue() -> RequestQueue:
    """Retrieve the global request queue.

    Returns:
        RequestQueue: The initialized request queue.

    Raises:
        RuntimeError: If the queue has not been initialized.
    """
    if _queue is None:
        raise RuntimeError("Queue not initialized")
    return _queue
