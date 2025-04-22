import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
import os
from tabulate import tabulate

def split_set_items(set_: set, seprator: str = ',') -> set:
    new_set = set()
    for item in set_:
        if seprator in item:
            new_set.update([i.strip() for i in item.split(seprator)])
        else:
            new_set.add(item)
    return new_set

def compute_df_intersections(dfs: list, by: str, lowercase: bool = False, separator:str=None) -> pd.DataFrame:
    """
    Compute intersections between all the dataframes in the `dfs` list based on the column specified by `by`.
    Optionally, lowercase the values in the `by` column before matching.

    Parameters:
        dfs (list): List of pandas DataFrames.
        by (str): The column to match on.
        lowercase (bool): Whether to lowercase the values before matching.
        separator (str): If the values in the column are separated by a character, specify it here.

    Returns:
        pd.DataFrame: A grid with integer values indicating the number of intersections.
    """
    # Optionally lowercase values in the specified column
    if lowercase:
        dfs = [df.assign(**{by: df[by].str.lower()}) for df in dfs]

    # Initialize the intersection matrix
    intersections = pd.DataFrame(index=range(len(dfs)), columns=range(len(dfs)), dtype=float).fillna(0)

    # Compute pairwise intersections
    for i, j in combinations(range(len(dfs)), 2):
        set_a = set(dfs[i][by].dropna())
        set_b = set(dfs[j][by].dropna())
        if separator:
            set_a = split_set_items(set_a, separator)
            set_b = split_set_items(set_b, separator) 
        intersect_count = len(set_a & set_b)
        intersections.iloc[i, j] = intersect_count
        intersections.iloc[j, i] = intersect_count
            
    # Add set size to diagonal
    for i in range(len(dfs)):
        intersections.iloc[i, i] = len(dfs[i][by].dropna()) 

    return intersections

def compute_csv_intersections(paths: list, by: str, lowercase: bool = False, separator:str=None) -> pd.DataFrame:
    """
    Load CSV files, compute intersections using compute_df_intersections().

    Parameters:
        paths (list): List of paths to CSV files.
        by (str): The column to match on.
        lowercase (bool): Whether to lowercase the values before matching.
        separator (str): If the values in the column are separated by a character, specify it here.

    Returns:
        pd.DataFrame: A grid with integer values indicating the number of intersections.
    """
    # Load CSV files into DataFrames
    dfs = [pd.read_csv(path) for path in paths]

    # Ensure the required columns are present
    for df, path in zip(dfs, paths):
        if by not in df.columns:
            raise ValueError(f"Column '{by}' not found in file: {path}")

    # Compute and return the intersection matrix
    return compute_df_intersections(dfs, by, lowercase, separator)



def jaccard_heatmap_intersection_matrix(intersection_matrix: pd.DataFrame, labels: list = None):
    """
    Draw a heatmap of the Jaccard Index for the given intersections matrix.

    Parameters:
        intersection_matrix (pd.DataFrame): DataFrame containing the intersections counts.
        labels (list): Optional list of human-readable labels for the DataFrames. If not provided,
                       the index of the matrix will be used.

    Returns:
        None: Displays a heatmap.
    """
    
    raise "not implemented"
    # Calculate the Jaccard Index matrix based on the intersection counts
    jaccard_indices = intersection_matrix.copy()
    num_dataframes = intersection_matrix.shape[0]

    for i in range(num_dataframes):
        for j in range(num_dataframes):
            if i != j:
                # Calculate the union for the Jaccard Index
                union_count = intersection_matrix.iloc[i].sum() + intersection_matrix.iloc[j].sum() - intersection_matrix.iloc[i, j]
                if union_count > 0:  # Avoid division by zero
                    jaccard_indices.iloc[i, j] = intersection_matrix.iloc[i, j] / union_count
                else:
                    jaccard_indices.iloc[i, j] = float('nan')  # No union
            
    # Set diagonal to NaN (self-intersections don't make sense)
    for idx in range(num_dataframes):
        jaccard_indices.iloc[idx, idx] = float('nan')

    # Determine labels
    if labels is None:
        labels = [f"DataFrame {i+1}" for i in range(num_dataframes)]

    if len(labels) != num_dataframes:
        raise ValueError("Number of labels must match the size of the intersection matrix.")

    # Plot the heatmap
    plt.figure(figsize=(10, 8))
    plt.imshow(jaccard_indices, cmap="viridis", interpolation="nearest")
    plt.colorbar(label="Jaccard Index")

    # Set tick labels
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.yticks(range(len(labels)), labels)

    # Add annotations with Jaccard Index values
    for i in range(jaccard_indices.shape[0]):
        for j in range(jaccard_indices.shape[1]):
            if not pd.isna(jaccard_indices.iloc[i, j]):  # Skip NaN (self-intersections)
                plt.text(j, i, f"{jaccard_indices.iloc[i, j]:.2f}", ha="center", va="center", color="white")

    # Add title and axis labels
    plt.title("Jaccard Index Heatmap")
    plt.xlabel("DataFrame")
    plt.ylabel("DataFrame")

    # Show the heatmap
    plt.tight_layout()
    plt.show()
    
    
    
