# unit tests for core algorithms: 2-sum, hash table, bst, and interactions
# run with: python tests.py

from app import two_sum, check_meds, pair_key
from hash_table import HashTable
import bst

passed = 0
total = 0


def run_test(name, fn):
    global passed, total
    total += 1
    try:
        fn()
        print(f"PASS: {name}")
        passed += 1
    except AssertionError as e:
        print(f"FAIL: {name} -> {e}")
    except Exception as e:
        print(f"FAIL: {name} -> unexpected error: {e}")


# 1. 2-SUM: exactly 2 pairs
def test_twosum_two_pairs():
    # 5 drugs with costs [5, 10, 15, 20, 12]
    # target 25 should pair (5+20) and (10+15), metformin (12) has no match
    drugs = [
        {"name": "aspirin", "cost": 5},
        {"name": "ibuprofen", "cost": 10},
        {"name": "amoxicillin", "cost": 15},
        {"name": "atorvastatin", "cost": 20},
        {"name": "metformin", "cost": 12},
    ]
    pairs = two_sum(drugs, "cost", 25)
    # expected pairs: ('amoxicillin', 'ibuprofen') and ('aspirin', 'atorvastatin')
    norm = sorted([tuple(sorted(p)) for p in pairs])
    assert len(norm) == 2, f"expected 2 pairs, got {len(norm)}"
    assert norm == [("amoxicillin", "ibuprofen"), ("aspirin", "atorvastatin")]


# 2. 2-SUM: no pairs
def test_twosum_no_pairs():
    # same drug list, but target 99 cannot be formed by any pair
    drugs = [
        {"name": "aspirin", "cost": 5},
        {"name": "ibuprofen", "cost": 10},
        {"name": "amoxicillin", "cost": 15},
        {"name": "atorvastatin", "cost": 20},
        {"name": "metformin", "cost": 12},
    ]
    pairs = two_sum(drugs, "cost", 99)
    # expected: empty list
    assert len(pairs) == 0, f"expected 0 pairs, got {len(pairs)}"


# 3. 2-SUM: duplicate costs
def test_twosum_duplicate_costs():
    # aspirin and lisinopril both cost 10
    # target 25 should match both with simvastatin (15) -> 2 pairs
    # target 20 should match aspirin with lisinopril (10 + 10) -> 1 pair
    drugs = [
        {"name": "aspirin", "cost": 10},
        {"name": "lisinopril", "cost": 10},
        {"name": "simvastatin", "cost": 15},
        {"name": "metformin", "cost": 8},
    ]
    pairs_25 = sorted([tuple(sorted(p)) for p in two_sum(drugs, "cost", 25)])
    assert pairs_25 == [("aspirin", "simvastatin"), ("lisinopril", "simvastatin")]

    pairs_20 = sorted([tuple(sorted(p)) for p in two_sum(drugs, "cost", 20)])
    assert pairs_20 == [("aspirin", "lisinopril")]


# 4. Hash table: chaining
def test_hash_table_chaining():
    # size 7: ord('a')=97, ord('h')=104, ord('o')=111 all have ord % 7 == 6
    # so 'a', 'h', 'o' all land in bucket 6
    ht = HashTable(7, "chaining")
    ht.put("a", 10)
    ht.put("h", 20)
    ht.put("o", 30)

    # get checks
    assert ht.get("a") == 10
    assert ht.get("h") == 20
    assert ht.get("o") == 30

    # update existing key
    ht.put("a", 99)
    assert ht.get("a") == 99

    # missing key returns None
    assert ht.get("z") is None

    # remove key from chain
    assert ht.remove("h") is True
    assert ht.get("h") is None
    assert ht.get("a") == 99 and ht.get("o") == 30


# 5. Hash table: linear probing
def test_hash_table_linear():
    # size 7: 'a' takes slot 6, 'h' collides and wraps to slot 0, 'o' wraps to slot 1
    ht = HashTable(7, "linear")
    ht.put("a", 10)
    ht.put("h", 20)
    ht.put("o", 30)

    assert ht.get("a") == 10
    assert ht.get("h") == 20
    assert ht.get("o") == 30

    # update existing
    ht.put("h", 77)
    assert ht.get("h") == 77

    # missing key
    assert ht.get("z") is None


# 6. Hash table: double hashing
def test_hash_table_double():
    # size 7: 'a', 'h', 'o' collide on primary hash h1=6
    # step size h2 resolves them to different probe sequences
    ht = HashTable(7, "double")
    ht.put("a", 10)
    ht.put("h", 20)
    ht.put("o", 30)

    assert ht.get("a") == 10
    assert ht.get("h") == 20
    assert ht.get("o") == 30

    # update existing
    ht.put("o", 55)
    assert ht.get("o") == 55

    # missing key
    assert ht.get("z") is None


