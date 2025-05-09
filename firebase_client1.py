import firebase_admin
from firebase_admin import credentials, db

class firebase_client1: #전체 firebase class
    def __init__(self, key_path: str, db_url: str): #키 파일과 URL 읽어오는 기본 함수
        cred = credentials.Certificate(key_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': db_url
            })
        self.root_ref = db.reference()

    def create_or_update(self, path: str, data: dict): #기존 데이터가 없을 시 새로 만들거나 있다면 업데이트
        self.root_ref.child(path).set(data)

    def read(self, path: str = ""): #데이터 읽어오는 함수
        if path:
            return self.root_ref.child(path).get()
        else:
            return self.root_ref.get()


    def update(self, path: str, data: dict): #무조건 업데이트
        self.root_ref.child(path).update(data)

    def delete(self, path: str): #데이터 삭제하는 함수
        self.root_ref.child(path).delete()