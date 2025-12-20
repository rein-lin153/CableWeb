# amazon-lite/routers/admin_costs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import models, schemas
from database import get_db
from dependencies import get_current_active_superuser # 🟢 关键：引入超级管理员权限依赖
from typing import Optional
from sqlalchemy import select, desc
from services.pricing import sync_prices_with_copper # 如果需要复用

# 🟢 定义加工费常量 (RMB/吨)
PROCESS_FEES = {
    "BVR": 1000,
    "BV": 200,   # 单丝
    "RVV": 700   # 合股
}

# ⚠️ 整个 Router 强制要求管理员权限
router = APIRouter(
    prefix="/api/v1/admin/costs",
    tags=["Admin Cost Calculation"],
    dependencies=[Depends(get_current_active_superuser)] 
)


def calculate_copper_usd_price(market_cny: float, exchange_rate: float, category: str) -> float:
    """
    🟢 核心公式：将人民币含税铜价转换为美元原材料成本 ($/kg)
    公式: (当前人民币铜价 * 0.935 + 1500运费 + 加工费) / 汇率
    """
    # 1. 基础税后价 + 运费
    base_cny = (market_cny * 0.935) + 1500.0
    
    # 2. 叠加加工费 (根据分类)
    # 模糊匹配：如果 category 包含 'BVR' 则加 1000
    surcharge = 0
    cat_upper = category.upper() if category else ""
    
    if "BVR" in cat_upper:
        surcharge = PROCESS_FEES["BVR"]
    elif "RVV" in cat_upper:
        surcharge = PROCESS_FEES["RVV"]
    elif "BV" in cat_upper: # BV 通常指单丝
        surcharge = PROCESS_FEES["BV"]
    
    final_cny_ton = base_cny + surcharge
    
    # 3. 换汇并转为 kg 单价
    usd_ton = final_cny_ton / exchange_rate
    usd_kg = usd_ton / 1000.0
    
    return usd_kg

@router.post("/sync-market-prices", response_model=dict)
async def sync_costs_with_market(db: AsyncSession = Depends(get_db)):
    """
    🟢 一键按钮：根据最新铜价表，重新计算所有成本和参考售价
    """
    # 1. 获取最新市场铜价 (从 CopperPrice 表)
    res = await db.execute(
        select(models.CopperPrice).order_by(models.CopperPrice.updated_at.desc()).limit(1)
    )
    latest_price = res.scalars().first()
    
    if not latest_price:
        raise HTTPException(status_code=400, detail="未找到市场铜价记录，请先去首页刷新铜价")

    market_cny = latest_price.cny_price
    rate = latest_price.exchange_rate
    
    # 2. 获取所有成本记录
    res_costs = await db.execute(select(models.ProductCost))
    all_costs = res_costs.scalars().all()
    
    updated_count = 0
    
    for cost in all_costs:
        # 3. 动态计算该产品的 铜原材料单价 ($/kg)
        new_copper_price_usd = calculate_copper_usd_price(market_cny, rate, cost.category)
        
        # 4. 更新该记录的 copper_price 字段
        cost.copper_price = round(new_copper_price_usd, 4)
        
        # 5. 重新触发核心计算公式 (计算总成本 total_cost)
        # 注意：这里需要把 SQLAlchemy 对象转为 Pydantic 这里的入参格式有点差异，
        # 我们直接调用逻辑函数，或者手动更新字段
        
        # 复用之前的计算逻辑 (手动展开以确保准确)
        # --- 重新计算导体重量 ---
        density_coeff = 0.214 if cost.material == "Al" else 0.7
        total_cond_weight = 0.0
        for group in cost.core_structure: # 假设是 list[dict]
             # 注意：从DB取出的JSON已经是dict list
             g_w = (group['gauge']**2 * group['strands'] * group['cores'] * density_coeff * cost.length) / 100.0
             total_cond_weight += g_w
             
        # --- 更新成本字段 ---
        cost.copper_weight = round(total_cond_weight, 4)
        cost.copper_amount = round(total_cond_weight * cost.copper_price, 2)
        
        pvc_weight = max(0.0, cost.total_weight - total_cond_weight)
        cost.pvc_weight = round(pvc_weight, 4)
        cost.pvc_amount = round(pvc_weight * cost.pvc_price, 2) # pvc_price 保持原样不自动变
        
        cost.total_cost = round(cost.copper_amount + cost.pvc_amount + cost.labor_cost, 2)
        
        # 6. 🟢 计算参考售价 (成本 + 15%)
        cost.reference_price = round(cost.total_cost * 1.15, 2)
        
        updated_count += 1
        
    await db.commit()
    
    return {
        "message": f"成功同步 {updated_count} 条数据",
        "market_cny": market_cny,
        "rate": rate
    }

