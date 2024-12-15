from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.variants import variants_filter
from collections import Counter
import math
from itertools import combinations
from multiprocessing import Pool

def levenshtein(s1, s2):
    dp = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]
    for i in range(len(s1) + 1):
        for j in range(len(s2) + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[len(s1)][len(s2)]

def compute_variant_variability(event_log):
    variants = variants_filter.get_variants(event_log)
    return len(variants)

def compute_edit_distance_chunk(chunk):
    results = []
    for trace1, trace2 in chunk:
        results.append(levenshtein(trace1, trace2))
    return results

def chunk_traces(traces, chunk_size):
    all_pairs = list(combinations(traces, 2))
    for i in range(0, len(all_pairs), chunk_size):
        yield all_pairs[i:i + chunk_size]

def compute_edit_distance_variability(event_log, num_processes=4):
    variants = list(variants_filter.get_variants(event_log).keys())
    n = len(variants)
    if n < 2:
        return 0
    
    chunk_size = len(variants) // num_processes
    trace_chunks = list(chunk_traces(variants, chunk_size))
    
    with Pool(num_processes) as pool:
        results = pool.map(compute_edit_distance_chunk, trace_chunks)
    
    all_distances = [distance for chunk in results for distance in chunk]
    return sum(all_distances) / len(all_distances)

def compute_my_variability(event_log):
    activity_counter = Counter()
    for trace in event_log:
        for event in trace:
            activity_counter[event['concept:name']] += 1
    total = sum(activity_counter.values())
    entropy = -sum((count / total) * math.log2(count / total) for count in activity_counter.values())
    return entropy

def write_results_to_file(results, filename="output_results.txt"):
    with open(filename, "w") as file:
        for log, metrics in results.items():
            file.write(f"Results for {log}:\n")
            for metric, value in metrics.items():
                file.write(f"  {metric}: {value}\n")
            file.write("\n")
    print(f"Results written to {filename}")


def main():
    logs = {
        #"BPI Challenge 2011": "BPIChallenge2011.xes",
        "Concept Drift": "concept_drift.xes",
        "Concept Drift Type 1": "concept_drift_type1.xes",
        "Concept Drift Type 2": "concept_drift_type2.xes"
    }
    
    results = {}
    for log_name, log_path in logs.items():
        print(f"Processing log: {log_name}...")
        event_log = xes_importer.apply(log_path)
        results[log_name] = {
            "Variants": compute_variant_variability(event_log),
            "Edit Distance": compute_edit_distance_variability(event_log, 8),
            "Custom Variability": compute_my_variability(event_log)
        }
    
    for log, metrics in results.items():
        print(f"Results for {log}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")

    # Write results to a file
    write_results_to_file(results)

if __name__ == "__main__":
    main()
