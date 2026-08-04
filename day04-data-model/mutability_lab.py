#Demo 1: 
a = [1, 2, 3] #makes a list, ties the tag a to it.
b = a #ties a second tag b to the same list. No new list is made.
b.append(4) #adds 4 to the list, reaching it through b
print("a is:", a) #prints the value of a
print("id(a):", id(a), "id(b):", id(b)) #prints the memory address of a and b, which are the same since they point to the same list.

x = [1, 2, 3]
y = [1, 2, 3]
print ("x == y:", x == y) 
print ("x is y:", x is y) #x and y are different lists, so they are not the same object in memory.

my_list = [1, 2, 3] #creates a list object and ties the tag my_list to it.
print("list id before:", id(my_list)) #prints the memory address of my_list before modification.
my_list.append(4) # adds 4 to the list, which is a mutable object, so the list is modified in place.
print("list id after:", id(my_list)) #prints the memory address of my_list after modification, which is the same as before since the list was modified in place.

my_string = "hello" # creates a string object and ties the tag my_string to it.
print("string id before:", id(my_string)) #prints the memory address of my_string before reassignment.
my_string = my_string + " world" # creates a new string object and reassigns the tag my_string to it, since strings are immutable.
print("string id after:", id(my_string)) # prints the memory address of my_string after reassignment, which is different from before.

def add_item(original, item): 
    new_list = original.copy() #creates a copy of the original list, so that the original list is not modified.
    new_list.append(item) #adds the new item to the copied list.
    return new_list #returns the new list with the added item, leaving the original list unchanged.

my_original = [1, 2, 3]
result = add_item(my_original, 4) # calls the add_item function, passing in the original list and the new item to be added. The function returns a new list with the added item, while leaving the original list unchanged.
print("original:", my_original) #prints the value of the original list, which remains unchanged.
print("result:", result) #prints the value of the new list returned by the add_item function, which contains the original items plus the new item.