# Sample HW config
[component]
name = 'hypothetical component'
host_ip_addr = '10.1.1.1'
username = 'super'
password = 'awesome'

[api]
header = 'http://thisisveryawesome:80'

[sw]
version = '1.23.04'
check_enable = true
kernel = '0.3.0'

[mcu]
id = 'Cortex A51'
freq = '1999999'

[flash]
size = '64mb'

[eeprom]
size = '32kb'

[temp.sensor.i2c]
sensor_1 = '0x45'
sensor_2 = '0x46'
sensor_3 = '0x47'
sensor_4 = '0x48'

[vrail_1]
nominal = 0.850
low_limit = 0.80
high_limit = 0.90
multipler = 1
name = 'vcc'

[vrail_2]
nominal = 1.80
low_limit = 1.75
high_limit = 1.85
multipler = 1
name = 'vaux'

[vrail_3]
nominal = 2.5
low_limit = 2.45
high_limit = 2.55
multipler = 2
name = '5v_logic'