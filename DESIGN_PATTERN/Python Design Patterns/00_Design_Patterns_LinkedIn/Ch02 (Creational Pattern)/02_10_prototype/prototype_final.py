import copy


class Prototype:
    def __init__(self):
        self._objects = {}
        
    def register_object(self, name, obj):
        """Register an object"""
        self._objects[name] = obj
        
    def unregister_object(self, name):
        """Unregister an object"""
        del self._objects[name]
        
    def clone(self, name, **attr):
        """Clone a registered object and update its attributes"""
        obj = copy.deepcopy(self._objects.get(name))
        obj.__dict__.update(attr)
        return obj


class Car:
    def __init__(self, color):
        self.name = "Skylark"
        self.color = color
        self.options = "Ex"
        
    def __str__(self):
        return '{} | {} | {}'.format(self.name, self.color, self.options)


if __name__ == '__main__':
    c = Car('Red')
    prototype = Prototype()
    prototype.register_object('skylark', c)

    c1 = prototype.clone('skylark')
    print(c1)

    c2 = prototype.clone('skylark')
    print(c2)

    c = Car('Blue')
    # prototype.unregister_object('skylark')
    # prototype = Prototype()
    prototype.register_object('skylark', c)
    c1 = prototype.clone('skylark')
    print(c1)
    c2 = prototype.clone('skylark')
    print(c2)
