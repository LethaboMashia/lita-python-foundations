class Node: # Define a class for a node in a linked list
    def __init__(self, value): # Initialize a new node with a value and a next pointer
        self.value = value # Store the value of the node
        self.next = None # Initialize the next pointer to None

# Stack: all operations (push/pop/peek) only touch self.head directly —
# no walking through the chain — so they stay O(1) no matter how many items are stored.
class Stack: # doesnt use tail pointer because we only add/remove from head regardless of how long the list is. O(1) time complexity for push/pop
    def __init__(self):
        self.head = None

    def push(self, value):
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node

    def pop(self):
        if self.head is None:
            return None
        popped_node = self.head
        self.head = self.head.next
        return popped_node.value

    def peek(self):
        if self.head is None:
            return None
        return self.head.value

    def is_empty(self):
        return self.head is None

# O(1) time complexity for push/pop because we only add/remove from head regardless of how long the list is.
# Queue: all operations (enqueue/dequeue/peek) only touch self.head and self.tail directly — no walking through the chain — so they stay O(1) no matter how many items are stored.
class Queue:
    def __init__(self):
        self.head = None
        self.tail = None
    # O(1) — attaches directly to self.tail, no traversal needed.
    def enqueue(self, value):
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        # O(1) — removes directly from self.head, no traversal needed.
    def dequeue(self):
        if self.head is None:
            return None
        dequeued_node = self.head
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        return dequeued_node.value

    def is_empty(self):
        return self.head is None

# Demo: Stack (LIFO)
s = Stack()
s.push(10)
s.push(20)
s.push(30)
print(s.pop())
print(s.pop())
print(s.pop())

# Demo: Queue (FIFO)
q = Queue()
q.enqueue("A")
q.enqueue("B")
q.enqueue("C")
print(q.dequeue())
print(q.dequeue())
print(q.dequeue())