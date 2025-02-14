#!/usr/bin/env python3

import sys
import os
import udapi
from collections import Counter, defaultdict

# =============================================================================
# Helpers for processing morphological features
# =============================================================================
def parse_feats(feats):
    """
    Parse a morphological features string into a dictionary.
    
    Parameters:
        feats (str or None): A string like "Number=Sing|Person=3" or "_" or None.
        
    Returns:
        dict: Parsed key-value pairs. If feats is "_" or None, returns {}.
    """
    if feats is None or str(feats) == '_':
        return {}
    try:
        return dict(item.split('=') for item in str(feats).split('|'))
    except Exception:
        return {}

def process_feats(node_feats_raw, parent_feats_raw):
    """
    Merge node and parent feature dictionaries and return both the node's features
    and the merged features as strings.
    
    Parameters:
        node_feats_raw (str): Raw features of the node.
        parent_feats_raw (str): Raw features of the parent (can be None).
        
    Returns:
        tuple: (node_feats_str, merged_feats_str)
            - node_feats_str: string from node_feats (unsorted)
            - merged_feats_str: string from merged features (sorted alphabetically by key)
    """
    node_feats = parse_feats(node_feats_raw)
    parent_feats = parse_feats(parent_feats_raw) if parent_feats_raw else {}

    # In a merge, node features override parent features if keys overlap.
    merged_feats = {**parent_feats, **node_feats}
    merged_feats_sorted = dict(sorted(merged_feats.items()))
    
    node_feats_str = "|".join(f"{k}={v}" for k, v in node_feats.items())
    merged_feats_str = "|".join(f"{k}={v}" for k, v in merged_feats_sorted.items())
    
    return node_feats_str, merged_feats_str

# =============================================================================
# Helpers for traversing the tree structure
# =============================================================================
def get_all_descendants(node):
    """
    Recursively collect all descendant nodes of a given node.
    """
    descendants = []
    for child in node.children:
        descendants.append(child)
        descendants.extend(get_all_descendants(child))
    return descendants

def are_subtrees_functional(node, functional_upos=('ADP', 'AUX', 'CCONJ', 'DET', 'PUNCT')):
    """
    Determine whether all descendant nodes of a given node have a UPOS tag 
    that belongs to a set of functional categories.
    """
    descendants = get_all_descendants(node)
    return all(child.upos in functional_upos for child in descendants)

def collect_nodes_with_state_and_relationships(tree):
    """
    Collect nodes along with a computed 'state' (leaf or non-leaf),
    the parent node, and all descendant nodes.
    """
    nodes_info = []
    for node in tree.descendants:
        # If node has descendants and not all are functional, mark as non-leaf.
        state = 'non-leaf' if node.descendants and not are_subtrees_functional(node) else 'leaf'
        parent_node = node.parent  # May be None for root
        children_nodes = node.descendants
        nodes_info.append((node, state, parent_node, children_nodes))
    return nodes_info

# =============================================================================
# Functions to add empty nodes based on features
# =============================================================================
def add_abstract_nodes_for_dropped_pronouns(tree):
    """
    For nodes that contain 'psor' features, add an empty child node if certain
    conditions are met. Uses a mapping from specific features to a pronoun form.
    """
    form_mapping = {
        "Case=Gen|Number=Sing|Person=1|PronType=Prs": "benim",
        "Case=Gen|Number=Sing|Person=2|PronType=Prs": "senin",
        "Case=Gen|Number=Sing|Person=3|PronType=Prs": "onun",
        "Case=Gen|Number=Plur|Person=1|PronType=Prs": "bizim",
        "Case=Gen|Number=Plur|Person=2|PronType=Prs": "sizin",
        "Case=Gen|Number=Plur|Person=3|PronType=Prs": "onların"
    }
    
    for node in tree.descendants:
        # Extract features whose keys contain 'psor'
        psor_feats = {k: v for k, v in node.feats.items() if 'psor' in k}
        if not psor_feats:
            continue
        
        # Build the features string we want to add
        abs_feats_parts = [f"{k.replace('[psor]', '')}={v}" for k, v in psor_feats.items()]
        abs_feats_str = "Case=Gen|" + "|".join(abs_feats_parts) + "|PronType=Prs"
        
        # Conditions: 
        #   - no child with the same feats (abs_feats_str)
        #   - no child with 'nmod:poss' or 'nsubj' in deprel
        #   - no 'Reflex' in node.feats
        #   - node.upos != 'PROPN'
        children_feats_ok = all(str(child.feats) != abs_feats_str for child in node.children)
        children_deprel_ok = all(child.deprel != 'nmod:poss' and 'nsubj' not in child.deprel
                                 for child in node.children)
        if (children_feats_ok and children_deprel_ok 
            and ('Reflex' not in node.feats) 
            and (node.upos != 'PROPN')):
            form = form_mapping.get(abs_feats_str)
            if form:
                node.create_empty_child(form=form, upos='PRON', deprel='dep', misc=abs_feats_str)

