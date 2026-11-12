"""FEATURE 3: UNUSUAL TRANSACTION DETECTION USING ISOLATION FOREST
SmartFlow AIML Module - 3rd Year AIML Major Project

Algorithm: Isolation Forest (iForest)
Implementation: Hybrid architecture (scikit-learn with pure-Python iForest fallback for 100% portability)
Objective: Identify statistically unusual transaction outliers (abnormal amounts, velocities, tenders)
and flag records for administrative audit review without blocking users.
"""
import math
import random
from backend.app.extensions import db
from backend.app.models.order import Transaction


class IsolationTreeNode:
    """Node in an Isolation Tree (iTree)."""
    def __init__(self, left=None, right=None, split_feature=None, split_value=None, size=0):
        self.left = left
        self.right = right
        self.split_feature = split_feature
        self.split_value = split_value
        self.size = size
        self.is_leaf = (left is None and right is None)


class PurePythonIsolationTree:
    """Single Isolation Tree recursively partitioning feature space."""
    def __init__(self, max_depth: int):
        self.max_depth = max_depth
        self.root = None

    def fit(self, X: list[list[float]], current_depth: int = 0) -> IsolationTreeNode:
        n_samples = len(X)
        if n_samples <= 1 or current_depth >= self.max_depth:
            return IsolationTreeNode(size=n_samples)

        n_features = len(X[0])
        q = random.randint(0, n_features - 1)  # Random feature index
        vals = [row[q] for row in X]
        min_v, max_v = min(vals), max(vals)

        if min_v == max_v:
            return IsolationTreeNode(size=n_samples)

        p = random.uniform(min_v, max_v)  # Random split point

        left_X = [row for row in X if row[q] < p]
        right_X = [row for row in X if row[q] >= p]

        left_node = self.fit(left_X, current_depth + 1)
        right_node = self.fit(right_X, current_depth + 1)

        return IsolationTreeNode(left=left_node, right=right_node, split_feature=q, split_value=p, size=n_samples)

    def path_length(self, x: list[float], node: IsolationTreeNode, current_depth: int = 0) -> float:
        """Compute path length from root to terminal leaf."""
        if node.is_leaf:
            # Average path length correction for unbuilt subtrees c(node.size)
            return current_depth + self._c(node.size)

        if x[node.split_feature] < node.split_value:
            return self.path_length(x, node.left, current_depth + 1)
        else:
            return self.path_length(x, node.right, current_depth + 1)

    @staticmethod
    def _c(n: int) -> float:
        """Euler-Mascheroni constant approximation for average unsuccessful search in BST."""
        if n <= 1:
            return 0.0
        if n == 2:
            return 1.0
        euler = 0.5772156649
        return 2.0 * (math.log(n - 1) + euler) - (2.0 * (n - 1) / n)


class PurePythonIsolationForest:
    """Ensemble of Isolation Trees (Zero C-extension dependency)."""
    def __init__(self, n_estimators: int = 50, contamination: float = 0.03):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.trees = []
        self.max_samples = 256
        self.threshold = 0.60

    def fit(self, X: list[list[float]]):
        n_samples = len(X)
        if n_samples == 0:
            return self

        subsample_size = min(self.max_samples, n_samples)
        max_depth = int(math.ceil(math.log2(max(subsample_size, 2))))

        self.trees = []
        for _ in range(self.n_estimators):
            subsample = random.sample(X, subsample_size) if n_samples > subsample_size else X
            tree = PurePythonIsolationTree(max_depth=max_depth)
            tree.root = tree.fit(subsample)
            self.trees.append(tree)

        # Compute scores on training data to calibrate contamination threshold
        scores = self.decision_function(X)
        sorted_scores = sorted(scores, reverse=True)  # Higher score = more anomalous
        cutoff_idx = max(int(len(sorted_scores) * self.contamination), 1)
        self.threshold = sorted_scores[cutoff_idx - 1]
        return self

    def decision_function(self, X: list[list[float]]) -> list[float]:
        """Compute anomaly score s(x, n) = 2^(- E(h(x)) / c(n)).
        Range: 0.0 to 1.0. Score > 0.60 indicates a strong anomaly.
        """
        n = len(X)
        c_n = PurePythonIsolationTree._c(min(self.max_samples, n))
        if c_n == 0:
            c_n = 1.0

        scores = []
        for row in X:
            avg_h = sum(tree.path_length(row, tree.root) for tree in self.trees) / len(self.trees)
            # Anomaly score formula
            s = math.pow(2.0, - (avg_h / c_n))
            scores.append(s)
        return scores

    def predict(self, X: list[list[float]]) -> list[int]:
        """Returns -1 for anomaly, 1 for normal."""
        scores = self.decision_function(X)
        return [-1 if s >= self.threshold else 1 for s in scores]


