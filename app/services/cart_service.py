import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.cart import Cart, CartItem
from app.schemas.cart import CartCreate, CartItemCreate, CartItemUpdate


class CartService:

    @staticmethod
    async def get_cart(db: AsyncSession, cart_id: uuid.UUID) -> Cart:
        result = await db.execute(
            select(Cart).where(Cart.id == cart_id).options(selectinload(Cart.items))
        )
        cart = result.scalar_one_or_none()
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return cart

    @staticmethod
    async def create_cart(db: AsyncSession, cart_data: CartCreate) -> Cart:
        cart = Cart(user_id=cart_data.user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        return cart

    @staticmethod
    async def add_item(db: AsyncSession, cart_id: uuid.UUID, item_data: CartItemCreate) -> CartItem:
        cart = await CartService.get_cart(db, cart_id)
        
        result = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == item_data.product_id
            )
        )
        existing_item = result.scalar_one_or_none()

        if existing_item:
            existing_item.quantity += item_data.quantity
            existing_item.unit_price = item_data.unit_price
            await db.commit()
            await db.refresh(existing_item)
            return existing_item

        new_item = CartItem(
            cart_id=cart_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price
        )
        db.add(new_item)
        cart.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(new_item)
        return new_item

    @staticmethod
    async def update_item(db: AsyncSession, cart_id: uuid.UUID, item_id: uuid.UUID, item_data: CartItemUpdate) -> CartItem:
        result = await db.execute(
            select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        item.quantity = item_data.quantity
        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def remove_item(db: AsyncSession, cart_id: uuid.UUID, item_id: uuid.UUID) -> None:
        result = await db.execute(
            select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

        await db.delete(item)
        await db.commit()

    @staticmethod
    async def clear_cart(db: AsyncSession, cart_id: uuid.UUID) -> None:
        cart = await CartService.get_cart(db, cart_id)
        cart.status = "abandoned"
        for item in cart.items:
            await db.delete(item)
        await db.commit()

    @staticmethod
    async def merge_carts(db: AsyncSession, target_cart_id: uuid.UUID, source_cart_id: uuid.UUID) -> Cart:
        target_cart = await CartService.get_cart(db, target_cart_id)
        source_cart = await CartService.get_cart(db, source_cart_id)

        for source_item in source_cart.items:
            existing = next(
                (i for i in target_cart.items if i.product_id == source_item.product_id), None
            )
            if existing:
                existing.quantity += source_item.quantity
            else:
                new_item = CartItem(
                    cart_id=target_cart_id,
                    product_id=source_item.product_id,
                    quantity=source_item.quantity,
                    unit_price=source_item.unit_price
                )
                db.add(new_item)

        source_cart.status = "merged"
        target_cart.updated_at = datetime.utcnow()
        await db.commit()
        return await CartService.get_cart(db, target_cart_id)

    @staticmethod
    def calculate_total(cart: Cart) -> Decimal:
        return sum(item.quantity * item.unit_price for item in cart.items)