def add_abstract_nodes_for_null_subjects(tree):
    """
    Add empty nodes for verbs/auxiliaries based on morphological features.
    """
    form_mapping = {
        "Case=Nom|Number=Sing|Person=1|PronType=Prs": "ben",
        "Case=Nom|Number=Sing|Person=2|PronType=Prs": "sen",
        "Case=Nom|Number=Sing|Person=3|PronType=Prs": "o",
        "Case=Nom|Number=Plur|Person=1|PronType=Prs": "biz",
        "Case=Nom|Number=Plur|Person=2|PronType=Prs": "siz",
        "Case=Nom|Number=Plur|Person=3|PronType=Prs": "onlar"
    }
    
    for node in list(tree.descendants):
        if node.upos == 'VERB':
            feats_dict = parse_feats(node.feats)
            if 'Number' in feats_dict and 'Person' in feats_dict and 'VerbForm' not in feats_dict:
                # If no child with deprel = 'nsubj'
                if not any(child.deprel == 'nsubj' for child in node.children):
                    np_feats = [f"{k}={v}" for k, v in node.feats.items() if k in ['Number', 'Person']]
                    abs_feats_str = "Case=Nom|" + "|".join(np_feats) + "|PronType=Prs"
                    form = form_mapping.get(abs_feats_str)
                    if form:
                        node.create_empty_child(form=form, upos='PRON', deprel='nsubj', misc=abs_feats_str)
        elif node.upos == 'AUX':
            np_feats = [item for item in node.feats.items() if item[0] in ['Number', 'Person']]
            # If both Number and Person exist
            if len(np_feats) > 1:
                parent = node.parent
                if parent:
                    parent_feats = parse_feats(parent.feats)
                    node_feats = parse_feats(node.feats)
                    condition = (
                        ('PronType' not in parent_feats) or
                        (
                            parent_feats.get('PronType') != 'Prs' and
                            (
                                node_feats.get('Number') != parent_feats.get('Number') or
                                node_feats.get('Person') != parent_feats.get('Person')
                            )
                        )
                    )
                    if condition:
                        has_nsubj_sibling = any(
                            sibling.deprel == 'nsubj' for sibling in parent.children if sibling != node
                        )
                        already_exists = any(
                            child.is_empty() and child.deprel == 'nsubj' for child in parent.children
                        )
                        if not has_nsubj_sibling and not already_exists:
                            np_feats_list = [f"{k}={v}" for k, v in node.feats.items() if k in ['Number', 'Person']]
                            abs_feats_str = "Case=Nom|" + "|".join(np_feats_list) + "|PronType=Prs"
                            form = form_mapping.get(abs_feats_str)
                            if form:
                                node.create_empty_child(form=form, upos='PRON', deprel='nsubj', misc=abs_feats_str)

