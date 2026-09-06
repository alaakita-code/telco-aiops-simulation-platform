"""
地理編碼模組
將地址轉換為座標（使用 Nominatim OpenStreetMap）
"""
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import streamlit as st
from typing import Optional, Tuple
import time


class GeoCoder:
    """地理編碼器（使用 Nominatim）"""

    def __init__(self, user_agent: str = "telco_data_platform"):
        self.geocoder = Nominatim(user_agent=user_agent, timeout=10)
        self._last_request_time = 0
        self._min_delay = 1.0  # Nominatim 限制：每秒最多 1 次請求

    def _rate_limit(self):
        """速率限制（遵守 Nominatim 使用政策）"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request_time = time.time()

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """將地址轉換為座標"""
        try:
            self._rate_limit()
            location = self.geocoder.geocode(address)

            if location:
                return (location.latitude, location.longitude)
            else:
                return None

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            st.warning(f"地理編碼超時，請稍後再試：{str(e)}")
            return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """將座標轉換為地址"""
        try:
            self._rate_limit()
            location = self.geocoder.reverse(f"{lat}, {lon}")

            if location:
                return location.address
            else:
                return None

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            st.warning(f"反向地理編碼超時：{str(e)}")
            return None


@st.cache_resource
def get_geocoder() -> GeoCoder:
    """建立並快取地理編碼器"""
    return GeoCoder(user_agent="telco_data_platform")


def geocode_taiwan_address(address: str) -> Optional[Tuple[float, float]]:
    """地理編碼台灣地址"""
    geocoder = get_geocoder()

    # 如果地址沒有包含「台灣」，自動加入
    if "台灣" not in address and "Taiwan" not in address:
        address = f"台灣 {address}"

    return geocoder.geocode_address(address)


def get_taiwan_bbox() -> Tuple[float, float, float, float]:
    """取得台灣全島的座標範圍"""
    return (119.5, 21.5, 122.5, 25.5)
