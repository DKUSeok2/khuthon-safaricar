from firebase_client1 import firebase_client1

if __name__ == "__main__":
    client = firebase_client1(
        "khuton-firebase-adminsdk-fbsvc-896da2cdf0.json",
        "https://khuton-default-rtdb.firebaseio.com/"
    )

    client.create_or_update("notes/note1", {"message": "updating..."})
    print(client.read("notes/note1"))
    print("전체 루트 데이터:", client.read())
    print("노트 메시지:", client.read("notes/note1"))
