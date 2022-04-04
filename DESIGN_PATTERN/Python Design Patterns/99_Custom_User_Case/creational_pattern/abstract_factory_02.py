"""
source: https://medium.com/geekculture/factory-design-pattern-in-python-811a1d3b9cbc
"""
from abc import ABC, abstractmethod


class Ticket(ABC):
    @staticmethod
    @abstractmethod
    def ticket_type():
        pass


class IncidentTicket(Ticket):
    @staticmethod
    def ticket_type():
        return f'{__class__.__name__} has been created'


class ProblemTicket(Ticket):
    @staticmethod
    def ticket_type():
        return f'{__class__.__name__} has been created'


class ServiceRequest(Ticket):
    @staticmethod
    def ticket_type():
        return f'{__class__.__name__} has been created'


class TicketFactory:
    @staticmethod
    def create_ticket(t_type):
        tickets = {
            'incident': IncidentTicket,
            'problem': ProblemTicket,
            'servicerequest': ServiceRequest
        }
        assert t_type in tickets, f'Ticket type "{t_type}" is not supported'
        return tickets[t_type]


def client_code(ticket_type):
    """
    The client_code does not need to be changed, only need to create the new class and add it to the "factory"
    """
    factory = TicketFactory()
    ticket = factory.create_ticket(ticket_type)
    print(ticket.ticket_type())


if __name__ == '__main__':
    client_code('incident')
    client_code('problem')
    client_code('servicerequest')
