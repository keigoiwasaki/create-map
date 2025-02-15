import folium
import branca.colormap as cm
from shapely.geometry import LineString
import geopandas as gpd

def create_colormap() -> cm.LinearColormap:
    """
    カラーマップを作成する関数。
    
    Returns:
        cm.LinearColormap: 逆順にしたカラーマップ
    """
    colormap = cm.linear.RdYlBu_10.scale(0, 0.5)
    colormap.colors.reverse()
    return colormap

def draw_routes_on_map(m: folium.Map, gdf: gpd.GeoDataFrame, color: str) -> None:
    """
    GeoDataFrame のデータを Folium マップに描画する関数。

    Parameters:
        m (folium.Map): Folium マップオブジェクト
        gdf (gpd.GeoDataFrame): 描画するジオデータフレーム
        color (str): ラインの色
    """
    for _, row in gdf.iterrows():
        popup_text = f"<b>from_to</b>: {row['from_stop_name']}:{row['to_stop_name']}"
        if isinstance(row['geometry'], LineString):
            folium.PolyLine(
                locations=[(point[1], point[0]) for point in row['geometry'].coords],
                color=color, weight=2, popup=popup_text
            ).add_to(m)

def generate_map(concat_drive_gdf: gpd.GeoDataFrame, concat_all_gdf: gpd.GeoDataFrame, save_path: str = "data/map.html") -> None:
    """
    Folium を使用してルートを描画し、HTML に保存する関数。

    Parameters:
        concat_drive_gdf (gpd.GeoDataFrame): drive用のGeoDataFrame
        concat_all_gdf (gpd.GeoDataFrame): all用のGeoDataFrame
        save_path (str): 保存先のHTMLファイル名（デフォルトは "map.html"）
    """
    colormap = create_colormap()
    
    m = folium.Map(location=[34.002755, 131.221862], tiles='cartodbpositron', zoom_start=12)
    
    draw_routes_on_map(m, concat_drive_gdf, 'green')
    draw_routes_on_map(m, concat_all_gdf, 'red')
    
    m.add_child(colormap)
    m.save(save_path)

def save_geojson(gdf: gpd.GeoDataFrame, save_path: str = "data/map_data.geojson") -> None:
    """
    GeoDataFrame を GeoJSON ファイルとして保存する関数。

    Parameters:
        gdf (gpd.GeoDataFrame): 保存するGeoDataFrame
        save_path (str): 保存先のGeoJSONファイル名（デフォルトは "map_data.geojson"）
    """
    gdf.to_file(save_path, driver="GeoJSON", encoding="utf-8")
