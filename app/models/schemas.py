from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: float
    location: str
    harvestDate: str
    description: str

class ReviewBase(BaseModel):
    review_id: str
    rating: float = Field(..., description="리뷰 평점 (1-5)", ge=1, le=5)
    content: str = Field(..., description="리뷰 내용")
    date: str = Field(..., description="리뷰 작성 날짜 (YYYY-MM-DD)")

class SentimentEnum(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class ReviewStatistics(BaseModel):
    positive_ratio: float = Field(..., description="긍정적인 리뷰 비율 (%)", ge=0, le=100)
    negative_ratio: float = Field(..., description="부정적인 리뷰 비율 (%)", ge=0, le=100)
    neutral_ratio: float = Field(..., description="중립적인 리뷰 비율 (%)", ge=0, le=100)

class ReviewAnalysis(BaseModel):
    summary: str = Field(..., description="모든 리뷰의 AI 생성 요약")
    average_rating: float = Field(..., description="평균 평점", ge=0, le=5)
    total_reviews: int = Field(..., description="전체 리뷰 수", ge=0)
    sentiment: SentimentEnum = Field(..., description="전반적인 감성 분석 결과")
    recent_reviews: List[ReviewBase] = Field(..., description="최근 리뷰 3개")
    statistics: ReviewStatistics = Field(..., description="리뷰 통계")

class ReviewResponse(BaseModel):
    field_id: str
    reviews: List[ReviewBase] 