# =============================================================================
# Extraction of combinations with counts
# =============================================================================
def extract_combinations_with_counts(nodes_info, columns, filters=None):
    """
    Extract unique combinations of specified columns from nodes_info,
    apply optional filters, and count their occurrences.
    
    Returns:
        Counter: Keys are tuples representing the combination, and values are counts.
    """
    combination_counts = Counter()

    def make_hashable(x):
        try:
            hash(x)
            return x
        except TypeError:
            return str(x)

    for node, state, parent, children in nodes_info:
        # Skip nodes with no features
        if str(node.feats) == '_':
            if filters and 'upos' in filters and node.upos in filters['upos']:
                node.misc['MS_feats'] = '_'
            else:
                node.misc['MS_feats'] = '|'
            continue

        # Use parent's merged features if available
        if parent:
            parent_feats_raw = parent.misc.get('MS_feats', None)
            if not parent_feats_raw or parent_feats_raw in ['_', '|']:
                parent_feats_raw = parent.feats
        else:
            parent_feats_raw = None

        # Merge feats
        node_feats_str, merged_feats_str = process_feats(node.feats, parent_feats_raw)

        # Check filters if provided
        passes = True
        for col, allowed_values in (filters or {}).items():
            if col == 'state':
                value = state
            elif col == 'parent' and parent:
                parent_feats_value = parent.misc.get('MS_feats', parent.feats)
                if parent_feats_value in ['_', '|']:
                    parent_feats_value = parent.feats
                value = f"{parent.upos}_{parent_feats_value}"
            elif col == 'children' and children:
                value = "_".join(f"{child.upos}_{child.feats}" for child in children)
            elif col == 'feats':
                value = node_feats_str
            else:
                value = getattr(node, col, None)
            if value not in allowed_values:
                if node.misc.get('MS_feats', ''):
                    _, merged_feats_str = process_feats(node.misc['MS_feats'], node.feats)
                    node.misc['MS_feats'] = merged_feats_str
                else:
                    node.misc['MS_feats'] = node_feats_str
                passes = False
                break
        if not passes:
            continue

        # Build combination tuple
        combination_list = []
        for col in columns:
            if col == 'state':
                combination_list.append(state)
            elif col == 'merged_feats':
                combination_list.append(merged_feats_str)
            elif col == 'parent' and parent:
                parent_feats_value = parent.misc.get('MS_feats', parent.feats)
                if parent_feats_value in ['_', '|']:
                    parent_feats_value = parent.feats
                combination_list.append(parent_feats_value)
            elif col == 'children' and children:
                combination_list.append("_".join(f"{child.upos}_{child.feats}" for child in children))
            elif col == 'feats':
                combination_list.append(node_feats_str)
            else:
                combination_list.append(getattr(node, col, None))
        combination = tuple(make_hashable(x) for x in combination_list)
        combination_counts[combination] += 1

        # Update misc fields
        node.misc['MS_feats'] = '_'
        if parent:
            parent.misc['MS_feats'] = merged_feats_str

    return combination_counts

# =============================================================================
# Grouping and printing helpers
# =============================================================================

def group_combinations(combination_counts, source_columns, target_columns, all_columns):
    """
    Group combination counts by source vs. target columns.
    """
    col_index = {col: idx for idx, col in enumerate(all_columns)}
    grouped = defaultdict(Counter)
    for combination, count in combination_counts.items():
        # Build composite keys for source and target
        source_key = tuple(combination[col_index[col]] for col in source_columns)
        target_key = tuple(combination[col_index[col]] for col in target_columns)
        # Filter out certain placeholders
        if source_key[1] != '_' and target_key and len(target_key[0]) > 0 and not target_key[0].endswith('_'):
            grouped[source_key][target_key] += count
    return grouped

def print_grouped_results(grouped_results, source_columns, target_columns, color_map, reset_color):
    """
    Print the grouped combination results using ANSI colors.
    """
    for source, targets in grouped_results.items():
        source_str = ", ".join(
            f"{color_map.get(col, '')}{col}: {val}{reset_color}" 
            for col, val in zip(source_columns, source)
        )
        print(f"Functional Child Node: {source_str}")
        for target, cnt in targets.most_common():
            target_str = ", ".join(
                f"{color_map.get(col, '')}{col}: {val}{reset_color}" 
                for col, val in zip(target_columns, target)
            )
            print(f"  -> Parent Content Node: {target_str}, count: {cnt}")

# =============================================================================
# Final File Post-processing
# =============================================================================