# 7. BST: in_order and search
def test_bst_inorder_and_search():
    # insert 5 keys in known order: 20, 10, 30, 5, 25
    root = None
    for k in [20, 10, 30, 5, 25]:
        root = bst.insert(root, k, f"val_{k}")

    # in-order should give sorted keys: [5, 10, 20, 25, 30]
    keys = [k for k, v in bst.in_order(root)]
    assert keys == [5, 10, 20, 25, 30]

    # search found and not found
    node = bst.search(root, 25)
    assert node is not None and node.value == "val_25"
    assert bst.search(root, 99) is None


# 8. BST: predecessor
def test_bst_predecessor():
    root = None
    for k in [20, 10, 30, 5, 25]:
        root = bst.insert(root, k, k)

    # predecessor of 20 is 10, predecessor of 25 is 20, min element 5 has none
    assert bst.predecessor(root, 20).key == 10
    assert bst.predecessor(root, 25).key == 20
    assert bst.predecessor(root, 5) is None


# 9. BST: select and rank
def test_bst_select_rank():
    # sorted order: 5 (k=1), 10 (k=2), 20 (k=3), 25 (k=4), 30 (k=5)
    root = None
    for k in [20, 10, 30, 5, 25]:
        root = bst.insert(root, k, k)

    assert bst.select(root, 1).key == 5
    assert bst.select(root, 3).key == 20
    assert bst.select(root, 5).key == 30

    # rank is count of keys strictly smaller
    assert bst.rank(root, 5) == 0    # 0 smaller
    assert bst.rank(root, 20) == 2   # 5, 10 are smaller
    assert bst.rank(root, 30) == 4   # 5, 10, 20, 25 are smaller


# 10. BST: delete (leaf, 1 child, 2 children)
def test_bst_delete():
    # tree structure:
    #       20
    #      /  \
    #    10    30
    #   /     /
    #  5     25
    root = None
    for k in [20, 10, 30, 5, 25]:
        root = bst.insert(root, k, k)

    # 1. delete leaf (5 has no children)
    root = bst.delete(root, 5)
    assert [k for k, v in bst.in_order(root)] == [10, 20, 25, 30]

    # 2. delete node with 1 child (30 only has left child 25)
    root = bst.delete(root, 30)
    assert [k for k, v in bst.in_order(root)] == [10, 20, 25]

    # 3. delete node with 2 children (20 has children 10 and 25)
    root = bst.delete(root, 20)
    assert [k for k, v in bst.in_order(root)] == [10, 25]


# 11. BST: rotate_left and rotate_right keep in-order the same
def test_bst_rotations():
    root = None
    for k in [20, 10, 30, 5, 25]:
        root = bst.insert(root, k, k)

    original_order = [k for k, v in bst.in_order(root)]

    # rotate left around root
    root = bst.rotate_left(root)
    assert [k for k, v in bst.in_order(root)] == original_order

    # rotate right around new root
    root = bst.rotate_right(root)
    assert [k for k, v in bst.in_order(root)] == original_order


# 12. Interaction check symmetry
def test_interaction_symmetry():
    # check that pair_key normalizes order so (a, b) and (b, a) give identical hits
    assert pair_key("warfarin", "aspirin") == pair_key("aspirin", "warfarin") == "aspirin|warfarin"

    res_ab = check_meds(["warfarin", "aspirin"])
    res_ba = check_meds(["aspirin", "warfarin"])

    assert len(res_ab) == 1 and len(res_ba) == 1
    assert res_ab[0]["severity"] == "major"
    assert res_ba[0]["severity"] == "major"
    assert res_ab[0]["note"] == res_ba[0]["note"]


if __name__ == "__main__":
    run_test("2-SUM: tiny list with exactly 2 correct pairs", test_twosum_two_pairs)
    run_test("2-SUM: target with no matching pairs", test_twosum_no_pairs)
    run_test("2-SUM: duplicate cost values pair correctly", test_twosum_duplicate_costs)
    run_test("Hash table: separate chaining collisions, get, update, missing, remove", test_hash_table_chaining)
    run_test("Hash table: linear probing collisions, get, update, missing", test_hash_table_linear)
    run_test("Hash table: double hashing collisions, get, update, missing", test_hash_table_double)
    run_test("BST: in_order traversal and search", test_bst_inorder_and_search)
    run_test("BST: predecessor lookup", test_bst_predecessor)
    run_test("BST: select (k-th smallest) and rank", test_bst_select_rank)
    run_test("BST: delete (leaf, one child, two children)", test_bst_delete)
    run_test("BST: rotate_left and rotate_right maintain in-order sorted order", test_bst_rotations)
    run_test("Interaction check: pair symmetry (a,b vs b,a)", test_interaction_symmetry)

    print(f"\n{passed} of {total} passed")
