from flask import Flask, request, jsonify
import xgboost as xgb
import numpy as np

app = Flask(__name__)

print("APP STARTED", flush=True)
model1 = xgb.Booster()
model2 = xgb.Booster()
model1.load_model("model/xgboost_1.model")
model2.load_model("model/xgboost_2.model")


###Helper
NEAREST_NEIGHBOR_DG = {
    'AA': -1.00, 'TT': -1.00, 'AT': -0.88, 'TA': -0.58,
    'CA': -1.45, 'TG': -1.45, 'GT': -1.44, 'AC': -1.44,
    'CT': -1.28, 'AG': -1.28, 'GA': -1.30, 'TC': -1.30,
    'CG': -2.17, 'GC': -2.24, 'GG': -1.84, 'CC': -1.84
}
def build_position_features(seq):
    seq = seq.upper()

    features = []

    for i in range(79):  # 60 → 59 dinucleotides
        dinuc = seq[i:i+2]
        dg = NEAREST_NEIGHBOR_DG.get(dinuc, 0.0)
        features.append(dg)

    return features

def to_model_vector(seq):
    feats = build_position_features(seq)

    X = np.array(feats).reshape(1, -1)  

    return X


def generate_windows(seq, window_size=80, step=10):
    return [
        seq[i:i+window_size]
        for i in range(0, len(seq) - window_size + 1, step)
    ]

def build_features(seq):
    seq = seq.upper()

    feats = []

    for i in range(79):
        dinuc = seq[i:i+2]
        feats.append(NEAREST_NEIGHBOR_DG.get(dinuc, 0.0))

    return feats

def predict_window(seq):
    X = build_features(seq)
    dmatrix = xgb.DMatrix([X])

    score1 = float(model1.predict(dmatrix)[0])

    if score1 >= 0.5:
        return score1

    score2 = float(model2.predict(dmatrix)[0])
    return score2

def predict_sequence(seq):
    windows = generate_windows(seq)

    results = []

    for i, w in enumerate(windows):
        score  = predict_window(w)

        results.append({
            "start": i * 10,
            "end": i * 10 + 80,
            "window": w,
            "score": score
        })

    return results

def parse_fasta(raw):
    sequences = []
    header = None
    seq = []

    for line in raw.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(">"):
            if header is not None:
                sequences.append({
                    "header": header,
                    "sequence": "".join(seq).upper()
                })

            header = line[1:].strip()
            seq = []
        else:
            seq.append(line)

    if header is not None:
        sequences.append({
            "header": header,
            "sequence": "".join(seq).upper()
        })

    return sequences


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    raw = data.get("fasta", "")

    parsed = parse_fasta(raw)

    if len(parsed) == 0:
        return jsonify({"error": "No valid sequences"}), 400

    results = []

    for item in parsed:
        seq = item["sequence"]
        header = item["header"]

        n = len(seq)

        base_result = {
            "header": header,
            "sequence": seq,
            "length": n
        }

        if n < 80:
            results.append({
                **base_result,
                "status": "invalid",
                "error": "Sequence too short"
            })
            continue

        if n == 80:
            score = predict_window(seq)

            if score < 0.91:
                flag = "low confidence"
            elif score < 0.94:
                flag = "mid confidence"
            else:
                flag = "high confidence"

            results.append({
                **base_result,
                "status": "ok",
                "mode": "single",
                "final_score": float(score),
                "flag": flag,
                "peak_window": {
                    "start": 0,
                    "end": 80,
                    "score": float(score),
                    "sequence": seq
                }
            })
            continue

        windows = predict_sequence(seq)

        best = max(windows, key=lambda x: x["score"])
        best_start = best["start"]
        best_end = best["end"]
        score = float(best["score"])


        if score < 0.91:
            flag = "low confidence"
        elif score < 0.94:
            flag = "mid confidence"
        else:
            flag = "high confidence"

        results.append({
            **base_result,
            "status": "ok",
            "mode": "best_window",
            "final_score": score,
            "flag": flag,
            "peak_window": {
                "start": best["start"],
                "end": best["end"],
                "score": score,
                "sequence": best["window"][best_start:best_end]
            }
        })

    return jsonify({
        "mode": "batch",
        "n_sequences": len(results),
        "results": results
    })








@app.route("/health")
def health():
    print("HEALTH HIT", flush=True)
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)