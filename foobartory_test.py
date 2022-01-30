import asyncio
import unittest

from foobartory import (
    BAR_MINING_REQUEST,
    BUY_ROBOT_REQUEST,
    BUY_ROBOT_RESPONSE,
    FOO_BAR_PROCESS_REQUEST,
    FOO_BAR_SELL_REQUEST,
    FOO_MINING_REQUEST,
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


if __name__ == "__main__":
    unittest.main()
