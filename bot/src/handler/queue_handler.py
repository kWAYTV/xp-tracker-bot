import asyncio
from queue import Queue
from src.util.logger import Logger
from src.steam.checker import Checker
from concurrent.futures import ThreadPoolExecutor

class QueueHandler:
    def __init__(self):
        self.queue = Queue()
        self.logger = Logger()
        self.checker = Checker()
        self.proccessing = False
        self.check_results = {}

    # Pushes an order to the queue
    def push_order(self, order):
        self.queue.put(order)

    # Returns the queue length
    def get_queue_length(self):
        return self.queue.qsize()

    # Returns the queue data as a list
    def get_queue_data(self):
        return self.queue.queue

    # Processes the queue
    async def process_queue(self):
        try:

            while not self.queue.empty():
                self.proccessing = True
                order = self.queue.get()
                steamid64 = order['steamid64']
                queue_id = order['queue_id']
                requested_by = order['requested_by']

                self.logger.log("INFO", f"Processing order {queue_id} from user {requested_by} for Steam ID: {steamid64}.")

                # Use asyncio's run_in_executor to run blocking functions in a thread
                with ThreadPoolExecutor(max_workers=int(1)) as executor:
                    for _ in range(int(1)):
                        success, result = await asyncio.get_event_loop().run_in_executor(executor, self.checker.get_player_info, steamid64, queue_id)

                self.check_results[steamid64] = (success, result)

                # Remove the completed order from the queue
                self.queue.task_done()
                await asyncio.sleep(1)

            self.proccessing = False
            
        except Exception as e:
            self.proccessing = False
            self.logger.log("ERROR", f"Error processing queue: {e}")

    # Function to get the results of a check
    async def get_check_results(self, steamid64):
        results = self.check_results.get(steamid64)
        return results  # If the check was not done yet, return (None, None)

    # Checks if the queue is empty and if it's not empty nor being processed, processes it
    async def force_check_start(self):
        try:
            if not self.queue.empty() and not self.proccessing:
                await self.process_queue()
        except Exception as e:
            self.proccessing = False
            self.logger.log("ERROR", f"Error force-checking the queue: {e}")