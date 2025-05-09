import firebase_admin
from firebase_admin import credentials, db

class firebase_client1:
    def __init__(self, key_path: str, db_url: str):
        cred = credentials.Certificate(key_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': db_url
            })
        self.root_ref = db.reference()

    def create_or_update(self, path: str, data: dict):
        self.root_ref.child(path).set(data)

    def read(self, path: str = ""):
        if path:
            return self.root_ref.child(path).get()
        else:
            return self.root_ref.get()


    def update(self, path: str, data: dict):
        self.root_ref.child(path).update(data)

    def delete(self, path: str):
        self.root_ref.child(path).delete()
