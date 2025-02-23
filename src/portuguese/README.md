Steps:

1) preprocess_input_poss.py --> det with feature "Poss=Yes" are converted to nmod:poss
2) portuguese.py --> script that handles most of the changes
3) process_comp_pt.py --> script dealing with comparative/superlative, manual input required for ambiguous cases
4) postprocess_output_poss.py --> nmod:poss converted back to det to keep the alignment with the PT annotations in Porttinari corpus
