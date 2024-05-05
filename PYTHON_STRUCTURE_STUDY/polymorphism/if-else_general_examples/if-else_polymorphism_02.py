"""
source: https://levelup.gitconnected.com/if-else-is-a-poor-mans-polymorphism-ab0b333b7265

Original code (in C#):

public enum UserUpdateReason {
  AddressChanged,
  UsernameChanged,
  EmailChanged,
  EnableTwoFactor,
}

// Inside UserRepository Class
public async Task UpdateAsync(UserUpdateReason reason, User user) {
  if (reason == UserUpdateReason.AddressChanged) {
    // Update user info in the database
  } else if (reason == UserUpdateReason.UsernameChanged) {
    // Update user info in the database
  } else if (reason == UserUpdateReason.EmailChanged) {
    // Update user info in the database
  } else if (reason == UserUpdateReason.EnableTwoFactor) {
    // Update user info in the database
  } else {
    throw new ArgumentException(($"Unknown {nameof(reason)}");
  }
"""


from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class User:
    address: str
    username: str
    email: str
    TwoFactorAuth: bool


class IUpdateReason(ABC):
    @abstractmethod
    def UpdateAsync(self, user):
        pass


class AddressChanged(IUpdateReason):
    def UpdateAsync(self, user: User, info: str):
        user.address = info
        print(f'{user.username} address changed')


class UsernameChanged(IUpdateReason):
    def UpdateAsync(self, user: User, info: str):
        user.username = info
        print(f'{user.username} username changed')


class EmailChanged(IUpdateReason):
    def UpdateAsync(self, user: User, info: str):
        user.email = info
        print(f'{user.username} email changed')


class EnableTwoFactor(IUpdateReason):
    def UpdateAsync(self, user: User, info: bool):
        user.TwoFactorAuth = info
        print(f'{user.username} Two Factor Auth is updated')


class masterDB:
    def __init__(self):
        self.userInfo = []

    def add_user(self, user: User):
        self.userInfo.append(user)

    def show_user(self):
        for user in self.userInfo:
            print(f'{user}')

    def updateDB(self, updateReason: IUpdateReason, user: User, info: Any):
        updateReason.UpdateAsync(user, info)


if __name__ == '__main__':
    user1 = User('123 A St', 'John', 'john@email.com', False)
    user2 = User('456 B St', 'Lisa', 'lisa@email.com', True)
    user3 = User('789 C St', 'Kelly', 'kelly@email.com', False)
    m = masterDB()
    m.add_user(user1)
    m.add_user(user2)
    m.add_user(user3)
    m.show_user()
    m.updateDB(EmailChanged(), user1, 'john@abc.com')
    m.updateDB(EnableTwoFactor(), user3, True)
    m.updateDB(UsernameChanged(), user2, 'Lizzy')
    m.updateDB(AddressChanged(), user2, '3456 Z St.')
    m.show_user()
