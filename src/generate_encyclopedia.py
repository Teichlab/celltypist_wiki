#!/usr/bin/env python
import os
import sqlite3
import pandas as pd
import numpy as np
from celltypist import models

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))

COUNTS_THRESHOLD = 10
NUMBER_OF_CELLS = 91
IMMUNE_META_SHAPE = 738647
SELECTED_MODEL = "Immune_All_Low.pkl"
IMMUNE_META_CSV = f"{ROOT_PATH}/tables/celltypist_immune_meta.csv"
BASIC_CELLTYPE_XLSX = f"{ROOT_PATH}/tables/Basic_celltype_information.xlsx"
FINAL_ENCYCLOPEDIA_XLSX = f"{ROOT_PATH}/encyclopedia/encyclopedia_table.xlsx"

def generate_encyclopedia_data() -> pd.DataFrame:
    """
    Integrate data into a single encyclopedia DataFrame and write outputs (excel and sqlite)
    """

    #Tissue & Dataset
    print(f"[+] Reading immune and meta data from {IMMUNE_META_CSV}")
    TD = pd.read_csv(IMMUNE_META_CSV)
    assert TD.shape[0] == IMMUNE_META_SHAPE

    #filter
    print(f"[+] Fitlering data (keep counts >= {COUNTS_THRESHOLD})")
    combine = TD.re_harmonise_annotation + TD.Tissue + TD.Dataset
    counts = combine.value_counts()
    keep = counts.index[counts >= COUNTS_THRESHOLD]
    TD = TD[np.isin(combine, keep)]


    #main
    print("[+] Building celltypes dataframe with tissues and datasets joined")
    celltypes = np.unique(TD.re_harmonise_annotation)
    assert len(celltypes) ==  NUMBER_OF_CELLS, "Wrong numnber of cell types in meta file"
    tissues  = [', '.join(list(np.unique(TD.loc[TD.re_harmonise_annotation == celltype, 'Tissue']))) for celltype in celltypes]
    datasets = [', '.join(list(np.unique(TD.loc[TD.re_harmonise_annotation == celltype, 'Dataset']))) for celltype in celltypes]
    df_TD = pd.DataFrame(dict(Tissues = tissues, Datasets = datasets), index = celltypes)


    #Top 10 markers
    print(f"[+] Retrieving model info from celltypist")    
    model = models.Model.load(SELECTED_MODEL)
    features = model.features
    celltypes = model.cell_types
    coef = model.classifier.coef_
    print("[+] Running quick sanity check")
    assert len(celltypes) == NUMBER_OF_CELLS, "Wrong numnber of cell types in model. Make sure the {SELECTED_MODEL} is the right model/version"
    assert len(features) == coef.shape[1], "Model features info doesn't match Classifier features"
    assert len(celltypes) == coef.shape[0], "Model celltypes info doesn't match Classifier celltypes"
    
    #main
    gene_index = np.argsort(-coef, axis = 1)[:, :10]
    gene_index = features[gene_index]
    gene_index = [", ".join(list(x)) for x in gene_index]
    df_T10 = pd.DataFrame(gene_index, index = celltypes, columns = ['Top 10 important genes from the Celltypist model'])

    #Basic
    print(f"[+] Reading basic celltype information from {BASIC_CELLTYPE_XLSX}")
    df_Basic = pd.read_excel(BASIC_CELLTYPE_XLSX)
    df_Basic.set_index('Low-hierarchy cell types', inplace=True, drop = False)

    #Order
    print("[+] Group tissues, datasets and top 10 markers by low-hierarchy cell types")
    df_TD = df_TD.loc[df_Basic['Low-hierarchy cell types']]
    df_T10 = df_T10.loc[df_Basic['Low-hierarchy cell types']]

    #Combine
    print("[+] Integrating data into a single data frame")
    integrated_df = df_Basic[
            ['High-hierarchy cell types','Low-hierarchy cell types','Description','Cell Ontology ID']
        ].join(
            df_TD[['Tissues', 'Datasets']]
        ).join(
            df_Basic[['Curated markers']]
        ).join(
            df_T10[['Top 10 important genes from the Celltypist model']]
        )
    
    write_excel(integrated_df)
    write_database(integrated_df, tissues=TD.Tissue.unique(), datasets=TD.Dataset.unique())


def write_excel(df: pd.DataFrame):
    """
    Write encyclopedia excel file
    """
    print(f"[+] Writing excel file to {FINAL_ENCYCLOPEDIA_XLSX}")
    with pd.ExcelWriter(FINAL_ENCYCLOPEDIA_XLSX) as writer:
        df.to_excel(writer, sheet_name = "Main", index = False)