def heatmap_inclusion_percentage(intersection_matrix: pd.DataFrame, labels: list = None, cmap="Blues", figsize=None):
    """
    Draw a heatmap of the inclusion percentage for the intersections matrix.

    Parameters:
        intersection_matrix (pd.DataFrame): DataFrame containing the intersections counts.
        labels (list): Optional list of human-readable labels for the DataFrames. If not provided,
                       the index of the matrix will be used.

    Returns:
        None: Displays a heatmap.
    """
    # Initialize the inclusion percentage matrix
    inclusion_percentages = pd.DataFrame(index=range(intersection_matrix.shape[0]), 
                                          columns=range(intersection_matrix.shape[0]), 
                                          dtype=float).fillna(0)

    num_dataframes = intersection_matrix.shape[0]

    # Compute inclusion percentages
    for i in range(num_dataframes):
        for j in range(num_dataframes):
            if i != j:
                set_size = intersection_matrix.iloc[i,i]
                if set_size > 0:  # Avoid division by zero
                    inclusion_percentages.iloc[i, j] = (intersection_matrix.iloc[i, j] / set_size) * 100

    # Set diagonal to NaN (self-intersections don't make sense)
    for idx in range(num_dataframes):
        inclusion_percentages.iloc[idx, idx] = float('nan')

    # Determine labels
    if labels is None:
        labels = [f"DataFrame {i+1}" for i in range(num_dataframes)]

    if len(labels) != num_dataframes:
        raise ValueError("Number of labels must match the size of the intersection matrix.")

    # Plot the heatmap
    plt.figure(figsize=figsize)
    plt.imshow(inclusion_percentages, cmap=cmap, interpolation="nearest")
    plt.colorbar(label="Inclusion Percentage (%)")

    # Set tick labels
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.yticks(range(len(labels)), labels)

    # Add annotations with inclusion percentage values
    for i in range(inclusion_percentages.shape[0]):
        for j in range(inclusion_percentages.shape[1]):
            if not pd.isna(inclusion_percentages.iloc[i, j]):  # Skip NaN (self-intersections)
                plt.text(j, i, f"{inclusion_percentages.iloc[i, j]:.1f}%", ha="center", va="center", color="white")

    # Add title and axis labels
    plt.title("Inclusion Percentage Heatmap")
    plt.ylabel("Source set")
    plt.xlabel("Target set")

    # Show the heatmap
    #plt.tight_layout()
    plt.show()



def set_comparison_table(sets: list[set], labels: list[str] = None):
    """
    Draws a table with columns containing the set items, ordered alphabetically,
    which are 1) in all sets (intersection of A, B, ...), 2) only in set A, 3) only in set B, etc.

    Args:
    sets (list[set]): A list of sets to compare.
    labels (list[str], optional): A list of labels for the sets. Defaults to None.

    Returns:
    str: A string representation of the table.
    """

    # Check if there are at least two sets
    if len(sets) < 2:
        raise ValueError("At least two sets are required for comparison.")

    # Get the intersection of all sets
    intersection = set.intersection(*sets)

    # Initialize lists to store the items in each category
    all_sets = list(intersection)
    all_sets.sort()
    only_in_sets = []

    # Iterate over each set
    for s in sets:
        # Get the items that are in the current set but not in the intersection
        items = list(s - intersection) 
        items.sort()
        only_in_sets.append(items)
        

    # Create a list of labels for the columns
    if labels is None:
        labels = [f"Only in set {i+1}" for i in range(len(sets))]
    
    labels.insert(0, "Intersection")

    # Create a table with the items in each category
    table = [['\n'.join(all_sets)] + ['\n'.join(items) for items in only_in_sets]]
    
    return tabulate(table, headers=labels, tablefmt="grid")