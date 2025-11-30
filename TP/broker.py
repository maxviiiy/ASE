# 012
# 3456
# 6789
import threading
from typing import List

MAT = [ [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
        [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
        [0, 1, 4, 2, 8, 11, 23, 5, 7, 3],
        [0, 1, 4, 2, 8, 11, 23, 5, 7, 3] ]

def column_sum(col_index: int, matrix: List[List[int]], result: List[int]) -> None:
    col_sum = 0
    for row in matrix:
        col_sum += row[col_index]
    result[col_index] = col_sum


    