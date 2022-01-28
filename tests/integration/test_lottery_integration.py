from brownie import network
import pytest
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, get_account, fund_with_link
from scripts.deploy_lottery import deploy_lottery
import time


def test_can_pick_winner():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    transaction.wait(2)
    i = 0
    # looping for one hour (360 loops), waiting for random number
    while lottery.randomness() == 0 and i < 360:
        time.sleep(10)
        i += 1
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
