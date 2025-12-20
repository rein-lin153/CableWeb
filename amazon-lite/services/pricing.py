# amazon-lite/services/pricing.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import models

async def sync_prices_with_copper(db: AsyncSession, current_copper_price_per_ton: float):
    """
    基础服务：根据当前铜价 (元/吨)，更新【普通产品表】(ProductVariant) 的售价。
    注意：这是给前台商城用的，不是给后台成本核算模块用的。
    """
    # 1. 换算成 元/kg
    copper_price_kg = current_copper_price_per_ton / 1000.0
    
    # 2. 找出所有“启用了自动定价”的产品 (即铜重 > 0 的)
    stmt = select(models.ProductVariant).filter(models.ProductVariant.copper_weight > 0)
    result = await db.execute(stmt)
    variants = result.scalars().all()
    
    updated_count = 0
    
    for v in variants:
        # 公式：新价格 = (铜单价 * 铜重) + 加工费
        new_price = (copper_price_kg * v.copper_weight) + v.process_cost
        
        # 精度控制
        if abs(v.price - new_price) > 0.01:
            v.price = round(new_price, 2)
            updated_count += 1
            
    await db.commit()
    return updated_count