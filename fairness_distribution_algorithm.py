import random


class User:
    def __init__(self, username, arrival_time):
        self.id = username
        self.arrival_time = arrival_time
        self.queue_position = None


class Ticket:
    def __init__(self, username):
        self.id = username
        self.locked = False

    def is_locked(self):
        return self.locked

    def try_lock(self):
        if not self.locked:
            self.locked = True
            return True
        return False


class WaitingRoomService:
    def __init__(self):
        self.waiting_room = []

    def add_user(self, user):
        self.waiting_room.append(user)

    def get_waiting_room(self):
        return self.waiting_room


class QueueManagerService:
    def __init__(self, waiting_room_service, acceptable_range):
        self.waiting_room_service = waiting_room_service
        self.acceptable_range = acceptable_range

    def manage_queue(self):
        users = self.waiting_room_service.get_waiting_room()

        for user in users:
            queue_position = self.calculate_queue_position(user, users)
            user.queue_position = queue_position

    def calculate_queue_position(self, user, users):
        if user and not users:
            return 0
        else:
            lower_bound = max(0, len(users) - self.acceptable_range)
            return random.randint(lower_bound, len(users))


class QueueService:
    def __init__(self, waiting_room_service, tickets):
        self.waiting_room_service = waiting_room_service
        self.tickets = tickets.copy()

    def process_queue(self):
        users = sorted(self.waiting_room_service.get_waiting_room(), key=lambda user: user.queue_position)
        for user in users:
            self.attempt_purchase(user)

    def attempt_purchase(self, user):
        for ticket in self.tickets:
            if ticket.try_lock():
                print(f"User {user.id} arriving at time {user.arrival_time} purchased ticket {ticket.id}")
                self.waiting_room_service.get_waiting_room().remove(user)
                self.tickets.remove(ticket)
                break


class TicketingSystem:
    def __init__(self, acceptable_range, start_ticket_sale, max_tickets):
        self.acceptable_range = acceptable_range
        self.start_ticket_sale = start_ticket_sale
        self.waiting_room_service = WaitingRoomService()
        self.queue_manager_service = QueueManagerService(self.waiting_room_service, acceptable_range)
        self.max_tickets = max_tickets
        self.tickets = []

    def setup_tickets(self, ticket_count):
        for i in range(ticket_count):
            self.tickets.append(Ticket(i))

    def add_user_to_waiting_room(self, user_id, arrival_time):
        user = User(user_id, arrival_time)
        self.waiting_room_service.add_user(user)
        self.queue_manager_service.manage_queue()

    def user_queue_position(self, user_id):
        users = self.waiting_room_service.get_waiting_room()
        for user in users:
            if user.id == user_id:
                return user.queue_position
        return None  # User not found in the waiting room

    def process_waiting_room(self):
        queue_service = QueueService(self.waiting_room_service, self.tickets)
        queue_service.process_queue()
