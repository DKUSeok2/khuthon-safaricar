import tkinter as tk
from data_factory import data_factory
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

class FarmApp(tk.Tk):
    # 생성자
    def __init__(self):
        super().__init__()
        self.current_user_id = "user_test_001"  # 나중에 로그인 기능이 생기면 여기에 할당
        self.df = data_factory()
        
        self.title("나의 농장 앱")
        self.geometry("360x640")
        self.configure(bg="white")

        self.user_info = {"name": "", "phone": "", "address": ""}
        self.farm_data = self.get_subscribed_farms()
    
        self.active_frame = None
        self.create_bottom_menu()
        self.switch_frame("farm")
        
    # 메뉴생성
    def create_bottom_menu(self):
        self.menu_frame = tk.Frame(self, bg="white", height=50)
        self.menu_frame.pack(side="bottom", fill="x")

        self.farm_btn = tk.Button(self.menu_frame, text="나의농장", command=lambda: self.switch_frame("farm"))
        self.search_btn = tk.Button(self.menu_frame, text="검색", command=lambda: self.switch_frame("search"))
        self.profile_btn = tk.Button(self.menu_frame, text="나의정보", command=lambda: self.switch_frame("profile"))

        self.farm_btn.pack(side="left", expand=True, fill="x")
        self.search_btn.pack(side="left", expand=True, fill="x")
        self.profile_btn.pack(side="left", expand=True, fill="x")
    # 메뉴변경
    def switch_frame(self, name):
        if self.active_frame:   # 현재 화면 삭제
            self.active_frame.destroy()

        if name == "farm":      # 새로운 화면 띄우기
            #user_info = self.get_users_information()[self.current_user_id]
            self.active_frame = self.create_farm_page()
        elif name == "search":
            self.active_frame = self.create_label_frame("작물을 검색하세요.")
        elif name == "profile":
            self.active_frame = self.create_profile_form()

        self.active_frame.pack(expand=True, fill="both")

    def create_label_frame(self, text):
        frame = tk.Frame(self, bg="#f5f5f5")
        label = tk.Label(frame, text=text, font=("Helvetica", 16))
        label.pack(pady=50)
        return frame

    # (1) 나의 농장 페이지
    def create_farm_page(self):
        user_info = self.df.get_user_info(self.current_user_id)
        frame = tk.Frame(self, bg="white")
        # 1. 사용자 이름 출력
        user_name = user_info["name"]
        title = tk.Label(frame, text=f"{user_name}님의 구독 농장", font=("Helvetica", 16, "bold"), bg="white")
        title.pack(pady=10)
        
        # 2. 개인정보 보기버튼
        view_info_btn = tk.Button(frame, text="개인정보 보기", command=lambda: self.show_user_info(user_info), bg="lightblue")
        view_info_btn.pack(pady=(0, 10))

        # 3. 구독한 농장
        subscribed_farms = user_info["subscription_fields"].keys()

        canvas = tk.Canvas(frame, bg="white", highlightthickness=0)
        scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        list_frame = tk.Frame(canvas, bg="white")
        
        for farm_id in subscribed_farms:
            farm_data = self.df.get_subscription_farm(farm_id)
            self.create_farm_card(list_frame, farm_data)

        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"), yscrollcommand=scroll_y.set)

        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        return frame
    # - 개인정보 팝업창
    def show_user_info(self, user_info):
        info_window = tk.Toplevel(self)
        info_window.title("개인정보")
        info_window.geometry("300x200")
        info_window.configure(bg="white")

        tk.Label(info_window, text="📱 전화번호", font=("Helvetica", 12, "bold"), bg="white").pack(pady=(20, 5))
        tk.Label(info_window, text=user_info["phoneNum"], bg="white", font=("Helvetica", 12)).pack()

        tk.Label(info_window, text="🏠 주소", font=("Helvetica", 12, "bold"), bg="white").pack(pady=(20, 5))
        tk.Label(info_window, text=user_info["address"], bg="white", font=("Helvetica", 12), wraplength=250, justify="center").pack()

    # - 카드 생성
    def create_farm_card(self, parent, farm):
        card = tk.Frame(parent, bd=1, relief="ridge", bg="white")
        card.pack(padx=10, pady=10, fill="x")

        # 이미지 불러오기 (없으면 회색배경)
        try:
            img = Image.open(farm["image_path"])
        except:
            img = Image.new("RGB", (300, 180), color="#cccccc")
        img = img.resize((320, 180))
        photo = ImageTk.PhotoImage(img)

        image_label = tk.Label(card, image=photo)
        image_label.image = photo
        image_label.pack()

        image_label.bind("<Button-1>", lambda e, farm=farm: self.show_farm_detail(farm))

        overlay = tk.Label(
            card,
            text=f"{farm['name']} | {farm['amount']}개 | {farm['price']}원",
            bg="black", fg="white",
            font=("Helvetica", 12),
            anchor="w"
        )
        overlay.place(relx=0, rely=1.0, anchor="sw", relwidth=1)
    # - 클릭 시, 화면
    def show_farm_detail(self, farm):
        detail_window = tk.Toplevel(self)
        detail_window.title(f"{farm['name']} 정보")
        detail_window.geometry("360x500")
        detail_window.configure(bg="white")
        # 농장이름
        tk.Label(detail_window, text=farm["name"], font=("Helvetica", 16, "bold"), bg="white").pack(pady=10)
        # # 구독유무
        # subscribed_var = tk.BooleanVar(value=farm.get("subscribed", False))
        # sub_check = tk.Checkbutton(detail_window, text="구독 중", variable=subscribed_var, bg="white")
        # sub_check.pack()
        # 가격
        tk.Label(detail_window, text=f"가격: {farm['price']}원", font=("Helvetica", 12), bg="white").pack(pady=5)
        # 설명
        description = farm.get("description", "이 농장은 신선한 작물을 제공합니다.")
        tk.Label(detail_window, text="설명", font=("Helvetica", 12, "bold"), bg="white", anchor="w").pack(fill="x", padx=20, pady=(10,0))
        tk.Label(detail_window, text=description, wraplength=300, justify="left", bg="white").pack(padx=20, pady=5)
        # 리뷰 및 평점
        tk.Label(detail_window, text="리뷰 및 평점", font=("Helvetica", 12, "bold"), bg="white", anchor="w").pack(fill="x", padx=20, pady=(10,0))
        review_frame = tk.Frame(detail_window, bg="white")
        review_frame.pack(fill="both", padx=20)
        
        def render_reviews():
            for widget in review_frame.winfo_children():
                widget.destroy()
            for review in farm.get("reviews", []):
                tk.Label(review_frame, text=f"{review['user']} ({review['rating']}점): {review['text']}", wraplength=300,
                        justify="left", bg="white", anchor="w").pack(anchor="w", pady=2)
        render_reviews()

        # 리뷰 작성
        tk.Label(detail_window, text="리뷰 작성", font=("Helvetica", 12, "bold"), bg="white", anchor="w").pack(fill="x", padx=20, pady=(10,0))
        review_entry = tk.Entry(detail_window)
        review_entry.pack(padx=20, fill="x", pady=5)

        # 별점 선택
        tk.Label(detail_window, text="별점 선택 (1~5)", bg="white", anchor="w").pack(fill="x", padx=20)
        rating_var = tk.StringVar(value="5")  # 기본값 5점
        rating_combo = ttk.Combobox(detail_window, textvariable=rating_var, values=["1", "2", "3", "4", "5"], state="readonly")
        rating_combo.pack(padx=20, fill="x", pady=(0, 10))
        
        def submit_review():
            review_text = review_entry.get().strip()
            rating = rating_var.get()
            
            if review_text:
                new_review = {"user": "나", "rating": 5, "text": review_text}
                farm.setdefault("reviews", []).append({
                    "user": "나",
                    "rating": int(rating),
                    "text": review_text
                })
                review_entry.delete(0, tk.END)
                rating_var.set("5")  # 다시 기본값으로
                render_reviews()
                messagebox.showinfo("리뷰 제출", "리뷰가 등록되었습니다!")
            else:
                messagebox.showwarning("입력 오류", "리뷰 내용을 입력해주세요.")

        tk.Button(detail_window, text="리뷰 제출", command=submit_review, bg="green", fg="white").pack(pady=10)
    # - 데이터셋
    def get_subscribed_farms(self):
        return [
            {
                "name": "당근농장",
                "amount": 100,  #
                "price": 1400,  
                "image_path": "farm1.jpg",
                "description": "유기농 당근을 재배하는 농장입니다. 매일 아침 수확하여 신선함을 자랑합니다.",
                "subscribed": True, #
                "reviews": [    #
                    {"user": "김철수", "rating": 5, "text": "정말 신선하고 맛있어요!"},
                    {"user": "박영희", "rating": 4, "text": "배송도 빠르고 만족합니다."}
                ]
            },
            {
                "name": "배추농장",
                "amount": 150,
                "price": 2000,
                "image_path": "farm2.jpg",
                "description": "김장철 맞춤 배추를 생산하는 농장입니다. 무농약 인증을 받았습니다.",
                "subscribed": True,
                "reviews": [
                    {"user": "이민수", "rating": 5, "text": "배추가 정말 신선하고 알이 꽉 찼어요."}
                ]
            }
        ]
    def get_users_information(self):
        return {
            "userA": {
                "name": "김하늘",
                "phoneNum": "010-1234-5678",
                "address": "서울특별시 마포구",
                "password": "hashed_pw_1",
                "Subscription_Field_id": {
                    "당근농장": "2024-03-15",
                    "배추농장": "2024-04-10"
                }
            },
            "userB": {
                "name": "이준호",
                "phoneNum": "010-9876-5432",
                "address": "부산광역시 해운대구",
                "password": "hashed_pw_2",
                "Subscription_Field_id": {
                    "토마토농장": "2024-05-01"
                }
            },
            "userC": {
                "name": "최유진",
                "phoneNum": "010-5678-1234",
                "address": "대전광역시 서구",
                "password": "hashed_pw_3",
                "Subscription_Field_id": {
                    "당근농장": "2024-02-28",
                    "고구마농장": "2024-03-20",
                    "배추농장": "2024-04-05"
                }
            }
        }
    def get_fields_information(self):
        return {
            "당근농장": {
                "FarmerID": "farmer01",
                "Crops": "당근",
                "Avg_rating": 4.6,
                "Coast": 1400.0,
                "harvest_yield": {
                    "Avg_harvest_yield": 95.3,
                    "Max_harvest_yield": 120.0,
                    "Min_harvest_yield": 80.0,
                },
                "Log": {
                    "2024-03-01": 100.5,
                    "2024-03-15": 92.0
                },
                "Remain_Percentage": 82.5,
                "Subscription": [
                    {"Amount": 30.0, "userID": "userA", "start_date": "2024-03-15"},
                    {"Amount": 25.0, "userID": "userC", "start_date": "2024-02-28"}
                ]
            },
            "배추농장": {
                "FarmerID": "farmer02",
                "Crops": "배추",
                "Avg_rating": 4.9,
                "Coast": 2000.0,
                "harvest_yield": {
                    "Avg_harvest_yield": 102.7,
                    "Max_harvest_yield": 130.0,
                    "Min_harvest_yield": 85.0,
                },
                "Log": {
                    "2024-03-10": 105.0,
                    "2024-04-05": 95.0
                },
                "Remain_Percentage": 76.0,
                "Subscription": [
                    {"Amount": 35.0, "userID": "userA", "start_date": "2024-04-10"},
                    {"Amount": 20.0, "userID": "userC", "start_date": "2024-04-05"}
                ]
            },
            "토마토농장": {
                "FarmerID": "farmer03",
                "Crops": "토마토",
                "Avg_rating": 4.2,
                "Coast": 1100.0,
                "harvest_yield": {
                    "Avg_harvest_yield": 87.0,
                    "Max_harvest_yield": 100.0,
                    "Min_harvest_yield": 70.0,
                },
                "Log": {
                    "2024-04-01": 88.5
                },
                "Remain_Percentage": 68.0,
                "Subscription": [
                    {"Amount": 50.0, "userID": "userB", "start_date": "2024-05-01"}
                ]
            },
            "고구마농장": {
                "FarmerID": "farmer04",
                "Crops": "고구마",
                "Avg_rating": 4.5,
                "Coast": 1700.0,
                "harvest_yield": {
                    "Avg_harvest_yield": 93.5,
                    "Max_harvest_yield": 110.0,
                    "Min_harvest_yield": 78.0,
                },
                "Log": {
                    "2024-03-01": 97.0,
                    "2024-03-20": 89.0
                },
                "Remain_Percentage": 59.0,
                "Subscription": [
                    {"Amount": 40.0, "userID": "userC", "start_date": "2024-03-20"}
                ]
            }
        }
    def get_crops_information(self):
        return {
            "당근": {
                "Crop_price": 1400,
                "Description": "달콤하고 아삭한 유기농 당근입니다. 샐러드와 주스로 활용하기 좋아요.",
                "Image_url": "carrot.jpg",
                "Name": "당근"
            },
            "배추": {
                "Crop_price": 2000,
                "Description": "김장철 필수! 속이 꽉 찬 무농약 배추입니다.",
                "Image_url": "cabbage.jpg",
                "Name": "배추"
            },
            "토마토": {
                "Crop_price": 1100,
                "Description": "신선한 토마토로 샐러드와 파스타를 더욱 풍성하게!",
                "Image_url": "tomato.jpg",
                "Name": "토마토"
            },
            "고구마": {
                "Crop_price": 1700,
                "Description": "쪄먹어도 구워먹어도 맛있는 달콤한 고구마!",
                "Image_url": "sweet_potato.jpg",
                "Name": "고구마"
            }
        }


    # (3) 회원가입 페이지
    def create_profile_form(self):
        frame = tk.Frame(self, bg="white", padx=20, pady=20)

        tk.Label(frame, text="이름", anchor="w").pack(fill="x")
        self.name_entry = tk.Entry(frame)
        self.name_entry.insert(0, self.user_info["name"])
        self.name_entry.pack(fill="x", pady=5)

        tk.Label(frame, text="전화번호", anchor="w").pack(fill="x")
        self.phone_entry = tk.Entry(frame)
        self.phone_entry.insert(0, self.user_info["phone"])
        self.phone_entry.pack(fill="x", pady=5)

        tk.Label(frame, text="주소", anchor="w").pack(fill="x")
        self.address_entry = tk.Entry(frame)
        self.address_entry.insert(0, self.user_info["address"])
        self.address_entry.pack(fill="x", pady=5)

        self.save_btn = tk.Button(frame, text="저장하기", command=self.save_user_info, bg="orange", fg="white")
        self.save_btn.pack(pady=10)

        return frame

    def save_user_info(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_entry.get()

        self.user_info["name"] = name
        self.user_info["phone"] = phone
        self.user_info["address"] = address

        # Entry & 버튼 비활성화
        self.name_entry.config(state="disabled")
        self.phone_entry.config(state="disabled")
        self.address_entry.config(state="disabled")
        self.save_btn.pack_forget()
        
        messagebox.showinfo("저장 완료", "사용자 정보가 저장되었습니다!")

if __name__ == "__main__":
    app = FarmApp()
    app.mainloop()