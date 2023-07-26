import sys
import pandas as pd
import igraph as ig

def read_edges(file_name):
    edges_df = pd.read_csv(file_name, sep='\t', header=None, names=['parentSystem', 'childSystem', 'relType'])
    return edges_df

def generate_graph(edges_df):
    graph = ig.Graph.TupleList(edges_df.itertuples(index=False), directed=True)
    return graph

def topological_sort(graph):
    if not graph.is_dag():
        graph = graph.simplify()
    sorted_nodes_indices = graph.topological_sorting(mode='in')
    sorted_nodes_names = [graph.vs[node_index]['name'] for node_index in sorted_nodes_indices]
    return sorted_nodes_names

def write_sorted_nodes(sorted_nodes, output_file):
    sorted_nodes_df = pd.DataFrame({'systemID': sorted_nodes})
    sorted_nodes_df.to_csv(output_file, sep='\t', index=False, header=False)

def main():
    if len(sys.argv) != 3:
        print("Usage: python topological_sort.py <input_edge_file> <output_file>")
        return

    input_edge_file = sys.argv[1]
    output_file = sys.argv[2]

    edges_df = read_edges(input_edge_file)
    graph = generate_graph(edges_df)
    sorted_nodes = topological_sort(graph)
    write_sorted_nodes(sorted_nodes, output_file)

if __name__ == '__main__':
    main()
