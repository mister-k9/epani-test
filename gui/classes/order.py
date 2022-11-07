import sqlite3
from datetime import datetime
import requests
from random import randint

class Order():
    def __init__(self):
        self.volume = ''
        self.amount = 0
        self.tap = ''
        self.cardNo = ''
        self.internet_available = True
        self.dispensed_volume = ''
        self.available_balance = ''
        self.holder_name  = ''

    def get_tap(self):
        return self.tap

    def get_volume(self):
        return self.volume

    def get_amount(self):
        return self.amount

    def set_tap(self, tap):
        self.tap = tap

    def set_volume(self, volume=0, amount=0):
        self.volume += volume
        self.amount += amount

    def set_cardno(self, card_no=''):
        self.cardNo = card_no

    def process_payment(self):
        if not self.internet_available:

            conn = sqlite3.connect("/home/pi/epani-rpi/epani.db")

            cur = conn.cursor()
            query = 'SELECT name,balance FROM cards_info WHERE card_number =\'' + self.cardNo + "\'"
            cur.execute(query)
            tst = cur.fetchmany()[0]

            current_balance = tst[1]
            card_owner = tst[0]

            if current_balance >= self.amount:
                final_balance = current_balance - self.amount
                nw = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute('UPDATE cards_info SET balance=' + str(final_balance) + ',last_txn_volume=' + str(
                    self.amount) + ',last_txn_timestamp=\'' + nw + "\'" + ' WHERE card_number =\'' + self.cardNo + "\'")
                status = "completed"
                conn.execute('INSERT INTO orders_info (order_id,card_number,volume,amount,txn_status,timestamp) VALUES (?,?,?,?,?,?)',["orderid",self.cardNo, self.volume, self.amount,status,nw])
                conn.commit()
                self.available_balance = final_balance
                self.holder_name = card_owner
                print(card_owner, current_balance, final_balance)
                return "payment_done"
            else:
                print("No Balance")
                return "payment_failed"
            conn.close()
        else:
            self.internet_available_func()
            return "payment_done"

    def is_volume_set(self):
        return self.volume != '' and self.amount != 0

    def is_card_set(self):
        return self.cardNo != ''

    def is_tap_set(self):
        return self.tap != ''

    def print_all(self):
        print("Volume:", self.volume)
        print("Amount:", self.amount)
        print("Card No:", self.cardNo)
        print("Tap:", self.tap)

    def internet_available_func(self):
        try:
            # TODO: IF NOT API WORKING SHOULD NOT GO TO TAP SELECTION, SHOW ERROR
            # TODO: CARD NOT FOUND MESSAGE
            # TODO: NO BALANCE MESSAGE
            # auth_endpoint = "http://localhost:8000/api/auth/"
            # auth_resp = requests.post(auth_endpoint, json={"username": "machine1", "password": "k9k9k9k9"})

            # if auth_resp.status_code == 200:
            #     token = auth_resp.json()['token']

            token = '30aa15ffa73024254b94e0135950b827c30e8202'

            headers = {
                "Authorization": f"Bearer {token}"
            }

            get_card_details_api = f"https://epani-django.herokuapp.com/api/cards/{self.cardNo}/"
            get_card_details = requests.get(get_card_details_api, headers=headers)

            res = get_card_details.json()
            print(res)
            current_balance = res['balance']
            self.holder_name = res['holder_name']
            if current_balance >= self.amount:
                final_balance = current_balance - self.amount
                nw = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            res['balance'] = final_balance
            self.available_balance = final_balance

            update_card_details_api = f"https://epani-django.herokuapp.com/api/cards/{self.cardNo}/update/"
            update_card_details = requests.put(update_card_details_api, json=res, headers=headers)
            print(update_card_details.status_code)



            # order_id = last order id  + 1
            value = randint(0, 1000000)

            data = {
                'order_id': str(value),
                'machine_id': '900000001',
                'card_number': f'{self.cardNo}',
                'order_status': 'DONE_PAYMENT',
                'amount': f'{self.amount}',
                'volume_in_ml': f'{self.volume}',
                'sync_status': 'SYNCED',
                'local_timestamp': f'{nw}',
            }

            post_order_api = "https://epani-django.herokuapp.com/api/orders/"
            post_order = requests.post(post_order_api, json=data, headers=headers)
            print(post_order.status_code)
        except Exception as e:
            print(e)