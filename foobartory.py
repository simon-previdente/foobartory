import asyncio
from typing import List

BUY_ROBOT_REQUEST = "buy_robot_request"
BUY_ROBOT_RESPONSE = "buy_robot_response"
ROBOT_READY = "robot_ready"


class Manager:
    def __init__(self) -> None:
        # Messaging with bots
        self.requests: asyncio.Queue[str] = asyncio.Queue()
        self.results: asyncio.Queue[str] = asyncio.Queue()
        # Bag
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

    async def _run_until_the_goal_is_reached(self) -> None:
        while len(self.robots) < 30:
            await self.results.get()
            self.add_robot()
            await self.requests.put(BUY_ROBOT_REQUEST)
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
