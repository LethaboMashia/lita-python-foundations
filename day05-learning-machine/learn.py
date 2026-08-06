# Each point is [feature1, feature2], label is 0 (small) or 1 (big)
data = [ 
    ([1, 1], 0), 
    ([2, 1], 0),
    ([1, 2], 0),
    ([6, 5], 1),
    ([7, 8], 1),
    ([8, 6], 1),
]

# The model: two weights and a bias, all starting at zero (knows nothing yet)
w1 = 0
w2 = 0
bias = 0
learning_rate = 0.1

# The model: two weights and a bias, all starting at zero (knows nothing yet)
# Three numbers that will be adjusted during training to make the model more accurate. The weights are multiplied by the features of each point, and the bias is added to the result. The learning rate controls how much the weights and bias are adjusted during training.
w1 = 0
w2 = 0
bias = 0
learning_rate = 0.1

# predict: dot product of weights and features, plus bias, through a 0/1 gate
def predict(point):
    total = w1 * point[0] + w2 * point[1] + bias
    if total > 0:
        return 1
    else:
        return 0

# accuracy: run predict on every lead, count how many match the true label
def accuracy():
    correct = 0
    for features, label in data:
        if predict(features) == label:
            correct = correct + 1
    return correct / len(data) 



# training: for each lead, guess, measure the miss, nudge weights toward less miss
def train(epochs):
    global w1, w2, bias
    for e in range(epochs):
        for features, label in data:
            prediction = predict(features)
            error = label - prediction
            w1 = w1 + learning_rate * error * features[0] # when the guess is right the error is 0, so the whole adjustment becomes 0 and the weight stays the same; only wrong guesses move the weights and bias in the right direction.
            w2 = w2 + learning_rate * error * features[1]
            bias = bias + learning_rate * error

print("Accuracy before training:", accuracy())
train(10) 
print("Accuracy after training:", accuracy())            