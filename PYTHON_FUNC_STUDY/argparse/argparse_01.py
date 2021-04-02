import argparse


# Create the parser
my_parser = argparse.ArgumentParser(description='IPERF3 custom arguments')

# Add the arguments
my_parser.add_argument('-t', '--time', type=int, help='IPERF runtime')
my_parser.add_argument('-q', '--qos', type=bool, help='IPERF QoS enabled')
my_parser.add_argument('--pattern', type=int, help='IPERF predefined QoS pattern of either 0 or 1')
my_parser.add_argument('--ports', type=int, help='IPERF number of ports sent from the client; min=1 and max=24 ports')

# Execute the parse_args() method
args = my_parser.parse_args()

print(args.time)
print(args.qos)
print(args.pattern)
print(args.ports)