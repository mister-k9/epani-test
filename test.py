import requests
from datetime import datetime
import sqlite3
from random import randint

conn = sqlite3.connect("epani.db")
cur = conn.cursor()
creds = (cur.execute('SELECT * FROM mac_info')).fetchone()
mid, mtoken = creds[1], creds[2]
conn.close()

deduct_balance_endpoint = f"http://127.0.0.1:8000/api/deduct_card_balance/"
nw = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
value = randint(0, 1000000)

params = {
    'mid': mid,
    'mtoken': mtoken
}

data = {
    'order_id': str(value),
    'machine_id': mid,
    'card_number': 'CA624919',
    'order_status': 'DONE_PAYMENT',
    'amount': '5',
    'volume_in_ml': '1',
    'sync_status': 'SYNCED',
    'local_timestamp': nw,
}

post_order_api = "http://127.0.0.1:8000/api/create_order/"
post_order = requests.post(
post_order_api, json=data, params=params)
print(post_order.json())