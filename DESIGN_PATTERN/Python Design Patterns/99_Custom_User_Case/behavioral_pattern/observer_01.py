"""
source: https://towardsdatascience.com/understand-machine-learning-through-more-design-patterns-9c8430fd2ae8
"""
from abc import ABC, abstractmethod


class Observable:
    models_list = []

    def add_model(self, observer):
        self.models_list.append(observer)

    def notify_models(self, data):
        for model in self.models_list:
            model.update(data)


class Data(Observable):
    __data = None

    def __init__(self, data):
        self.__data = data

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data, drift = None):
        # drift informs us of the necessity to re-fit the models
        self.__data = data
        if drift:
            print('There is a drift !')
            self.notify_models(data)


class ModelObserver(ABC):
    @property
    def model(self):
        raise NotImplementedError

    def fit(self, train_data):
        self.model.fit(*train_data)

    @abstractmethod
    def update(self, observable):
        pass


class DT(ModelObserver):
    model = DecisionTreeRegressor()

    def update(self, observable):
        print("Refitting the Decision Tree Regressor model ..")
        self.model.fit(*observable)


class KNR(ModelObserver):
    model = KNeighborsRegressor()

    def update(self, observable):
        print("Refitting the K Neighbors Regressor model ..")
        self.model.fit(*observable)


if __name__ == '__main__':
    # Data class
    data_before_drift = Data((X_train, y_train))

    # Model observers
    dt = DT()
    dt.fit(data_before_drift.data)

    knr = KNR()
    knr.fit(data_before_drift.data)

    data_before_drift.add_model(dt)
    data_before_drift.add_model(knr)
