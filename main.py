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
             avg_yield, max_yield, min_yield,
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
    # 기존 리뷰 배열 불러오기 → 없으면 빈 배열
    path = f"review_fields/{field_id}/reviews"
    existing_reviews = client.read(path) or {}

    next_index = str(len(existing_reviews))

    existing_reviews[next_index] = review

    client.create_or_update(path, existing_reviews)


if __name__ == "__main__":
    client = firebase_client1(
        "khuton-firebase-adminsdk-fbsvc-896da2cdf0.json",
        "https://khuton-default-rtdb.firebaseio.com/"
    )

    # 1. 사용자 등록
    User(
        user_id="user_test_001",
        name="김테스트",
        phoneNum="010-1234-5678",
        address="서울시 중구 리뷰로 1길",
        password="testpw123",
        subscription_fields={
            "field_test_001": {
                "start_date": "2025-05-01"
            }
        }
    )

    # 2. 작물 등록 (crop_id는 crop 이름으로 단순 설정)
    Crops(
        crop_id="crop_lettuce",
        name="상추",
        crop_price=2200,
        description="신선한 상추입니다.",
        image_url="https://example.com/lettuce.jpg"
    )

    # 3. 밭 등록
    Farm(
        field_id="field_test_001",
        farmer_id="farmer_placeholder",  # 분석 목적상 농부 정보는 무시
        crops="상추",
        avg_rating=5,
        coast=2300.0,
        avg_yield=180.0,
        max_yield=210.0,
        min_yield=160.0,
        log={
            "2025-05-01": {
                "harvest_yield": 190.5,
                "remain_percentage": 85.0
            }
        },
        subscription={
            "userID": "user_test_001",
            "amount": 25.0,
            "start_date": "2025-05-01"
        }
    )

    # 4. 리뷰 등록
    Review_Field(
        field_id="field_test_001",
        user_id="user_test_001",
        content="상추가 정말 신선하고 맛있었습니다. 재구매 의사 있어요!",
        date="2025-05-09",
        rating=5
    )

        # 1. 사용자 등록
    User(
        user_id="user_test_002",
        name="이리뷰",
        phoneNum="010-2345-6789",
        address="부산광역시 리뷰구 평가동 22-1",
        password="reviewpass456",
        subscription_fields={
            "field_test_002": {
                "start_date": "2025-04-15"
            }
        }
    )

    # 2. 작물 등록
    Crops(
        crop_id="crop_sweetpotato",
        name="고구마",
        crop_price=2400,
        description="달콤한 밤고구마입니다.",
        image_url="https://example.com/sweetpotato.jpg"
    )

    # 3. 밭 등록
    Farm(
        field_id="field_test_002",
        farmer_id="farmer_placeholder",  # 농부 정보 생략
        crops="고구마",
        avg_rating=4,
        coast=2600.0,
        avg_yield=160.0,
        max_yield=220.0,
        min_yield=140.0,
        log={
            "2025-04-15": {
                "harvest_yield": 175.3,
                "remain_percentage": 88.0
            }
        },
        subscription={
            "userID": "user_test_002",
            "amount": 30.0,
            "start_date": "2025-04-15"
        }
    )

    # 4. 리뷰 등록
    Review_Field(
        field_id="field_test_002",
        user_id="user_test_002",
        content="고구마가 달고 부드러워서 정말 맛있었어요. 아이들도 좋아해요!",
        date="2025-04-20",
        rating=4
    )
