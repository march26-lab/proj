def main():
    MAX_DEPTH = 20

    queue = [1]

    print("depth, (node,...)")

    for depth in range(0, MAX_DEPTH + 1):
        print(f"{depth}, ("
              + ", ".join(f"{n}" for n in queue)
              + ")")

        queue = get_next_queue(queue)

def get_next_queue(queue):
    next_queue = []

    for number in queue:
        next_queue.append(number * 2)

        if number % 6 == 4 and number != 4:
            next_queue.append((number - 1) // 3)

    return next_queue

if __name__ == "__main__":
    main()
