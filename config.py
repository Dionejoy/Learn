import os

# WebSocket 配置
WEBSOCKET_CONFIG = {
    "请求URL": "wss://streaming.forexpros.com/echo/335/4uejq4ye/websocket",
    "请求方法": "GET",
    "状态代码": "101 Switching Protocols",
    "主机": "streaming.forexpros.com",
    "来源": "https://cn.investing.com",
    "用户代理": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
    "接受编码": "gzip, deflate, br, zstd",
    "接受语言": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "缓存控制": "no-cache",
    "pragma": "no-cache",
    "sec-websocket-extensions": "permessage-deflate; client_max_window_bits",
    "sec-websocket-key": "T/jcmZ8UjizjtLk+7WxwYw==",
    "sec-websocket-version": "13",
    "订阅消息": '{\"_event\":\"bulk-subscribe\",\"tzID\":8,\"message\":\"isOpenExch-103:%%isOpenExch-54:%%pid-40820:%%pid-28930:%%pid-179:%%isOpenExch-21:%%pid-178:%%isOpenExch-20:%%pid-1175152:%%isOpenExch-152:%%pid-1175153:%%pid-8827:%%isOpenExch-1004:%%pid-1167762:%%isOpenExch-NaN:%%pid-100858:%%pid-1075487:%%pid-944841:%%pid-1096030:%%pid-944521:%%pid-944402:%%pid-944073:%%pid-945020:%%pid-100989:%%pid-1115063:%%pid-8969:%%pid-1155537:%%pid-41609:%%pid-996093:%%pid-8849:%%pid-8833:%%pid-8830:%%pid-8836:%%pid-8862:%%pid-8831:%%pid-8916:%%pid-941155:%%isOpenExch-1:%%pid-102047:%%pid-6378:%%isOpenExch-2:%%pid-102911:%%pid-6435:%%pid-26490:%%pid-6408:%%pid-1:%%isOpenExch-1002:%%pid-2111:%%isOpenExch-1001:%%pid-961728:%%pid-1817:%%pid-3:%%pid-5:%%pid-2:%%pid-6369:%%pid-243:%%pid-267:%%pid-7888:%%pid-284:%%isOpenExch-3:%%pid-352:%%isOpenExch-4:%%pid-169:%%pid-20:%%pid-166:%%pid-172:%%pid-27:%%pid-167:%%isOpenExch-9:%%pid-8832:%%pid-7:%%pid-9:%%pid-10:%%pid-252:%%pid-6497:%%pid-238:%%pid-6507:%%pid-8128:%%pid-13989:%%pid-39107:%%pid-32486:%%pid-101060:%%pid-942630:%%pid-945006:%%pid-945513:%%pid-994504:%%pid-1017433:%%pid-1051076:%%pid-1062255:%%pid-945629:%%pid-1057391:%%pid-308:%%pid-332:%%pid-10520:%%pid-20246:%%pid-32212:%%pid-39111:%%pid-40823:%%pid-941708:%%pid-941888:%%pid-1054246:%%pid-44336:%%pid-942977:%%pid-23705:%%pid-13994:%%pid-8575:%%pid-9217:%%pid-20245:%%pid-100276:%%pid-100287:%%pid-100289:%%pid-100290:%%pid-100299:%%pid-100303:%%pid-100310:%%pid-100320:%%pid-100350:%%pid-100493:%%pid-100673:%%pid-100727:%%pid-100978:%%pid-101062:%%pid-101064:%%pid-101072:%%pid-101073:%%pid-101076:%%pid-101078:%%pid-101079:%%pid-101083:%%pid-101084:%%pid-101097:%%pid-101099:%%pid-101103:%%pid-101113:%%pid-101119:%%pid-101122:%%pid-101123:%%pid-101137:%%pid-101143:%%pid-101158:%%pid-944122:%%pid-944220:%%pid-944315:%%pid-944451:%%pid-944524:%%pid-944533:%%pid-944579:%%pid-944897:%%pid-955759:%%pid-995189:%%pid-1017555:%%pid-1076874:%%pid-1112831:%%pid-100768:%%isOpenExch-0:%%pid-100996:%%pid-944375:%%pid-944670:%%pid-945334:%%pid-946593:%%pid-950802:%%pid-994553:%%pid-994572:%%pid-100380:%%pid-100786:%%pid-100856:%%pid-942831:%%pid-944022:%%pid-944080:%%pid-944347:%%pid-944429:%%pid-944563:%%pid-944583:\"}'
}

# 邮件配置
EMAIL_CONFIG = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,
    "sender_email": "max17788556699@163.com",
    "password": "XHVFjimTQ7srtVaJ",
    "receiver_email": "977226416@qq.com"
}
# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 数据库路径
DB_PATH = os.path.join(DATA_DIR, "stock_data.db")

# 警报设置
DEFAULT_ALERT_THRESHOLD = 1.5  # 默认价格变化警报阈值（百分比）
DEFAULT_INTERVAL_SECONDS = 120  # 默认监控时间间隔（秒）
