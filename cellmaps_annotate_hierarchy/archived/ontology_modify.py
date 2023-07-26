import pandas as pd 
from sklearn.cluster import KMeans

def find_children(parent, edges):
    children = edges[edges['parent'] == parent]['child'].tolist()
    return children

# Get all the descendant of the lineage
def get_descendants(lineage, edges):
    descendants = []
    children = edges.loc[edges['parent'] == lineage, 'child'].values
    descendants.extend(children)
    for child in children:
        descendants.extend(get_descendants(child, edges))
    return descendants

def parent_unique_genes(parent, children, nodes):
    parent_genes = set(nodes[nodes['term'] == parent]['genes'].str.split().values[0])
    children_genes = set()

    for child in children:
        child_genes = set(nodes[nodes['term'] == child]['genes'].str.split().values[0])
        children_genes |= child_genes

    unique_genes = parent_genes - children_genes
    return unique_genes

def count_children(parent, edges):
    return len(find_children(parent, edges))


# Function to generate step child node names
def generate_step_child(parent, num_clusters):
    return [f"{parent}_{i}" for i in range(1, num_clusters + 1)]

# Function to perform k-means clustering on unique genes
def perform_kmeans_clustering(unique_genes, embedding_file, average_genes_per_cluster=30, max_genes_per_cluster=50):
    emb = pd.read_csv(embedding_file, sep=',', index_col=0)
    gene_embedding = emb.loc[unique_genes].values
    num_genes= len(unique_genes)
    num_clusters = int(num_genes/average_genes_per_cluster) # I want average 30 genes per cluster

    # Perform k-means clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(gene_embedding)
    cluster_labels = kmeans.labels_
    # update the genes_per_cluster using the maximum number of genes in a cluster
    genes_per_cluster = max(pd.Series(cluster_labels).value_counts())

    # when the number of genes per cluster is greater than the max_genes_per_cluster, increase the number of clusters until the condition is met
    if genes_per_cluster > max_genes_per_cluster:
        print(f'There is a big cluster with genes more than {max_genes_per_cluster}, add one more cluster')
        num_clusters += 1
        kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(gene_embedding)
        cluster_labels = kmeans.labels_
        #update the genes_per_cluster using the maximum number of genes in a cluster
        genes_per_cluster = max(pd.Series(cluster_labels).value_counts())

    return cluster_labels, num_clusters