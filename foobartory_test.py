import asyncio
import unittest

from foobartory import (
    BAR_MINING_REQUEST,
    BAR_MINING_RESPONSE,
    BUY_ROBOT_REQUEST,
    BUY_ROBOT_RESPONSE,
    FOO_BAR_PROCESS_FAILURE_RESPONSE,
    FOO_BAR_PROCESS_REQUEST,
    FOO_BAR_PROCESS_SUCCESS_RESPONSE,
    FOO_BAR_SELL_REQUEST,
    FOO_BAR_SELL_RESPONSE,
    FOO_MINING_REQUEST,
    FOO_MINING_RESPONSE,
    Manager,
    Robot,
)


class TestManager(unittest.TestCase):
    def test_next_action_should_be_to_mine_foo(self):
        manager = Manager()
        assert manager.determine_next_activity() == FOO_MINING_REQUEST
        assert manager.foo_cnt == 0  # no foo yet

    def test_next_action_should_be_to_mine_bar(self):
        manager = Manager()
        manager.foo_cnt = 1
        assert manager.determine_next_activity() == BAR_MINING_REQUEST
        assert manager.foo_cnt == 1  # should not be changed
        assert manager.bar_cnt == 0  # no bar yet

    def test_next_action_should_be_to_process_foo_bar(self):
        manager = Manager()
        manager.foo_cnt = 1
        manager.bar_cnt = 1
        assert manager.determine_next_activity() == FOO_BAR_PROCESS_REQUEST

    def test_next_action_should_be_to_sell_foo_bar(self):
        manager = Manager()
        manager.foobar_cnt = 5
        assert manager.determine_next_activity() == FOO_BAR_SELL_REQUEST

    def test_next_action_should_be_to_buy_robot(self):
        manager = Manager()
        manager.foo_cnt = 6
        manager.money = 3
        assert manager.determine_next_activity() == BUY_ROBOT_REQUEST


class TestRobot(unittest.TestCase):
    async def sleep_stub(self, **kwargs):
        self.sleep_kwargs = kwargs

    def setUp(self) -> None:
        self.manager = Manager()
        self.robot = Robot(manager=self.manager)
        self.robot.sleep = self.sleep_stub

    def test_manage_foo_mining_request(self):
        response = asyncio.get_event_loop().run_until_complete(
            future=self.robot.manage_request(FOO_MINING_REQUEST)
        )
        assert self.sleep_kwargs["delay"] == 1.0
        assert response == FOO_MINING_RESPONSE

    def test_manage_bar_mining_request(self):
        response = asyncio.get_event_loop().run_until_complete(
            future=self.robot.manage_request(BAR_MINING_REQUEST)
        )
        assert 0.5 < self.sleep_kwargs["delay"] < 2.0
        assert response == BAR_MINING_RESPONSE

    def test_manage_foo_bar_process_request(self):
        response = asyncio.get_event_loop().run_until_complete(
            future=self.robot.manage_request(FOO_BAR_PROCESS_REQUEST)
        )
        assert self.sleep_kwargs["delay"] == 2.0
        assert (
            response == FOO_BAR_PROCESS_SUCCESS_RESPONSE
            or response == FOO_BAR_PROCESS_FAILURE_RESPONSE
        )

    def test_manage_foo_bar_sell_request(self):
        response = asyncio.get_event_loop().run_until_complete(
            future=self.robot.manage_request(FOO_BAR_SELL_REQUEST)
        )
        assert self.sleep_kwargs["delay"] == 10.0
        assert response == FOO_BAR_SELL_RESPONSE

    def test_manage_buy_robot_request(self):
        response = asyncio.get_event_loop().run_until_complete(
            future=self.robot.manage_request(BUY_ROBOT_REQUEST)
        )
        assert response == BUY_ROBOT_RESPONSE


if __name__ == "__main__":
    unittest.main()
