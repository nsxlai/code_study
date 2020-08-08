from .p01_single_responsibility import SpaceStation
from pytest import mark


def test_sensors():
    iss = SpaceStation()
    assert iss.sensors.run_sensors() == None


def test_supplies_add_items():
    iss = SpaceStation()
    iss.supply_hold.get_supplies("tricorder")
    sh = iss.supply_hold
    assert sh == 'Current supplies available: {}'


    # iss.supply_hold.use_supplies("tricorder", 2)
    # iss.supply_hold.load_supplies("tricorder", 10)
    # iss.supply_hold.get_supplies("energy_converter")