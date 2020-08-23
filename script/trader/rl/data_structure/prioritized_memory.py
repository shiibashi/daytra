import numpy
import random

class PrioritizedMemory(object):
    e = 0.0001
    a = 0.6

    def __init__(self, capacity):
        self.tree = SumTree(capacity)
        self.capacity = capacity

    def _getPriority(self, error):
        return (error + self.e) ** self.a


    def add(self, sample):
        """
        sample = {
                "x": x,
                "y": y,
                "time": t,
                "error": error,
                "history": history
            }
        """
        error = sample["error"]
        p = self._getPriority(error)
        self.tree.add(p, sample) 

    def sample_tree_data(self, n):
        batch = []
        segment = self.tree.total() / n

        for i in range(n):
            a = segment * i
            b = segment * (i + 1)

            s = random.uniform(a, b)
            (idx, p, data) = self.tree.get(s)
            batch.append( (idx, data) )

        return batch

    def sample(self, n, sampling_algorithm="uniform"):
        assert sampling_algorithm in ["uniform", "simple_probably"]
        if sampling_algorithm == "uniform":
            batch = []
            segment = self.tree.total() / n

            for i in range(n):
                a = segment * i
                b = segment * (i + 1)

                s = random.uniform(a, b)
                (idx, p, data) = self.tree.get(s)
                #batch.append(data)
                batch.append((idx, p, data))
        elif sampling_algorithm == "simple_probably":
            batch = []
            max_p = self.tree.total()
            for i in range(n):
                s = random.uniform(0, max_p)
                (idx, p, data) = self.tree.get(s)
                #batch.append(data)
                batch.append((idx, p, data))
        else:
            raise
        return batch


    def update(self, idx, error):
        p = self._getPriority(error)
        self.tree.update(idx, p)

    def trainable(self, n):
        return numpy.array([0 if d == 0 else 1 for d in self.tree.data]).sum() >= n * 2

class SumTree(object):
    write = 0 # 書き込む参照位置

    def __init__(self, capacity):
        self.capacity = capacity
        self.tree = numpy.zeros(2*capacity - 1 )
        self.data = numpy.zeros(capacity, dtype=object )

    def _propagate(self, idx, change):
        parent = (idx - 1) // 2

        self.tree[parent] += change

        if parent != 0:
            self._propagate(parent, change)

    def _retrieve(self, idx, s):
        left = 2 * idx + 1
        right = left + 1

        if left >= len(self.tree):
            return idx

        if s <= self.tree[left]:
            return self._retrieve(left, s)
        else:
            return self._retrieve(right, s-self.tree[left])

    def total(self):
        return self.tree[0]

    def add(self, p, data):
        idx = self.write + self.capacity - 1

        self.data[self.write] = data
        self.update(idx, p)

        self.write += 1
        if self.write >= self.capacity:
            self.write = 0

    def update(self, idx, p):
        change = p - self.tree[idx]

        self.tree[idx] = p
        self._propagate(idx, change)

    def get(self, s):
        idx = self._retrieve(0, s)
        dataIdx = idx - self.capacity + 1

        return (idx, self.tree[idx], self.data[dataIdx])
