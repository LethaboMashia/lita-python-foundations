# Slow way: check every possible pair until two add up to the target
def two_sum_slow(nums, target): # takes a list of numbers and a target number
    for i in range(len(nums)): # the outer loop goes through each number in the list
        for j in range(i + 1, len(nums)): # the inner loop goes through the remaining numbers   
            if nums[i] + nums[j] == target: # if the sum of the two numbers equals the target, return their indices
                return [i, j] # return None # if no pair is found, return None
# This is slow because for every number, the inner loop checks almost every other number, so the time complexity is O(n^2). This is fine for small lists, but for large lists, it can be very slow.
print(two_sum_slow([2, 7, 11, 15], 9)) # Output: [0, 1]

# Fast way: walk the list once, remember numbers seen so far, check the complement
def two_sum_fast(nums, target): # takes a list of numbers and a target number
    seen = {} # a dictionary to store numbers seen so far and their indices
    for i in range(len(nums)): # loop through each number in the list
        num = nums[i] # the current number
        complement = target - num # the number that would add with the current number to reach the target
        if complement in seen: # if the complement of the current number is already in the seen dictionary, it means we have found a pair that adds up to the target
            return [seen[complement], i] # return the indices of the complement and the current number
        seen[num] = i # if the complement is not found, add the current number and its index to the seen dictionary

# This is fast because each number only needs one pass through the list, and checking for the complement in a dictionary is O(1) on average, so the overall time complexity is O(n). This is much faster for large lists.
print(two_sum_fast([2, 7, 11, 15], 9)) # Output: [0, 1]
print(two_sum_slow( [3, 4, 6, 15, 20], 10)) # Output: [1, 2]
print(two_sum_fast( [3, 4, 6, 15, 20], 10)) # Output: [1, 2]
