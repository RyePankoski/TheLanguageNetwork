import random


def handle_color_gene(new_gene_vector, bias_flags):
    new_gene_vector = new_gene_vector
    bias_flags = bias_flags

    # Take the first 9 genes and split them into 3 chunks for RGB
    r_gene = sum(new_gene_vector[0:3])
    g_gene = sum(new_gene_vector[3:6])
    b_gene = sum(new_gene_vector[6:9])

    # Normalize each component to 0-255
    # Assuming gene values range from -100 to 100
    def normalize(value):
        return int(max(0, min(255, ((value + 1000) * 255) / 2000)))

    r = normalize(r_gene)
    g = normalize(g_gene)
    b = normalize(b_gene)

    return r, g, b


def compute_family_marker(gene_vector, group_size=2):
    marker = ""
    # Define valid characters (could be customized)
    valid_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&"
    num_chars = len(valid_chars)

    for i in range(0, 10, group_size):
        group = gene_vector[i:i + group_size]
        avg = sum(group) / len(group)

        # Adjust normalization for larger character set
        normalized = (avg + 1000) * ((num_chars - 1) / 2000)  # Map to 0 to (num_chars-1)
        bucket = int(normalized)
        bucket = max(0, min(num_chars - 1, bucket))

        char = valid_chars[bucket]
        marker += char

    return marker


def handle_complex_gene(parent, threshold=100):
    new_gene_vector = parent.gene_vector.copy()
    gene_flags = parent.bias_flags.copy()

    # Get parent's family_anchor or default to gene_vector
    anchor_vector = parent.family_anchor if hasattr(parent, 'family_anchor') else parent.gene_vector

    # Handle case when parent.family is 0 (initial/default value)
    if parent.family == 0:
        return new_gene_vector, gene_flags, compute_family_marker(new_gene_vector), new_gene_vector.copy()

    new_family_marker = list(parent.family)  # Now safe to convert to list
    new_family_anchor = anchor_vector.copy()

    # Process each gene
    for i in range(len(new_gene_vector)):
        if gene_flags[i]:
            new_gene_vector[i] += 10
        else:
            new_gene_vector[i] -= 10

        max_mutation = 1000
        new_gene_vector[i] = max(-max_mutation, min(max_mutation, new_gene_vector[i] + random.randint(-20, 20)))
        gene_flags[i] = new_gene_vector[i] > 0

    # Check each pair against threshold
    valid_chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&"
    num_chars = len(valid_chars)

    for i in range(0, 10, 2):
        # Calculate drift for this pair
        pair_drift = abs(sum(new_gene_vector[i:i + 2]) - sum(anchor_vector[i:i + 2]))

        if pair_drift > threshold:
            # Update this pair's letter
            pair_avg = sum(new_gene_vector[i:i + 2]) / 2
            normalized = (pair_avg + 1000) * ((num_chars - 1) / 2000)
            bucket = int(max(0, min(num_chars - 1, normalized)))
            new_family_marker[i // 2] = valid_chars[bucket]
            # Update anchor for this pair
            new_family_anchor[i:i + 2] = new_gene_vector[i:i + 2]

    return new_gene_vector, gene_flags, ''.join(new_family_marker), new_family_anchor


def is_upstream(current_node, target_node):
    # Compare how far each node is from zero vector
    current_magnitude = sum(abs(x) for x in current_node.gene_vector)
    target_magnitude = sum(abs(x) for x in target_node.gene_vector)

    return target_magnitude < current_magnitude


def compute_likelihood(current_node, target_node):
    vector_difference = 0
    correct_drift_p = 0
    family_differences = 5

    current_vector = current_node.gene_vector
    current_biases = current_node.bias_flags
    current_family = current_node.family
    target_vector = target_node.gene_vector
    target_family = target_node.family
    downstream = False

    stream_value = abs(sum(current_vector)) - abs(sum(target_vector))
    downstream = stream_value >= 0

    if downstream:
        for i in range(len(current_vector)):
            if (current_biases[i] and current_vector[i] > target_vector[i]) or \
                    (not current_biases[i] and current_vector[i] < target_vector[i]):
                correct_drift_p += 1
            else:
                correct_drift_p -= 1
            vector_difference += abs(current_vector[i] - target_vector[i])
    else:
        for i in range(len(current_vector)):
            if (current_biases[i] and current_vector[i] < target_vector[i]) or \
                    (not current_biases[i] and current_vector[i] > target_vector[i]):
                correct_drift_p += 1
            else:
                correct_drift_p -= 1
            vector_difference += abs(current_vector[i] - target_vector[i])

        for i in range(len(current_family)):
            if current_family[i] == target_family[i]:
                family_differences -= 1

    return family_differences, correct_drift_p, vector_difference, downstream
