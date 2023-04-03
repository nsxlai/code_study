# source: https://stackoverflow.com/questions/48359957/pytest-with-argparse-how-to-test-user-is-prompted-for-confirmation
import sys
import argparse


def confirm():
    notification_str = "Please respond with 'y' or 'n'"
    while True:
        choice = input("Confirm [Y/n]? ").lower()
        if choice == 'yes' or not choice:  # Original code: choice in 'yes'; this is a bug
            print('Confirmed!')            # If user enters 'e' or 's', this will be "confirmed" as well.
            return True
        if choice == 'no':
            print('Not confirmed!')
            return False
        print(notification_str)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--destructive', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args(sys.argv[1:])
    if args.destructive:
        if not confirm():
            sys.exit()


if __name__ == '__main__':
    main()

