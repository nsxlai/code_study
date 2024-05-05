# -------------------- With classes --------------------


class AUsefulThing:
    def __init__(self, aStrategicAlternative):
        self.howToDoX = aStrategicAlternative

    def doX(self, someArg):
        self. howToDoX.theAPImethod(someArg, self)


class StrategicAlternative:
    pass


class AlternativeOne(StrategicAlternative):
    def theAPIMethod(self, someArg, theUsefulThing):
        pass  # an implementation


class AlternativeTwo(StrategicAlternative):
    def theAPIMethod(self, someArg, theUsefulThing):
        pass  # another implementation


t = AUsefulThing(AlternativeOne())
t.doX('arg')
