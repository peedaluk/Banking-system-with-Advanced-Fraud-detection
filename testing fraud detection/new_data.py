import pandas as pd
from collections import defaultdict
from datetime import timedelta
from io import StringIO

#############################
# 1. BUILD THE HYPERGRAPH
#############################

import pandas as pd

def build_hypergraph_from_dataset(csv_path):
    df = pd.read_csv(csv_path).head(30000)
    # Strip any whitespace from column names
    df.columns = df.columns.str.strip()

    # Print columns for verification
    print(f"Columns in dataset: {df.columns.tolist()}")

    hypergraph = defaultdict(list)
    for idx, row in df.iterrows():
        src = f"{row['From Bank']}_{row['Account']}"
        # Use 'Account.1' for destination; fallback to 'Account' if not present
        dst = f"{row['To Bank']}_{row['Account.1'] if 'Account.1' in df.columns else row['Account']}"
        txn = {
            'amount': row['Amount Received'],
            'currency': row['Receiving Currency'],
            'payment_format': row['Payment Format'],
            'timestamp': pd.to_datetime(row['Timestamp']),
            'is_laundering': row.get('Is Laundering', 0)
        }
        hypergraph[src].append((dst, txn))
        if (idx % 10000 == 0):
            print(f"Example hypergraph edge of idx : {idx} : {src} -> {dst} | {txn}")
    print(f"Built hypergraph with {len(hypergraph)} unique accounts.")
    return hypergraph

# Usage:
# hypergraph = build_hypergraph_from_dataset('LI-Small_Trans.csv')


#############################
# 2. FRAUD CYCLE DETECTION
#############################

def detect_fraud_cycles(
    hypergraph, alpha=0.5, min_length=2, max_length=6, max_cycle_time=timedelta(days=3)
):
    print(f"[INFO] Starting cycle detection...")
    cycles = []
    visited_edges = set()
    edge_list = []
    for src in hypergraph:
        for dst, txn in hypergraph[src]:
            if src == dst: 
                continue
            edge_list.append((src, dst, txn))
    edge_list.sort(key=lambda x: x[2]['timestamp'])
    print(f"[INFO] Sorted {len(edge_list)} edges by timestamp.")

    def dfs(path, start_edge, current_node, depth):
        if depth > max_length:
            return
        last_txn = path[-1][2]
        for neighbor, txn in hypergraph.get(current_node, []):
            edge_id = (current_node, neighbor, txn['timestamp'])
            if edge_id in visited_edges:
                continue
            if abs(start_edge[2]['amount'] - txn['amount']) > alpha * start_edge[2]['amount']:
                continue
            if txn['timestamp'] <= last_txn['timestamp']:
                continue
            new_path = path + [(current_node, neighbor, txn)]
            if neighbor == start_edge[0] and min_length <= depth + 1 <= max_length:
                if (txn['timestamp'] - start_edge[2]['timestamp']) <= max_cycle_time:
                    cycles.append(new_path)
                    print(f"[DEBUG] Found cycle: {[ (s,d,round(t['amount'],2)) for s,d,t in new_path ]}")
                    continue
            visited_edges.add(edge_id)
            dfs(new_path, start_edge, neighbor, depth + 1)
            visited_edges.remove(edge_id)

    for i, (src, dst, txn) in enumerate(edge_list):
        if i % 10000 == 0 and i > 0:
            print(f"[INFO] Processed {i} edges...")
        start_edge = (src, dst, txn)
        visited_edges.add((src, dst, txn['timestamp']))
        dfs([start_edge], start_edge, dst, 1)
        visited_edges.remove((src, dst, txn['timestamp']))
    print(f"[INFO] Cycle detection finished. Found {len(cycles)} cycles.")
    return cycles

#############################
# 3. PARSE GROUND TRUTH TXT
#############################

def parse_results_txt(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    data_lines = []
    recording = False
    for line in lines:
        line = line.strip()
        if line.startswith('BEGIN LAUNDERING ATTEMPT'):
            recording = True
            continue
        if line.startswith('END LAUNDERING ATTEMPT'):
            recording = False
            continue
        if recording and line and not line.startswith('BEGIN'):
            data_lines.append(line)
    columns = ['Timestamp', 'From Bank', 'From Account', 'To Bank', 'To Account',
               'Amount Received', 'Receiving Currency', 'Amount Paid', 'Payment Currency', 'Payment Format', 'Label']
    csv_data = '\n'.join(data_lines)
    provided_df = pd.read_csv(StringIO(csv_data), names=columns)
    provided_set = set()
    for idx, row in provided_df.iterrows():
        src = f"{row['From Bank']}_{row['From Account']}"
        dst = f"{row['To Bank']}_{row['To Account']}"
        amount = float(row['Amount Received'])
        timestamp = pd.to_datetime(row['Timestamp'])
        provided_set.add((src, dst, amount, timestamp))
    return provided_set

#############################
# 4. COMPARE RESULTS
#############################

def detected_cycles_to_set(detected_cycles):
    detected_set = set()
    for cycle in detected_cycles:
        for src, dst, txn in cycle:
            detected_set.add((src, dst, float(txn['amount']), pd.to_datetime(txn['timestamp'])))
    return detected_set

def compare_results(detected_set, provided_set):
    true_positives = detected_set & provided_set
    false_positives = detected_set - provided_set
    false_negatives = provided_set - detected_set

    print("True Positives:", len(true_positives))
    print("False Positives:", len(false_positives))
    print("False Negatives:", len(false_negatives))
    print("Sample True Positives:", list(true_positives)[:5])
    print("Sample False Positives:", list(false_positives)[:5])
    print("Sample False Negatives:", list(false_negatives)[:5])

    precision = len(true_positives) / (len(true_positives) + len(false_positives) + 1e-9)
    recall = len(true_positives) / (len(true_positives) + len(false_negatives) + 1e-9)
    f1 = 2 * precision * recall / (precision + recall + 1e-9)
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

#############################
# 5. MAIN PIPELINE
#############################

if __name__ == "__main__":
    # Step 1: Build the hypergraph
    hypergraph = build_hypergraph_from_dataset('LI-Small_Trans.csv')

    # Step 2: Detect fraud cycles
    fraud_cycles = detect_fraud_cycles(
        hypergraph,
        alpha=0.1,          # 10% amount tolerance
        min_length=2,
        max_length=6,
        max_cycle_time=timedelta(days=3)
    )
    print(f"[INFO] Detected {len(fraud_cycles)} suspicious cycles.")

    # Step 3: Parse ground truth laundering attempts from results.txt
    provided_set = parse_results_txt('results.txt')

    # Step 4: Convert detected cycles to set format
    detected_set = detected_cycles_to_set(fraud_cycles)

    # Step 5: Compare and print results
    compare_results(detected_set, provided_set)
