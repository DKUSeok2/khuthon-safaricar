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
            self.create_farm_card(list_frame, farm_data, farm_id)

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
    def create_farm_card(self, parent, farm, farm_id):
        user = self.df.get_subscription_user_info(farm_id, self.current_user_id)
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
            text=f"{farm['crops']} | {user['amount']}개 | {farm['coast']}원",
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