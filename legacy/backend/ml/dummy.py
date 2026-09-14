import numpy as np
class DummyXGB:
    def predict_proba(self, X):
        return np.array([[0.1, 0.9]])
class DummyIForest:
    def decision_function(self, X):
        return np.array([0.95])
