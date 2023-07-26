from file_io import get_model_directory_path
import os
import pandas as pd

def load_nodes_edges(model_name, version, file_prefix):
    '''
    Load the nodes and edges from the files in the model directory
    model_name: The name of the model (model folder)
    version: The version of the model (version folder)
    file_prefix: The prefix of the files to load
    return: A tuple of the nodes and edges dataframes
    '''
    edge_path = os.path.join(get_model_directory_path(model_name, version), file_prefix + ".edges")
    print(edge_path)
    nodes_path = os.path.join(get_model_directory_path(model_name, version), file_prefix + ".nodes")
    print(nodes_path)

    nodes_df = pd.read_csv(nodes_path, sep='\t', header=None)
    if nodes_df.shape[1] == 4:
        nodes_df.columns = ['term', 'size', 'genes', 'stability']
    elif nodes_df.shape[1] == 5:
        nodes_df.columns = ['term', 'size', 'genes', 'stability', 'unique_genes']
    edges_df = pd.read_csv(edge_path, sep='\t', header=None, names=['parent', 'child', 'type'])

    return nodes_df, edges_df


def get_genes(node, node_table):
    """
    Function to retrieve the gene list for a given child from the node table.
    """
    child_row = node_table[node_table['term'] == node]
    genes = child_row['genes'].str.split().values[0]
    return genes