from firebase_client1 import firebase_client1
client = None

# 1. 사용자 저장
def register_user(user_id, name, phoneNum, address):
    client.create_or_update(f"users/{user_id}", {
        "name": name, # 사용자 이름
        "phoneNum": phoneNum, #사용자 전화번호
        "address": address #작물을 전달 받을 주소
    })

# 2. 작물 정보 저장
def add_crop(crop_id, name, description, image_url, crop_price):
    client.create_or_update(f"crops/{crop_id}", {
        "name": name, #작물 이름
        "description": description, #작물에 대한 설명명
        "image_url": image_url, #UI에서 보일 작물 이미지
        "crop_price": crop_price #판매 및 구매를 위한 작물 가격
    })

# 3. 구독 요청 저장
def subscribe_crop(sub_id, user_id, crop_id, amount, frequency, start_date):
    client.create_or_update(f"subscriptions/{sub_id}", {
        "user_id": user_id, #유저 ID(기본키)
        "crop_id": crop_id, #농작물 ID
        "amount": amount, #요청할 작물의 양
        "frequency": frequency, #구독 횟수(달 단위)
        "start_date": start_date #구독 시작 일일
    })


# 4. 생육 정보 저장
def record_growth(crop_id, date, status, image_url):
    client.create_or_update(f"growth_logs/{crop_id}/{date}", {
        "status": status, #작물 상태(시들, 파릇, 병듦 etc.)
        "image_url": image_url #생육 정보를 보여주는 이미지(얼마나 잘 자라고 있는가)
    })


# 5. 리뷰 저장
def submit_review(review_id, user_id, crop_id, rating, content, date):
    client.create_or_update(f"reviews/{review_id}", {
        "user_id": user_id, #유저 ID(기본키)
        "crop_id": crop_id, #농작물 ID
        "rating": rating, #농작물에 대한 평점(범위 : 1~5)
        "content": content, #리뷰 내용
        "date": date #리뷰 작성일일
    })


if __name__ == "__main__": #기본적으로 
    client = firebase_client1(
        "khuton-firebase-adminsdk-fbsvc-896da2cdf0.json",
        "https://khuton-default-rtdb.firebaseio.com/"
    )

    client.create_or_update("notes/note1", {"message": "updating..."})
    #print("전체 루트 데이터:", client.read()) -> 전체 데이터 출력 부분
    #print("노트 메시지:", client.read("notes/note1"))