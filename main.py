from firebase_client1 import firebase_client1

client = None

# 이용자 등록
def User(user_id, name, phoneNum, address, password, subscription_fields=None):
    user_data = {
        "name": name,
        "phoneNum": phoneNum,
        "address": address,
        "password": password,
        "subscription_fields": subscription_fields or {}
    }
    client.create_or_update(f"users/{user_id}", user_data)


# 농부 등록
def Farmer(farmer_id, name, phoneNum, address, password, field_id):
    farmer_data = {
        "name": name,
        "phoneNum": phoneNum,
        "address": address,
        "password": password,
        "field_id": field_id
    }
    client.create_or_update(f"farmers/{farmer_id}", farmer_data)


# 농작물 추가
def Crops(crop_id, name, crop_price, description, image_url):
    crop_data = {
        "name": name,
        "crop_price": crop_price,
        "description": description,
        "image_url": image_url
    }
    client.create_or_update(f"crops/{crop_id}", crop_data)



# 농장 추가
def Farm(field_id, farmer_id, crops, avg_rating, coast,
             avg_yield, max_yield, min_yield,remain_percentage,
             log=None, subscription=None):
    farm_data = {
        "farmer_id": farmer_id,
        "crops": crops,
        "avg_rating": avg_rating,
        "coast": coast,
        "harvest_yield": {
            "avg_harvest_yield": avg_yield,
            "max_harvest_yield": max_yield,
            "min_harvest_yield": min_yield
        },
        "remain_percentage": remain_percentage,
        "log": log or {},
        "subscription": subscription or {}
    }
    client.create_or_update(f"farms/{field_id}", farm_data)



#밭 리뷰 등록
def Review_Field(field_id, user_id, content, date, rating):
    review = {
        "user_id": user_id,
        "content": content,
        "date": date,
        "rating": rating
    }
    path = f"review_fields/{field_id}/reviews"
    existing_reviews = client.read(path)

    if not isinstance(existing_reviews, dict):
        existing_reviews = {}

    if existing_reviews:
        max_index = max(int(k) for k in existing_reviews.keys())
        next_index = str(max_index + 1)
    else:
        next_index = "0"

    existing_reviews[next_index] = review
    client.create_or_update(path, existing_reviews)



if __name__ == "__main__":
    client = firebase_client1(
        "khuton-firebase-adminsdk-fbsvc-896da2cdf0.json",
        "https://khuton-default-rtdb.firebaseio.com/"
    )

# 사용자 등록
User(
    user_id="user_test_010",
    name="이은정",
    phoneNum="010-1234-8888",
    address="경기도 고양시 덕양구 상추길 99",
    password="testpw456",
    subscription_fields={
        "field_lettuce_001": {
            "start_date": "2025-05-01"
        }
    }
)

# 농부 등록
Farmer(
    farmer_id="farmer_test_010",
    name="최농부",
    phoneNum="010-9999-1234",
    address="강원도 평창군 상추마을 8-1",
    password="farmsecure",
    field_id="field_lettuce_001"
)

# 작물 등록
Crops(
    crop_id="crop_lettuce",
    name="상추",
    crop_price=1400,
    description="유기농 인증 상추입니다. 쌈에 최적화된 품질입니다.",
    image_url="https://example.com/lettuce.jpg"
)

# 밭 등록
Farm(
    field_id="field_lettuce_001",
    farmer_id="farmer_test_010",
    crops="상추",
    avg_rating=4.6,
    coast=1400.0,
    avg_yield=95.0,
    max_yield=110.0,
    min_yield=80.0,
    remain_percentage=73.0,
    log={
        "2025-05-01": {
            "harvest_yield": 97.5,
            "remain_percentage": 73.0
        }
    },
    subscription={
        "user_test_010": {
            "amount": 20.0,
            "start_date": "2025-05-01"
        }
    }
)
# 리뷰 등록
Review_Field(
    field_id="field_lettuce_001",
    user_id="user_test_010",
    content="상추가 신선하고 맛이 좋아요. 포장도 깔끔했습니다.",
    date="2025-05-10",
    rating=5
)