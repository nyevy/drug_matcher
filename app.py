# flask web backend for drug interaction matching and 2-sum search
# loads our custom hash table and bst structures to serve the frontend api
from flask import Flask, jsonify, request, render_template

import bst
from hash_table import HashTable
from data import DRUGS, INTERACTIONS, PATIENTS

app = Flask(__name__)

# the tables are built once when the server starts
drug_table = HashTable(101, "chaining")          # name -> drug info
interaction_table = HashTable(101, "chaining")   # "a|b" -> interaction info
trees = {"name": None, "cost": None, "dose": None}  # three BSTs, one per sort field


def pair_key(a, b):
    # sort the names so (a,b) and (b,a) give the same key
    x, y = sorted([a, b])
    return x + "|" + y


def tree_key(drug, by):
    # name tree uses the name, others use (value, name) so keys are unique
    if by == "name":
        return drug["name"]
    return (drug[by], drug["name"])


def add_drug(name, drug_class, dose, cost):
    drug = {"name": name, "class": drug_class, "dose": dose, "cost": cost}
    drug_table.put(name, drug)
    for by in trees:
        trees[by] = bst.insert(trees[by], tree_key(drug, by), drug)
    return drug


def load_data():
    for name, cls, dose, cost in DRUGS:
        add_drug(name, cls, dose, cost)
    for a, b, sev, note in INTERACTIONS:
        interaction_table.put(pair_key(a, b), {"severity": sev, "note": note})


load_data()


def check_meds(meds):
    # check every pair of meds, k meds means k*(k-1)/2 hash lookups
    found = []
    for i in range(len(meds)):
        for j in range(i + 1, len(meds)):
            hit = interaction_table.get(pair_key(meds[i], meds[j]))
            if hit:
                found.append({"a": meds[i], "b": meds[j], **hit})
    order = {"major": 0, "moderate": 1, "minor": 2}
    found.sort(key=lambda x: order[x["severity"]])
    return found


def two_sum(drugs, field, target, record_steps=False):
    # hash version of 2-sum: store value -> drugs, then look up target - value
    table = HashTable(101, "chaining")
    for d in drugs:
        key = str(d[field])
        names = table.get(key)
        if names is None:
            table.put(key, [d["name"]])
        else:
            names.append(d["name"])
    pairs = []
    steps = []
    for d in drugs:
        val = d[field]
        needed = target - val
        partners = table.get(str(needed))
        if partners:
            for other in partners:
                # name ordering stops us from listing the same pair twice
                if d["name"] < other:
                    pairs.append((d["name"], other))
            other_names = [p for p in partners if p != d["name"]]
            if record_steps:
                if other_names:
                    steps.append(f"{d['name']} ({val}): need {needed}, found {', '.join(other_names)}")
                else:
                    steps.append(f"{d['name']} ({val}): need {needed}, not found")
        else:
            if record_steps:
                steps.append(f"{d['name']} ({val}): need {needed}, not found")
    if record_steps:
        return pairs, steps
    return pairs


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/drugs")
def api_drugs():
    by = request.args.get("by", "name")
    items = [v for k, v in bst.in_order(trees[by])]
    return jsonify({"drugs": items, "height": bst.height(trees[by])})


@app.route("/api/patients")
def api_patients():
    return jsonify(PATIENTS)


@app.route("/api/check", methods=["POST"])
def api_check():
    meds = request.json.get("meds", [])
    unknown = [m for m in meds if drug_table.get(m) is None]
    known = [m for m in meds if m not in unknown]
    pairs_checked = len(known) * (len(known) - 1) // 2
    return jsonify({
        "interactions": check_meds(known),
        "unknown": unknown,
        "pairs_checked": pairs_checked,
        "lookups": pairs_checked
    })


