from src.infrastructure.io import load_osmid_csv, load_drive_osmnx_graph, load_all_osmnx_graph,load_stop_names

import pandas as pd

def merge_osmid_with_nodes(osmid_df: pd.DataFrame, nodes_df: pd.DataFrame) -> pd.DataFrame:
    """
    osmidデータにノードの座標情報を結合する関数。

    Parameters:
        osmid_df (pd.DataFrame): osmidのデータフレーム
        nodes_df (pd.DataFrame): ノード情報（osmid, x, y などを含む）データフレーム

    Returns:
        pd.DataFrame: 座標情報が追加されたデータフレーム
    """
    return pd.merge(osmid_df, nodes_df, on=['osmid'], how='left')

def merge_osmid_with_stops(osmid_df: pd.DataFrame, stop_name_df: pd.DataFrame) -> pd.DataFrame:
    """
    osmidデータとstop_nameデータをstop_idをキーに結合する関数。

    Parameters:
        osmid_df (pd.DataFrame): osmidのデータフレーム
        stop_name_df (pd.DataFrame): stop_nameを含むデータフレーム

    Returns:
        pd.DataFrame: 結合後のデータフレーム
    """
    return pd.merge(osmid_df, stop_name_df, on=['stop_id'])


def split_drive_all_osmid(osmid_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    osmidデータフレームをdrive用（yがNaNでないもの）とall用（yがNaNのもの）に分割する関数。
    drive用のGraphを使うのでall用のネットワークは欠損値となる

    Parameters:
        osmid_df (pd.DataFrame): osmidのデータフレーム

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (drive_osmid_df, all_osmid_df)
    """
    drive_osmid_df = osmid_df.loc[~osmid_df['y'].isna()].reset_index(drop=True)
    all_osmid_df = osmid_df.loc[osmid_df['y'].isna()].reset_index(drop=True)
    return drive_osmid_df, all_osmid_df


def merge_route_with_osmid(osmid_df: pd.DataFrame, bus_stop_segment_df: pd.DataFrame) -> pd.DataFrame:
    """
    bus_stop_segmentデータとosmidデータを結合し、from_stopとto_stopの情報を整理する関数。

    Parameters:
        osmid_df (pd.DataFrame): osmidのデータフレーム
        bus_stop_segment_df (pd.DataFrame): バス路線区間のデータフレーム

    Returns:
        pd.DataFrame: 結合後のデータフレーム
    """
    # from_stop_id に対して結合
    merge_df = pd.merge(
        osmid_df, bus_stop_segment_df,
        left_on=['stop_id'], right_on=['from_stop_id'], how='right'
    )

    # from_stop のカラム名変更
    merge_df = merge_df.rename(columns={'osmid': 'from_osmid', 'lon': 'from_lon', 'lat': 'from_lat'})

    # 必要なカラムのみ残す
    merge_df = merge_df[['from_stop_id', 'to_stop_id', 'from_stop_name', 'from_osmid', 'from_lon', 'from_lat']]

    # to_stop_id に対して結合
    merge_df = pd.merge(
        merge_df, osmid_df,
        left_on=['to_stop_id'], right_on=['stop_id'], how='left'
    )

    # to_stop のカラム名変更
    merge_df = merge_df.rename(columns={'osmid': 'to_osmid', 'stop_name': 'to_stop_name', 'lon': 'to_lon', 'lat': 'to_lat'})

    # 最終的なカラム整理
    merge_df = merge_df[['from_stop_id', 'to_stop_id', 'from_stop_name', 'to_stop_name',
                         'from_osmid', 'to_osmid', 'from_lon', 'from_lat', 'to_lon', 'to_lat']]
    
    return merge_df

def normalize_stop_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    バス停の名称を統一する（名寄せ）関数。

    Parameters:
        df (pd.DataFrame): バス停データフレーム

    Returns:
        pd.DataFrame: 名寄せ後のデータフレーム
    """
    name_mapping = {
        '宇部興産中央病院': '宇部興産中央病院（中）',
        '八幡宮': '八幡宮'
    }

    for original, standardized in name_mapping.items():
        df.loc[df['from_stop_name'].str.contains(original, na=False), 'from_stop_name'] = standardized
        df.loc[df['to_stop_name'].str.contains(original, na=False), 'to_stop_name'] = standardized

    return df

def split_by_missing_values(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    欠損値を含む行（all net）と欠損値のない行（drive net）を分割する関数。

    Parameters:
        df (pd.DataFrame): 欠損値を含む可能性のあるデータフレーム

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (drive_df, all_df)
            - drive_df: 欠損値のないデータ
            - all_df: 欠損値を含むデータ
    """
    drive_df = df.dropna().reset_index(drop=True)  # 欠損値を含まないデータ
    all_df = df[df.isna().any(axis=1)].reset_index(drop=True)  # 欠損値を含むデータ
    return drive_df, all_df

