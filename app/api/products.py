from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import os
import aiofiles
from datetime import datetime
from app.services.firebase import firebase_service

router = APIRouter()

# 이미지를 저장할 디렉토리 설정
UPLOAD_DIRECTORY = "uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)
    # 디렉토리 권한 설정
    os.chmod(UPLOAD_DIRECTORY, 0o777)

@router.post("/products", 
          summary="상품 등록",
          description="새로운 상품을 등록합니다.")
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    quantity: float = Form(...),
    location: str = Form(...),
    harvestDate: str = Form(...),
    description: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    try:
        print("Received product data:", {
            "name": name,
            "price": price,
            "quantity": quantity,
            "location": location,
            "harvestDate": harvestDate,
            "description": description,
            "has_image": image is not None
        })

        # 이미지 저장
        image_url = None
        if image:
            try:
                # 파일 확장자 검증
                file_extension = os.path.splitext(image.filename)[1].lower()
                if file_extension not in ['.jpg', '.jpeg', '.png', '.gif']:
                    raise HTTPException(status_code=400, detail="지원하지 않는 이미지 형식입니다.")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}{file_extension}"
                file_path = os.path.join(UPLOAD_DIRECTORY, filename)
                
                # 이미지 파일 저장
                async with aiofiles.open(file_path, "wb") as buffer:
                    content = await image.read()
                    await buffer.write(content)
                
                image_url = f"/uploads/{filename}"
                print(f"Image saved successfully at: {file_path}")
            except Exception as e:
                print(f"Error saving image: {str(e)}")
                raise HTTPException(status_code=500, detail=f"이미지 저장 중 오류가 발생했습니다: {str(e)}")

        # Firebase에 상품 데이터 저장
        product_data = {
            "name": name,
            "price": float(price),
            "quantity": float(quantity),
            "location": location,
            "harvestDate": harvestDate,
            "description": description,
            "image_url": image_url,
            "created_at": datetime.now().isoformat()
        }

        if not firebase_service.save_product(product_data):
            print("Warning - Firebase save failed")
        
        return {
            "status": "success",
            "message": "상품이 성공적으로 등록되었습니다.",
            "data": product_data
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error in create_product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"상품 등록 중 오류가 발생했습니다: {str(e)}")

@router.get("/products", 
         summary="상품 목록 조회",
         description="등록된 모든 상품을 조회합니다.")
async def get_products():
    try:
        crops_data = firebase_service.get_products()
        
        if not crops_data:
            return {
                "status": "success",
                "data": []
            }
        
        products_list = []
        for crop_id, crop_data in crops_data.items():
            product = {
                "id": crop_id,
                "name": crop_data.get("name", ""),
                "price": float(crop_data.get("crop_price", 0)),
                "description": crop_data.get("description", ""),
                "image_url": crop_data.get("image_url", None)
            }
            products_list.append(product)
        
        return {
            "status": "success",
            "data": products_list
        }
        
    except Exception as e:
        print(f"Error in get_products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 