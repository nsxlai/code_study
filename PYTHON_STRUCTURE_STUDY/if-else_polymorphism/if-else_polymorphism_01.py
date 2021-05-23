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
"""
from datetime import datetime
from abc import ABC, abstractmethod


class BookingStateBase(ABC):
    @abstractmethod
    def EnterState(self, booking: Booking):
        pass

    @abstractmethod
    def Cancel(self, booking: Booking, reason: str):
        pass

    @abstractmethod
    def Accept(self, booking: Booking):
        pass


class Booking:
    def __init__(self, pid: str, attendeeName: str, state: BookingStateBase):
        self.pid = pid
        self.stateBase = state
        self.AttendeeName = attendeeName
        self.BookingDate = datetime.now()

    @classmethod
    def createNew(cls, pid: str, attendeeName: str):
        cls.state = ProcessedState()
        return cls(pid, attendeeName, cls.state)

    def TransitionToState(self, newState: BookingStateBase):
        self.state = newState
        self.state.EnterState(self)

    def Accept(self):
        # this.state.Accept(this)
        pass

    def Cancel(self, cancellationReason: str):
        # this.state.Cancel(this, cancellationReason)
        pass


class PendingState(BookingStateBase):
    def EnterState(self, booking: Booking):
        print('PendingState: EnterState')

    def Cancel(self, booking: Booking, reason: str):
        print('PendingState: CancelState')
        booking.TransitionToState(CancelledState())

    def Accept(self, booking: Booking):
        print('PendingState: AcceptState')
        booking.TransitionToState(ProcessedState())


class ProcessedState(BookingStateBase):
    def EnterState(self, booking: Booking):
        print('ProcessState: EnterState')

    def Cancel(self, booking: Booking, reason: str):
        print('ProcessState: CancelState')
        booking.TransitionToState(CancelledState())

    def Accept(self, booking: Booking):
        print('ProcessState: AcceptState')
        booking.TransitionToState(ProcessedState())


class CancelledState(BookingStateBase):
    def EnterState(self, booking: Booking):
        print('CancelledState: EnterState')

    def Cancel(self, booking: Booking, reason: str):
        print('CancelledState: CancelState')
        booking.TransitionToState(CancelledState())

    def Accept(self, booking: Booking):
        print('CancelledState: AcceptState')
        booking.TransitionToState(ProcessedState())


if __name__ == '__main__':
    nb = Booking.createNew(pid='001', attendeeName='John')
