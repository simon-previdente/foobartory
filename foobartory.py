import asyncio
from typing import List

FOO_MINING_REQUEST = "foo_mining_request"
BAR_MINING_REQUEST = "bar_mining_request"
FOO_BAR_PROCESS_REQUEST = "foo_bar_process_request"
FOO_BAR_SELL_REQUEST = "foo_bar_sell_request"
BUY_ROBOT_REQUEST = "buy_robot_request"
BUY_ROBOT_RESPONSE = "buy_robot_response"
ROBOT_READY = "robot_ready"


class Manager:
    def __init__(self) -> None:
        # Messaging with bots
        self.requests: asyncio.Queue[str] = asyncio.Queue()
        self.results: asyncio.Queue[str] = asyncio.Queue()
        # Bag
        self.foo_cnt = 0
        self.bar_cnt = 0
        self.foobar_cnt = 0
        self.money = 0
        self.robots: List[Robot] = []

    def run(self) -> None:
        asyncio.get_event_loop().run_until_complete(
            future=self._run_until_the_goal_is_reached()
        )

    def add_robot(self) -> None:
        robot = Robot(manager=self)
        self.robots.append(robot)
        asyncio.ensure_future(robot.run())
        print("%d robot" % len(self.robots))

    def determine_next_activity(self) -> str:
        """Determines the next required action based on inventory"""
        if self.foo_cnt >= 6 and self.money >= 3:
            return BUY_ROBOT_REQUEST
        elif self.foobar_cnt >= 5:
            return FOO_BAR_SELL_REQUEST
        elif self.foo_cnt >= 1 and self.bar_cnt >= 1 and self.money < 3:
            return FOO_BAR_PROCESS_REQUEST
        elif self.foo_cnt > self.bar_cnt:
            return BAR_MINING_REQUEST
        else:
            return FOO_MINING_REQUEST

    async def _run_until_the_goal_is_reached(self) -> None:
        while len(self.robots) < 30:
            await self.results.get()
            self.add_robot()

            activity_needed = self.determine_next_activity()
            await self.requests.put(activity_needed)
        for robot in self.robots:
            robot.stop()


class Robot:
    def __init__(self, manager: Manager) -> None:
        self._running = True
        self.manager = manager

    async def run(self) -> None:
        await self.manager.results.put(ROBOT_READY)
        while self._running:
            await self.manager.requests.get()
            await self.manager.results.put(BUY_ROBOT_RESPONSE)

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    manager = Manager()
    manager.add_robot()
    manager.add_robot()
    manager.run()
