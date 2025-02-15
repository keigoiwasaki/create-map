import pandas as pd 
import folium
import branca.colormap as cm
import numpy as np 
import geopandas as gpd
from tqdm import tqdm
tqdm.pandas()
from shapely.geometry import LineString, Point
import pickle
import osmnx as ox
import networkx as nx



def load_osmid_csv(file_path: str) -> pd.DataFrame:
    """
    指定されたCSVファイルを読み込み、'osmid'列を整数型に変換する関数。

    Parameters:
        file_path (str): CSVファイルのパス

    Returns:
        pd.DataFrame: 読み込まれたデータフレーム
    """
    df = pd.read_csv(file_path)
    df['osmid'] = df['osmid'].astype(int)
    return df



def load_drive_osmnx_graph(file_path: str) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    指定されたpklファイルからOSMnxのグラフを読み込み、投影後にGeoDataFrameに変換する関数。

    Parameters:
        file_path (str): OSMnxグラフのpklファイルのパス

    Returns:
        tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]: (ノードのGeoDataFrame, エッジのGeoDataFrame)
    """
    with open(file_path, "rb") as f:
        G = pickle.load(f)
    
    G = ox.project_graph(G)
    
    nodes, edges = ox.graph_to_gdfs(G)
    nodes = nodes.reset_index()
    
    return G,nodes, edges


def load_all_osmnx_graph(file_path: str) -> nx.MultiDiGraph:
    """
    指定されたpklファイルからOSMnxのグラフを読み込み、投影を行う関数。

    Parameters:
        file_path (str): OSMnxグラフのpklファイルのパス

    Returns:
        nx.MultiDiGraph: 投影後のOSMnxグラフ
    """
    with open(file_path, "rb") as f:
        G = pickle.load(f)
    
    return ox.project_graph(G)


def load_compute_shortest_path(file_path: str) -> pd.DataFrame:
    """
    指定されたExcelファイルを読み込み、'via' 列をリスト形式に変換する関数。

    Parameters:
        file_path (str): Excelファイルのパス

    Returns:
        pd.DataFrame: 読み込まれ、'via' 列がリスト形式に変換されたデータフレーム
    """
    df = pd.read_excel(file_path)
    df['via'] = df['via'].astype(str)
    df["via"] = df["via"].apply(lambda x: list(map(int, x.split(','))))
    return df