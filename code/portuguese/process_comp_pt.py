import re

def process_conllu(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    updated_lines = []
    sentence = []
    
    for line in lines:
        if line.startswith("#") or line.strip() == "":
            # Process the sentence before adding new lines
            if sentence:
                updated_sentence = process_sentence(sentence)
                updated_lines.extend(updated_sentence)
                sentence = []
            updated_lines.append(line)
        else:
            sentence.append(line)
    
    if sentence:
        updated_sentence = process_sentence(sentence)
        updated_lines.extend(updated_sentence)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

def process_sentence(sentence):
    tokens = [line.split("\t") for line in sentence]
    adj_indices = [i for i, t in enumerate(tokens) if t[3] == "ADJ" or t[3] == "ADV"]
    
    for adj_index in adj_indices:
        adj_token = tokens[adj_index]
        head_index = int(adj_token[6]) - 1
        
        head_token = tokens[head_index]
        deprel = adj_token[7]
        
        dependents = [t for t in tokens if t[6] == adj_token[0]]
        has_comp_marker = any(t[2] in {"mais", "menos"} for t in dependents)
        
        if has_comp_marker:
            head_dependents = [t for t in tokens if t[6] == head_token[0]]
            if head_dependents:
                if deprel == "amod":
                    if any(t[2] == "o" for t in head_dependents):
                        adj_token[-1] = adj_token[-1].strip() + "|Degree=Sup\n"
                    elif any(t[2] == "um" for t in head_dependents):
                        adj_token[-1] = adj_token[-1].strip() + "|Degree=Cmp\n"
                else:
                    preceding_token = tokens[adj_index - 1] if adj_index > 0 else None
                    if preceding_token and preceding_token[2] == "o":
                        adj_token[-1] = adj_token[-1].strip() + "|Degree=Sup\n"
                    else:
                        adj_token[-1] = adj_token[-1].strip() + "|Degree=Cmp\n"
            else:
                adj_token[-1] = adj_token[-1].strip() + "|Degree=Cmp\n"

        if adj_token[2] in ["maior", "menor", "melhor", "pior"]:
            preceding_token = tokens[adj_index - 1] if adj_index > 0 else None
            if preceding_token:
                # Check if preceding token has a definite article
                if "Definite=Def" in preceding_token[5]:
                    adj_token[-1] = adj_token[-1].strip() + "|Degree=Sup\n"
                elif "Definite=Ind" in preceding_token[5]:
                    adj_token[-1] = adj_token[-1].strip() + "|Degree=Cmp\n"
                elif preceding_token[3] == "ADP":
                    # If preceding token is ADP, prompt the user for input
                    print("Sentence:", " ".join([t[1] for t in tokens]))  # Print the sentence
                    degree_choice = input("Choose Degree (Sup/Cmp): ").strip()
                    if degree_choice.lower() == "sup":
                        adj_token[-1] = adj_token[-1].strip() + "|Degree=Sup\n"
                    elif degree_choice.lower() == "cmp":
                        adj_token[-1] = adj_token[-1].strip() + "|Degree=Cmp\n"
                    else:
                        print("Invalid input. No change made.")
                else:
                    # Default handling if no specific conditions match
                    adj_token[-1] = adj_token[-1].strip() + "|Degree=Cmp\n"

    return ["\t".join(t) for t in tokens]

# Example usage
input_file = "./input/pt_porttinari-ud-dev-morph.conllu"
output_file = "./input/pt_porttinari-ud-dev-morph-comp.conllu"
process_conllu(input_file, output_file)
