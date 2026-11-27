# custom hash table implementation without built-in python dicts
# supports separate chaining, linear probing, and double hashing for collision handling


class HashTable:
    def __init__(self, size=101, method="chaining"):
        # size should be prime so double hashing can reach every slot
        self.size = size
        self.method = method
        self.count = 0
        self.collisions = 0   # inserts where the first slot was already taken
        self.probes = 0       # slots looked at during lookups
        if method == "chaining":
            self.slots = [[] for _ in range(size)]   # each bucket is a list of [key, value]
        else:
            self.slots = [None] * size                # None means empty

    def _h1(self, key):
        # simple polynomial string hash
        h = 0
        for ch in key:
            h = (h * 31 + ord(ch)) % self.size
        return h

    def _h2(self, key):
        # second hash for double hashing, can never be 0
        h = 0
        for ch in key:
            h = (h * 17 + ord(ch)) % (self.size - 1)
        return h + 1

    def _step(self, key):
        if self.method == "double":
            return self._h2(key)
        return 1   # linear probing just moves one slot at a time

    def put(self, key, value):
        start = self._h1(key)
        if self.method == "chaining":
            bucket = self.slots[start]
            for pair in bucket:
                if pair[0] == key:
                    pair[1] = value   # key exists, just update it
                    return
            if len(bucket) > 0:
                self.collisions += 1
            bucket.append([key, value])
            self.count += 1
            return

        # open addressing
        step = self._step(key)
        i = start
        for n in range(self.size):
            slot = self.slots[i]
            if slot is None:
                if n > 0:
                    self.collisions += 1
                self.slots[i] = [key, value]
                self.count += 1
                return
            if slot[0] == key:
                slot[1] = value
                return
            i = (i + step) % self.size
        raise RuntimeError("hash table is full")

    def get(self, key):
        # returns the value or None if the key is not there
        start = self._h1(key)
        if self.method == "chaining":
            for pair in self.slots[start]:
                self.probes += 1
                if pair[0] == key:
                    return pair[1]
            self.probes += 1   # count the empty/end check too
            return None

        step = self._step(key)
        i = start
        for n in range(self.size):
            self.probes += 1
            slot = self.slots[i]
            if slot is None:
                return None
            if slot[0] == key:
                return slot[1]
            i = (i + step) % self.size
        return None

    def remove(self, key):
        # only chaining supports delete here (open addressing would need tombstones)
        if self.method != "chaining":
            raise NotImplementedError("remove only works with chaining")
        bucket = self.slots[self._h1(key)]
        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket.pop(i)
                self.count -= 1
                return True
        return False

    def keys(self):
        out = []
        for s in self.slots:
            if self.method == "chaining":
                for pair in s:
                    out.append(pair[0])
            elif s is not None:
                out.append(s[0])
        return out

    def load_factor(self):
        return self.count / self.size
