class Employee:
    def __init__(self, password, pay, balance):
        self.password = password
        self.pay = pay
        self.balance = balance

    def pay_money(self):
        self.balance += self.pay

    def __pay_money(self):
        # double underscore will turn this method into private method (not accessible from outside)
        self.balance += self.pay

    def display_balance(self):
        print(f'Balance is {self.balance}')

    def confirm_pass(self, pswd):
        if pswd == self.password:
            self.pay_money()
        else:
            print("Incorrect password!")

    def confirm_pass1(self, pswd):
        if pswd == self.password:
            self.__pay_money()
        else:
            print("Incorrect password!")


if __name__ == '__main__':
    e = Employee('test', 25, 0)
    e.display_balance()
    print('Add to balance from confirm_pass')
    e.confirm_pass('test')
    e.display_balance()
    e.confirm_pass('badPassword')
    e.display_balance()
    print('Supplied bad password and balance stayed the same; however, if access pay_money method directly:')
    e.pay_money()
    e.display_balance()
    try:
        e.__pay_money1()
    except AttributeError:
        print('AttributeError from accessing private method')
    e.display_balance()
    e.confirm_pass1('test')
    e.display_balance()

