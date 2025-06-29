from datetime import timedelta

def tarjan_scc(graph):
    """
    graph: dict {node: list of (neighbor, transaction_dict)}
    transaction_dict: {'amount': float, 'timestamp': datetime, ...}
    Returns: list of SCCs (each SCC is a list of node IDs)
    """
    index = 0
    stack = []
    indices = {}
    lowlink = {}
    on_stack = set()
    sccs = []

    def strong_connect(v):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w, _ in graph.get(v, []):
            if w not in indices:
                strong_connect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            if len(scc) > 1:  # Only consider cycles/multi-node SCCs
                sccs.append(scc)

    for v in graph:
        if v not in indices:
            strong_connect(v)
    return sccs

def get_transactions_in_scc(scc, graph):
    """
    Returns a list of transactions (dicts) forming the SCC.
    """
    txns = []
    for src in scc:
        for dst, txn in graph.get(src, []):
            if dst in scc:
                txns.append({'src': src, 'dst': dst, **txn})
    return txns

def is_temporal_ordered(txns, max_cycle_time=timedelta(hours=24)):
    """
    Checks if transactions are in timestamp order and within a reasonable time window.
    """
    sorted_txns = sorted(txns, key=lambda x: x['timestamp'])
    times = [t['timestamp'] for t in sorted_txns]
    return all(earlier <= later for earlier, later in zip(times, times[1:])) and \
           (times[-1] - times[0] <= max_cycle_time)

def is_value_similar(txns, alpha=0.1):
    """
    Checks if all amounts are within alpha (e.g., 10%) of the first txn.
    """
    amounts = [t['amount'] for t in txns]
    base = amounts[0]
    return all(abs(a - base) <= alpha * base for a in amounts)

def detect_suspicious_cycles(graph, alpha=0.1, min_cycle_length=3, max_cycle_time=timedelta(hours=24)):
    
    sccs = tarjan_scc(graph)
    suspicious = []
    for scc in sccs:
        if len(scc) >= min_cycle_length:
            txns = get_transactions_in_scc(scc, graph)
            if is_temporal_ordered(txns, max_cycle_time) and is_value_similar(txns, alpha):
                suspicious.append({'accounts': scc, 'transactions': txns})
    return suspicious
