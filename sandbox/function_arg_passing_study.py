

# =============== RealPython Example =======================
def concatenate(**kwargs):
    result = ""
    # Iterating over the keys of the Python kwargs dictionary
    for arg in kwargs:
        result += arg
    return result
# =============== End of Example ===========================


# =============== Part 1 ===================================
def functional_test1(test_name,
                     module=False,
                     timeout=1800,
                     hardware_check=False,
                     retry=0,
                     skip_fail=False,
                     skip_fail_pars_list=False):
    """This is horrible function construction;
          1. multiple argument inputs
          2. pass boolean as argument
          3. should be handled as a class"""
    print(f'test name = {test_name}')
    print(f'module = {module}')
    print(f'timeout = {timeout}')
    print(f'hardware_check = {hardware_check}')
    print(f'retry = {retry}')
    print(f'skip_fail = {skip_fail}')
    print(f'skip_fail_pars_list = {skip_fail_pars_list}')

    result = set_state()
    if not result and not skip_fail:
        raise ValueError('Error found: {}'.format('invalid test'))
    return True


def set_state():
    return True
# =============== End of Part 1 ============================


# =============== Part 2 ===================================
def default_arg(func):
    def wrapper(test_name, **kwargs):
        status = functional_test2(test_name, **kwargs)
        return status
    return wrapper


def functional_test2(test_name, **kwargs):
    print(f'kwargs = {kwargs}')
    print(f'test name = {test_name}')
    print(f'module = {kwargs["module"]}')

    for key, value in kwargs.items():
        print(f'{key} = {value}')

    result = set_state()
    if not result and not kwargs['skip_fail']:
        raise ValueError('Error found: {}'.format('invalid test'))
    return True
# =============== End of Part 2 ============================


# =============== Part 3 ===================================
class default_args:
    def __init__(self, test_name):
        self.test_name = test_name
        self.module = False
        self.timeout = 1800
        self.hardware_check = False
        self.retry = 0
        self.skip_fail = False
        self.skip_fail_pars_list = False


def functional_test3(test_name):
    arg_obj = default_args(test_name)
    print(f'test name = {arg_obj.test_name}')
    print(f'module = {arg_obj.module}')
    print(f'timeout = {arg_obj.timeout}')
    print(f'hardware_check = {arg_obj.hardware_check}')
    print(f'retry = {arg_obj.retry}')
    print(f'skip_fail = {arg_obj.skip_fail}')
    print(f'skip_fail_pars_list = {arg_obj.skip_fail_pars_list}')

    result = set_state()
    if not result and not arg_obj.skip_fail:
        raise ValueError('Error found: {}'.format('invalid test'))
    return True
# =============== End of Part 3 ============================


# =============== Part 4 ===================================
class gen_args:
    def __init__(self):
        self._test_name = ''
        self.module = False
        self.timeout = 1800
        self.hardware_check = False
        self.retry = 0
        self.skip_fail = False
        self.skip_fail_pars_list = False

    @property
    def test_name(self):
        return self._test_name

    @test_name.setter
    def test_name(self, name):
        self._test_name = name


def functional_test4():
    print(f'test name = {product.test_name}')
    print(f'module = {product.module}')
    print(f'timeout = {product.timeout}')
    print(f'hardware_check = {product.hardware_check}')
    print(f'retry = {product.retry}')
    print(f'skip_fail = {product.skip_fail}')
    print(f'skip_fail_pars_list = {product.skip_fail_pars_list}')

    result = set_state()
    if not result and not product.skip_fail:
        raise ValueError('Error found: {}'.format('invalid test'))
    return True
# =============== End of Part 4 ============================


if __name__ == '__main__':
    # Example from RealPython;
    # test = dict(a="Real", b="Python", c="Is", d="Great", e="!")
    # print(concatenate(**test))

    # Part 1: Original code structure - Horrible
    # status = functional_test1('CPU test')

    # Part 2: Update 1 code structure - Better
    # kwargs = {'module': False, 'timeout': 1800, 'hardware_check': False, 'retry': 0,
    #           'skip_fail': False, 'skip_fail_pars_list': False}
    # kwargs=dict(module=False, timeout=1800, hardware_check=False, retry=0, skip_fail=False, skip_fail_pars_list=False)
    # status = functional_test2('CPU test', **kwargs)

    # Part 3: Update code into a class structure
    # print(functional_test3('CPU test'))

    # Part 4: Update the default_arg class into more general implementation
    product = gen_args()  # Global product instance instantiation. No need to pass it to the functional_test4 function
    product.test_name = 'CPU_test'
    print(functional_test4())

    product.test_name = 'MEM_test'
    print(functional_test4())