def write_database(df: pd.DataFrame, tissues: list, datasets: list):
    """
    Write encyclopedia SQLite database
    """

    images_file = f'{ROOT_PATH}/images/celltype_to_image.csv'
    print(f"[+] Reading image mapping from {images_file}")
    images = pd.read_csv(images_file, index_col=0, header=None)
    images.columns=["image"]

    extra_dataset_info_file = f'{ROOT_PATH}/tables/dataset_to_PMID.csv'
    print(f"[+] Reading extra info for datasets from {extra_dataset_info_file}")
    datasets_extra = pd.read_csv(extra_dataset_info_file, index_col=0, header=None)
    datasets_extra.columns=["PMID"]

    output_file = f'{ROOT_PATH}/encyclopedia/encyclopedia.db'
    print(f"[+] Writing database to {output_file}")

    # Connect to the Encyclopedia database.
    with sqlite3.connect(output_file, isolation_level=None) as db:
        cursor = db.cursor()

        # create table schema
        print("[+] Creating database schema")
        cursor.executescript(create_tables)

        # insert tissues
        print("[+] Populating 'tissues' table")
        for tissue in tissues:
            cursor.execute(tissue_insert, [tissue])
        tissues = pd.read_sql_query('SELECT id_tissue, name FROM tissues', db, index_col='id_tissue')

        # insert datasets
        print("[+] Populating 'datasets' table")
        for dataset in datasets:
            pubmed_id = datasets_extra.loc[dataset]["PMID"]
            url = ""
            if not pubmed_id.isnumeric():
                url = pubmed_id
                pubmed_id = ""

            cursor.execute(datasets_insert, [dataset, pubmed_id, url])
        datasets = pd.read_sql_query('SELECT id_dataset, name FROM datasets', db, index_col='id_dataset')

        # insert hight celltypes
        print("[+] Populating high/low cell type tables and linking tissues and datasets")
        for hhct in df['High-hierarchy cell types'].unique():
            hhct = hhct.strip()
            cursor.execute(high_herarchy_insert, [hhct])
            id_high = cursor.lastrowid
            
            # insert low celltypes
            for _, row in df[df['High-hierarchy cell types'] == hhct].iterrows():
                low = row['Low-hierarchy cell types']
                image = images.loc[low].image
                cursor.execute(low_herarchy_insert, [
                               id_high, low, 
                               row['Description'], row['Cell Ontology ID'], 
                               image ])
                id_low = cursor.lastrowid

                # insert curated mareks
                if not pd.isnull(row['Curated markers']):
                    for curated_marker in row['Curated markers'].split(','):
                        cursor.execute(curated_marker_insert, [
                                       id_low, curated_marker.strip()])
                else:
                    print(f"[x] Missing curated markers for {low}")

                # insert top 10 take the last column as the top 10 genes
                if not pd.isnull(row[-1]):
                    for top_10 in row[-1].split(','):
                        cursor.execute(top_10_insert, [id_low, top_10.strip()])
                else:
                    print(f"[x] Missing top markers for {low}")

                # insert celltype <-> tissue relation
                if not pd.isnull(row['Tissues']):
                    for t in row['Tissues'].split(','):
                        tissue = tissues[tissues['name'] == t.strip()]
                        id_tissue = int(tissue.index[0])

                        cursor.execute(cell_type_tissues_insert,
                                       [id_tissue, id_low])
                else:
                    print(f"[x] Missing tissue for {low}")

                # insert celltype <-> dataset relation
                if not pd.isnull(row['Datasets']):
                    for d in row['Datasets'].split(','):
                        dataset = datasets[datasets['name'] == d.strip()]
                        id_dataset = int(dataset.index[0])
                        cursor.execute(cell_type_datasets_insert, [
                                       id_dataset, id_low])
                else:
                    print(f"[x] Missing dataset for {low}")

        cursor.close()


## database related queries and structures
create_tables = """
    DROP TABLE IF EXISTS high_herarchy_cell_types; 
    CREATE TABLE high_herarchy_cell_types (
        id_high INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );
    ---
    DROP TABLE IF EXISTS low_herarchy_cell_types;
    CREATE TABLE low_herarchy_cell_types (
        id_low  INTEGER PRIMARY KEY AUTOINCREMENT,
        id_high INT,
        name TEXT,
        description TEXT,
        ontology TEXT,
        image TEXT
    );
    ---
    DROP TABLE IF EXISTS datasets;
    CREATE TABLE datasets (
        id_dataset INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        pubmed_id TEXT,
        url TEXT
    );
    ---
    DROP TABLE IF EXISTS cell_type_datasets;
    CREATE TABLE cell_type_datasets (
        id_low INTEGER,
        id_dataset INTEGER
    );
    ---
    DROP TABLE IF EXISTS tissues;
    CREATE TABLE tissues (
        id_tissue INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT);
    ---
    DROP TABLE IF EXISTS cell_type_tissues;
    CREATE TABLE cell_type_tissues (
        id_low INTEGER,
        id_tissue INTEGER
    );
    ---
    DROP TABLE IF EXISTS curated_markers;
    CREATE TABLE curated_markers (
        id_marker INTEGER PRIMARY KEY AUTOINCREMENT,
        id_low INTEGER,
        name TEXT
    );
    ---
    DROP TABLE IF EXISTS top_10;
    CREATE TABLE top_10 (
        id_low INTEGER,
        name TEXT
    );
    ---
    DROP TABLE IF EXISTS database_info;
    CREATE TABLE database_info (
        version  TEXT,
        date TEXT
    );
    """

high_herarchy_insert = """INSERT INTO high_herarchy_cell_types (name) VALUES (?);"""
low_herarchy_insert = """INSERT INTO low_herarchy_cell_types (id_high, name, description, ontology, image) VALUES (?,?,?,?,?);"""
tissue_insert = """INSERT INTO tissues (name) VALUES (?);"""
datasets_insert = """INSERT INTO datasets (name, pubmed_id, url) VALUES (?,?,?);"""
curated_marker_insert = """INSERT INTO curated_markers (id_low, name) VALUES (?, ?);"""
top_10_insert = """INSERT INTO top_10 (id_low, name) VALUES (?, ?);"""
cell_type_datasets_insert = """INSERT INTO cell_type_datasets (id_dataset, id_low) VALUES (?, ?);"""
cell_type_tissues_insert = """INSERT INTO cell_type_tissues (id_tissue, id_low) VALUES (?, ?);"""


if __name__ == '__main__':
    generate_encyclopedia_data()
