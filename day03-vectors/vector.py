class Vector:
    def __init__ (self, components):
        self.components = components

    def __repr__(self):
        return f"Vector({self.components})"

    def dot(self, other):
        if len(self.components) != len(other.components):
            raise ValueError("Vectors must be the same length to compare")

        total = 0
        for i in range(len(self.components)):
            total = total + self.components [i] * other.components[i]
        return total

    def magnitude(self):
        total = 0
        for i in range(len(self.components)):
            total = total + self.components[i] ** 2
        return total ** 0.5

    def cosine_similarity(self, other):
        denominator = self.magnitude() * other.magnitude()
        if denominator == 0:
            return 0.0
        return self.dot(other) / denominator
        

if __name__ == "__main__":
    v = Vector ([81, 77, 66, 50])
    print (v)




    a = Vector ([3, 0, 1])
    b = Vector ([6, 0, 2])
    print(a.dot(b))
    print(a.magnitude())
    print(a.cosine_similarity(b))