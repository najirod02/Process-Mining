#pm4py library
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.variants import variants_filter

#modules to compute pairs
from collections import Counter
from itertools import combinations

#modules to compute variabilities
from functools import lru_cache
from rapidfuzz.distance import Levenshtein
import math

from tqdm import tqdm
import os

# ----------- user defined functions ----------- 
'''
Compute the edit distance by using the levenshtein distance
and a small cache optimization to speed up a little the
computation
'''
@lru_cache(maxsize=None)
def levenshtein_word_level_cached(trace1, trace2):
    #prepare the string by removing the first and last char which 
    # are '(' ')' and create a list of words from the traces
    trace1 = trace1[1:-1]
    trace2 = trace2[1:-1]
    words1 = trace1.split(",")
    words2 = trace2.split(",")

    return Levenshtein.distance(words1, words2)


'''
A wrap function that prepares the input data for the edit distance
function and that also keeps in consideration the number of
frequencies of each trace
'''
def compute_edit_distance(variant_pair, frequencies):
    var1, var2 = variant_pair
    distance = levenshtein_word_level_cached(str(var1), str(var2))
    #consider frequencies of variants
    weight = frequencies[var1] * frequencies[var2]
    return distance * weight, weight


'''
Given the log file and name, process the three functions 
and return the results as a dictionary
'''
def process_log(log_name, log_path):
    print(f"\nProcessing log: {log_name}...")
    event_log = xes_importer.apply(log_path)
    results = {
        "log_name": log_name,
        "Unique activities": compute_unique_activities(event_log),
        "Variants": compute_variant_variability(event_log),
        "Edit Distance Variability": compute_edit_distance_variability(event_log),
        "Custom Variability (Entropy)": compute_my_variability(event_log)
    }
    return results


'''
Given a dictionary of results, defined as in process_log, write
them in the given filename
'''
def write_results_to_file(results, filename="output_results.txt"):
    # Read the existing file (if it exists) and store already written logs
    if os.path.exists(filename):
        with open(filename, "r") as file:
            existing_logs = set(line.strip().split(":")[1].strip() for line in file if line.startswith("Results for"))
    else:
        existing_logs = set()

    # Open the file in write mode to overwrite it
    with open(filename, "w") as file:
        for log, metrics in results.items():
            file.write(f"Results for {log}:\n")
            for metric, value in metrics.items():
                file.write(f"  {metric}: {value}\n")
            file.write("\n")


'''
Returning the number of unique activities in the event log
'''
def compute_unique_activities(event_log):
    activity_counter = set()
    for trace in event_log:
        for event in trace:
            activity_counter.add(event['concept:name'])
    return len(activity_counter)
# ----------- user defined functions ----------- 


# ----------- requested functions for the project ----------- 
'''
Returning the number of variants of the event log
'''
def compute_variant_variability(event_log):
    return len(variants_filter.get_variants(event_log))


'''
Returning the average edit distance between pairs of traces
'''
def compute_edit_distance_variability(event_log):
    #extract unique variants and their frequencies
    variants_info = variants_filter.get_variants(event_log)
    #little speed up for big logs
    variants = sorted(variants_info.keys(), key=lambda x: len(" ".join(x).split(" ")))
    frequencies = {variant: len(traces) for variant, traces in variants_info.items()}

    all_pairs = list(combinations(variants, 2))
    total_weighted_distance = 0
    total_pairs = 0

    #using tqdm to display progress bar
    for pair in tqdm(all_pairs, desc="Computing Edit Distance", unit="pair"):
        weighted_distance, weight = compute_edit_distance(pair, frequencies)
        total_weighted_distance += weighted_distance
        total_pairs += weight

    return total_weighted_distance / total_pairs if total_pairs > 0 else 0


'''
Entropy computation based solely on the control flow of the traces.
The entropy tells you how much omogeneous are distributed the activities.
'''
def compute_my_variability(event_log):
    activity_counter = Counter()
    for trace in event_log:
        for event in trace:
            activity_counter[event['concept:name']] += 1
    total = sum(activity_counter.values())
    return -sum((count / total) * math.log2(count / total) for count in activity_counter.values())
# ----------- requested functions for the project ----------- 


def main():
    #the logs to analyze (name, path)
    logs = {
        "Concept Drift": "input_logs/concept_drift.xes",
        "Concept Drift Type 1": "input_logs/concept_drift_type1.xes",
        "Concept Drift Type 2": "input_logs/concept_drift_type2.xes",
        "BPIChallenge2011": "input_logs/BPIChallenge2011.xes",
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
        print("\n\n")

    #write results on file
    write_results_to_file(results)

if __name__ == "__main__":
    main()