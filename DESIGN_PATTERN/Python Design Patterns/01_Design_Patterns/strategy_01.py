class StrategyExample:

    def __init__(self, func=None):
        if func:
            self.execute = func

    def execute(self):
        print("Original execution")


def executeReplacement1(self):
    print("Strategy 1")


def executeReplacement2(self):
    print("Strategy 2")


if __name__ == "__main__":
    strat0 = StrategyExample()
    strat1 = StrategyExample(executeReplacement1)
    strat2 = StrategyExample(executeReplacement2)

    strat0.execute()
    strat1.execute()
    strat2.execute()
