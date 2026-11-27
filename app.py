# drug interaction and dosage matcher
# run with: python app.py  then open http://127.0.0.1:5000
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


def two_sum(drugs, field, target):
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
    for d in drugs:
        partners = table.get(str(target - d[field]))
        if partners:
            for other in partners:
                # name ordering stops us from listing the same pair twice
                if d["name"] < other:
                    pairs.append((d["name"], other))
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
    return jsonify({"interactions": check_meds(known), "unknown": unknown,
                    "pairs_checked": len(known) * (len(known) - 1) // 2})


@app.route("/api/twosum", methods=["POST"])
def api_twosum():
    body = request.json
    field = body.get("field", "cost")
    target = int(body.get("target", 0))
    names = body.get("meds") or drug_table.keys()
    drugs = [drug_table.get(n) for n in names if drug_table.get(n)]
    results = []
    for a, b in two_sum(drugs, field, target):
        hit = interaction_table.get(pair_key(a, b))
        sev = hit["severity"] if hit else "none"
        if body.get("safe_only") and sev == "major":
            continue
        results.append({"a": a, "b": b, "severity": sev,
                        "note": hit["note"] if hit else "no known interaction"})
    return jsonify({"pairs": results, "searched": len(drugs)})


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
    size = 1009
    rows = []
    for load in (0.3, 0.5, 0.7, 0.9):
        n = int(size * load)
        keys = ["rx%05d" % i for i in range(n)]
        row = {"load": load}
        for method in ("chaining", "linear", "double"):
            t = HashTable(size, method)
            for k in keys:
                t.put(k, 1)
            t.probes = 0
            for k in keys:
                t.get(k)
            row[method] = {"collisions": t.collisions,
                           "avg_probes": round(t.probes / n, 2)}
        rows.append(row)
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
