# 0.019
# 190000000000000000
from logging import exception
from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import fund_with_link, get_contract
from web3 import Web3
import pytest

from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENV, get_account


def test_get_entrance_fee():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    # Act
    # 2,000 eth / usd
    # usdEntryFee is $50
    # 2000/1 == 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Assert
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_is_winner_picked_correctly():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    for i in range(1, 3):
        lottery.enter({"from": get_account(index=i), "value": lottery.getEntranceFee()})
    # ACT
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777

    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    # ASSERT
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == balance_of_lottery + starting_balance_of_account
