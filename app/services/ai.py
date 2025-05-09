from typing import Optional, Dict, List
from enum import Enum
import openai
import os

class SentimentEnum(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class AIService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """OpenAI 클라이언트 초기화 및 설정"""
        print("\n=== OpenAI 클라이언트 초기화 시작 ===")
        try:
            # OpenAI API 키 설정
            api_key = ""
            print(f"API 키 길이: {len(api_key)}")
            print(f"API 키 시작: {api_key[:10]}...")
            
            print("OpenAI 모듈 버전 확인중...")
            print(f"OpenAI 버전: {openai.__version__}")
            
            print("클라이언트 초기화 시도...")
            try:
                self.client = openai.OpenAI(api_key=api_key)
                print("클라이언트 객체 생성됨")
                
                # 테스트 API 호출
                print("테스트 API 호출 시도...")
                test_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                print("테스트 API 호출 성공!")
                print(f"응답: {test_response.choices[0].message.content}")
                
            except Exception as client_error:
                print(f"클라이언트 초기화 실패: {str(client_error)}")
                print(f"에러 타입: {type(client_error)}")
                self.client = None
                raise
                
        except Exception as e:
            print(f"전체 초기화 실패: {str(e)}")
            print(f"에러 타입: {type(e)}")
            self.client = None
        finally:
            print(f"클라이언트 상태: {'초기화됨' if self.client else '초기화 실패'}")
            print("=== OpenAI 클라이언트 초기화 종료 ===\n")
    
    def summarize_text(self, text: str) -> str:
        """여러 리뷰를 하나의 간단한 문장으로 요약"""
        if not self.client:
            return "OpenAI 클라이언트가 초기화되지 않았습니다."
            
        try:
            # 입력 텍스트가 너무 짧은 경우
            if len(text) < 10:
                return text
                
            # 텍스트 전처리
            text = text.replace('\n', ' ').strip()
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
                    Summarize multiple product reviews into a single, complete Korean sentence.

                    Summary Rules:
                    1. Write a complete sentence with subject and predicate in Korean
                    2. Must end with "~입니다." format
                    3. Prioritize including the most frequently mentioned key features
                    4. Mention duplicate content only once
                    5. Keep the summary within 50 characters
                    6. Use objective and clear expressions
                    7. Include the product's main features and advantages
                    8. MUST output in Korean language only
                    
                    Example:
                    Input: "신선하고 아삭해요. 포장도 깔끔하네요. 신선도가 좋아요. 크기도 적당해요."
                    Output: "신선하고 아삭한 식감과 깔끔한 포장, 적당한 크기로 만족도가 높은 상품입니다."
                    """},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            summary = response.choices[0].message.content.strip()
            
            # 요약이 너무 길면 자르기
            if len(summary) > 50:
                # 마지막 완전한 문장까지만 포함
                last_sentence = summary[:47].rsplit('.', 1)[0]
                summary = last_sentence + "..."
                
            # 문장 끝 처리
            if not summary.endswith('다.'):
                summary = summary.rstrip('.。') + "입니다."
                
            return summary
            
        except Exception as e:
            print(f"Summarization error: {str(e)}")
            # 에러 발생 시 첫 문장 반환
            sentences = text.split('.')
            if sentences:
                first_sentence = sentences[0].strip()
                if len(first_sentence) > 47:
                    return first_sentence[:47] + "..." + "입니다."
                return first_sentence + "입니다."
            return text[:47] + "..." + "입니다." if len(text) > 50 else text + "입니다."
    
    def analyze_sentiment(self, text: str, rating: Optional[float] = None) -> SentimentEnum:
        """텍스트와 평점을 기반으로 감성 분석"""
        try:
            # 평점이 있는 경우 우선 사용
            if rating is not None:
                if rating >= 4:
                    return SentimentEnum.positive
                elif rating <= 2:
                    return SentimentEnum.negative
                return SentimentEnum.neutral
            
            # 평점이 없는 경우 OpenAI로 분석
            if self.client:
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": """
                            다음 리뷰의 감성을 분석해서 positive, neutral, negative 중 하나로만 답하세요.
                            규칙:
                            - positive: 긍정적인 내용이 지배적인 경우
                            - negative: 부정적인 내용이 지배적인 경우
                            - neutral: 중립적이거나 긍정/부정이 비슷한 경우
                            답변은 positive, neutral, negative 중 하나로만 해주세요.
                            """},
                            {"role": "user", "content": text}
                        ],
                        temperature=0,
                        max_tokens=10
                    )
                    
                    result = response.choices[0].message.content.strip().lower()
                    if result in ['positive', 'negative', 'neutral']:
                        return SentimentEnum(result)
                        
                except Exception as e:
                    print(f"OpenAI sentiment analysis error: {str(e)}")
            
            # 기본값 반환
            return SentimentEnum.neutral
            
        except Exception as e:
            print(f"Sentiment analysis error: {str(e)}")
            return SentimentEnum.neutral
    
    def analyze_reviews_sentiment(self, reviews: List[Dict]) -> SentimentEnum:
        """여러 리뷰의 전체적인 감성 분석"""
        if not reviews:
            return SentimentEnum.neutral
            
        try:
            # 모든 리뷰 텍스트를 하나로 합치기
            all_reviews = " ".join([r.get('content', '') for r in reviews])
            avg_rating = sum(float(r.get('rating', 0)) for r in reviews) / len(reviews)
            
            # OpenAI로 전체 감성 분석
            if self.client:
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": f"""
                            다음은 전체 {len(reviews)}개의 리뷰이고, 평균 평점은 {avg_rating:.1f}점입니다.
                            이 리뷰들의 전체적인 감성을 분석해서 positive, neutral, negative 중 하나로만 답하세요.
                            규칙:
                            - positive: 긍정적인 리뷰가 더 많은 경우
                            - negative: 부정적인 리뷰가 더 많은 경우
                            - neutral: 중립적이거나 긍정/부정이 비슷한 경우
                            답변은 positive, neutral, negative 중 하나로만 해주세요.
                            """},
                            {"role": "user", "content": all_reviews}
                        ],
                        temperature=0,
                        max_tokens=10
                    )
                    
                    result = response.choices[0].message.content.strip().lower()
                    if result in ['positive', 'negative', 'neutral']:
                        return SentimentEnum(result)
                        
                except Exception as e:
                    print(f"OpenAI reviews analysis error: {str(e)}")
            
            # OpenAI 실패 시 평점 기반으로 판단
            if avg_rating >= 4:
                return SentimentEnum.positive
            elif avg_rating <= 2:
                return SentimentEnum.negative
            return SentimentEnum.neutral
            
        except Exception as e:
            print(f"Reviews analysis error: {str(e)}")
            return SentimentEnum.neutral
    
    def is_ready(self) -> bool:
        """서비스가 준비되었는지 확인"""
        return self.client is not None

# Create a singleton instance
ai_service = AIService() 