from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any, List
from datetime import datetime
from app.models.schemas import ReviewAnalysis, ReviewBase, SentimentEnum, ReviewStatistics, ReviewResponse
from app.services.firebase import firebase_service
from app.services.ai import ai_service

router = APIRouter()

@router.get("/reviews", 
         summary="모든 리뷰 가져오기",
         description="모든 농장의 리뷰 데이터를 가져옵니다.")
async def get_reviews():
    try:
        reviews_data = firebase_service.get_reviews()
        
        if not reviews_data:
            return {
                "status": "success",
                "data": []
            }
        
        reviews_list = []
        for field_id, field_data in reviews_data.items():
            if 'reviews' in field_data:
                field_reviews = []
                for review in field_data['reviews']:
                    field_reviews.append({
                        "review_id": f"{field_id}_{review.get('user_id')}",
                        "rating": float(review.get("rating", 0)),
                        "content": review.get("content", ""),
                        "date": review.get("date", datetime.now().strftime("%Y-%m-%d"))
                    })
                reviews_list.append({
                    "field_id": field_id,
                    "reviews": field_reviews
                })
        
        return {
            "status": "success",
            "data": reviews_list
        }
        
    except Exception as e:
        print(f"Error in get_reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviews/{field_id}", 
         summary="특정 농장의 리뷰 가져오기",
         description="특정 농장의 모든 리뷰를 가져옵니다.")
async def get_field_reviews(
    field_id: str = Path(..., description="리뷰를 가져올 농장의 ID")
):
    try:
        reviews_data = firebase_service.get_reviews(field_id)
        
        if not reviews_data:
            return {
                "status": "success",
                "data": {
                    "field_id": field_id,
                    "reviews": []
                }
            }
        
        field_reviews = []
        for review in reviews_data:
            field_reviews.append({
                "review_id": f"{field_id}_{review.get('user_id')}",
                "rating": float(review.get("rating", 0)),
                "content": review.get("content", ""),
                "date": review.get("date", datetime.now().strftime("%Y-%m-%d"))
            })
        
        return {
            "status": "success",
            "data": {
                "field_id": field_id,
                "reviews": field_reviews
            }
        }
        
    except Exception as e:
        print(f"Error in get_field_reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-review/field-id")
async def get_current_review_field_id():
    """현재 선택된 리뷰의 field_id를 반환합니다."""
    try:
        if not firebase_service.is_connected():
            raise HTTPException(status_code=503, detail="Firebase connection not available")
            
        # Get the current review's field_id from Firebase
        current_review = firebase_service.get_current_review()
        
        if not current_review or 'field_id' not in current_review:
            raise HTTPException(status_code=404, detail="현재 선택된 리뷰가 없습니다.")
        
        return {
            "status": "success",
            "field_id": current_review['field_id']
        }
        
    except Exception as e:
        print(f"Error in get_current_review_field_id: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{field_id}", 
         response_model=ReviewAnalysis,
         summary="농장 리뷰 분석",
         description="특정 농장의 모든 리뷰를 분석하여 요약, 감성 분석, 통계 정보를 제공합니다.")
async def analyze_field_reviews(
    field_id: str = Path(..., description="분석할 농장의 ID")
):
    try:
        if not firebase_service.is_connected():
            raise HTTPException(status_code=503, detail="Firebase connection not available")
            
        # Get reviews for specific field
        reviews_data = firebase_service.get_field_reviews(field_id)
        
        if not reviews_data:
            return ReviewAnalysis(
                summary="아직 리뷰가 없습니다.",
                average_rating=0,
                total_reviews=0,
                sentiment=SentimentEnum.neutral,
                recent_reviews=[],
                statistics=ReviewStatistics(
                    positive_ratio=0,
                    negative_ratio=0,
                    neutral_ratio=0
                )
            )
        
        # Convert reviews data to list format
        reviews = []
        for review in reviews_data:
            reviews.append({
                "review_id": f"{field_id}_{review.get('user_id')}",
                "rating": float(review.get("rating", 0)),
                "content": review.get("content", ""),
                "date": review.get("date", datetime.now().strftime("%Y-%m-%d"))
            })
        
        if not reviews:
            return ReviewAnalysis(
                summary="아직 리뷰가 없습니다.",
                average_rating=0,
                total_reviews=0,
                sentiment=SentimentEnum.neutral,
                recent_reviews=[],
                statistics=ReviewStatistics(
                    positive_ratio=0,
                    negative_ratio=0,
                    neutral_ratio=0
                )
            )
        
        # 리뷰 텍스트 결합
        all_comments = " ".join([review["content"] for review in reviews])
        
        # AI 모델을 사용하여 리뷰 요약 생성
        summary_text = ai_service.summarize_text(all_comments)
        
        # 평균 평점 계산
        avg_rating = sum(review["rating"] for review in reviews) / len(reviews)
        
        # AI 모델을 사용하여 감성 분석
        sentiment = ai_service.analyze_reviews_sentiment(reviews)
        
        # 최근 리뷰 3개 (날짜 기준 정렬)
        sorted_reviews = sorted(reviews, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
        recent_reviews = sorted_reviews[:3]
        
        # 각 리뷰의 감성 분석
        sentiments = [ai_service.analyze_sentiment(review["content"], review["rating"]) for review in reviews]
        positive_reviews = sentiments.count(SentimentEnum.positive)
        negative_reviews = sentiments.count(SentimentEnum.negative)
        neutral_reviews = sentiments.count(SentimentEnum.neutral)
        
        return ReviewAnalysis(
            summary=summary_text,
            average_rating=round(avg_rating, 2),
            total_reviews=len(reviews),
            sentiment=sentiment,
            recent_reviews=recent_reviews,
            statistics=ReviewStatistics(
                positive_ratio=round(positive_reviews / len(reviews) * 100, 1),
                negative_ratio=round(negative_reviews / len(reviews) * 100, 1),
                neutral_ratio=round(neutral_reviews / len(reviews) * 100, 1)
            )
        )
    except Exception as e:
        print(f"Error in analyze_field_reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 