class User:
    def __init__(self, username, arrival_time):
        self.id = username
        self.arrival_time = arrival_time
        self.cluster_number = None


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


class LinkedListNode:
    def __init__(self):
        self.cluster = []
        self.next = None


class WaitingRoomService:
    def __init__(self, cluster_size):
        self.cluster_size = cluster_size
        self.head = LinkedListNode()

    def add_user(self, user):
        current_node = self.head
        while current_node.next is not None and len(current_node.cluster) >= self.cluster_size:
            current_node = current_node.next

        if len(current_node.cluster) >= self.cluster_size:
            new_node = LinkedListNode()
            current_node.next = new_node
            current_node = new_node

        current_node.cluster.append(user)

    def get_waiting_room(self):
        current_node = self.head
        waiting_room = []
        print(current_node)
        #print(waiting_room)
        while current_node is not None:
            print(current_node)
            if current_node.cluster:
                waiting_room.extend(current_node.cluster)
            current_node = current_node.next
        #print(current_node)

        return waiting_room


class QueueManagerService:
    def __init__(self, waiting_room_service, acceptable_range):
        self.waiting_room_service = waiting_room_service
        self.acceptable_range = acceptable_range

    def manage_queue(self):
        users = self.waiting_room_service.get_waiting_room()
        cluster_index = 0

        for user in users:
            user.cluster_number = cluster_index

            cluster_index += 1


class TicketingSystem:
    def __init__(self, acceptable_range, start_ticket_sale, max_tickets):
        self.acceptable_range = acceptable_range
        self.start_ticket_sale = start_ticket_sale
        self.waiting_room_service = WaitingRoomService(acceptable_range)
        self.queue_manager_service = QueueManagerService(self.waiting_room_service, acceptable_range)
        self.max_tickets = max_tickets
        self.tickets = []

    def add_user_to_waiting_room(self, user_id, arrival_time):
        user = User(user_id, arrival_time)
        self.waiting_room_service.add_user(user)
        print(self.waiting_room_service.get_waiting_room())
        self.queue_manager_service.manage_queue()

    def user_cluster_number(self, username):
        users = self.waiting_room_service.get_waiting_room()
        for user in users:
            print("test..." + user.id)
            print("user_id..." + username)
            if user.id == username:
                print("enter")
                return user.cluster_number
        return None  # User not found in the waiting room

    def is_user_turn(self, user_id):
        users = self.waiting_room_service.get_waiting_room()
        if not users or users[0].id == user_id:
            return True
        return False

    def available_booth_slots(self):
        # Implement your logic to check the number of available booth slots
        return 3  # Replace with your actual logic

    def users_in_waiting_room(self):
        users = self.waiting_room_service.get_waiting_room()
        return bool(users)

    def process_queue(self, user_id):
        users = self.waiting_room_service.get_waiting_room()
        for user in users:
            if not users or users[0].id == user_id:
                self.waiting_room_service.get_waiting_room().remove(user)
