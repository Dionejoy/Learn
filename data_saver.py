import threading
import queue
import sqlite3
from config import DB_PATH


class DataSaver:
    def __init__(self):
        """初始化数据保存器"""
        self.save_queue = queue.Queue()
        self._init_database()
        self._start_save_thread()

    def _init_database(self):
        """初始化数据库结构"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 创建股票数据表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            产品id TEXT,
            最新价格 REAL,
            买价 REAL,
            卖价 REAL,
            当日最高价 REAL,
            当日最低价 REAL,
            昨日收盘价 REAL,
            价格变化百分比 REAL,
            时间 TEXT,
            时间戳 TEXT,
            北京时间 TEXT
        )
        """)

        # 创建警报历史表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            产品id TEXT,
            基准价格 REAL,
            当前价格 REAL,
            变化率 REAL,
            基准时间 TEXT,
            当前时间 TEXT,
            警报时间 TEXT,
            警报类型 TEXT
        )
        """)

        conn.commit()
        conn.close()

    def _save_worker(self):
        """数据保存线程的工作函数"""
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()

        while True:
            item = self.save_queue.get()
            if item is None:
                break  # 支持优雅退出

            save_type, data = item

            try:
                if save_type == "stock_data":
                    pid, stock_data = data
                    cursor.execute("""
                        INSERT INTO stock_data (
                            产品id, 最新价格, 买价, 卖价,
                            当日最高价, 当日最低价, 昨日收盘价,
                            价格变化百分比, 时间, 时间戳, 北京时间
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        stock_data.get('产品ID', ''),
                        stock_data.get('最新价格', 0.0),
                        stock_data.get('买价', 0.0),
                        stock_data.get('卖价', 0.0),
                        stock_data.get('当日最高价', 0.0),
                        stock_data.get('当日最低价', 0.0),
                        stock_data.get('昨日收盘价', 0.0),
                        stock_data.get('价格变化百分比', 0.0),
                        stock_data.get('时间', ''),
                        stock_data.get('时间戳', ''),
                        stock_data.get('北京时间', '')
                    ))

                elif save_type == "alert":
                    alert_data = data
                    cursor.execute("""
                        INSERT INTO alert_history (
                            产品id, 基准价格, 当前价格, 变化率,
                            基准时间, 当前时间, 警报时间, 警报类型
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        alert_data.get('pid', ''),
                        alert_data.get('baseline_price', 0.0),
                        alert_data.get('current_price', 0.0),
                        alert_data.get('change_rate', 0.0),
                        alert_data.get('baseline_time', ''),
                        alert_data.get('current_time', ''),
                        alert_data.get('alert_time', ''),
                        alert_data.get('alert_type', '价格波动')
                    ))

                conn.commit()
            except Exception as e:
                print(f"[保存数据库异常] {e}")

            self.save_queue.task_done()

        conn.close()

    def _start_save_thread(self):
        """启动数据保存后台线程"""
        self.save_thread = threading.Thread(target=self._save_worker, daemon=True)
        self.save_thread.start()

    def save_stock_data(self, pid, data):
        """
        保存股票数据

        Args:
            pid: 产品ID
            data: 股票数据字典
        """
        self.save_queue.put(("stock_data", (pid, data)))

    def save_alert(self, alert_data):
        """
        保存警报历史

        Args:
            alert_data: 警报数据字典
        """
        self.save_queue.put(("alert", alert_data))

    def close(self):
        """关闭保存线程"""
        self.save_queue.put(None)
        self.save_thread.join()
