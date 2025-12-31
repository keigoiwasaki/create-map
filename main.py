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

from src.infrastructure.io import load_osmid_csv,load_drive_osmnx_graph,load_all_osmnx_graph,load_stop_names,load_bus_stop_segment_csv,load_compute_shortest_path,generate_map,save_geojson
from src.infrastructure.data_transformer import merge_osmid_with_nodes,merge_osmid_with_stops,split_drive_all_osmid,merge_route_with_osmid,normalize_stop_names,split_by_missing_values
from src.domain.service.bus_route_service import compute_shortest_paths,compute_and_convert_paths,create_geodataframe,merge_and_remove_duplicates


osmid_df = load_osmid_csv('data/osm/osmid.csv')

# 車道のネットワークを取得
drive_G,drive_nodes, drive_edges = load_drive_osmnx_graph('data/osm/osmnx_drive_graph.pkl')

# 全体（車道 + 歩道）のネットワークを取得
all_G = load_all_osmnx_graph('data/osm/osmnx_all_graph.pkl')

# 座標を付与
osmid_df = merge_osmid_with_nodes(osmid_df,drive_nodes)

# stop_nameを付与する
stop_name = load_stop_names('data/GTFS/stops.txt')

# stop_nameを付与する
osmid_df = merge_osmid_with_stops(osmid_df,stop_name)

# 車道と全体のネットワーク
drive_osmid_df, all_osmid_df  = split_drive_all_osmid(osmid_df)

# OD表を読み込み
bus_stop_segment_df = load_bus_stop_segment_csv('data/bus_stop_segment.csv')

# route_segmentデータとosmidデータを結合し、from_stopとto_stopの情報を整理する
merged_df = merge_route_with_osmid(osmid_df, bus_stop_segment_df)

# 名寄せ
merged_df = normalize_stop_names(merged_df)

# 車道と全てで分割する
drive_df, all_df = split_by_missing_values(merged_df)

# OSMnxのグラフを使って、各行の 'from_osmid' から 'to_osmid' までの最短経路を計算する
drive_df = compute_shortest_paths(drive_df, drive_G)  # drive 用
all_df = compute_shortest_paths(all_df, all_G)  # all net 用

drive_gdf = create_geodataframe(drive_df,drive_G)
all_gdf = create_geodataframe(all_df,all_G)

# 最短経路を計算し、GeoDataFrameに変換する関数。
drive_compute_shortes_df = compute_and_convert_paths(load_compute_shortest_path('data/via_node/compute_shortest_path_drive.xlsx'), drive_df, drive_G)
all_compute_shortes_df = compute_and_convert_paths(load_compute_shortest_path('data/via_node/compute_shortest_path_all.xlsx'), all_df, all_G)

concat_drive_gdf = merge_and_remove_duplicates(drive_compute_shortes_df, drive_gdf)
concat_all_gdf = merge_and_remove_duplicates(all_compute_shortes_df, all_gdf)

gdf = pd.concat([concat_drive_gdf,concat_all_gdf])

# mapを作成
bus_map = generate_map(concat_drive_gdf, concat_all_gdf)

# geogsonを保存
save_geojson(gdf)