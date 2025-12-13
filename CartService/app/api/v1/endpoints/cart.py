import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.cart import (
    CartCreate, CartResponse, CartItemCreate, CartItemResponse,
    CartItemUpdate, CartMergeRequest
)
from app.services.cart_service import CartService

router = APIRouter(prefix="/carts", tags=["carts"])


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(cart_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """获取购物车详情（包含所有商品项和计算后的总价）"""
    cart = await CartService.get_cart(db, cart_id)
    total_price = CartService.calculate_total(cart)
    response = CartResponse.model_validate(cart)
    response.total_price = total_price
    return response


@router.post("", response_model=CartResponse, status_code=201)
async def create_cart(cart_data: CartCreate, db: AsyncSession = Depends(get_db)):
    """创建新购物车"""
    cart = await CartService.create_cart(db, cart_data)
    return CartResponse.model_validate(cart)


@router.post("/{cart_id}/items", response_model=CartItemResponse, status_code=201)
async def add_item(cart_id: uuid.UUID, item_data: CartItemCreate, db: AsyncSession = Depends(get_db)):
    """添加商品到购物车。如果商品已存在，则增加数量"""
    item = await CartService.add_item(db, cart_id, item_data)
    return CartItemResponse.model_validate(item)


@router.patch("/{cart_id}/items/{item_id}", response_model=CartItemResponse)
async def update_item(cart_id: uuid.UUID, item_id: uuid.UUID, item_data: CartItemUpdate, db: AsyncSession = Depends(get_db)):
    """更新商品数量"""
    item = await CartService.update_item(db, cart_id, item_id, item_data)
    return CartItemResponse.model_validate(item)


@router.delete("/{cart_id}/items/{item_id}", status_code=204)
async def remove_item(cart_id: uuid.UUID, item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """移除单个商品"""
    await CartService.remove_item(db, cart_id, item_id)


@router.delete("/{cart_id}", status_code=204)
async def clear_cart(cart_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """清空购物车"""
    await CartService.clear_cart(db, cart_id)


@router.post("/{cart_id}/merge", response_model=CartResponse)
async def merge_carts(cart_id: uuid.UUID, merge_data: CartMergeRequest, db: AsyncSession = Depends(get_db)):
    """用户登录后，将匿名购物车合并到用户购物车"""
    cart = await CartService.merge_carts(db, cart_id, merge_data.source_cart_id)
    total_price = CartService.calculate_total(cart)
    response = CartResponse.model_validate(cart)
    response.total_price = total_price
    return response
