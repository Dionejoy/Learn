from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
from config import DB_PATH, DEFAULT_ALERT_THRESHOLD, DEFAULT_INTERVAL_SECONDS
from flask_cors import CORS


app = Flask(__name__)
CORS(app)



@app.route('/api/stock/list', methods=['GET'])
def get_stock_list():
    """获取所有股票ID列表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT 产品id FROM stock_data")
        products = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({"status": "success", "data": products})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/stock/data/<pid>', methods=['GET'])
def get_stock_data(pid):
    """获取指定股票的历史数据"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', default=100, type=int)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM stock_data 
            WHERE 产品id = ? 
            ORDER BY 时间戳 DESC 
            LIMIT ?
        """, (pid, limit))

        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        conn.close()

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/stock/latest/<pid>', methods=['GET'])
def get_latest_stock_data(pid):
    """获取指定股票的最新数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM stock_data 
            WHERE 产品id = ? 
            ORDER BY 时间戳 DESC 
            LIMIT 1
        """, (pid,))

        row = cursor.fetchone()
        if row:
            data = dict(row)
        else:
            data = {}
        conn.close()

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/alert/list', methods=['GET'])
def get_alert_list():
    """获取警报历史列表"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', default=100, type=int)
        pid = request.args.get('pid', default=None)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if pid:
            cursor.execute("""
                SELECT * FROM alert_history 
                WHERE 产品id = ? 
                ORDER BY id DESC 
                LIMIT ?
            """, (pid, limit))
        else:
            cursor.execute("""
                SELECT * FROM alert_history 
                ORDER BY id DESC 
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        data = [dict(row) for row in rows]
        conn.close()

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """获取或更新警报设置"""
    if request.method == 'GET':
        # 获取当前设置
        return jsonify({
            "status": "success",
            "data": {
                "interval_seconds": DEFAULT_INTERVAL_SECONDS,
                "alert_threshold": DEFAULT_ALERT_THRESHOLD
            }
        })
    else:
        # 更新设置
        data = request.json
        try:
            new_interval = data.get('interval_seconds')
            new_threshold = data.get('alert_threshold')

            # 实际项目中这里应该保存到数据库或配置文件
            # 这里只是示例，返回接收到的设置
            return jsonify({
                "status": "success",
                "message": "设置已更新",
                "data": {
                    "interval_seconds": new_interval if new_interval else DEFAULT_INTERVAL_SECONDS,
                    "alert_threshold": new_threshold if new_threshold else DEFAULT_ALERT_THRESHOLD
                }
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400


def run_api_server(host='127.0.0.1', port=5000):
    """启动API服务器"""
    app.run(host=host, port=port, debug=False)
