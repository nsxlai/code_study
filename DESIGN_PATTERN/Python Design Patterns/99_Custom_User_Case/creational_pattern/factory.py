class uut:
    def __init__(self):
        self._sn = None
        self._mac = None
        self._pid = None
        self._hw_type = None

    def __repr__(self):
        out = f'Product detail:\n' \
              f'   1. SN = {self._sn}\n' \
              f'   2. MAC = {self._mac}\n' \
              f'   3. PID = {self._pid}\n' \
              f'   4. HW TYPE = {self._hw_type}\n'
        return out

    def get_info(self):
        return self._pid


class queenspark_24(uut):
    def __init__(self, sn, mac):
        self._sn = sn
        self._mac = mac
        self._pid = 'queenspark_24'
        self._hw_type = 'M4'


class queenspark_36(uut):
    def __init__(self, sn, mac):
        self._sn = sn
        self._mac = mac
        self._pid = 'queenspark_24'
        self._hw_type = 'M4'


class olympia_40(uut):
    def __init__(self, sn, mac):
        self._sn = sn
        self._mac = mac
        self._pid = 'olympia_40'
        self._hw_type = 'M5'


class olympia_48(uut):
    def __init__(self, sn, mac):
        self._sn = sn
        self._mac = mac
        self._pid = 'olympia_48'
        self._hw_type = 'M5'


class knightsbridge_56(uut):
    def __init__(self, sn, mac):
        self._sn = sn
        self._mac = mac
        self._pid = 'knightsbridge_56'
        self._hw_type = 'M5'


class uutFactory:
    # @staticmethod (original)
    @classmethod
    def create_uut(cls, uut):
        if uut[0] == 'queenspark_24':
            return queenspark_24(uut[1], uut[2])
        elif uut[0] == 'queenspark_36':
            return queenspark_36(uut[1], uut[2])
        elif uut[0] == 'olympia_40':
            return olympia_40(uut[1], uut[2])
        elif uut[0] == 'olympia_48':
            return olympia_48(uut[1], uut[2])
        elif uut[0] == 'knightsbridge_56':
            return knightsbridge_56(uut[1], uut[2])


if __name__ == '__main__':
    uut_list = [('queenspark_24', 123, 'ff1a'), ('knightsbridge_56', 456, 'ff1d'), ('olympia_40', 743, 'ff1e'),
                ('olympia_48', 358, 'ffe2'), ('queenspark_36', 934, 'ff03'), ('olympia_48', 568, 'ff81')]
    # uut_obj = []
    # for index, uut_detail in enumerate(uut_list):
    #     uut_obj[index] = uutFactory.create_uut(uut_detail)
    #
    # print(uut_obj[0])
    uut = uutFactory.create_uut(uut_list[0])
    print(uut)
    print(uut.get_info())