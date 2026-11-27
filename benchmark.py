# performance benchmarks comparing hash tables, 2-sum, list scanning, and bst height
# run with: python benchmark.py

import random
import time
import math
import sys
from hash_table import HashTable
import bst
from app import two_sum

# increase recursion limit for sorted bst inserts
sys.setrecursionlimit(25000)


def format_table(title, headers, rows):
    print(f"\n=== {title} ===")
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
    header_str = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    sep_str = "-+-".join("-" * widths[i] for i in range(len(headers)))
    print(header_str)
    print(sep_str)
    for row in rows:
        print(" | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)))


# Brute force 2-SUM for comparison
def two_sum_brute_force(drugs, field, target):
    pairs = []
    n = len(drugs)
    for i in range(n):
        d1 = drugs[i]
        v1 = d1[field]
        for j in range(i + 1, n):
            d2 = drugs[j]
            if v1 + d2[field] == target:
                a, b = sorted([d1["name"], d2["name"]])
                pairs.append((a, b))
    return pairs


# 1. Hash table collision methods
def bench_hash_tables():
    size = 1009
    rng = random.Random(42)
    loads = [0.3, 0.5, 0.7, 0.9]
    methods = ["chaining", "linear", "double"]
    headers = ["Load Factor", "Method", "Items (N)", "Collisions", "Avg Probes"]
    rows = []

    for load in loads:
        n = int(size * load)
        keys = [f"key_{rng.randint(100000, 999999)}_{i}" for i in range(n)]

        for method in methods:
            ht = HashTable(size, method)
            for k in keys:
                ht.put(k, 1)
            cols = ht.collisions

            # successful lookups
            ht.probes = 0
            for k in keys:
                ht.get(k)
            avg_hit = round(ht.probes / n, 2)

            rows.append([f"{load:.1f}", method, n, cols, avg_hit])

    format_table("1. Hash Table Collision Strategies (Table Size = 1009, Seeded Random Keys)", headers, rows)


# 2. 2-SUM Hash vs Brute Force
def bench_twosum():
    sizes = [100, 1000, 5000, 10000]
    target = 50
    headers = ["Size N", "Hash 2-SUM (ms)", "Brute Force (ms)", "Speedup", "Pairs Found", "Output Match?"]
    rows = []
    rng = random.Random(42)

    for n in sizes:
        # generate artificial drug list
        drugs = [{"name": f"rx_{i}", "cost": rng.randint(1, 100)} for i in range(n)]

        # runs: 3 runs for small/medium, 1 run for 10000 brute force to stay fast
        runs = 3 if n <= 1000 else 1

        # time hash 2-sum
        t0 = time.perf_counter()
        for _ in range(runs):
            pairs_hash = two_sum(drugs, "cost", target)
        hash_time = ((time.perf_counter() - t0) / runs) * 1000

        # time brute force
        t0 = time.perf_counter()
        for _ in range(runs):
            pairs_bf = two_sum_brute_force(drugs, "cost", target)
        bf_time = ((time.perf_counter() - t0) / runs) * 1000

        speedup = f"{bf_time / max(hash_time, 0.0001):.1f}x"
        matched = sorted(pairs_hash) == sorted(pairs_bf)

        rows.append([n, f"{hash_time:.3f}", f"{bf_time:.3f}", speedup, len(pairs_hash), "PASS" if matched else "FAIL"])

    format_table("2. 2-SUM Hash Table O(n) vs Brute Force O(n^2)", headers, rows)


# 3. Hash Table lookup vs Plain List scan
def bench_lookup_vs_list():
    sizes = [100, 1000, 5000, 10000]
    headers = ["Size N", "Queries", "Hash Table (ms)", "List Scan (ms)", "Speedup"]
    rows = []
    rng = random.Random(42)

    for n in sizes:
        drugs = [{"name": f"rx_{i}", "cost": rng.randint(1, 100)} for i in range(n)]
        # build hash table
        ht = HashTable(int(n * 1.5) + 7, "chaining")
        for d in drugs:
            ht.put(d["name"], d)

        # 100 queries: 50 existing keys, 50 missing keys
        queries = [f"rx_{rng.randint(0, n - 1)}" for _ in range(50)] + [f"missing_{i}" for i in range(50)]

        # hash table lookup timing
        t0 = time.perf_counter()
        for q in queries:
            _ = ht.get(q)
        hash_time = (time.perf_counter() - t0) * 1000

        # list scan timing
        t0 = time.perf_counter()
        for q in queries:
            _ = any(d["name"] == q for d in drugs)
        list_time = (time.perf_counter() - t0) * 1000

        speedup = f"{list_time / max(hash_time, 0.0001):.1f}x"
        rows.append([n, len(queries), f"{hash_time:.3f}", f"{list_time:.3f}", speedup])

    format_table("3. Hash Table O(1) Lookup vs Plain List O(n) Linear Scan", headers, rows)


# 4. BST Height: Random vs Sorted
def bench_bst():
    sizes_height = [50, 100, 250, 500, 1000, 1500]
    headers_a = ["Size N", "Random Insert Height", "Sorted Insert Height", "Theoretical Min Height"]
    rows_a = []
    rng = random.Random(42)

    for n in sizes_height:
        keys = list(range(n))
        random_keys = list(keys)
        rng.shuffle(random_keys)

        # random insert
        root_rnd = None
        for k in random_keys:
            root_rnd = bst.insert(root_rnd, k, k)
        h_rnd = bst.height(root_rnd)

        # sorted insert
        root_sort = None
        for k in keys:
            root_sort = bst.insert(root_sort, k, k)
        h_sort = bst.height(root_sort)

        min_h = math.ceil(math.log2(n + 1))
        rows_a.append([n, h_rnd, h_sort, min_h])

    format_table("4. BST Height: Random Insert vs Sorted Degenerate Case", headers_a, rows_a)


if __name__ == "__main__":
    print("Running drug_matcher benchmarks (average over runs with time.perf_counter)...")
    bench_hash_tables()
    bench_twosum()
    bench_lookup_vs_list()
    bench_bst()
    print("\nAll benchmarks completed successfully.")
