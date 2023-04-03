class Subject:  # Represents what is being 'observed'
    def __init__(self):
        """
        This where references to all the observers are being kept
        Note that this is a one-to-many relationship: there will be one subject to be observed by multiple _observers
        """
        self._observers = []

    def attach(self, observer):
        """
        If the observer is not already in the observers list, append the observer to the list
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """
        Simply remove the observer
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, modifier=None):
        """
        For all the observers in the list, don't notify the observer who is actually updating the temperature and
        alert the observers!
        """
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class Core(Subject):
    def __init__(self, name=''):
        Subject.__init__(self)
        self._name = name
        self._temp = 0

    @property
    def temp(self):
        return self._temp

    @temp.setter
    def temp(self, temp):
        self._temp = temp
        self.notify()


class TempViewer:
    def __init__(self, name):
        self.name = name

    def update(self, subject):
        """
        Alert method that is invoked when notify() method in a concrete subject is invoked
        """
        print(f"Temperature Viewer {self.name}: {subject._name} has Temperature {subject._temp}")


if __name__ == '__main__':
    # Let's create our subjects
    c1 = Core("Core 1")
    c2 = Core("Core 2")

    # Let's create our observers
    v1 = TempViewer('v1')
    v2 = TempViewer('v2')

    # Let's attach our observers to the first core
    c1.attach(v1)
    c1.attach(v2)
    print(f'{c1._observers = }')

    # Let's change the temperature of our first core
    c1.temp = 80
    c1.temp = 90
    c1.temp = 95
    c1.temp = 100