# === 🟢 新增接口：获取所有分类列表 ===
@router.get("/categories", response_model=List[str])
async def get_cost_categories(db: AsyncSession = Depends(get_db)):
    """获取所有已存在的分类名称 (去重)"""
    # select distinct category from product_costs where category is not null
    query = select(models.ProductCost.category).where(models.ProductCost.category != None).distinct()
    result = await db.execute(query)
    categories = result.scalars().all()
    
    # 过滤掉空字符串，并排序返回
    return sorted([c for c in categories if c])

def calculate_formulas(data: schemas.CostBase) -> dict:
    """
    🟢 多维结构计算引擎
    """
    # 1. 确定密度系数
    # 铜: ~0.7 (系数), 铝: ~0.214
    density_coeff = 0.214 if data.material == "Al" else 0.7

    # 2. 循环计算所有线芯组的导体重量
    total_conductor_weight = 0.0
    
    for group in data.core_structure:
        # 单组公式: 丝号² * 根数 * 芯数 * 系数 * 长度 / 100
        group_weight = (group.gauge * group.gauge * group.strands * group.cores * density_coeff * data.length) / 100.0
        total_conductor_weight += group_weight

    # 3. 导体金额
    conductor_amount = total_conductor_weight * data.copper_price
    
    # 4. 塑料重量 (总重 - 导体重)
    # 这里的 pvc_price 代表所有非导体材料(绝缘XLPE/PVC + 填充PP + 护套PVC)的加权均价
    pvc_weight = max(0.0, data.total_weight - total_conductor_weight)
    
    # 5. 塑料金额
    pvc_amount = pvc_weight * data.pvc_price
    
    # 6. 总成本
    total_cost = conductor_amount + pvc_amount + data.labor_cost
    
    return {
        "copper_weight": round(total_conductor_weight, 4),
        "copper_amount": round(conductor_amount, 2),
        "pvc_weight": round(pvc_weight, 4),
        "pvc_amount": round(pvc_amount, 2),
        "total_cost": round(total_cost, 2)
    }

@router.post("/", response_model=schemas.CostResponse)
async def create_cost_record(cost_in: schemas.CostCreate, db: AsyncSession = Depends(get_db)):
    # 后端强制计算
    calc_res = calculate_formulas(cost_in)
    
    new_cost = models.ProductCost(
        **cost_in.dict(),
        **calc_res # 写入计算结果
    )
    db.add(new_cost)
    await db.commit()
    await db.refresh(new_cost)
    return new_cost

@router.put("/{cost_id}", response_model=schemas.CostResponse)
async def update_cost_record(cost_id: int, cost_in: schemas.CostUpdate, db: AsyncSession = Depends(get_db)):
    """[新增] 编辑功能：重新计算成本并保存"""
    # 1. 查是否存在
    res = await db.execute(select(models.ProductCost).filter(models.ProductCost.id == cost_id))
    db_cost = res.scalars().first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="记录未找到")
        
    # 2. 重新计算核心公式
    calc_res = calculate_formulas(cost_in)
    
    # 3. 更新字段
    update_data = cost_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    # 4. 更新计算结果
    for field, value in calc_res.items():
        setattr(db_cost, field, value)
        
    await db.commit()
    await db.refresh(db_cost)
    return db_cost

@router.get("/", response_model=List[schemas.CostResponse])
async def read_cost_records(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None, # [新增] 筛选参数
    search: Optional[str] = None,   # [新增] 搜索参数
    db: AsyncSession = Depends(get_db)
):
    query = select(models.ProductCost).order_by(desc(models.ProductCost.updated_at))
    
    if category:
        query = query.filter(models.ProductCost.category == category)
    
    if search:
        # 搜索规格名称或备注
        query = query.filter(
            (models.ProductCost.spec_name.contains(search)) | 
            (models.ProductCost.remark.contains(search))
        )
        
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


# 🟢 [新增] 获取今日建议导体单价 API
@router.get("/calculate-unit-price")
async def get_calculated_unit_price(category: str = "", db: AsyncSession = Depends(get_db)):
    """
    根据最新市场铜价和产品分类，计算建议的导体单价 ($/kg)
    """
    # 1. 获取最新行情
    res = await db.execute(
        select(models.CopperPrice).order_by(models.CopperPrice.updated_at.desc()).limit(1)
    )
    latest = res.scalars().first()
    
    if not latest:
        raise HTTPException(status_code=400, detail="未找到市场铜价，请先在首页刷新行情")
    
    # 2. 调用之前的计算公式 (复用 calculate_copper_usd_price 函数)
    # 注意：确保 calculate_copper_usd_price 函数在当前文件中可见
    unit_price = calculate_copper_usd_price(latest.cny_price, latest.exchange_rate, category)
    
    return {
        "price": round(unit_price, 4),
        "market_cny": latest.cny_price,
        "rate": latest.exchange_rate,
        "message": "获取成功"
    }


