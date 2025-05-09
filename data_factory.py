from firebase_client1 import firebase_client1
    


class data_factory:
    def __init__(self):
        self.client = firebase_client1(
        "khuton-firebase-adminsdk-fbsvc-896da2cdf0.json",
        "https://khuton-default-rtdb.firebaseio.com/"
    )
        
    def get_user_info(self, user_id):
        dict_user_info = self.client.read("users/"+user_id)
        
        return dict_user_info
        
        
if __name__ == "__main__":
    df = data_factory()
    df.get_user_info("user_test_001")