@app.route("/api/twosum", methods=["POST"])
def api_twosum():
    body = request.json or {}
    field = body.get("field", "cost")
    raw_target = body.get("target")
    if raw_target is None or str(raw_target).strip() == "":
        return jsonify({"error": "Target sum cannot be empty"}), 400
    try:
        target = int(raw_target)
    except (ValueError, TypeError):
        return jsonify({"error": "Target sum must be a valid integer"}), 400

    names = body.get("meds") or drug_table.keys()
    drugs = [drug_table.get(n) for n in names if drug_table.get(n)]
    pairs, steps = two_sum(drugs, field, target, record_steps=True)
    results = []
    for a, b in pairs:
        hit = interaction_table.get(pair_key(a, b))
        sev = hit["severity"] if hit else "none"
        if body.get("safe_only") and sev == "major":
            continue
        results.append({"a": a, "b": b, "severity": sev,
                        "note": hit["note"] if hit else "no known interaction"})

    capped_steps = steps[:15]
    if len(steps) > 15:
        capped_steps.append(f"... and {len(steps) - 15} more")

    return jsonify({"pairs": results, "searched": len(drugs), "steps": capped_steps})


@app.route("/api/bst")
def api_bst():
    by = request.args.get("by", "cost")
    op = request.args.get("op")
    root = trees[by]
    name = request.args.get("drug", "")
    drug = drug_table.get(name) if name else None

    if op == "select":
        node = bst.select(root, int(request.args.get("k", 1)))
        return jsonify({"drug": node.value if node else None})
    if drug is None:
        return jsonify({"error": "drug not found"}), 404
    key = tree_key(drug, by)
    if op == "rank":
        return jsonify({"rank": bst.rank(root, key) + 1, "total": bst.size(root)})
    if op == "predecessor":
        node = bst.predecessor(root, key)
        return jsonify({"drug": node.value if node else None})
    return jsonify({"error": "unknown op"}), 400


@app.route("/api/rotate", methods=["POST"])
def api_rotate():
    # rotating the root keeps sorted order, only the shape changes
    by = request.json.get("by", "cost")
    direction = request.json.get("dir", "left")
    root = trees[by]
    if direction == "left" and root.right:
        trees[by] = bst.rotate_left(root)
    elif direction == "right" and root.left:
        trees[by] = bst.rotate_right(root)
    return jsonify({"height": bst.height(trees[by]), "root": trees[by].value["name"]})


@app.route("/api/drug", methods=["POST"])
def api_add_drug():
    b = request.json
    name = str(b.get("name", "")).strip().lower()
    if not name or drug_table.get(name):
        return jsonify({"error": "need a new, non-empty name"}), 400
    try:
        dose, cost = int(b["dose"]), int(b["cost"])
    except (KeyError, ValueError):
        return jsonify({"error": "dose and cost must be whole numbers"}), 400
    return jsonify(add_drug(name, b.get("class", "custom"), dose, cost))


@app.route("/api/drug/<name>", methods=["DELETE"])
def api_delete_drug(name):
    drug = drug_table.get(name)
    if not drug:
        return jsonify({"error": "not found"}), 404
    drug_table.remove(name)
    for by in trees:
        trees[by] = bst.delete(trees[by], tree_key(drug, by))
    return jsonify({"deleted": name})


@app.route("/api/benchmark")
def api_benchmark():
    # same fake keys into each collision method at different load factors
    # uses seeded random keys so linear probing behaves realistically
    import random
    rng = random.Random(42)
    size = 1009
    rows = []
    for load in (0.3, 0.5, 0.7, 0.9):
        n = int(size * load)
        keys = [f"k_{rng.randint(100000, 999999)}_{i}" for i in range(n)]
        row = {"load": load}
        for method in ("chaining", "linear", "double"):
            t = HashTable(size, method)
            for k in keys:
                t.put(k, 1)
            # successful lookups
            t.probes = 0
            for k in keys:
                t.get(k)
            hit_probes = round(t.probes / n, 2)
            row[method] = {"collisions": t.collisions,
                           "avg_probes": hit_probes}
        rows.append(row)
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
