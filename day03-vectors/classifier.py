# Feature slots (order fixed for every vector in this file):
# 0: rooms   1: property   2: skin   3: pupils   4: booking

from vector import Vector



hospitality = Vector([3, 1, 0, 0, 3])
real_estate = Vector([1, 3, 0, 0, 0])
beauty      = Vector([0, 0, 3, 0, 3])
schools     = Vector([0, 0, 0, 3, 0])

FEATURES = ["rooms", "properties", "skin", "pupils", "booking"]

def describe(text):
    counts = []
    for word in FEATURES:
        counts.append(text.lower() .count(word))
    return Vector(counts)

descriptions = [
    "Family luxury hotel with a variety of rooms and amenities for guests",
    "A school with a variety of subjects and extracurricular activities for pupils",
    "Real estate firm; we help you live in your dream home with a variety of properties to choose from",
    "A beauty salon offering skincare and makeup services",
    "A booking platform for hotels, flights, and rental cars",
]

niche_names = ["Boutique Hospitality", "Real Estate", "Beauty & Aesthetics", "Independent Schools"]
niche_vectors = [hospitality, real_estate, beauty, schools]

for text in descriptions:
    v = describe(text)
    print(text)
    best_score = -1
    best_name = ""
    for i in range(len(niche_names)):
        score = v.cosine_similarity(niche_vectors[i])
        print(f"   {niche_names[i]}: {round(score, 3)}")
        if score > best_score:
            best_score = score
            best_name = niche_names[i]
    print(f"   WINNER: {best_name}")
    print()