def final_post_processing(input_file_path, output_file_path):
    """
    Process the file line-by-line for final adjustments:
      - Insert '_' in the second-last column for lines with decimal or dash IDs.
      - Rearrange lines containing 'MS_feats=' as needed.
    """
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    processed_lines = []
    for line in lines:
        line = line.rstrip('\n')
        # Skip empty or comment lines as is
        if not line or line.startswith('#'):
            processed_lines.append(line)
            continue
        
        cols = line.split('\t')
        # If it's a multi-word token line or empty node line (e.g. "1-2" or "1.1")
        if ('.' in cols[0] or '-' in cols[0]) and len(cols) >= 8:
            # Insert '_' in the second-last position
            cols.insert(-1, '_')
            processed_lines.append('\t'.join(cols))
        elif 'MS_feats=' in line and len(cols) >= 8:
            # Attempt to isolate MS_feats= portion
            start_index = line.find('MS_feats=') + len('MS_feats=')
            if 'SpaceAfter=No' in line:
                end_index = line.find('SpaceAfter=No')
                substring = line[start_index:end_index].strip()
                # Rebuild line
                modified_line = (
                    line[:start_index - len('MS_feats=')] 
                    + line[end_index:] 
                    + '\t' 
                    + substring.rstrip('=').rstrip()
                )
                processed_lines.append(modified_line)
            else:
                substring = line[start_index:].strip()
                modified_line = (
                    line[:start_index - len('MS_feats=')]
                    + '_\t'
                    + substring
                )
                processed_lines.append(modified_line)
        else:
            processed_lines.append(line)

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for pline in processed_lines:
            output_file.write(pline + '\n')

# =============================================================================
# Main Document Processing
# =============================================================================

def process_document(input_file, output_file):
    """
    Load a UD document, collect node info, extract combinations,
    add empty nodes, and store the result to an intermediate file.
    """
    # Columns for combination extraction and grouping
    COLUMNS_TO_EXTRACT = ['upos', 'feats', 'parent', 'merged_feats'] 
    COLUMN_FILTERS = {'state': 'leaf', 'upos': ['ADP', 'AUX', 'CCONJ', 'DET', 'PUNCT']}
    SOURCE_COLUMNS = ['upos', 'feats']
    TARGET_COLUMNS = ['parent', 'merged_feats']

    # ANSI color codes for printing
    COLOR_MAP = {
        'upos': '\033[94m',         # Blue
        'feats': '\033[92m',        # Green
        'parent': '\033[93m',       # Yellow
        'merged_feats': '\033[95m', # Magenta
    }
    RESET_COLOR = '\033[0m'

    # Load the document using udapi
    document = udapi.Document(input_file)

    combination_counts = Counter()

    # Process each tree in the document
    for bundle in document.bundles:
        tree = bundle.get_tree()
        nodes_info = collect_nodes_with_state_and_relationships(tree)
        counts = extract_combinations_with_counts(nodes_info, COLUMNS_TO_EXTRACT, COLUMN_FILTERS)
        combination_counts.update(counts)

        # Add empty nodes for certain morphological features
        add_abstract_nodes_for_dropped_pronouns(tree)
        add_abstract_nodes_for_null_subjects(tree)

    # Print stats
    total_keys = len(combination_counts)
    keys_more_than_one = sum(1 for count in combination_counts.values() if count > 1)
    print(f"Processed: {input_file}")
    print(f"Total unique combination keys: {total_keys}")
    print(f"Combination keys with count > 1: {keys_more_than_one}")

    # Group and print results
    grouped_results = group_combinations(
        combination_counts, SOURCE_COLUMNS, TARGET_COLUMNS, COLUMNS_TO_EXTRACT
    )
    print_grouped_results(grouped_results, SOURCE_COLUMNS, TARGET_COLUMNS, COLOR_MAP, RESET_COLOR)

    # Store the updated document in an intermediate conllu file
    document.store_conllu(output_file)

def main():
    """
    Main entry point:
      - Expects one or more .conllu file paths as arguments.
      - Produces corresponding .msf files.
    """
    input_files = sys.argv[1:]
    if not input_files:
        print("Usage: python turkish_msf_generator.py <file1.conllu> <file2.conllu> ...")
        sys.exit(1)

    for in_file in input_files:
        if not in_file.endswith('.conllu'):
            print(f"Skipping '{in_file}' (not a .conllu file).")
            continue
        
        # Construct output .msf file name
        out_file_temp = in_file.replace('.conllu', '.temp.conllu')
        out_file_msf = in_file.replace('.conllu', '.msf')

        # First: parse, transform, and store to an intermediate file
        process_document(in_file, out_file_temp)

        # Then: final post-processing to produce the .msf file
        final_post_processing(out_file_temp, out_file_msf)

        # Optional: remove the temp file
        if os.path.exists(out_file_temp):
            os.remove(out_file_temp)

if __name__ == "__main__":
    main()
