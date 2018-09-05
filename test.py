## this is for testing

from queue import PriorityQueue

pq = PriorityQueue()
pq.put((2, "rank 2"))
pq.put((1, "rank"))
pq.put((float(1) / float(3), "rank"))

while (not pq.empty()):
    print(pq.get())


l = [1, 2, 3, 4, 5, 6]

ll = map(lambda i: i*i, l)
print ll
print l
