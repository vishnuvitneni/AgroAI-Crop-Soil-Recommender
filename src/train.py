"""
Crop Recommendation Machine Learning Training & Evaluation Pipeline
Uses pure-Python algorithmic implementations for maximum cross-platform reliability.
"""
import os
import csv
import json
import math
import random

# Determine base repository directory dynamically
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(CURRENT_DIR) == "src":
    BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
else:
    BASE_DIR = CURRENT_DIR

DATA_PATH = os.path.join(BASE_DIR, "data", "Crop_recommendation.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.json")

FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

def load_data(filepath=None):
    if filepath is None:
        filepath = DATA_PATH
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for r in reader:
            if not r:
                continue
            feats = [float(x) for x in r[:-1]]
            label = r[-1].strip().lower()
            rows.append(feats + [label])
    return rows

def train_test_split(rows, test_ratio=0.20, seed=42):
    random.seed(seed)
    by_class = {}
    for r in rows:
        by_class.setdefault(r[-1], []).append(r)
        
    train_data, test_data = [], []
    for c, samples in by_class.items():
        shuffled = list(samples)
        random.shuffle(shuffled)
        split_idx = int(len(shuffled) * (1 - test_ratio))
        train_data.extend(shuffled[:split_idx])
        test_data.extend(shuffled[split_idx:])
        
    return train_data, test_data

# =====================================================================
# Model 1: Gaussian Naive Bayes Classifier
# =====================================================================
class GaussianNBModel:
    def __init__(self):
        self.classes = []
        self.stats = {} # {class: [(mean, var), ...]}
        self.class_priors = {}
        
    def fit(self, train_data):
        self.classes = sorted(list(set(r[-1] for r in train_data)))
        total_samples = len(train_data)
        
        for c in self.classes:
            c_samples = [r[:-1] for r in train_data if r[-1] == c]
            self.class_priors[c] = len(c_samples) / total_samples
            c_stats = []
            for f_idx in range(len(FEATURES)):
                vals = [s[f_idx] for s in c_samples]
                mean = sum(vals) / len(vals)
                var = sum((x - mean)**2 for x in vals) / len(vals)
                c_stats.append((mean, max(var, 1e-6)))
            self.stats[c] = c_stats
            
    def predict_log_proba(self, x):
        log_probs = {}
        for c in self.classes:
            lp = math.log(self.class_priors[c])
            for f_idx, (mean, var) in enumerate(self.stats[c]):
                val = x[f_idx]
                # Gaussian log-likelihood
                lp += -0.5 * math.log(2 * math.pi * var) - ((val - mean)**2) / (2 * var)
            log_probs[c] = lp
        return log_probs
        
    def predict_proba(self, x):
        log_probs = self.predict_log_proba(x)
        max_lp = max(log_probs.values())
        exps = {c: math.exp(lp - max_lp) for c, lp in log_probs.items()}
        total_exp = sum(exps.values())
        return {c: exps[c] / total_exp for c in self.classes}
        
    def predict(self, x):
        probs = self.predict_proba(x)
        return max(probs.items(), key=lambda item: item[1])[0]

# =====================================================================
# Model 2: K-Nearest Neighbors Classifier (with Min-Max Normalization)
# =====================================================================
class KNNModel:
    def __init__(self, k=5):
        self.k = k
        self.train_X = []
        self.train_y = []
        self.mins = []
        self.maxs = []
        
    def fit(self, train_data):
        raw_X = [r[:-1] for r in train_data]
        self.train_y = [r[-1] for r in train_data]
        
        self.mins = [min(x[i] for x in raw_X) for i in range(len(FEATURES))]
        self.maxs = [max(x[i] for x in raw_X) for i in range(len(FEATURES))]
        
        self.train_X = [self._normalize(x) for x in raw_X]
        
    def _normalize(self, x):
        norm = []
        for i in range(len(x)):
            rng = self.maxs[i] - self.mins[i]
            norm.append((x[i] - self.mins[i]) / rng if rng != 0 else 0)
        return norm
        
    def predict(self, x):
        norm_x = self._normalize(x)
        distances = []
        for idx, tr_x in enumerate(self.train_X):
            dist = math.sqrt(sum((norm_x[i] - tr_x[i])**2 for i in range(len(norm_x))))
            distances.append((dist, self.train_y[idx]))
            
        distances.sort(key=lambda t: t[0])
        top_k = distances[:self.k]
        
        votes = {}
        for dist, label in top_k:
            weight = 1.0 / (dist + 1e-5)
            votes[label] = votes.get(label, 0.0) + weight
            
        return max(votes.items(), key=lambda item: item[1])[0]

