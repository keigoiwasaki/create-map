import pandas as pd

def load_stop_names(file_path: str) -> pd.DataFrame:
    """
    指定されたGTFSのstops.txtファイルを読み込み、stop_idとstop_nameのみを抽出する関数。

    Parameters:
        file_path (str): GTFSのstops.txtファイルのパス

    Returns:
        pd.DataFrame: stop_idとstop_nameを含むデータフレーム
    """
    df = pd.read_csv(file_path, usecols=['stop_id', 'stop_name'])
    return df


def load_bus_stop_segment_csv(file_path: str) -> pd.DataFrame:
    """
    指定されたCSVファイルを読み込み、バス停区間データを取得する関数。

    Parameters:
        file_path (str): CSVファイルのパス

    Returns:
        pd.DataFrame: 読み込まれたデータフレーム
    """
    return pd.read_csv(file_path)