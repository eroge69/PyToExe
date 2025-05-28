from collections import Counter

def read_numbers(filename):
    with open(filename, 'r') as f:
        numbers = [int(line.strip()) for line in f if line.strip().isdigit()]
    return numbers

def predict_next(numbers):
    recent_numbers = numbers[:100]
    counter = Counter(recent_numbers)
    most_common = counter.most_common(5)
    return most_common

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Укажите путь к файлу с числами (по одному в строке).")
    else:
        nums = read_numbers(sys.argv[1])
        prediction = predict_next(nums)
        print("Наиболее вероятные числа:")
        for num, freq in prediction:
            print(f"{num} (встречалось {freq} раз за последние 100 игр)")