class AnomalyDetector:
    def __init__(self, contamination: float = 0.03):
        self.contamination = contamination
        self.use_sklearn = False

        try:
            from sklearn.ensemble import IsolationForest
            self.model = IsolationForest(contamination=contamination, random_state=42, n_estimators=60)
            self.use_sklearn = True
        except Exception:
            self.model = PurePythonIsolationForest(n_estimators=50, contamination=contamination)

    def fit_predict(self, X: list) -> tuple[list[int], list[float]]:
        """Fit Isolation Forest and return (labels, anomaly_scores)."""
        if len(X) > 0 and not isinstance(X[0], (list, tuple)):
            X = [[float(v)] for v in X]
        if self.use_sklearn:
            import numpy as np
            arr = np.array(X)
            self.model.fit(arr)
            preds = list(self.model.predict(arr))
            scores = list(self.model.decision_function(arr))
        else:
            self.model.fit(X)
            preds = self.model.predict(X)
            scores = self.model.decision_function(X)
        return preds, scores

    def _extract_feature_rows(self, transactions: list[Transaction]) -> list[list[float]]:
        """Extract: [amount, payment_method_code, source_code, hour_of_day, day_of_week]."""
        pay_map = {'CASH': 1.0, 'UPI': 2.0, 'CARD': 3.0, 'ONLINE_NETBANKING': 4.0}
        src_map = {'STORE': 1.0, 'ONLINE': 2.0}

        rows = []
        for t in transactions:
            amt = float(t.amount)
            pm = pay_map.get(t.payment_method, 1.0)
            src = src_map.get(t.source, 1.0)
            hr = float(t.created_at.hour) if t.created_at else 12.0
            dow = float(t.created_at.weekday()) if t.created_at else 2.0
            rows.append([amt, pm, src, hr, dow])
        return rows

    def fit_and_flag(self, update_db: bool = True) -> dict:
        """Run Isolation Forest detection across transaction database."""
        txns = Transaction.query.order_by(Transaction.id.asc()).all()
        if len(txns) < 10:
            return {
                'total_analyzed': len(txns),
                'anomalies_detected': 0,
                'message': 'Insufficient transactions for Isolation Forest (minimum 10 required).'
            }

        X = self._extract_feature_rows(txns)

        if self.use_sklearn:
            import numpy as np
            self.model.fit(np.array(X))
            preds = list(self.model.predict(np.array(X)))
            scores = list(self.model.decision_function(np.array(X)))
        else:
            self.model.fit(X)
            preds = self.model.predict(X)
            scores = self.model.decision_function(X)

        flagged_count = 0
        anomaly_list = []

        for i, txn in enumerate(txns):
            is_anomaly = bool(preds[i] == -1)
            raw_score = float(scores[i])

            if update_db:
                txn.is_flagged_anomaly = is_anomaly
                txn.anomaly_score = raw_score

            if is_anomaly:
                flagged_count += 1
                anomaly_list.append({
                    'transaction_id': txn.transaction_id,
                    'amount': float(txn.amount),
                    'source': txn.source,
                    'payment_method': txn.payment_method,
                    'score': round(raw_score, 4),
                    'reason': f"Outlier detected: Statistical deviation in {txn.payment_method} tender of ₹{float(txn.amount):.2f}"
                })

        if update_db:
            db.session.commit()

        return {
            'total_analyzed': len(txns),
            'anomalies_detected': flagged_count,
            'contamination_rate': self.contamination,
            'anomalies': anomaly_list[:20],
            'algorithm': 'Isolation Forest (iTree ensemble)',
            'message': f"Isolation Forest scanned {len(txns)} transactions and flagged {flagged_count} statistical outliers for review."
        }
