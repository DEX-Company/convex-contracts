"""

    Test Convex ddo register contract for starfish

"""

import pytest
import secrets

from convex_api import (
    Account as ConvexAccount,
    ConvexAPI
)
from convex_api.exceptions import ConvexAPIError

from convex_contracts.contracts.ddo_registry_contract import DDORegistryContract
from tests.helpers import (
    topup_accounts,
    deploy_contract
)

is_contract_deployed = False
TEST_CONTRACT_NAME = 'starfish-test.ddo'

@pytest.fixture
def ddo_contract(convex, account_import):
    global is_contract_deployed
    contract = DDORegistryContract(convex, TEST_CONTRACT_NAME)
    deploy_contract(convex, contract, account_import, is_contract_deployed)
    is_contract_deployed = True
    return contract


def test_contract_version(convex, ddo_contract):
    deploy_version = ddo_contract.deploy_version
    assert(deploy_version)
    assert(deploy_version == ddo_contract.version)


def test_contract_did_register_assert_did(convex, ddo_contract, accounts):

    topup_accounts(convex, accounts)

    account_test = accounts[0]
    did_bad = secrets.token_hex(20)
    did_valid = secrets.token_hex(32)
    ddo = 'test - ddo'
    command = f'(register "{did_bad}" "{ddo}")'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = ddo_contract.send(command, account_test)

    command = f'(register "" "{ddo}")'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = ddo_contract.send(command, account_test)

    command = f'(register 42 "{ddo}")'
    with pytest.raises(ConvexAPIError, match='INVALID'):
        result = ddo_contract.send(command, account_test)

    command = f'(register 0x{did_valid} "{ddo}")'
    result = ddo_contract.send(command, account_test)
    assert(result['value'])
    assert(result['value'] == did_valid)


def test_contract_did_register_resolve(convex, ddo_contract, accounts):

    account_test = accounts[0]
    account_other = accounts[1]

    topup_accounts(convex, accounts)

    did_hex = secrets.token_hex(32)
    did = f'0x{did_hex}'
    ddo = 'test - ddo'


    # call register

    command = f'(register {did} "{ddo}")'
    result = ddo_contract.send(command, account_test)
    assert(result['value'])
    assert(result['value'] == did_hex)

    # call resolve did to ddo

    command = f'(resolve {did})'
    result = ddo_contract.query(command)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call resolve did to ddo on other account

    command = f'(resolve {did})'
    result = ddo_contract.query(command)
    assert(result['value'])
    assert(result['value'] == ddo)

    # call owner? on owner account
    command = f'(owner? {did})'
    result = ddo_contract.query(command, account_test)
    assert(result['value'])

    # call owner? on owner account_other
    command = f'(owner? {did})'
    result = ddo_contract.query(command, account_other)
    assert(not result['value'])

    # call resolve unknown
    bad_did = f'0x{secrets.token_hex(32)}'
    command = f'(resolve {bad_did})'
    result = ddo_contract.query(command)
    assert(result['value'] is None)


    new_ddo = 'new - ddo'
    # call register - update

    command = f'(register {did} "{new_ddo}")'
    result = ddo_contract.send(command, account_test)
    assert(result['value'])
    assert(result['value'] == did_hex)


    # call register - update from other account

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(register {did} "{ddo}")'
        result = ddo_contract.send(command, account_other)


    # call resolve did to new_ddo

    command = f'(resolve {did})'
    result = ddo_contract.query(command)
    assert(result['value'])
    assert(result['value'] == new_ddo)


    # call unregister fail - from other account

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(unregister {did})'
        result = ddo_contract.send(command, account_other)


    # call unregister

    command = f'(unregister {did})'
    result = ddo_contract.send(command, account_test)
    assert(result['value'])
    assert(result['value'] == did_hex)

    # call resolve did to empty

    command = f'(resolve {did})'
    result = ddo_contract.query(command)
    assert(result['value'] is None)


    # call unregister - unknown did

    command = f'(unregister {bad_did})'
    result = ddo_contract.send(command, account_test)
    assert(result['value'] is None)



def test_contract_ddo_transfer(convex, ddo_contract, accounts):
    # register and transfer

    account_test = accounts[0]
    account_other = accounts[1]
    topup_accounts(convex, accounts)

    did_hex = secrets.token_hex(32)
    did = f'0x{did_hex}'
    ddo = 'test - ddo'

    command = f'(register {did} "{ddo}")'
    result = ddo_contract.send(command, account_test)
    assert(result['value'])
    assert(result['value'] == did_hex)

    # call owner? on owner account
    command = f'(owner? {did})'
    result = ddo_contract.query(command, account_test)
    assert(result['value'])

    # call owner? on account_other
    command = f'(owner? {did})'
    result = ddo_contract.query(command, account_other)
    assert(not result['value'])


    command = f'(transfer {did} {account_other.address})'
    result = ddo_contract.send(command, account_test)
    assert(result['value'])
    assert(result['value'][0] == did_hex)

    #check ownership to different accounts

    # call owner? on owner account
    command = f'(owner? {did})'
    result = ddo_contract.query(command, account_test)
    assert(not result['value'])

    # call owner? on account_other
    command = f'(owner? {did})'
    result = ddo_contract.query(command, account_other)
    assert(result['value'])

    # call unregister fail - from account_test (old owner)

    with pytest.raises(ConvexAPIError, match='NOT-OWNER'):
        command = f'(unregister {did})'
        result = ddo_contract.send(command, account_test)


    # call unregister from account_other ( new owner )

    command = f'(unregister {did})'
    result = ddo_contract.send(command, account_other)
    assert(result['value'])
    assert(result['value'] == did_hex)


def test_contract_ddo_bulk_register(convex, ddo_contract, accounts):
    account_test = accounts[0]

    for index in range(0, 2):
        topup_accounts(convex, account_test)
        did_hex = secrets.token_hex(32)
        did = f'0x{did_hex}'
#        ddo = secrets.token_hex(51200)
        ddo = secrets.token_hex(1024)

        command = f'(register {did} "{ddo}")'
        result = ddo_contract.send(command, account_test)
        assert(result['value'])
        assert(result['value'] == did_hex)


def test_contract_ddo_owner_list(convex, ddo_contract, accounts):

    account_test = accounts[0]
    account_other = accounts[1]

    did_list = []
    for index in range(0, 4):
        topup_accounts(convex, accounts)
        did_hex = secrets.token_hex(32)
        did = f'0x{did_hex}'
        did_list.append(did_hex)
#        ddo = secrets.token_hex(51200)
        ddo = f'ddo test - {index}'

        command = f'(register {did} "{ddo}")'
        result = ddo_contract.send(command, account_test)
        assert(result['value'])
        assert(result['value'] == did_hex)


    command = f'(owner-list {account_test.address})'
    result = ddo_contract.query(command)
    assert(result['value'])
    for did_hex in did_list:
        assert(did_hex in result['value'])

