# utils/transaction_graph.py

from threading import Lock

class TransactionGraph:
    def __init__(self):
        self.graph = {}  # {src_account: [(dst_account, txn_dict), ...]}
        self.lock = Lock()

    def add_transaction(self, src, dst, amount, timestamp):
        with self.lock:
            txn = {'amount': float(amount), 'timestamp': timestamp}
            self.graph.setdefault(src, []).append((dst, txn))

    def get_graph(self):
        with self.lock:
            # Return a deep copy if you want to avoid concurrency issues
            return {k: list(v) for k, v in self.graph.items()}

# Singleton instance
transaction_graph = TransactionGraph() 
