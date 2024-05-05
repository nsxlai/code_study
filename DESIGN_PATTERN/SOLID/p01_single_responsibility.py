# https://medium.com/@severinperez/writing-flexible-code-with-the-single-responsibility-principle-b71c4f3f883f
# The code was originally written in Ruby
HEADER_LEN = 65


class SpaceStation:
    # attr_reader :sensors, :supply_hold, :supply_reporter,
    # :fuel_tank, :fuel_reporter, :thrusters

    def __init__(self):
        self.sensors = Sensors()
        self.supply_hold = SupplyHold()
        self.supply_reporter = SupplyReporter(self.supply_hold)
        self.fuel_tank = FuelTank()
        self.fuel_reporter = FuelReporter(self.fuel_tank)
        self.thrusters = Thrusters(self.fuel_tank)


class Sensors:
    def run_sensors(self):
        print(" Sensor Action ".center(HEADER_LEN, '-'))
        print("Running sensors!")


class SupplyHold:
    def __init__(self):
        self.supplies = {}

    def __repr__(self):
        return f'Current supplies available: {self.supplies}'

    def get_supplies(self, ptype):
        print(" Supply Action ".center(HEADER_LEN, '-'))
        if self.supplies.get(ptype, None):
            print(f'Current supply hold on {ptype}: {self.supplies[ptype]}')
        else:
            print(f'There is no supply hold on {ptype}')

    def load_supplies(self, ptype, quantity):
        print(" Supply Action ".center(HEADER_LEN, '-'))
        if ptype == 'fuel':
            print('Use the fuel_tank.load_fuel instead')
            return

        print(f"Loading {quantity} units of {ptype} in the supply hold.")

        if self.supplies.get(ptype, None):
            self.supplies[ptype] += quantity
        else:
            self.supplies.setdefault(ptype, quantity)

    def use_supplies(self, ptype, quantity):
        print(" Supply Action ".center(HEADER_LEN, '-'))
        if self.supplies.get(ptype, None):
            if self.supplies[ptype] >= quantity:
                print(f"Using {quantity} of {ptype} from the supply hold.")
                self.supplies[ptype] -= quantity
            else:
                print(f"Supply Error: Insufficient {ptype} in the supply hold.")
        else:
            print(f'There is no supply hold on {ptype}')


class FuelTank:
    def __init__(self):
        self.fuel = 0

    def __repr__(self):
        return f'Current fuel level: {self.fuel} unit'

    def get_fuel(self):
        return self.fuel

    def get_fuel_levels(self):
        print(" Fuel Action ".center(HEADER_LEN, '-'))
        print(f'{self.fuel} units of fuel available')

    def load_fuel(self, quantity):
        print(" Fuel Action ".center(HEADER_LEN, '-'))
        self.fuel += quantity
        print(f"Loading {quantity} units of fuel in the tank.")

    def use_fuel(self, quantity):
        print(" Fuel Action ".center(HEADER_LEN, '-'))
        self.fuel -= quantity
        print(f"Using {quantity} units of fuel from the tank.")


class Thrusters:
    FUEL_PER_THRUST = 10

    def __init__(self, fuel_tank: FuelTank):
        self.linked_fuel_tank = fuel_tank

    def activate_thrusters(self):
        print(" Thruster Action ".center(HEADER_LEN, '-'))

        if self.linked_fuel_tank.get_fuel() >= self.FUEL_PER_THRUST:
            print("Thrusting action successful.")
            self.linked_fuel_tank.use_fuel(self.FUEL_PER_THRUST)
        else:
            print("Thruster Error: Insufficient fuel available.")


class Reporter:
    def __init__(self, item: str, ptype: str):
        self.linked_item = item
        self.ptype = ptype

    def report(self):
        print(f"----- {self.ptype} Report -----")


class FuelReporter(Reporter):
    def __init__(self, item):
        super().__init__(item, "fuel")

    def report(self):
        print(" Fuel Report ".center(HEADER_LEN, '-'))
        print(f"{self.linked_item.get_fuel()} units of fuel available.")


class SupplyReporter(Reporter):
    def __init__(self, item):
        super().__init__(item, "supply")

    def report(self):
        print(" Supplies Report ".center(HEADER_LEN, '-'))
        if self.linked_item.supplies:
            for k, v in self.linked_item.supplies.items():
                # print(self.linked_item.supplies)
                print(f"{k}: {v} units available")
        else:
            print("Supply hold is empty.")


if __name__ == '__main__':
    iss = SpaceStation()

    iss.sensors.run_sensors()
    # Running sensors!

    iss.supply_hold.get_supplies("energy_converter")
    # There is no supply hold on energy_converter
    iss.supply_hold.use_supplies("energy_converter", 2)
    # There is no supply hold on energy_converter
    iss.supply_hold.load_supplies("energy_converter", 10)
    # Loading 10 units of parts in the supply hold.
    iss.supply_hold.use_supplies("energy_converter", 5)
    # Using 5 of parts from the supply hold.
    iss.supply_hold.use_supplies("energy_converter", 6)
    # Supply Error: Insufficient energy_converter in the supply hold.
    iss.supply_hold.get_supplies("energy_converter")
    # Current supply hold on energy_converter: 5 (did not execute earlier code)

    iss.supply_reporter.report()
    # energy_converter: 5 units available

    # print(iss.fuel_tank)
    iss.fuel_tank.get_fuel_levels()
    iss.fuel_tank.load_fuel(50)
    iss.fuel_reporter.report()
    iss.thrusters.activate_thrusters()
    iss.thrusters.activate_thrusters()
    iss.thrusters.activate_thrusters()
    iss.fuel_reporter.report()
    iss.thrusters.activate_thrusters()
    iss.thrusters.activate_thrusters()
    iss.thrusters.activate_thrusters()
    iss.fuel_reporter.report()

