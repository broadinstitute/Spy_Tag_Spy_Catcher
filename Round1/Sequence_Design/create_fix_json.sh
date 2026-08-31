parse_multiple_chains.py --input_path input --output_path input.jsonl
assign_fixed_chains.py --input_path input.jsonl --output_path input_assigned.jsonl --chain_list "A"
make_fixed_positions_dict.py --specify_non_fixed \
--position_list "10 59 60 67 68 94" --chain_list "A" \
--input_path input.jsonl --output_path input_fixed_pos.jsonl
