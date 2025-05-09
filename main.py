from firebase_client1 import firebase_client1

# 1. 사용자 저장
def register_user(user_id, name, phoneNum, address):
    client.create_or_update(f"users/{user_id}", {
        "name": name,
        "phoneNum": phoneNum,
        "address": address
    })

# 2. 작물 정보 저장
def add_crop(crop_id, name, description, image_url, crop_price):
    client.create_or_update(f"crops/{crop_id}", {
        "name": name,
        "description": description,
        "image_url": image_url,
        "crop_price": crop_price
    })

# 3. 구독 요청 저장
def subscribe_crop(sub_id, user_id, crop_id, amount, frequency, start_date):
    client.create_or_update(f"subscriptions/{sub_id}", {
        "user_id": user_id,
        "crop_id": crop_id,
        "amount": amount,
        "frequency": frequency,
        "start_date": start_date    
    })


# 4. 생육 정보 저장
def record_growth(crop_id, date, status, image_url):
    client.create_or_update(f"growth_logs/{crop_id}/{date}", {
        "status": status,
        "image_url": image_url
    })


# 5. 리뷰 저장
def submit_review(review_id, user_id, crop_id, rating, content, date):
    client.create_or_update(f"reviews/{review_id}", {
        "user_id": user_id,
        "crop_id": crop_id,
        "rating": rating,
        "content": content,
        "date": date
    })


if __name__ == "__main__":
    client = firebase_client1(
        "khuton-firebase-adminsdk-fbsvc-896da2cdf0.json",
        "https://khuton-default-rtdb.firebaseio.com/"
    )

    client.create_or_update("notes/note1", {"message": "updating..."})
    #print("전체 루트 데이터:", client.read()) -> 전체 데이터 출력 부분
    #print("노트 메시지:", client.read("notes/note1"))

    # 1. 사용자 등록 테스트
    register_user("user001", "홍길동", "010-1234-5678", "서울시 강남구")
    print("▶ 사용자 정보:", client.read("users/user001"))

    # 2. 작물 등록 테스트
    add_crop("lettuce", "상추", "비타민이 풍부한 잎채소", "https://example.com/lettuce.jpg", 15000)
    print("▶ 작물 정보:", client.read("crops/lettuce"))

    # 3. 구독 요청 테스트
    subscribe_crop("sub001", "user001", "lettuce", 3, 7, "2024-05-08")
    print("▶ 구독 정보:", client.read("subscriptions/sub001"))

    # 4. 생육 정보 기록 테스트
    record_growth("lettuce", "2024-05-08", "4일차 생육 정상", "https://example.com/growth/day4.jpg")
    print("▶ 생육 정보:", client.read("growth_logs/lettuce/2024-05-08"))

    # 5. 사용자 리뷰 작성 테스트
    submit_review("review001", "user001", "lettuce", 5, "아주 신선하고 만족스러웠습니다!", "2024-05-10")
    print("▶ 리뷰 정보:", client.read("reviews/review001"))
