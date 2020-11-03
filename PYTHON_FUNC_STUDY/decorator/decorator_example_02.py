# source: https://medium.com/better-programming/decorators-in-python-72a1d578eac4

def say(func):

    def employer():
        print("Say something about you.")

    def say_name():
        print("My name is Guido van Rossum.")

    def say_nationality():
        print("I am from Netherlands.")

    def wrapper():
        employer()
        say_name()
        say_nationality()
        func()
    return wrapper


@say
def start_interview():
    print("Real interview Started...")


if __name__ == '__main__':
    start_interview()
