# A node holds one value and a pointer to the next node in the chain
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None   

# LinkedList keeps track of the first node (the head). Everything else is reached via .next
class LinkedList:
    def __init__(self):
        self.head = None 

    def append(self, value):
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
    # Traversal is O(n) because linked list nodes are NOT stored next to each other
    # in memory like an array. An array can jump straight to index 5 with math
    # (address + 5*size). A node only knows the address of the NEXT node - there's
    # no index - so reaching node 5 means physically walking 1 -> 2 -> 3 -> 4 -> 5.
    def print_list(self):
        current = self.head
        while current is not None:
            print(current.value, end=" -> ")
            current = current.next
        print("None")
    # Insert/delete are O(1) once located: insert_after changes exactly 2 pointers
    # (new_node.next = current.next, then current.next = new_node); delete changes
    # exactly 1 pointer (current.next = current.next.next). Constant work, no matter
    # how long the list is - because once you're standing on the node, relinking
    # doesn't depend on the list's size.
    def insert_after(self, target_value, new_value):
        current = self.head
        while current is not None:
            if current.value == target_value:
                new_node = Node(new_value)
                new_node.next = current.next
                current.next = new_node
                return
            current = current.next
        
    

    def delete(self, value):
        if self.head is not None and self.head.value == value:
            self.head = self.head.next
            return
        current = self.head
        while current.next is not None:
            if current.next.value == value:
                current.next = current.next.next
                return
            current = current.next

# Example usage
ll = LinkedList()
ll.append(10)
ll.append(20)
ll.append(30)
ll.print_list()
ll.insert_after(20, 25)
ll.print_list()
ll.delete(25)
ll.print_list()
ll.delete(10)
ll.print_list()
   
    