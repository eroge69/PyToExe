import random

def weighted_random():
    numbers = list(range(1, 10001))
    weights = [0.8 if num == 746 else 0.2 / 9999 for num in numbers]
    return random.choices(numbers, weights=weights, k=1)[0]

# آزمایش
results = [weighted_random() for _ in range(10000)]
print(f"746 appeared {results.count(746)} times")
