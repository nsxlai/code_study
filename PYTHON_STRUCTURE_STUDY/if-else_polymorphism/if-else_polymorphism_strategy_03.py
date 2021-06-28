"""
source: https://levelup.gitconnected.com/remove-your-if-else-and-switch-cases-1ed2b625b4cf

The basis of the if-else substitution is using polymorphism and strategy design pattern
"""
import time
import types
from typing import Any
from abc import ABC, abstractmethod


class AccountState:
    """ Python Enum implementation
        The output for the enum type is actually the value assign to the variable. For example:
        a = AccountState.open   => The value of a is 1
    """
    open = 1
    closed = 2
    frozen = 3


class Username:
    def __init__(self, name: str):
        if len(name) == 0:
            raise ValueError('Must have a value')
        if len(name) > 50:
            raise ValueError('Cannot exceed 50 character')
        self.name = name


class Account_attribute:
    def __init__(self, user: Username, balance: int, isOverDraftAllowed: bool, account_state: int):  # AccountState=int
        self.user = user
        self.CurrentBalance = balance
        self.isOverDraftAllowed = isOverDraftAllowed
        self.State = account_state


class Account_original_code:
    def __init__(self, attr: Account_attribute):
        self.attr = attr
        self.CurrentBalance = attr.CurrentBalance
        self.isOverDraftAllowed = attr.isOverDraftAllowed
        self.State = attr.State

    def account_display(self):
        print(f'Current account for {self.attr.user.name} is {self.CurrentBalance}')

    def withdrawAmount(self, amount: int) -> None:
        if self.State == AccountState.open:
            if amount > self.CurrentBalance:
                if self.isOverDraftAllowed:
                    self.CurrentBalance -= amount
                else:
                    raise ValueError('Overdraft not allowed!')
            else:
                self.CurrentBalance -= amount
        elif self.State == AccountState.closed:
            raise ValueError('Account is closed')
        elif self.State == AccountState.frozen:
            raise ValueError('Account is frozen')


class AccountStateInterface(ABC):
    @abstractmethod
    def withdrawAmount(self, amount: int):
        pass


class Open(AccountStateInterface):
    def withdrawAmount(self, amount: int):
        if amount > self.CurrentBalance and not self.isOverDraftAllowed:
            raise ValueError('Overdraft is not allowed')
        self.CurrentBalance -= amount


class Closed(AccountStateInterface):
    def withdrawAmount(self, amount: int):
        raise ValueError('Account is closed')


class Frozen(AccountStateInterface):
    def withdrawAmount(self, amount: int):
        raise ValueError('Account is Frozen')


class Account_code_with_strategy_patttern:
    """
    Use the strategy pattern to replace the withdrawAmount method with specific ones. This move all the if-else
    to the interface classes instead of the 'Christmas Tree' if-else pattern
    """
    def __init__(self, attr: Account_attribute):
        self.attr = attr
        self.CurrentBalance = attr.CurrentBalance
        self.isOverDraftAllowed = attr.isOverDraftAllowed
        self.State = attr.State
        if self.State == AccountState.open:
            self.withdrawAmount = types.MethodType(Open.withdrawAmount, self)
        elif self.State == AccountState.closed:
            self.withdrawAmount = types.MethodType(Closed.withdrawAmount, self)
        elif self.State == AccountState.frozen:
            self.withdrawAmount = types.MethodType(Frozen.withdrawAmount, self)

    def account_display(self):
        print(f'Current account for {self.attr.user.name} is {self.CurrentBalance}')


def user_account(Account: Any):
    user_account_attribute = {'user': Username('John'),
                              'balance': 100,
                              'isOverDraftAllowed': True,
                              'account_state': AccountState.open}
    user_acc = Account_attribute(**user_account_attribute)
    user_activity = Account(user_acc)
    user_activity.withdrawAmount(50)
    user_activity.account_display()
    time.sleep(0.5)
    user_activity.withdrawAmount(100)
    user_activity.account_display()


if __name__ == '__main__':
    print(' Account_original_code '.center(60, '-'))
    user_account(Account_original_code)
    print(' Account_code_with_strategy_pattern '.center(60, '-'))
    user_account(Account_code_with_strategy_patttern)
    print(f'{type(AccountState.open) = }')
    print(f'{type(AccountEnum.open) = }')
