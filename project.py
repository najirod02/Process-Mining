from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.variants import variants_filter
from collections import Counter
from itertools import combinations
import math
from tqdm import tqdm

def levenshtein_word_level(trace1, trace2):
    """
    Compute Levenshtein distance at the word level between two traces.

    Parameters:
        trace1 (str): First trace string.
        trace2 (str): Second trace string.

    Returns:
        int: Word-level Levenshtein distance between trace1 and trace2.
    """
    words1 = trace1.split(" ")
    words2 = trace2.split(" ")
    
    dp = [[0] * (len(words2) + 1) for _ in range(len(words1) + 1)]
    
    for i in range(len(words1) + 1):
        for j in range(len(words2) + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif words1[i - 1] == words2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],
                                   dp[i][j - 1],
                                   dp[i - 1][j - 1])

    return dp[len(words1)][len(words2)]


def compute_edit_distance(variant_pair, frequencies):
    var1, var2 = variant_pair
    distance = levenshtein_word_level(str(var1), str(var2))
    #consider frequencies of variants
    weight = frequencies[var1] * frequencies[var2]
    return distance * weight, weight


def compute_edit_distance_variability(event_log):
    #extract unique variants and their frequencies
    variants_info = variants_filter.get_variants(event_log)
    variants = list(variants_info.keys())#unique variants
    frequencies = {variant: len(traces) for variant, traces in variants_info.items()}

    all_pairs = list(combinations(variants, 2))
    total_weighted_distance = 0
    total_pairs = 0
    #print(f"Total unique variant pairs: {len(all_pairs)}")

    #using tqdm to display progress bar
    for pair in tqdm(all_pairs, desc="Computing Edit Distance", unit="pair"):
        weighted_distance, weight = compute_edit_distance(pair, frequencies)
        total_weighted_distance += weighted_distance
        total_pairs += weight

    return total_weighted_distance / total_pairs if total_pairs > 0 else 0


def compute_variant_variability(event_log):
    return len(variants_filter.get_variants(event_log))


def compute_my_variability(event_log):
    activity_counter = Counter()
    for trace in event_log:
        for event in trace:
            activity_counter[event['concept:name']] += 1
    total = sum(activity_counter.values())
    return -sum((count / total) * math.log2(count / total) for count in activity_counter.values())


def process_log(log_name, log_path):
    print(f"\nProcessing log: {log_name}...")
    event_log = xes_importer.apply(log_path)
    results = {
        "log_name": log_name,
        "Variants": compute_variant_variability(event_log),
        "Edit Distance Variability": compute_edit_distance_variability(event_log),
        "Custom Variability (Entropy)": compute_my_variability(event_log)
    }
    return results


def write_results_to_file(results, filename="output_results.txt"):
    with open(filename, "w") as file:
        for log, metrics in results.items():
            file.write(f"Results for {log}:\n")
            for metric, value in metrics.items():
                file.write(f"  {metric}: {value}\n")
            file.write("\n")


def main():
    logs = {
        "Concept Drift": "concept_drift.xes",
        "Concept Drift Type 1": "concept_drift_type1.xes",
        "Concept Drift Type 2": "concept_drift_type2.xes",
        #"BPIChallenge2011": "BPIChallenge2011.xes"
    }

    results = {}
    for log_name, log_path in logs.items():
        results[log_name] = process_log(log_name, log_path)

    #print results on terminal
    print("\n-------------------------------------------------------")
    for log, metrics in results.items():
        print(f"\nResults for {log}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")

    #write results on file
    write_results_to_file(results)


if __name__ == "__main__":
    main()
