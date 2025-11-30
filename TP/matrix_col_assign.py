import threading
import queue
from typing import List
import re

# ROWS = 10
# COLS = 10
# MAT = [ [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
#         [0, 1, 4, 2, 8, 11, 23, 5, 7, 3] ]

def dispatcher(lines: List[str], q1: queue.Queue, q2: queue.Queue, q3: queue.Queue) -> None:
    for line in range(0, len(lines)):
        if line[0] in [A,B,C,D,E,F,G,H]:
            q1.put(line)
        elif line[0] in [I,J,K,L,M,N,O,P,Q]:
            q2.put(line)
        else: 
            q3.put(line)

    q1.put(None)
    q2.put(None)
    q3.put(None)


def col_worker(q: queue.Queue, lines: List[str], target: str, counts: List[int]) -> None:
	pattern = re.compile(rf"\b{re.escape(target)}\b", flags=re.IGNORECASE)
    local_count = 0
    while True:
        col = q.get()
        if col is None:
            q.task_done()
            break
        occurrences = pattern.findall(line)
		local_count += len(occurrences)
        counts.append(local_count)
        q.task_done()


def main():
    path = 'text.txt'
	with open(path, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
    
    target = "on"

    q1: queue.Queue = queue.Queue()
    q2: queue.Queue = queue.Queue()
    q3: queue.Queue = queue.Queue()

    col_sums: List[int] = []

    td = threading.Thread(target=dispatcher, args=(all_lines, q1, q2, q3), name='Dispatcher')
    td.start()

    td.join()

    t1 = threading.Thread(target=col_worker, args=(q1, all_lines, col_sums, 'Thread-1'), name='Thread-1')
    t2 = threading.Thread(target=col_worker, args=(q2, all_lines, col_sums, 'Thread-2'), name='Thread-2')
    t3 = threading.Thread(target=col_worker, args=(q3, all_lines, col_sums, 'Thread-3'), name='Thread-3')

    t1.start()
    t2.start()
    t3.start()

    q1.join()
    q2.join()
    q3.join()

    t1.join()
    t2.join()
    t3.join()

    total = sum(col_sums)
    print(f"Per-column occurences: {col_sums}")
    print(f"Total sum of occurences: {total}")
    return total


main()
