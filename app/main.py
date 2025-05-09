from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from datetime import datetime

from app.core.config import settings
from app.api import products, reviews
from app.services.firebase import firebase_service
from app.services.ai import ai_service
from app.models.schemas import ReviewAnalysis, ReviewStatistics, SentimentEnum

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for uploads
if not os.path.exists(settings.UPLOAD_DIRECTORY):
    os.makedirs(settings.UPLOAD_DIRECTORY)
    os.chmod(settings.UPLOAD_DIRECTORY, 0o777)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIRECTORY), name="uploads")

# Include routers
app.include_router(products.router, prefix=settings.API_V1_STR, tags=["products"])
app.include_router(reviews.router, prefix=settings.API_V1_STR, tags=["reviews"])

async def analyze_and_send_results(field_id: str):
    """리뷰 분석을 수행하고 결과를 Firebase에 저장"""
    try:
        print(f"📊 리뷰 데이터 가져오는 중 - field_id: {field_id}")
        # Get reviews for specific field
        reviews_data = firebase_service.get_field_reviews(field_id)
        
        if not reviews_data:
            print(f"⚠️ 리뷰 데이터 없음 - field_id: {field_id}")
            analysis_result = ReviewAnalysis(
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
        else:
            print(f"📝 리뷰 {len(reviews_data)}개 발견, 분석 시작...")
            # Convert reviews data to list format
            reviews = []
            for review in reviews_data:
                reviews.append({
                    "review_id": f"{field_id}_{review.get('user_id')}",
                    "rating": float(review.get("rating", 0)),
                    "content": review.get("content", ""),
                    "date": review.get("date", datetime.now().strftime("%Y-%m-%d"))
                })
            
            print("🤖 AI 모델로 리뷰 분석 중...")
            # 리뷰 텍스트 결합
            all_comments = " ".join([review["content"] for review in reviews])
            
            # AI 모델을 사용하여 리뷰 요약 생성
            print("1. 요약 생성 중...")
            summary_text = ai_service.summarize_text(all_comments)
            
            # 평균 평점 계산
            print("2. 평점 계산 중...")
            avg_rating = sum(review["rating"] for review in reviews) / len(reviews)
            
            # AI 모델을 사용하여 감성 분석
            print("3. 감성 분석 중...")
            sentiment = ai_service.analyze_reviews_sentiment(reviews)
            
            # 최근 리뷰 3개 (날짜 기준 정렬)
            print("4. 최근 리뷰 정렬 중...")
            sorted_reviews = sorted(reviews, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
            recent_reviews = sorted_reviews[:3]
            
            # 각 리뷰의 감성 분석
            print("5. 개별 리뷰 감성 분석 중...")
            sentiments = [ai_service.analyze_sentiment(review["content"], review["rating"]) for review in reviews]
            positive_reviews = sentiments.count(SentimentEnum.positive)
            negative_reviews = sentiments.count(SentimentEnum.negative)
            neutral_reviews = sentiments.count(SentimentEnum.neutral)
            
            print("6. 분석 결과 생성 중...")
            analysis_result = ReviewAnalysis(
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
        
        # 분석 결과를 Firebase에 저장
        print("💾 분석 결과 Firebase에 저장 중...")
        firebase_service.save_analysis_result(field_id, analysis_result.dict())
        
        # 분석이 완료되었음을 표시
        firebase_service.mark_analysis_complete(field_id)
        print(f"✅ 전체 분석 프로세스 완료 - field_id: {field_id}")
        
    except Exception as e:
        print(f"❌ Error in analyze_and_send_results: {str(e)}")
        # 에러 발생 시 Firebase에 에러 상태 저장
        firebase_service.save_analysis_error(field_id, str(e))

async def monitor_analysis_requests():
    """Firebase를 모니터링하여 분석 요청이 있는지 확인"""
    print("Starting Firebase monitoring for analysis requests...")
    while True:
        try:
            # Firebase에서 새로운 분석 요청 확인
            print("Checking for new analysis requests...")
            request = firebase_service.get_pending_analysis_request()
            
            if request and 'field_id' in request:
                field_id = request['field_id']
                print(f"✨ 새로운 분석 요청 감지! field_id: {field_id}")
                print(f"분석 시작 중...")
                
                # 분석 수행
                await analyze_and_send_results(field_id)
                print(f"✅ 분석 완료 - field_id: {field_id}")
            else:
                print("대기 중인 분석 요청 없음")
            
            # 1초 대기 후 다시 확인
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error in monitor_analysis_requests: {str(e)}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 Firebase 모니터링 시작"""
    print("🚀 Starting FastAPI server and initializing Firebase monitoring...")
    asyncio.create_task(monitor_analysis_requests())

@app.get("/")
async def root():
    return {
        "message": "리뷰 분석 AI 서버가 실행 중입니다",
        "firebase_status": "connected" if firebase_service.is_connected() else "disconnected",
        "ai_status": "ready" if ai_service.is_ready() else "not initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True) 