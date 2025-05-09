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
    
    def get_subscription_farm(self, farm_id):
        dict_user_info = self.client.read("farms/"+farm_id)
        
        return dict_user_info
    
    def get_review_info(self, field_id):
        dict_user_info = self.client.read("review_fields/"+field_id)
        
        return dict_user_info
    
    def get_crop_info(self, crop_id):
        dict_user_info = self.client.read("crops/"+crop_id)
        
        return dict_user_info
    
    def get_subscription_user_info(self, field_id, user_id):
        dict_user_info = self.client.read("farms/"+field_id+"/subscription/"+user_id)
        
        return dict_user_info
    
    def get_ai_review(self, field_id):
        self.client.create_or_update(f"get/field_id", field_id)
        
        ans = None
        while(True):
            ans = self.client.read("send")
            if ans != None:
                break
        
        return ans

        
if __name__ == "__main__":
    df = data_factory()
    print(df.client.read("aa"))