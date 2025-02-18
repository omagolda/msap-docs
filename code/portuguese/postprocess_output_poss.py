import re

# Input and output file names
input_file = "./input/pt_porttinari-ud-train-morph-comp.conllu"
output_file = "./output_files/pt_porttinari-ud-train_morph.conllu"

# Open input and output files
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        # Process only token lines (not metadata lines like # sent_id or # text)
        if re.match(r"^\d+\t", line):
            fields = line.strip().split("\t")
            if len(fields) > 5:
                feats = fields[5]  # Features column
                deprel = fields[7]  # Dependency relation column
                
                # Check if the token has possessive features and 'nmod:poss' relation
                if "Poss=Yes" in feats and "PronType=Prs" in feats and deprel == "nmod:poss":
                    fields[7] = "det"  # Change deprel back to 'det'

            # Write the modified line
            outfile.write("\t".join(fields) + "\n")
        else:
            # Write metadata and empty lines unchanged
            outfile.write(line)
            
print(f"Final updated file saved as: {output_file}")
