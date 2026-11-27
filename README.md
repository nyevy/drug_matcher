# Drug Interaction and Dosage Matcher

An educational algorithms project demonstrating core data structures and algorithmic techniques through a simulated pharmaceutical interaction and dosage pairing tool. (Toy data only, not medical advice.)

## What the Project Does

- **Drug Interaction Checker**: Evaluates all pairs in a patient's medication list for dangerous interactions using expected O(1) hash table lookups.
- **2-SUM Drug Matcher**: Finds pairs of medications that sum to an exact monthly cost or daily dose in expected O(n) time using a hash table, including duplicate-cost handling and a manual verification trace.
- **Sorted Catalog & Order Statistics (BST)**: Maintains drugs sorted by name, cost, or dose in an augmented Binary Search Tree that supports search, predecessor, rank, select (k-th smallest), and tree rotations.
- **Hash Table Collision Comparison**: Compares separate chaining, linear probing, and double hashing under various load factors with seeded random keys.

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```
*(The only external dependency is Flask.)*

### 2. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 3. Run the Test Suite
```bash
python tests.py
```
Runs assertions on small toy examples across 2-SUM, hash collision methods, BST operations, and interaction symmetry. Prints PASS/FAIL lines and a summary (`12 of 12 passed`).

### 4. Run the Benchmarks
```bash
python benchmark.py
```
Executes timing and probe count benchmarks using `time.perf_counter`, printing clean comparison tables for:
1. Hash table collision strategies (chaining, linear probing, double hashing at load factors 0.3, 0.5, 0.7, 0.9).
2. Hash-based 2-SUM O(n) vs brute-force O(n^2) on list sizes 100 to 10,000.
3. Hash table O(1) lookup vs linear list O(n) scan.
4. Unbalanced BST height (random insert order vs sorted degenerate case).

## File-by-File Structure

- `app.py`: Flask web server and API routes (`/api/check`, `/api/twosum`, `/api/drugs`, `/api/bst`, `/api/rotate`, `/api/benchmark`), including input validation and the hash-based 2-SUM implementation with trace step recording.
- `hash_table.py`: Custom hash table built from scratch (no Python dict storage) supporting separate chaining, linear probing, and double hashing.
- `bst.py`: Binary Search Tree augmented with subtree `size` fields for order statistics (select and rank), plus predecessor lookup, deletion (leaf, 1 child, 2 children), and left/right rotations.
- `data.py`: Toy dataset containing sample drugs, pairwise drug interactions with severity levels (major, moderate, minor), and preloaded patient profiles.
- `tests.py`: Unit test runner testing core algorithms against known hand-traceable toy cases with expected results documented in comments.
- `benchmark.py`: Empirical performance benchmarking suite producing clean tables for report analysis.
- `templates/index.html`: Web front-end featuring a 4-tab dashboard, collapsible "How it works" algorithm summaries, color legends, reachable sum hints, and manual verification step traces.