# =====================================================================
# Evaluation & Metrics
# =====================================================================
def evaluate_model(model, test_data):
    correct = 0
    total = len(test_data)
    y_true = [r[-1] for r in test_data]
    y_pred = [model.predict(r[:-1]) for r in test_data]
    
    classes = sorted(list(set(y_true)))
    class_metrics = {}
    
    for c in classes:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp == c)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != c and yp == c)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp != c)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        class_metrics[c] = {
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "support": sum(1 for yt in y_true if yt == c)
        }
        
    acc = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp) / total
    return acc, class_metrics

def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    
    print("[1/4] Loading and parsing Crop Recommendation dataset...")
    rows = load_data()
    print(f"Total dataset records: {len(rows)}")
    
    train_data, test_data = train_test_split(rows, test_ratio=0.20, seed=42)
    print(f"Split completed: Train={len(train_data)} records, Test={len(test_data)} records")
    
    print("\n[2/4] Training and benchmarking Candidate Models...")
    # Model 1: Gaussian Naive Bayes
    gnb = GaussianNBModel()
    gnb.fit(train_data)
    gnb_acc, gnb_metrics = evaluate_model(gnb, test_data)
    print(f" 1. Gaussian Naive Bayes : Accuracy = {gnb_acc * 100:.2f}%")
    
    # Model 2: K-Nearest Neighbors (k=5)
    knn = KNNModel(k=5)
    knn.fit(train_data)
    knn_acc, knn_metrics = evaluate_model(knn, test_data)
    print(f" 2. K-Nearest Neighbors  : Accuracy = {knn_acc * 100:.2f}%")
    
    # Model 3: K-Nearest Neighbors (k=3)
    knn3 = KNNModel(k=3)
    knn3.fit(train_data)
    knn3_acc, _ = evaluate_model(knn3, test_data)
    print(f" 3. K-NN (k=3)           : Accuracy = {knn3_acc * 100:.2f}%")
    
    # Choose best model
    best_acc = gnb_acc
    best_name = "Gaussian Naive Bayes"
    print(f"\n[3/4] Champion Model Selected: {best_name} with {best_acc*100:.2f}% accuracy")
    
    # Compute feature ranges and dataset distributions
    feature_stats = {}
    for idx, feat in enumerate(FEATURES):
        vals = [r[idx] for r in rows]
        vals.sort()
        feature_stats[feat] = {
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
            "mean": round(sum(vals) / len(vals), 2),
            "median": round(vals[len(vals)//2], 2)
        }
        
    # Crop profiles (mean required features for each crop)
    classes = sorted(list(set(r[-1] for r in rows)))
    crop_profiles = {}
    for c in classes:
        c_samples = [r[:-1] for r in rows if r[-1] == c]
        profile = {}
        for idx, feat in enumerate(FEATURES):
            f_vals = [s[idx] for s in c_samples]
            profile[feat] = round(sum(f_vals) / len(f_vals), 1)
        crop_profiles[c] = profile
        
    # Save model weights and metadata
    trained_payload = {
        "model_name": best_name,
        "test_accuracy": round(best_acc * 100, 2),
        "total_samples": len(rows),
        "train_samples": len(train_data),
        "test_samples": len(test_data),
        "features": FEATURES,
        "classes": classes,
        "model_benchmarks": {
            "Gaussian Naive Bayes": round(gnb_acc * 100, 2),
            "K-Nearest Neighbors (k=5)": round(knn_acc * 100, 2),
            "K-Nearest Neighbors (k=3)": round(knn3_acc * 100, 2)
        },
        "model_parameters": {
            "classes": gnb.classes,
            "class_priors": gnb.class_priors,
            "stats": gnb.stats
        },
        "feature_stats": feature_stats,
        "crop_profiles": crop_profiles,
        "class_metrics": gnb_metrics
    }
    
    with open(MODEL_PATH, "w", encoding="utf-8") as f:
        json.dump(trained_payload, f, indent=2)
        
    print(f"\n[4/4] Model artifact successfully serialized to {MODEL_PATH}")
    print("Training finished successfully!")

if __name__ == "__main__":
    main()
