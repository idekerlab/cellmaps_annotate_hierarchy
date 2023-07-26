
#### Notes
# using R's igraph rather than Python's networkx because it insists that the graph is cyclical when it is not!!! 
# Also networkx does not have a function to remove cycles
# Also, rpy2 is not available for python 3.11. No need to downgrade 
#


# print("starting topological sort")
## Read in arguments
args <- commandArgs(trailingOnly = TRUE)
# print(args)

modelPath = args[[1]]
  #'/Users/salkhairy/Desktop/projects/model_annotation/nesa/Krogan_230424/


edgesFile = args[[2]]
# hidef_50_0.75_5_leiden.edges'

## Load Libraries
library(plyr, quietly = TRUE)
library(tidyverse, quietly = TRUE)
library(igraph, quietly = TRUE)

## Read in .edges file
edgesFile_DF = read_delim(file = paste0(modelPath, "/", edgesFile),
                          delim = "\t", col_names = FALSE)
colnames(edgesFile_DF) = c("parentSystem", "childSystem", "relType")


## Generate graph from .edges file
edgesFile_graph = graph_from_data_frame(edgesFile_DF, directed = TRUE)
# If directed graph has cycles -> remove
if (!igraph::is_dag(edgesFile_graph)){
  # simplify -- removes cycles
  edgesFile_graph = simplify(edgesFile_graph)
}

## Generate topological sorting
edgesFile_topoSortList = topo_sort(edgesFile_graph, mode = "in")$name


## Write to file
write_delim(x = data_frame(systemID = edgesFile_topoSortList), 
            file = paste0(modelPath, "/topologicalSort_DF.txt"), 
            delim = "\t", col_names = FALSE)

