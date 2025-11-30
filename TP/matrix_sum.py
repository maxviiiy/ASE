import threading
import random
import queue
from typing import List

MAT = [[random.randint(0, 100) for _ in range(10)] for _ in range(10)]


def matrix_sum(q: queue.Queue, matrix: List[List[int]], result: List[int]) -> None:
    while True:
        row_index = q.get()
        if row_index is None:
            q.task_done()
            break
        row_sum = sum(matrix[row_index])
        result[row_index] = row_sum
        q.task_done()


def main():
    rows = len(MAT)
    N = 3
    result = [0] * rows
    q: queue.Queue = queue.Queue()

    for i in range(rows):
        q.put(i)

    for _ in range(N):
        q.put(None)

    threads: List[threading.Thread] = []
    for w in range(N):
        t = threading.Thread(target=matrix_sum, args=(q, MAT, result))
        threads.append(t)
        t.start()

    q.join()

    for t in threads:
        t.join()

    total = sum(result)
    print(f"Total sum: {total}")
    return total

main()


