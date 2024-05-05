"""
source: https://medium.com/swlh/stop-using-if-else-statements-f4d2323e6e4

This is the original code
def Accept():
    if not isPending
        if price > Limits.MAX:
            # do this
        else:
            # do this
    elif isExpired:
        raise InvalidOperationException('is expired!')
    elif isCancelled:
        if isExpired and price > 1000:
            # email user to reactive booking
        elif not isExpired:
            # do this
    else:
        # do default action

Will refactor the code above to state machine using polymorphism (avoiding using if-else)

On the surface, this example is very close to the state machine; however, state machine requires all the states to
be defined in the beginning of the programming and follow a specific program run decision pattern (yes/no). Like
data storage tape. This code example does not require all the state to be defined at run time but rather user input
define what the next state is going to be.
"""
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any


class BookingStateBase(ABC):
    @abstractmethod
    def EnterState(self, booking: Any):
        pass

    @abstractmethod
    def Cancel(self, booking: Any, reason: str):
        pass

    @abstractmethod
    def Accept(self, booking: Any):
        pass


class Booking:
    def __init__(self, pid: str, attendeeName: str, state: BookingStateBase):
        self.pid = pid
        self.state = state
        self.AttendeeName = attendeeName
        self.BookingDate = datetime.now()

    @classmethod
    def createNew(cls, pid: str, attendeeName: str):
        cls.state = PendingState()  # Create new and immediately put into PendingState
        cls.state.EnterState(cls)
        return cls(pid, attendeeName, cls.state)

    def TransitionToState(self, newState: BookingStateBase):
        self.state = newState
        self.state.EnterState(self)

    def Accept(self):
        # Transition to the next state with Accept path
        self.state.Accept(self)

    def Cancel(self, cancellationReason: str):
        # Transition to the next state with Accept path
        self.state.Cancel(self, cancellationReason)


class PendingState(BookingStateBase):
    order_check = False

    def EnterState(self, booking: Booking):
        print('Enter => PendingState')
        print('Initiate Order check...')
        self.order_check = True  # In realistic development, someone input hook will be here to update order_check

    def Cancel(self, booking: Booking, reason: str):
        print('PendingState => Cancel')
        print(f'Cancellation reason: {reason}')
        booking.TransitionToState(CancelledState())

    def Accept(self, booking: Booking):
        if self.order_check:
            print('PendingState => Accept')
            booking.TransitionToState(ProcessedState())
        else:
            print('PendingState => Cancel')
            booking.TransitionToState(CancelledState())


class ProcessedState(BookingStateBase):
    def EnterState(self, booking: Booking):
        print('Enter => ProcessedState')
        print(f'PID = {booking.pid}')

    def Cancel(self, booking: Booking, reason: str):
        print('ProcessState => Cancel')
        print(f'PID = {booking.pid}')
        print(f'Cancellation reason: {reason}')
        booking.TransitionToState(CancelledState())

    def Accept(self, booking: Booking):
        print('ProcessState => Accept')
        print(f'PID = {booking.pid}')
        print('End of state; no more transition')


class CancelledState(BookingStateBase):
    def EnterState(self, booking: Booking):
        print('Enter => CancelledState')
        print(f'PID = {booking.pid}')

    def Cancel(self, booking: Booking, reason: str):
        # This method is there but not used because of the interface requirement. Cancel the cancelledState
        # doesn't reverse back to either pendingState or processedState
        print('CancelledState => Cancel')
        print(f'PID = {booking.pid}')
        print(f'Cancellation reason: {reason}')

    def Accept(self, booking: Booking):
        # The cancel is accepted
        print('CancelledState => Accept')
        print(f'PID = {booking.pid}')
        print('End of state; no more transition')


if __name__ == '__main__':
    print(' Flow 1 '.center(40, '-'))
    nb = Booking.createNew(pid='001', attendeeName='John')
    nb.Accept()  # Accept the Pending state and move to Processed State
    nb.Accept()  # Accept the Processed state and reach end of the flow

    print(' Flow 2 '.center(40, '-'))
    nb = Booking.createNew(pid='002', attendeeName='Mary')
    nb.Accept()
    nb.Cancel('No longer needed')

    print(' Flow 3 '.center(40, '-'))
    nb = Booking.createNew(pid='003', attendeeName='Lisa')
    nb.Cancel('No longer needed')