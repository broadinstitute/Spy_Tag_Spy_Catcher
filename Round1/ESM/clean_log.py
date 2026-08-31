import re
import csv

def parse_log_metrics(log_filename, output_csv):
    # Regex patterns for the three specific targets
    # sample_(\d+) captures the digits after 'sample_'
    # pLDDT ([\d.]+) captures the decimal after 'pLDDT'
    # pTM ([\d.]+) captures the decimal after 'pTM'
    sample_pattern = re.compile(r"sample_(\d+)")
    plddt_pattern = re.compile(r"pLDDT ([\d.]+)")
    ptm_pattern = re.compile(r"pTM ([\d.]+)")

    data_rows = []

    try:
        with open(log_filename, 'r') as f:
            for line in f:
                # We only care about the "Predicted structure" lines
                if "Predicted structure" in line:
                    sample_match = sample_pattern.search(line)
                    plddt_match = plddt_pattern.search(line)
                    ptm_match = ptm_pattern.search(line)

                    # Only add to list if we found the core metrics
                    if sample_match and plddt_match and ptm_match:
                        data_rows.append({
                            'sample_id': f"sample_{sample_match.group(1)}",
                            'pLDDT': plddt_match.group(1),
                            'pTM': ptm_match.group(1)
                        })

        # Save to CSV
        with open(output_csv, 'w', newline='') as csvfile:
            fieldnames = ['sample_id', 'pLDDT', 'pTM']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(data_rows)

        print(f"Successfully extracted {len(data_rows)} records to {output_csv}")

    except FileNotFoundError:
        print(f"Error: Could not find the file '{log_filename}'")

# Usage
parse_log_metrics('esm_result.log', 'structure_metrics.csv')
