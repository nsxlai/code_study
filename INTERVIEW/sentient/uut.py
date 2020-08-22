import product_lib


def base_product_class():
    sn_list = ['ROC11111111', 'ROC22222222', 'ROC33333333', 'ROC44444444', 'ROC55555555',
               'ROC66666666', 'ROC77777777', 'ROC88888888', 'ROC99999999', 'ROC10101010']
    uut_list = []
    for i in range(len(sn_list)):
        uut = product_lib.BaseProduct(sn_list[i], 'POWER-001A')
        uut_list.append(uut)
    for uut in uut_list:
        print(uut.product_display())
    return uut_list


if __name__ == '__main__':
    uut_list = base_product_class()
    filtered_uut_list = [uut.serial_number for uut in uut_list if int(uut.serial_number[-2:]) % 2 != 0]
    print(filtered_uut_list)
