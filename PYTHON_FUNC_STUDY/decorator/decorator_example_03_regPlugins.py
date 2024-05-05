# source: https://medium.com/better-programming/decorators-in-python-72a1d578eac4

PLUGINS = dict()


def register(enable: bool):
    def register_func(func):
        if enable:
            PLUGINS[func.__name__] = func
        return func
    return register_func


@register(enable=True)
def add(a, b):
    return a + b


@register(enable=True)
def subtract(a, b):
    return a - b


@register(enable=True)
def multiply(a, b):
    return a * b


@register(enable=False)
def divide(a, b):
    return a / b


def operation(func_name, a, b):
    func = PLUGINS[func_name]
    return func(a, b)


if __name__ == '__main__':
    print(PLUGINS)
    print(f"{operation('add', 2, 3) = }")
    print(f"{operation('subtract', 2, 3) = }")
    print(f"{operation('multiply', 2, 3) = }")

    # Divide function is not registered and cannot perform this operation
    print(f"{operation('divide', 2, 3) = }")
