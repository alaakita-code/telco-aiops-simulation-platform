"""
網路掃描器
掃描區域內設備、Ping 測試、Port 掃描
"""
import subprocess
import socket
import concurrent.futures
import ipaddress
import platform
from typing import List, Dict, Optional
from loguru import logger


class NetworkScanner:
    """網路掃描器"""

    def __init__(self, subnet: str = "192.168.1"):
        self.subnet = self._normalize_subnet(subnet)
        logger.info(f"網路掃描器初始化：{subnet}")

    @staticmethod
    def _normalize_subnet(subnet: str) -> str:
        """標準化前三段 IPv4 子網路，例如 192.168.1。"""
        subnet = str(subnet).strip()
        parts = subnet.split(".")

        if len(parts) == 4:
            parts = parts[:3]

        if len(parts) != 3:
            logger.warning(f"子網路格式不正確，改用預設值：{subnet}")
            return "192.168.1"

        try:
            for part in parts:
                value = int(part)
                if value < 0 or value > 255:
                    raise ValueError
            return ".".join(parts)
        except ValueError:
            logger.warning(f"子網路格式不正確，改用預設值：{subnet}")
            return "192.168.1"

    @staticmethod
    def _build_ping_command(ip: str, timeout: int) -> List[str]:
        """依作業系統產生 ping 指令。"""
        if platform.system().lower().startswith("win"):
            return ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
        return ["ping", "-c", "1", "-W", str(timeout), ip]

    def ping_host(self, ip: str, timeout: int = 1) -> Dict:
        """
        Ping 單一主機

        Args:
            ip: IP 地址
            timeout: 超時時間（秒）

        Returns:
            Ping 結果
        """
        try:
            ipaddress.ip_address(ip)
            result = subprocess.run(
                self._build_ping_command(ip, timeout),
                capture_output=True,
                text=True,
                timeout=timeout + 1
            )

            if result.returncode == 0:
                # 解析 ping 結果
                output = result.stdout
                if "time=" in output:
                    time_part = output.split("time=")[1].split()[0]
                    ping_ms = float(time_part.replace("ms", "").replace("<", ""))
                elif "時間=" in output:
                    time_part = output.split("時間=")[1].split()[0]
                    ping_ms = float(time_part.replace("ms", "").replace("<", ""))
                else:
                    ping_ms = 0

                return {
                    "ip": ip,
                    "status": "online",
                    "ping_ms": ping_ms
                }
            else:
                return {
                    "ip": ip,
                    "status": "offline",
                    "ping_ms": None
                }

        except subprocess.TimeoutExpired:
            return {
                "ip": ip,
                "status": "timeout",
                "ping_ms": None
            }
        except Exception as e:
            logger.error(f"Ping 失敗 {ip}: {e}")
            return {
                "ip": ip,
                "status": "error",
                "ping_ms": None
            }

    def scan_subnet(self, timeout: int = 1, max_workers: int = 50) -> List[Dict]:
        """
        掃描整個子網路

        Args:
            timeout: Ping 超時時間
            max_workers: 並行 worker 數量

        Returns:
            所有主機的 Ping 結果
        """
        results = []

        max_workers = max(1, min(int(max_workers), 100))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(1, 255):
                ip = f"{self.subnet}.{i}"
                futures.append(executor.submit(self.ping_host, ip, timeout))

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result["status"] == "online":
                        results.append(result)
                except Exception as e:
                    logger.debug(f"掃描工作失敗：{e}")

        logger.info(f"掃描完成：找到 {len(results)} 台線上設備")
        return results

    def scan_port(self, ip: str, ports: List[int] = [80, 443, 22, 21]) -> Dict:
        """
        掃描指定 IP 的 Port

        Args:
            ip: IP 地址
            ports: 要掃描的 Port 列表

        Returns:
            Port 掃描結果
        """
        open_ports = []

        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((ip, port))
                    if result == 0:
                        open_ports.append(port)
            except Exception as e:
                logger.debug(f"Port {port} 掃描失敗：{e}")

        return {
            "ip": ip,
            "open_ports": open_ports
        }


def get_local_subnet() -> str:
    """取得本地子網路"""
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        subnet = ".".join(ip.split(".")[:3])
        return subnet
    except:
        return "192.168.1"
