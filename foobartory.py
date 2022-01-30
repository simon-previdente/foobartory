import asyncio
import random
from typing import List, Optional

TIME_MODIFIER = 1.0

FOO_MINING_REQUEST = "foo_mining_request"
FOO_MINING_RESPONSE = "foo_mining_response"
BAR_MINING_REQUEST = "bar_mining_request"
BAR_MINING_RESPONSE = "bar_mining_response"
FOO_BAR_PROCESS_REQUEST = "foo_bar_process_request"
FOO_BAR_PROCESS_SUCCESS_RESPONSE = "foo_bar_process_success_response"
FOO_BAR_PROCESS_FAILURE_RESPONSE = "foo_bar_process_failure_response"
FOO_BAR_SELL_REQUEST = "foo_bar_sell_request"
FOO_BAR_SELL_RESPONSE = "foo_bar_sell_response"
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

    def consume_resources(self, activity: str) -> None:
        """Consume resources before the activity"""
        if activity == BUY_ROBOT_REQUEST:
            self.foo_cnt -= 6
            self.money -= 3
        elif activity == FOO_BAR_SELL_REQUEST:
            self.foobar_cnt -= 5
        elif activity == FOO_BAR_PROCESS_REQUEST:
            self.foo_cnt -= 1
            self.bar_cnt -= 1

    def manage_result(self, result: str) -> None:
        """Provides resources based on the activity's result"""
        if result == FOO_MINING_RESPONSE:
            self.foo_cnt += 1
        elif result == BAR_MINING_RESPONSE:
            self.bar_cnt += 1
        elif result == FOO_BAR_PROCESS_SUCCESS_RESPONSE:
            self.foobar_cnt += 1
        elif result == FOO_BAR_PROCESS_FAILURE_RESPONSE:
            self.bar_cnt += 1
        elif result == FOO_BAR_SELL_RESPONSE:
            self.money += 1
        elif result == BUY_ROBOT_RESPONSE:
            self.add_robot()

    async def _run_until_the_goal_is_reached(self) -> None:
        while len(self.robots) < 30:
            result = await self.results.get()
            self.manage_result(result=result)

            activity_needed = self.determine_next_activity()
            self.consume_resources(activity=activity_needed)
            await self.requests.put(activity_needed)
        for robot in self.robots:
            robot.stop()


class Robot:
    def __init__(self, manager: Manager) -> None:
        self._running = True
        self.manager = manager
        self.last_activity: Optional[str] = None

    async def run(self) -> None:
        await self.manager.results.put(ROBOT_READY)
        while self._running:
            request = await self.manager.requests.get()
            response = await self.manage_request(request=request)
            await self.manager.results.put(response)

    def stop(self) -> None:
        self._running = False

    @staticmethod
    async def sleep(delay: float) -> asyncio.Future:
        return await asyncio.sleep(delay * TIME_MODIFIER)

    async def manage_request(self, request: str) -> str:
        task_duration = 0.0
        # Activity change
        if self.last_activity and self.last_activity != request:
            task_duration += 5.0
        self.last_activity = request
        # Activity process
        if request == FOO_MINING_REQUEST:
            task_duration += 1.0
            response = FOO_MINING_RESPONSE
        elif request == BAR_MINING_REQUEST:
            task_duration += random.uniform(a=0.5, b=2.0)
            response = BAR_MINING_RESPONSE
        elif request == FOO_BAR_PROCESS_REQUEST:
            task_duration += 2.0
            success = random.random() > 0.4
            if success:
                response = FOO_BAR_PROCESS_SUCCESS_RESPONSE
            else:
                response = FOO_BAR_PROCESS_FAILURE_RESPONSE
        elif request == FOO_BAR_SELL_REQUEST:
            task_duration += 10.0
            response = FOO_BAR_SELL_RESPONSE
        elif request == BUY_ROBOT_REQUEST:
            response = BUY_ROBOT_RESPONSE
        else:
            raise ValueError(f"Unknown request: {request}")
        await self.sleep(delay=task_duration)
        return response


if __name__ == "__main__":
    manager = Manager()
    manager.add_robot()
    manager.add_robot()
    manager.run()
