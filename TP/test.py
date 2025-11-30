import threading
import time

N = 3
barrier = threading.Barrier(N)

def count_to_fifty(thread_name):
    for i in range(1, 51):
        print(f"Thread {thread_name}: {i}")
        if i % 10 == 0:
            print(f"Thread {thread_name} reached {i}, waiting at barrier...")
            barrier.wait()
            print(f"Thread {thread_name} passed the barrier!")
    print(f"Thread {thread_name} finished counting!")

def main():
    thread1 = threading.Thread(target=count_to_fifty, args=("A",))
    thread2 = threading.Thread(target=count_to_fifty, args=("B",))
    thread3 = threading.Thread(target=count_to_fifty, args=("C",))
    
    print("Starting 3 threads to count from 1 to 50...")
    
    thread1.start()
    thread2.start()
    thread3.start()


main()