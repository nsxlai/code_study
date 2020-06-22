import types  # Import the types module


class Strategy:
    """The Strategy Pattern class"""
    def __init__(self, function=None):
        self.name = "Default Strategy"
        
        # If a reference to a function is provided, replace the execute() method with the given function
        if function:
            self.execute = types.MethodType(function, self)
            
    # def execute(self):  # This gets replaced by another version if another strategy is provided.
    #     """The defaut method that prints the name of the strategy being used"""
    #     print("{} is used!".format(self.name))


def strategy_one(self):
    """Replacement method 1"""
    print("{} is used to execute method 1".format(self.name))


def strategy_two(self):
    """Replacement method 2"""
    print("{} is used to execute method 2".format(self.name))


if __name__ == '__main__':
    # Let's create our default strategy
    # s0 = Strategy()

    # Let's execute our default strategy
    # s0.execute()

    # Let's create the first variation of our default strategy by providing a new behavior
    s1 = Strategy(strategy_one)
    s1.name = "Strategy One"
    s1.execute()

    s2 = Strategy(strategy_two)
    s2.name = "Strategy Two"
    s2.execute()

