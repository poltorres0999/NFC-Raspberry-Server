
from src.DBHandler import DBHandler

db = DBHandler("RFID_DB.db")
db.init_db()
print(db.get_all_master_keys())
print(db.get_all_tags())
print(db.get_logs())

if db.check_rfid_tag("123789"):
    print("Found")
