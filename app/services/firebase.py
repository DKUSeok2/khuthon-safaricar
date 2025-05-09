from firebase_admin import credentials, initialize_app, db, get_app
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

class FirebaseService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            # Get absolute path to the credential file
            cred_path = os.path.join(os.getcwd(), "firebase-key.json")
            
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"Firebase credential file not found at {cred_path}")
            
            try:
                self.app = get_app()
                print("Firebase app already initialized")
            except ValueError:
                print("Initializing new Firebase app")
                cred = credentials.Certificate(cred_path)
                self.app = initialize_app(cred, {
                    'databaseURL': 'https://khuton-default-rtdb.firebaseio.com'
                })
                print("Firebase app initialized successfully")
            
            # Initialize Realtime Database reference
            self.db = db.reference('/')
            print("Firebase Realtime Database initialized")
            
        except Exception as e:
            print(f"Firebase initialization error: {str(e)}")
            self.app = None
            self.db = None
    
    def get_reviews(self, field_id: Optional[str] = None) -> Dict[str, Any]:
        """Get reviews for a specific field or all reviews if field_id is None"""
        if not self.db:
            return None
            
        if field_id:
            reviews_ref = self.db.child(f'review_fields/{field_id}/reviews')
        else:
            reviews_ref = self.db.child('review_fields')
        
        return reviews_ref.get()
    
    def get_products(self) -> Dict[str, Any]:
        """Get all products from the crops node"""
        if not self.db:
            return None
            
        crops_ref = self.db.child('crops')
        return crops_ref.get()
    
    def save_product(self, product_data: Dict[str, Any]) -> bool:
        """Save a new product to the crops node"""
        if not self.db:
            return False
            
        try:
            product_ref = self.db.child('crops').child(product_data['name'].replace(" ", "_"))
            product_ref.set(product_data)
            return True
        except Exception as e:
            print(f"Error saving product: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected"""
        return self.db is not None

    def get_current_review(self) -> Optional[Dict[str, Any]]:
        """현재 선택된 리뷰 정보를 가져옵니다."""
        if not self.is_connected():
            return None
        try:
            return self.db.child('current_review').get()
        except Exception as e:
            print(f"Error getting current review: {str(e)}")
            return None

    def get_field_reviews(self, field_id: str) -> List[Dict[str, Any]]:
        """특정 농장의 모든 리뷰를 가져옵니다."""
        if not self.is_connected():
            return []
        try:
            # review_fields/{field_id} 아래의 모든 사용자 리뷰를 가져옴
            reviews_ref = self.db.child(f'review_fields/{field_id}').get()
            if not reviews_ref:
                return []

            reviews = []
            # 각 user_id 아래의 리뷰 데이터를 수집
            for user_id, review_data in reviews_ref.items():
                if isinstance(review_data, dict):  # user_id 아래의 데이터인 경우만 처리
                    review = {
                        'user_id': user_id,
                        'content': review_data.get('content', ''),
                        'rating': float(review_data.get('rating', 0)),
                        'date': review_data.get('date', datetime.now().strftime("%Y-%m-%d"))
                    }
                    reviews.append(review)
            
            print(f"Found {len(reviews)} reviews for field_id: {field_id}")
            return reviews
            
        except Exception as e:
            print(f"Error getting field reviews: {str(e)}")
            return []

    def get_pending_analysis_request(self) -> Optional[Dict[str, Any]]:
        """Firebase에서 대기 중인 분석 요청(get)을 가져옵니다."""
        if not self.is_connected():
            return None
        try:
            # get 노드에서 field_id 확인
            request = self.db.child('get').get()
            if request:
                # field_id 가져오기
                field_id = request.get('field_id')
                if field_id:
                    # get 노드 데이터 삭제
                    self.db.child('get').delete()
                    return {'field_id': field_id}
            return None
        except Exception as e:
            print(f"Error getting analysis request: {str(e)}")
            return None

    def save_analysis_result(self, field_id: str, result: Dict[str, Any]) -> bool:
        """분석 결과를 Firebase의 send 노드에 저장합니다."""
        if not self.is_connected():
            return False
        try:
            # 감정 분석 결과를 한글로 변환
            sentiment_kr = {
                'positive': '긍정적',
                'negative': '부정적',
                'neutral': '중립적'
            }.get(result['sentiment'], '중립적')
            
            # 통계 기반으로 상세한 감정 분석 문장 생성
            stats = result['statistics']
            total_reviews = result['total_reviews']
            if total_reviews == 0:
                sentiment_summary = "아직 리뷰가 없습니다."
            else:
                if stats['positive_ratio'] > 60:
                    sentiment_summary = f"전체 {total_reviews}개 리뷰 중 매우 긍정적인 평가가 많습니다. (긍정적 리뷰 {stats['positive_ratio']}%)"
                elif stats['positive_ratio'] > stats['negative_ratio']:
                    sentiment_summary = f"전체 {total_reviews}개 리뷰 중 대체로 긍정적인 평가가 있습니다. (긍정적 리뷰 {stats['positive_ratio']}%)"
                elif stats['negative_ratio'] > 60:
                    sentiment_summary = f"전체 {total_reviews}개 리뷰 중 부정적인 평가가 많습니다. (부정적 리뷰 {stats['negative_ratio']}%)"
                elif stats['negative_ratio'] > stats['positive_ratio']:
                    sentiment_summary = f"전체 {total_reviews}개 리뷰 중 다소 부정적인 평가가 있습니다. (부정적 리뷰 {stats['negative_ratio']}%)"
                else:
                    sentiment_summary = f"전체 {total_reviews}개 리뷰 중 긍정적인 평가와 부정적인 평가가 비슷합니다. (중립적 리뷰 {stats['neutral_ratio']}%)"

            # send 노드에 결과 저장
            self.db.child('send').set({
                'content': {
                    '요약': result['summary'],  # AI가 생성한 리뷰 요약
                    '감성': sentiment_summary   # 감성 분석 결과 한글 요약
                }
            })
            return True
        except Exception as e:
            print(f"Error saving analysis result: {str(e)}")
            return False

    def mark_analysis_complete(self, field_id: str) -> bool:
        """분석 완료 후 처리"""
        # 이 구현에서는 별도의 처리가 필요 없음
        return True

    def save_analysis_error(self, field_id: str, error_message: str) -> bool:
        """분석 중 발생한 에러를 Firebase의 send 노드에 저장합니다."""
        if not self.is_connected():
            return False
        try:
            # send 노드에 에러 정보 저장
            self.db.child('send').set({
                'content': {
                    'error': error_message,
                    'status': 'error'
                }
            })
            return True
        except Exception as e:
            print(f"Error saving analysis error: {str(e)}")
            return False

# Create a singleton instance
firebase_service = FirebaseService() 