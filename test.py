import sqlite3
import time
import serial
import requests
import subprocess

file = "epani.db"


def check_internet_connection(duration=None):
    if duration:
        start = time.time()
        while True:
            try:
                requests.get('https://www.google.com/')
                return True
            except:
                print("Internet Connection Is Not Active, Trying Again ...")
                time.sleep(5)
                pass
            end = time.time()
            if int(end - start) >= duration:
                return False

    else:
        while True:
            try:
                requests.get('https://www.google.com/')
                break
            except:
                print("Internet Connection Is Not Active, Trying Again ...")
                time.sleep(5)
                pass


def check_server_connection(duration=None):
    if duration:
        start = time.time()
        while True:
            try:
                requests.get('http://127.0.0.1:8000/')
                return True
            except:
                print("Server Down! Trying Again ... ")
                time.sleep(5)
                pass
            end = time.time()
            if int(end - start) >= duration:
                return False
    else:
        while True:
            try:
                requests.get('http://127.0.0.1:8000/')
                break
            except:
                print("Server Down! Trying Again ... ")
                time.sleep(5)
                pass


def get_or_set_machine_credentials():
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    # Create Mac Table
    cur.execute(
        "CREATE TABLE IF NOT EXISTS  mac_info (id INTEGER PRIMARY KEY AUTOINCREMENT,mid text, mtoken text);")
    # ------- MAC INFO ----------
    mac_creds_available = (cur.execute('SELECT * FROM mac_info')).fetchone()
    if not mac_creds_available:
        print("========================================================================")
        print("|                         Set Machine Credentials                      |")
        print("========================================================================")
        mid = input('Enter Machine Id: ')
        print("------------------------------------------------------------------------")
        mtoken = input('Enter Machine Token: ')
        print("------------------- Credentials Saved Successfully ---------------------")
        cur.execute(
            "INSERT INTO mac_info (mid,mtoken) VALUES (?,?)", [mid, mtoken])
        conn.commit()
        conn.close()
        return mid, mtoken
    conn.close()
    return mac_creds_available[1], mac_creds_available[2]


def server_local_orders_sync():
    print("Unsynced orders have been synced and cleared!")


def server_local_cards_sync():
    print('~~~~~~~~~~~~~~~~~~~~~~~~~ Server - Local Cards Sync Initiated ~~~~~~~~~~~~~~~~~~~~~~~~~~')
    if check_internet_connection(20):
        if check_server_connection(20):
            print("Syncing cards (posting all the cards to server)")
            print(
                "~~~~~~~~~~~~~~~~~~~~~~~~~ Server - Local Cards Sync Successful ~~~~~~~~~~~~~~~~~~~~~~~~~")
            check_serial_hardware()

        else:
            print(
                "~~~~~~~~~~~~~~~~~~~~~~~ Server - Local Cards Sync Failed ~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Since Time Limit Exceeded")
            check_serial_hardware()
            return
    else:
        print("~~~~~~~~~~~~~~~~~~~~~~~ Server - Local Cards Sync Failed ~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Since Time Limit Exceeded")
        check_serial_hardware()
        return

def run_gui_app():
    try:
       subprocess.call("py app.py",shell=True) 
    except Exception as e:
        print(e)
        
        

def check_serial_hardware():
    print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~ Checking Serial Hardware Connection ~~~~~~~~~~~~~~~~~~~~~~~~~")
    while True:
        try:
            serialport = serial.Serial(
                port='COM13',
                baudrate=115200,
                timeout=0.3
            )
            serialport.close()
            break
        except serial.SerialException as e:
            print("Serial Port Disconnected. Trying again!")
            time.sleep(2)
            pass
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~ Serial Hardware Is Connected ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    run_gui_app()


def setup_db():
    conn = sqlite3.connect(file)
    cur = conn.cursor()
    # -------- CARDS INFO ----------
    cur.execute("CREATE TABLE IF NOT EXISTS cards_info (id INTEGER PRIMARY KEY AUTOINCREMENT, card_number text,machine_id text, holder_name text, balance int, last_txn_volume int, last_txn_status text, last_txn_timestamp text);")
    local_cards = (cur.execute('SELECT * FROM cards_info')).fetchone()
    # print(local_cards)
    if not local_cards:
        check_internet_connection()
        check_server_connection()
        mid, mtoken = get_or_set_machine_credentials()
        # HARD CODE ENDPOINTS INTO CODE
        cards_endpoint = "http://127.0.0.1:8000/api/get_cards/"
        params = {
            'mid': mid,
            'mtoken': mtoken,
        }
        # WHEN CARDS SHOULD BE POSTED IS TO BE DISCUSSED
        print("\n========================================================================")
        print("|             Retrieving Cards With Machine Credentials                |")
        print("========================================================================")
        get_cards = requests.get(cards_endpoint, params=params)
        cards = get_cards.json()
        if cards == "Invalid Machine":
            print("The Machine Is Not Found!")
            cur.execute(
                'DELETE FROM mac_info WHERE id = (SELECT min(id) FROM mac_info) ')
            conn.commit()
            conn.close()
            get_or_set_machine_credentials()
        if cards == "Invalid Request!":
            print("The Machine Token Is Invalid!")
            cur.execute(
                'DELETE FROM mac_info WHERE id = (SELECT min(id) FROM mac_info) ')
            conn.commit()
            conn.close()
            get_or_set_machine_credentials()
        for card in cards:
            print(card)
            cur.execute("INSERT INTO cards_info (card_number,machine_id,holder_name,balance,last_txn_volume,last_txn_status,last_txn_timestamp) VALUES (?,?,?,?,?,?,?)", [
                        card['card_number'], card['machine_id'], card['holder_name'], card['balance'], card['last_txn_volume'], card['last_txn_status'], card['last_txn_timestamp']])
            conn.commit()
        print("--------------- Successfully Copied Cards To Local DB -----------------")
        check_serial_hardware()

    else:
        server_local_cards_sync()
        # server_local_orders_sync()


if __name__ == "__main__":
    setup_db()
