class User:
    def __init__(self, username, arrival_time):
        self.id = username
        self.arrival_time = arrival_time
        self.cluster_number = None


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

        while current_node is not None:

            if current_node.cluster:
                waiting_room.extend(current_node.cluster)
            current_node = current_node.next

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
    def __init__(self, acceptable_range, start_ticket_sale):
        self.acceptable_range = acceptable_range
        self.start_ticket_sale = start_ticket_sale
        self.waiting_room_service = WaitingRoomService(acceptable_range)
        self.queue_manager_service = QueueManagerService(self.waiting_room_service, acceptable_range)
        self.available_booths = acceptable_range

    def add_user_to_waiting_room(self, user_id, arrival_time):
        user = User(user_id, arrival_time)
        self.waiting_room_service.add_user(user)
        print(self.waiting_room_service.get_waiting_room())
        self.queue_manager_service.manage_queue()

    def user_cluster_number(self, username):
        users = self.waiting_room_service.get_waiting_room()
        for user in users:

            if user.id == username:

                return user.cluster_number
        return None  # User not found in the waiting room

    def is_user_turn(self, user_id):
        users = self.waiting_room_service.get_waiting_room()
        if not users or users[0].id == user_id:
            return True
        return False

    def users_in_waiting_room(self):
        users = self.waiting_room_service.get_waiting_room()
        return bool(users)

    def process_queue(self, user_id):
        users = self.waiting_room_service.get_waiting_room()
        for user in users:
            if not users or users[0].id == user_id:
                self.waiting_room_service.get_waiting_room().remove(user)

    def check_booth(self):
        if self.available_booths == self.acceptable_range:
            return True
        return False

    def release_booth(self):
        self.available_booths += 1

    def occupy_booth(self):
        self.available_booths -= 1
