import re

def process_protein_data(input_filename, fasta_output, scores_output):
    # Regex for key-value pairs (e.g., sample=1 or score=0.78)
    # This looks for 'key=' followed by numbers or decimals
    patterns = {
        'sample': re.compile(r"sample=([\d]+)"),
        'score': re.compile(r"score=([\d.]+)"),
        'global_score': re.compile(r"global_score=([\d.]+)"),
        'seq_recovery': re.compile(r"seq_recovery=([\d.]+)")
    }

    try:
        with open(input_filename, 'r') as f_in, \
             open(fasta_output, 'w') as f_fasta, \
             open(scores_output, 'w') as f_scores:
            
            f_scores.write("sample_id\tscore\tglobal_score\tseq_recovery\n")
            
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith(">"):
                    # Extract values safely
                    results = {}
                    for key, regex in patterns.items():
                        match = regex.search(line)
                        results[key] = match.group(1) if match else "N/A"
                    
                    # Use sample ID if found, otherwise use the whole header
                    s_id = results['sample']
                    header_name = f"sample_{s_id}" if s_id != "N/A" else line[1:].split(',')[0]
                    
                    f_fasta.write(f">{header_name}\n")
                    f_scores.write(f"{s_id}\t{results['score']}\t{results['global_score']}\t{results['seq_recovery']}\n")
                else:
                    f_fasta.write(f"{line}\n")
                    
        print(f"Done! Cleaned sequences in: {fasta_output}")
        print(f"Metadata extracted to: {scores_output}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the script
process_protein_data('SDC_155746_trunc.fa', 'SDC_155746_clean.fa', 'scores_metadata.txt')
