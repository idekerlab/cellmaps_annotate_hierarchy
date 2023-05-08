import os
import sys
import pandas as pd
import numpy as np
import csv





HGNCID_2_latestGeneSymbol_DF = pd.read_csv('lib/HGNCID_2_latestGeneSymbol_DF.txt', sep='\t')

geneSymbol_2_HGNCID_DF = pd.read_csv('lib/geneSymbol_2_HGNCID_DF.txt', sep='\t')

hgnc_raw_DF = pd.read_csv('lib/hgnc_idsymbolnamelocus_grouplocus_typestatus.txt', sep = '\t', dtype = {'hgnc_id': str, 'uniprot_ids': str, 'symbol':str})


hgnc_DF = hgnc_raw_DF[hgnc_raw_DF.symbol.isin(HGNCID_2_latestGeneSymbol_DF.geneSymbol)]

# force to be string, because it is not finding genes because Python is forcing it to be of type 'object' 
hgnc_DF['symbol'] =hgnc_DF.symbol.astype(str) 
hgnc_DF['uniprot_ids'] =hgnc_DF.uniprot_ids.astype(str) 
hgnc_DF['hgnc_id'] =hgnc_DF.hgnc_id.astype(str) 



HGNCID_2_latestGeneSymbol_Dict =  dict(zip(HGNCID_2_latestGeneSymbol_DF.HGNCID, HGNCID_2_latestGeneSymbol_DF.geneSymbol))

geneSymbol_2_HGNCID_Dict = dict(zip(geneSymbol_2_HGNCID_DF.geneSymbol, geneSymbol_2_HGNCID_DF.HGNCID))

latestGeneSymbol_2_uniprotID_Dict = dict(zip(hgnc_DF.symbol, hgnc_DF.uniprot_ids))                   

# ToDo: add paths as input to function 

def fixGeneSymbol(geneSymbol):
    if geneSymbol in HGNCID_2_latestGeneSymbol_Dict.values():
        return geneSymbol
    
    else:
    
        HGNCID = geneSymbol_2_HGNCID_Dict[geneSymbol]

        latestGeneSymbol = HGNCID_2_latestGeneSymbol_Dict[HGNCID]

        return latestGeneSymbol
        

                      
def latestGeneSymbol_2_uniprotID(latestGeneSymbol):
    uniprotID = None
    if latestGeneSymbol in latestGeneSymbol_2_uniprotID_Dict.keys():
        uniprotID = latestGeneSymbol_2_uniprotID_Dict[latestGeneSymbol]
        
    # ToDo: a couple have multiple uniprot IDs what to do with them?
    return uniprotID                 

# geneinfo_DF = pd.read_csv('lib/geneinfo.txt', sep='\t');
# geneinfo_ensemble_DF = geneinfo_DF[(~geneinfo_DF["ensembl_gene_id"].isnull())]
# EnsemblID_2_geneSymbol_Dict =  dict(zip(geneinfo_ensemble_DF.ensembl_gene_id, geneinfo_ensemble_DF.symbol))