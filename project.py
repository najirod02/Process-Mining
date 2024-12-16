from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.variants import variants_filter
from collections import Counter
import math
import os
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
import time

# Import the Cython-optimized Levenshtein function
from cython_levenshtein import levenshtein

'''
TODO:
i check che vengono fatti sono corretti nel senso che vengono
prese le coppie non ripetute però con file grandi (BPIChallenge) 
il numero di coppie è spropositato ed è impossibile, seppur usando parallelizzazione
ed altre strategie, avre risultati in tempi accettabili.

siamo sicuri che bisogna usare levenshtein per la edit dstance?
dobbiamo veramente controllare tutto il BPIChallenge? Contattare la professoressa
'''

# Compute Edit Distance Chunk
def compute_edit_distance_chunk(chunk):
    print(f"start chunk")
    start = time.time()
    for trace1, trace2 in chunk:
        # Compute Levenshtein distance between the two trace strings
        yield levenshtein(str(trace1), str(trace2))
    finish = time.time()
    print(f"time for a chunk: {finish-start}")

# Generate unique trace pairs (without duplicates)
def get_unique_pairs(variants):
    all_pairs = []
    for i in range(len(variants)):
        for j in range(i + 1, len(variants)):  # Only consider j > i to avoid duplicates
            all_pairs.append((variants[i], variants[j]))
    return all_pairs


# Compute Edit Distance Variability
def compute_edit_distance_variability(event_log, max_threads=8):
    variants = list(variants_filter.get_variants(event_log).keys())
    if len(variants) < 2:
        return 0

    # Generate all unique trace pairs (no duplicates)
    all_pairs = get_unique_pairs(variants)

    # Divide work into chunks
    chunk_size = max(1, len(all_pairs) // max_threads)
    chunk_size = 50
    #TODO: with this configuration, 30 seconds per chunk for a total of 80h :-(
    chunks = [all_pairs[i:i + chunk_size] for i in range(0, len(all_pairs), chunk_size)]
    print(f"number of chunks {len(chunks)}")
    print(f"size of each chunk {chunk_size}")

    # Use ThreadPoolExecutor for parallel computation
    with ThreadPoolExecutor(max_threads) as executor:
        results = executor.map(compute_edit_distance_chunk, chunks)

    # Flatten results and calculate average
    all_distances = [distance for result in results for distance in result]
    return sum(all_distances) / len(all_distances)


# Compute Variant Variability
def compute_variant_variability(event_log):
    variants = variants_filter.get_variants(event_log)
    return len(variants)


# Compute Custom Variability (Entropy)
def compute_my_variability(event_log):
    activity_counter = Counter()
    for trace in event_log:
        for event in trace:
            activity_counter[event['concept:name']] += 1
    total = sum(activity_counter.values())
    entropy = -sum((count / total) * math.log2(count / total) for count in activity_counter.values())
    return entropy


# Write Results to File
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
            if log not in existing_logs:  # Only write new logs
                file.write(f"Results for {log}:\n")
                for metric, value in metrics.items():
                    file.write(f"  {metric}: {value}\n")
                file.write("\n")
                print(f"Results written for {log}")  # Print the log name

# Process a Single Log File
def process_log(log_name, log_path, max_threads=8):
    print(f"Processing log: {log_name}...")
    event_log = xes_importer.apply(log_path)

    # Compute metrics
    results = {
        "log_name": log_name,
        "Variants": compute_variant_variability(event_log),
        "Edit Distance": compute_edit_distance_variability(event_log, max_threads),
        "Custom Variability": compute_my_variability(event_log)
    }

    print(f"Finished processing log: {log_name}")

    return results


# Main Function
def main():
    logs = {
        "BPI Challenge 2011": "BPIChallenge2011.xes",
        #"Concept Drift": "concept_drift.xes",
        #"Concept Drift Type 1": "concept_drift_type1.xes",
        #"Concept Drift Type 2": "concept_drift_type2.xes"
    }

    # Use multiprocessing to process each log in parallel
    with Pool(processes=4) as pool:  # Adjust based on number of CPU cores
        log_results = pool.starmap(
            process_log, [(name, path, 8) for name, path in logs.items()]
        )

    # Consolidate results (though it is no longer needed to write to file all at once)
    results = {log["log_name"]: {k: v for k, v in log.items() if k != "log_name"} for log in log_results}

    # Print results to console
    print("\n")
    for log, metrics in results.items():
        print(f"Results for {log}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
        print("\n\n")

    # Write results to a file
    write_results_to_file(results)



if __name__ == "__main__":
    main()
