import os
import glob
import csv
import gc
import torch
import statistics
import re
from tqdm import tqdm
from ESM3dG import ESM3dG, ESM3dG_predict

# --- Configuration ---
PDB_DIR = "design_fold"
OUTPUT_CSV = "ensemble_fold_stability.csv"
CHAIN = "A"  # Adjust if your designs use a different chain identifier

WEIGHTS = [
    "/data/mshekhar/Soft/ESM3dg_weights/ESM3dG_weights_augmented_1_lora.ckpt",
    "/data/mshekhar/Soft/ESM3dg_weights/ESM3dG_weights_augmented_2_lora.ckpt",
    "/data/mshekhar/Soft/ESM3dg_weights/ESM3dG_weights_augmented_3_lora.ckpt",
]

# --- Setup ---
def natural_sort_key(filepath):
    """Extracts numbers from the filename to ensure sample_2 comes before sample_10."""
    basename = os.path.basename(filepath)
    # Find all contiguous digits in the filename and convert to integers
    numbers = [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', basename)]
    return numbers

# Find all files, sort them naturally, and LIMIT to the first 100
all_pdb_files = glob.glob(os.path.join(PDB_DIR, "sample_*.pdb"))
pdb_files = sorted(all_pdb_files, key=natural_sort_key)

print(f"Test run: Found {len(all_pdb_files)} files. Processing the first {len(pdb_files)} sorted files.")

# Dictionary to store predictions
results = {os.path.basename(f).replace('.pdb', ''): [None] * len(WEIGHTS) for f in pdb_files}
failed_samples = []

# --- Processing ---
for i, weight_path in enumerate(WEIGHTS):
    print(f"\n--- Loading Model {i+1} of {len(WEIGHTS)} ---")
    model = ESM3dG(weight_path)
    
    for pdb_file in tqdm(pdb_files, desc=f"Predicting with Model {i+1}"):
        sample_id = os.path.basename(pdb_file).replace('.pdb', '')
        
        try:
            prediction = ESM3dG_predict(model, pdb_file, CHAIN)[1][0]
            results[sample_id][i] = prediction
        except Exception as e:
            if sample_id not in failed_samples:
                failed_samples.append(sample_id)
                tqdm.write(f"Error processing {sample_id} with Model {i+1}: {e}")
    
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# --- Aggregation & Saving ---
print(f"\n--- Calculating Ensembles and Saving to {OUTPUT_CSV} ---")

with open(OUTPUT_CSV, mode="w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["sample_id", "model_1", "model_2", "model_3", "mean", "std"])
    
    # Iterate over the sorted list to guarantee the CSV rows are ordered correctly
    for pdb_file in pdb_files:
        sample_id = os.path.basename(pdb_file).replace('.pdb', '')
        preds = results[sample_id]
        
        if None not in preds:
            mean_val = statistics.mean(preds)
            std_val = statistics.stdev(preds)
            
            writer.writerow([
                sample_id, 
                round(preds[0], 4), 
                round(preds[1], 4), 
                round(preds[2], 4), 
                round(mean_val, 4), 
                round(std_val, 4)
            ])
        else:
            row = [sample_id]
            for p in preds:
                row.append(round(p, 4) if p is not None else "NA")
            row.extend(["NA", "NA"])
            writer.writerow(row)

if failed_samples:
    print(f"\nWarning: {len(failed_samples)} samples had partial or full failures and were marked with 'NA'.")
else:
    print("\nSuccess! All test samples processed and saved in sorted order.")
