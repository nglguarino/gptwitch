import asyncio
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union
from utils.logger import get_logger

logger = get_logger()


class QueueItem:
    """
    Represents an item in the processing queue
    """

    def __init__(self,
                 data: Any,
                 priority: int = 0,
                 callback: Optional[Callable] = None,
                 created_at: float = None):
        self.data = data
        self.priority = priority  # Higher number = higher priority
        self.callback = callback
        self.created_at = created_at or time.time()

    def __lt__(self, other):
        # For priority queue comparison (higher priority first, then FIFO)
        if self.priority == other.priority:
            return self.created_at < other.created_at
        return self.priority > other.priority


class AsyncQueueManager:
    """
    Manages asynchronous processing queues with prioritization and rate limiting.
    Useful for handling Twitch chat messages and API requests.
    """

    def __init__(self,
                 max_workers: int = 1,
                 rate_limit: Optional[float] = None,
                 queue_name: str = "default"):
        """
        Initialize a new queue manager.

        Args:
            max_workers: Maximum number of concurrent workers
            rate_limit: Minimum time between processing items (in seconds)
            queue_name: Name for this queue (for logging)
        """
        self.queue = asyncio.PriorityQueue()
        self.max_workers = max_workers
        self.rate_limit = rate_limit
        self.queue_name = queue_name
        self.workers = []
        self.running = False
        self.last_processed_time = 0
        self.stats = {
            "enqueued": 0,
            "processed": 0,
            "errors": 0,
            "avg_processing_time": 0,
            "total_processing_time": 0
        }

    async def start(self):
        """Start the queue processing workers"""
        if self.running:
            return

        self.running = True
        logger.info(f"Starting queue manager '{self.queue_name}' with {self.max_workers} workers")

        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)

    async def stop(self):
        """Stop all queue processing workers"""
        if not self.running:
            return

        self.running = False
        logger.info(f"Stopping queue manager '{self.queue_name}'")

        # Wait for workers to complete
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers = []

    async def _worker(self, worker_id: int):
        """Worker task that processes queue items"""
        logger.debug(f"Worker {worker_id} started for queue '{self.queue_name}'")

        while self.running:
            try:
                # Get next item from queue
                _, item = await self.queue.get()

                # Apply rate limiting if enabled
                if self.rate_limit:
                    elapsed = time.time() - self.last_processed_time
                    if elapsed < self.rate_limit:
                        await asyncio.sleep(self.rate_limit - elapsed)

                # Process the item
                start_time = time.time()
                try:
                    # Execute callback with the data if provided
                    if item.callback:
                        if asyncio.iscoroutinefunction(item.callback):
                            await item.callback(item.data)
                        else:
                            item.callback(item.data)

                    # Update stats
                    self.stats["processed"] += 1
                    process_time = time.time() - start_time
                    total_time = self.stats["total_processing_time"] + process_time
                    count = self.stats["processed"]
                    self.stats["total_processing_time"] = total_time
                    self.stats["avg_processing_time"] = total_time / count

                except Exception as e:
                    self.stats["errors"] += 1
                    logger.exception(f"Error processing queue item: {e}")

                # Record last processing time for rate limiting
                self.last_processed_time = time.time()

                # Mark task as done
                self.queue.task_done()

            except asyncio.CancelledError:
                logger.debug(f"Worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.exception(f"Unexpected error in worker {worker_id}: {e}")

        logger.debug(f"Worker {worker_id} stopped")

    async def enqueue(self,
                      data: Any,
                      priority: int = 0,
                      callback: Optional[Callable] = None) -> None:
        """
        Add an item to the processing queue

        Args:
            data: The data to process
            priority: Priority level (higher = processed sooner)
            callback: Function to call with the data when processed
        """
        item = QueueItem(data, priority, callback)
        await self.queue.put((priority, item))
        self.stats["enqueued"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get current queue statistics"""
        stats = dict(self.stats)
        stats["queue_size"] = self.queue.qsize()
        stats["workers_active"] = len(self.workers)
        return stats

    async def wait_empty(self):
        """Wait until the queue is empty"""
        if self.queue.qsize() > 0:
            await self.queue.join()


class MessageQueue(AsyncQueueManager):
    """
    Specialized queue for handling chat messages with context awareness
    """

    def __init__(self,
                 processor_func: Callable[[Any], Coroutine],
                 max_workers: int = 1,
                 rate_limit: Optional[float] = None):
        """
        Initialize message queue with a processor function

        Args:
            processor_func: Async function to process messages
            max_workers: Maximum concurrent message processors
            rate_limit: Rate limit between messages (in seconds)
        """
        super().__init__(max_workers, rate_limit, "message_queue")
        self.processor_func = processor_func
        self.context = {}  # Stores context by channel

    async def add_message(self,
                          message: Any,
                          channel: str,
                          priority: int = 0):
        """
        Add a chat message to the queue

        Args:
            message: Message data
            channel: Channel the message belongs to
            priority: Message priority
        """
        # Wrap message with channel context
        data = {
            "message": message,
            "channel": channel
        }

        # Use the processor function as the callback
        await self.enqueue(data, priority, self.processor_func)

    def get_channel_context(self, channel: str) -> Dict:
        """Get the current context for a channel"""
        if channel not in self.context:
            self.context[channel] = {}
        return self.context[channel]

    def update_channel_context(self, channel: str, updates: Dict):
        """Update the context for a channel"""
        if channel not in self.context:
            self.context[channel] = {}
        self.context[channel].update(updates)