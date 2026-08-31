protein_mpnn_run.py --jsonl_path input.jsonl \
--chain_id_jsonl input_assigned.jsonl --fixed_positions_jsonl input_fixed_pos.jsonl \
--out_folder designs --num_seq_per_target 10000 --sampling_temp "0.1" \
--seed 0 --batch_size 1 --save_score 1 --save_probs 1
