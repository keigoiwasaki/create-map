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

def compute_shortest_paths(df: pd.DataFrame, graph) -> pd.DataFrame:
    """
    OSMnxのグラフを使って、各行の 'from_osmid' から 'to_osmid' までの最短経路を計算する関数。

    Parameters:
        df (pd.DataFrame): 'from_osmid' と 'to_osmid' を含むデータフレーム
        graph: OSMnxのグラフ (MultiDiGraph)

    Returns:
        pd.DataFrame: 'path' カラムを追加したデータフレーム
    """
    df['path'] = df.progress_apply(lambda row: ox.distance.shortest_path(graph, row['from_osmid'], row['to_osmid']), axis=1)
    return df


def compute_shortest_path(G, source, target, via_nodes=None):
    """
    route修正アルゴリズム
    via_nodes : list
    """
    # try:
    if via_nodes and isinstance(via_nodes, list) and len(via_nodes) > 0:
        path = []
        current = source
        for via in via_nodes:
            # ソースから最初の経由ノードへ
            sub_path = ox.shortest_path(G, current, via, weight='length')
            if path:
                # 先頭ノードが重複するため除外
                path += sub_path[1:]
            else:
                path = sub_path
            current = via
        # 最後の経由ノードからターゲットへ
        sub_path = ox.shortest_path(G, current, target, weight='length')
        if path:
            path += sub_path[1:]
        else:
            path = sub_path
    else:
        # 経由ノードがない場合
        path = ox.shortest_path(G, source, target, weight='length')
    return path

# 各行のosmidリストからLineStringまたはPointを作成する関数
def create_geometry(osmid_list,graph):
    coords = [(graph.nodes[node]['x'], graph.nodes[node]['y']) for node in osmid_list]
    
    if len(coords) > 1:
        return LineString(coords)  # 複数の座標がある場合はLineString
    elif len(coords) == 1:
        return Point(coords[0])  # 座標が1つしかない場合はPoint
    else:
        return None  # 座標がない場合はNone
    
def create_geodataframe(df: pd.DataFrame, graph) -> gpd.GeoDataFrame:
    """
    OSMノードIDのリストからGeoDataFrameを作成し、CRSを設定する関数。

    Parameters:
        df (pd.DataFrame): 'path' カラムを含むデータフレーム
        graph (nx.MultiDiGraph): OSMnxのグラフ

    Returns:
        gpd.GeoDataFrame: ジオメトリを追加し、CRSを設定したGeoDataFrame
    """
    df['geometry'] = df['path'].progress_apply(lambda x: create_geometry(x, graph))

    # GeoDataFrameを作成し、CRSを設定
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=graph.graph['crs'])

    # 緯度経度 (EPSG:4326) に変換
    gdf = gdf.to_crs(epsg=4326)

    gdf = gdf[['from_stop_id', 'to_stop_id', 'from_stop_name', 'to_stop_name','from_osmid', 'to_osmid','geometry']]
    
    return gdf

def compute_and_convert_paths(df: pd.DataFrame, ref_df: pd.DataFrame, graph) -> gpd.GeoDataFrame:
    """
    最短経路を計算し、GeoDataFrameに変換する関数。

    Parameters:
        df (pd.DataFrame): 'from_stop_name', 'to_stop_name', 'via' を含むデータフレーム
        ref_df (pd.DataFrame): OSMノードID情報を含むデータフレーム
        graph (nx.MultiDiGraph): OSMnxのグラフ

    Returns:
        gpd.GeoDataFrame: 最短ルートを追加し、CRSを設定したGeoDataFrame
    """
    df = pd.merge(df, ref_df, how='left', on=['from_stop_name', 'to_stop_name'])
    
    df['path'] = df.progress_apply(lambda row: compute_shortest_path(graph, row['from_osmid'], row['to_osmid'], row['via']), axis=1)
    df['geometry'] = df['path'].progress_apply(lambda x: create_geometry(x, graph))
    
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=graph.graph['crs'])
    gdf = gdf.to_crs(epsg=4326)
    gdf = gdf[['from_stop_id', 'to_stop_id', 'from_stop_name', 'to_stop_name','from_osmid', 'to_osmid','geometry']]
    return gdf

def merge_and_remove_duplicates(primary_gdf: gpd.GeoDataFrame, secondary_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    2つのGeoDataFrameを結合し、重複する `from_stop_name` と `to_stop_name` を削除する関数。

    Parameters:
        primary_gdf (gpd.GeoDataFrame): 優先的に保持したいデータフレーム
        secondary_gdf (gpd.GeoDataFrame): primary_gdf で上書きするデータフレーム

    Returns:
        gpd.GeoDataFrame: 重複を削除した統合データフレーム
    """
    merged_gdf = pd.concat([primary_gdf, secondary_gdf]).drop_duplicates(
        subset=['from_stop_name', 'to_stop_name'],
        keep='first'
    )
    return merged_gdf