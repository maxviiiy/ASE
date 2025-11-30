import threading
import re
from typing import List, Tuple


def search_chunk(start_line: int, lines: List[str], target: str, counts: List[int]) -> None:
	pattern = re.compile(rf"\b{re.escape(target)}\b", flags=re.IGNORECASE)
	local_count = 0
	for offset, line in enumerate(lines):
		occurrences = pattern.findall(line)
		local_count += len(occurrences)
		print(f'Thread {threading.current_thread().name} found {len(occurrences)} occurrences in line {start_line + offset + 1}')
	counts.append(local_count)

def main():
	path = 'text.txt'
	with open(path, 'r', encoding='utf-8') as f:
		all_lines = f.readlines()

	target = "on"

	chunk_size = 3
	chunks: List[List[str]] = []
	for i in range(0, len(all_lines), chunk_size):
		chunks.append(all_lines[i:i + chunk_size])

	counts: List[int] = []

	threads: List[threading.Thread] = []
	for chunk_index, chunk in enumerate(chunks):
		start_line = chunk_index * chunk_size
		t = threading.Thread(target=search_chunk, args=(start_line, chunk, target, counts), name=f'Searcher-{chunk_index}')
		threads.append(t)
		t.start()

	for t in threads:
		t.join()

	total_count = sum(counts)
	if total_count == 0:
		print(f'No occurrences of "{target}" found.')
	else:
		print(f'Found {total_count} occurrence(s) of "{target}"')

main()