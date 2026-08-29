from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean 
from sqlalchemy import Date, DateTime, ForeignKey, Text, func, or_
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
DATABASE_URL = "mysql+pymysql://root:Snk%4026112000@localhost/fasiondb"
engine = create_engine(DATABASE_URL,pool_pre_ping=True,pool_recycle=280,echo=False)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()
app = FastAPI(
    title="Designer & SKU Management API",
    version="1.0.0"
)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
class Designer(Base):
    __tablename__ = "designers"
    id = Column(Integer, primary_key=True, index=True)
    designer_code = Column(String(50), unique=True, nullable=False, index=True)
    designer_name = Column(String(150), nullable=False)
    brand = Column(String(150), nullable=False)
    owner_name = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True)
    phone = Column(String(30), nullable=True)
    city = Column(String(100), nullable=False)
    primary_category = Column(String(150), nullable=False)
    tier = Column(String(50), nullable=False, default="Emerging")
    take_rate = Column(Float, nullable=False, default=0)
    gst_number = Column(String(50), nullable=True)
    contract_end_date = Column(Date, nullable=True)
    stage = Column(String(50), nullable=False, default="LEAD")
    kyc_status = Column(String(50), nullable=False, default="PENDING")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    skus = relationship("SKU", back_populates="designer", cascade="all, delete-orphan")
class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    location = Column(String(100), nullable=True)
    warehouse_type = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    inventories = relationship("Inventory", back_populates="warehouse")
class SKU(Base):
    __tablename__ = "skus"
    id = Column(Integer, primary_key=True, index=True)
    sku_code = Column(String(200), unique=True, nullable=False, index=True)
    designer_id = Column(Integer, ForeignKey("designers.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    category = Column(String(150), nullable=False)
    colour = Column(String(100), nullable=False)
    size = Column(String(50), nullable=False)
    mrp = Column(Float, nullable=False, default=0)
    selling_price = Column(Float, nullable=False, default=0)
    stocking_location_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    fast_delivery_eligible = Column(Boolean, default=False)
    returnable = Column(Boolean, default=True)
    qa_status = Column(String(50), nullable=False, default="PENDING_QA")
    live_status = Column(String(50), nullable=False, default="NOT LIVE")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    designer = relationship("Designer", back_populates="skus")
    warehouse = relationship("Warehouse")
    inventory = relationship(
        "Inventory",
        back_populates="sku",
        cascade="all, delete-orphan"
    )
class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    available_qty = Column(Integer, default=0)
    reserved_qty = Column(Integer, default=0)
    sold_qty = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    sku = relationship("SKU", back_populates="inventory")
    warehouse = relationship("Warehouse", back_populates="inventories")
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    sku_id = Column(Integer, nullable=True)
    designer_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class DesignerCreate(BaseModel):
    designer_name: str
    brand: str
    owner_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: str
    primary_category: str
    tier: str = "Emerging"
    take_rate: float = 0
    gst_number: Optional[str] = None
    contract_end_date: Optional[date] = None
class DesignerUpdate(BaseModel):
    designer_name: Optional[str] = None
    brand: Optional[str] = None
    owner_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    primary_category: Optional[str] = None
    tier: Optional[str] = None
    take_rate: Optional[float] = None
    gst_number: Optional[str] = None
    contract_end_date: Optional[date] = None
class StageUpdate(BaseModel):
    stage: str
class KYCUpdate(BaseModel):
    kyc_status: str
class SKUCreate(BaseModel):
    designer_id: int
    product_name: str
    category: str
    colour: str
    size: str
    mrp: float = 0
    selling_price: float = 0
    stocking_location_id: int
    fast_delivery_eligible: bool = False
    returnable: bool = True
    initial_stock: int = 0
class SKUPriceUpdate(BaseModel):
    new_price: float
class QAUpdate(BaseModel):
    qa_status: str
class LiveStatusUpdate(BaseModel):
    live_status: str
class InventoryUpdate(BaseModel):
    available_qty: Optional[int] = None
    reserved_qty: Optional[int] = None
    sold_qty: Optional[int] = None
class WarehouseCreate(BaseModel):
    name: str
    location: Optional[str] = None
    warehouse_type: Optional[str] = None
VALID_STAGES = [
    "LEAD",
    "CONTACTED",
    "QUALIFIED",
    "PORTFOLIO",
    "REVIEW",
    "APPROVED",
    "CONTRACT",
    "SIGNED",
    "LIVE",
    "ACTIVE"
]
VALID_TIERS = [
    "Emerging",
    "Core",
    "Premium"
]
VALID_KYC = [
    "PENDING",
    "VERIFIED"
]
VALID_QA = [
    "PENDING_QA",
    "APPROVED",
    "REJECTED"
]
VALID_LIVE_STATUS = [
    "LIVE",
    "NOT LIVE"
]
def generate_designer_code(db: Session):
    count = db.query(Designer).count() + 1
    return f"DSG-{count:03d}"
def clean_code(value: str):
    return (
        value.upper()
        .replace(" ", "")
        .replace("&", "")
        .replace("/", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
def category_code(category: str):
    words = category.split()
    if len(words) >= 2:
        code = "".join(word[0] for word in words)
    else:
        code = category[:3]
    return clean_code(code)[:5]
def product_code(product: str):
    return clean_code(product)[:12]
def generate_sku_code(
    designer: Designer,
    category: str,
    product_name: str,
    colour: str,
    size: str
):
    designer_part = clean_code(designer.designer_name)[:3]
    category_part = category_code(category)
    product_part = product_code(product_name)
    colour_part = clean_code(colour)
    size_part = clean_code(size)
    return (
        f"ZNV-"
        f"{designer_part}-"
        f"{category_part}-"
        f"{product_part}-"
        f"{colour_part}-"
        f"{size_part}"
    )
def create_audit(
    db: Session,
    action: str,
    sku_id: Optional[int] = None,
    designer_id: Optional[int] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    changed_by: Optional[str] = "system"
):
    log = AuditLog(
        sku_id=sku_id,
        designer_id=designer_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by
    )
    db.add(log)
@app.get("/")
def root():
    return {
        "message": "Designer & SKU Management API",
        "status": "running"
    }
@app.post("/designers")
def create_designer(data: DesignerCreate,db: Session = Depends(get_db)):
    if data.tier not in VALID_TIERS:
        raise HTTPException(status_code=400,detail=f"Invalid tier. Use: {VALID_TIERS}")
    designer = Designer(
        designer_code=generate_designer_code(db),
        designer_name=data.designer_name,
        brand=data.brand,
        owner_name=data.owner_name,
        email=data.email,
        phone=data.phone,
        city=data.city,
        primary_category=data.primary_category,
        tier=data.tier,
        take_rate=data.take_rate,
        gst_number=data.gst_number,
        contract_end_date=data.contract_end_date,
        stage="LEAD",
        kyc_status="PENDING"
    )
    db.add(designer)
    db.commit()
    db.refresh(designer)
    return {
        "message": "Designer created successfully",
        "designer": {
            "id": designer.id,
            "designer_code": designer.designer_code,
            "designer_name": designer.designer_name,
            "brand": designer.brand,
            "owner_name": designer.owner_name,
            "email": designer.email,
            "phone": designer.phone,
            "city": designer.city,
            "primary_category": designer.primary_category,
            "tier": designer.tier,
            "take_rate": designer.take_rate,
            "gst_number": designer.gst_number,
            "contract_end_date": designer.contract_end_date,
            "stage": designer.stage,
            "kyc_status": designer.kyc_status
        }
    }
@app.get("/designers")
def get_designers(db: Session = Depends(get_db)):
    designers = db.query(Designer).order_by(Designer.id.desc()).all()
    return [
        {
            "id": d.id,
            "designer_code": d.designer_code,
            "designer_name": d.designer_name,
            "brand": d.brand,
            "owner_name": d.owner_name,
            "email": d.email,
            "phone": d.phone,
            "city": d.city,
            "primary_category": d.primary_category,
            "tier": d.tier,
            "take_rate": d.take_rate,
            "gst_number": d.gst_number,
            "contract_end_date": d.contract_end_date,
            "stage": d.stage,
            "kyc_status": d.kyc_status,
            "created_at": d.created_at
        }
        for d in designers
    ]
@app.get("/designers/{designer_id}")
def get_designer(designer_id: int,db: Session = Depends(get_db)):
    designer = db.query(Designer).filter(Designer.id == designer_id).first()
    if not designer:
        raise HTTPException(status_code=404,detail="Designer not found")
    return {
        "id": designer.id,
        "designer_code": designer.designer_code,
        "designer_name": designer.designer_name,
        "brand": designer.brand,
        "owner_name": designer.owner_name,
        "email": designer.email,
        "phone": designer.phone,
        "city": designer.city,
        "primary_category": designer.primary_category,
        "tier": designer.tier,
        "take_rate": designer.take_rate,
        "gst_number": designer.gst_number,
        "contract_end_date": designer.contract_end_date,
        "stage": designer.stage,
        "kyc_status": designer.kyc_status
    }
@app.put("/designers/{designer_id}")
def update_designer(designer_id: int,data: DesignerUpdate,db: Session = Depends(get_db)):
    designer = db.query(Designer).filter(Designer.id == designer_id).first()
    if not designer:
        raise HTTPException(status_code=404,detail="Designer not found")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(designer, field):
            setattr(designer, field, value)
    db.commit()
    db.refresh(designer)
    return {
        "message": "Designer updated successfully",
        "designer_id": designer.id
    }
@app.put("/designers/{designer_id}/stage")
def update_designer_stage(designer_id: int,data: StageUpdate,db: Session = Depends(get_db)):
    stage = data.stage.upper()
    if stage not in VALID_STAGES:
        raise HTTPException(status_code=400,detail=f"Invalid stage. Use: {VALID_STAGES}")
    designer = db.query(Designer).filter(Designer.id == designer_id).first()
    if not designer:
        raise HTTPException(status_code=404,detail="Designer not found")
    old_stage = designer.stage
    designer.stage = stage
    create_audit(
        db=db,
        action="DESIGNER_STAGE_CHANGE",
        designer_id=designer.id,
        old_value=old_stage,
        new_value=stage
    )
    db.commit()
    return {
        "message": "Designer stage updated",
        "designer_id": designer.id,
        "old_stage": old_stage,
        "new_stage": stage
    }
@app.put("/designers/{designer_id}/kyc")
def update_kyc(designer_id: int,data: KYCUpdate,db: Session = Depends(get_db)):
    status = data.kyc_status.upper()
    if status not in VALID_KYC:
        raise HTTPException(status_code=400,detail=f"Invalid KYC status. Use: {VALID_KYC}")
    designer = db.query(Designer).filter(Designer.id == designer_id).first()
    if not designer:
        raise HTTPException(status_code=404,detail="Designer not found")
    old_status = designer.kyc_status
    designer.kyc_status = status
    create_audit(
        db=db,
        action="KYC_STATUS_CHANGE",
        designer_id=designer.id,
        old_value=old_status,
        new_value=status
    )
    db.commit()
    return {
        "message": "KYC status updated",
        "designer_id": designer.id,
        "kyc_status": status
    }
@app.get("/dashboard/designer-summary")
def designer_summary(db: Session = Depends(get_db)):
    pipeline = db.query(Designer).count()
    selling_now = db.query(Designer).filter(Designer.stage.in_(["LIVE", "ACTIVE"])).count()
    kyc_pending = db.query(Designer).filter(Designer.kyc_status == "PENDING").count()
    return {
        "pipeline": pipeline,
        "selling_now": selling_now,
        "kyc_pending": kyc_pending
    }
@app.post("/warehouses")
def create_warehouse(data: WarehouseCreate,db: Session = Depends(get_db)):
    existing = db.query(Warehouse).filter(Warehouse.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400,detail="Warehouse already exists")
    warehouse = Warehouse(
        name=data.name,
        location=data.location,
        warehouse_type=data.warehouse_type,
        is_active=True
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return {
        "message": "Warehouse created successfully",
        "warehouse": {
            "id": warehouse.id,
            "name": warehouse.name,
            "location": warehouse.location,
            "warehouse_type": warehouse.warehouse_type
        }
    }
@app.get("/warehouses")
def get_warehouses(db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).order_by(Warehouse.id).all()
    return [
        {
            "id": w.id,
            "name": w.name,
            "location": w.location,
            "warehouse_type": w.warehouse_type
        }
        for w in warehouses
    ]
@app.post("/skus")
def create_sku(data: SKUCreate,db: Session = Depends(get_db)):
    designer = db.query(Designer).filter(Designer.id == data.designer_id).first()
    if not designer:
        raise HTTPException(status_code=404,detail="Designer not found")
    warehouse = db.query(Warehouse).filter(
        Warehouse.id == data.stocking_location_id,
        Warehouse.is_active == True).first()
    if not warehouse:
        raise HTTPException(status_code=404,detail="Warehouse not found")
    if data.mrp < 0 or data.selling_price < 0:
        raise HTTPException(status_code=400,detail="Price cannot be negative")
    if data.initial_stock < 0:
        raise HTTPException(status_code=400,detail="Initial stock cannot be negative")
    sku_code = generate_sku_code(
        designer,
        data.category,
        data.product_name,
        data.colour,
        data.size
    )
    original_code = sku_code
    counter = 1
    while db.query(SKU).filter(SKU.sku_code == sku_code).first():
        sku_code = f"{original_code}-{counter}"
        counter += 1
    sku = SKU(
        sku_code=sku_code,
        designer_id=designer.id,
        product_name=data.product_name,
        category=data.category,
        colour=data.colour,
        size=data.size,
        mrp=data.mrp,
        selling_price=data.selling_price,
        stocking_location_id=warehouse.id,
        fast_delivery_eligible=data.fast_delivery_eligible,
        returnable=data.returnable,
        qa_status="PENDING_QA",
        live_status="NOT LIVE"
    )
    db.add(sku)
    db.flush()
    inventory = Inventory(
        sku_id=sku.id,
        warehouse_id=warehouse.id,
        available_qty=data.initial_stock,
        reserved_qty=0,
        sold_qty=0
    )
    db.add(inventory)
    create_audit(
        db=db,
        action="SKU_CREATED",
        sku_id=sku.id,
        designer_id=designer.id,
        old_value=None,
        new_value=sku_code
    )
    db.commit()
    db.refresh(sku)
    return {
        "message": "SKU created successfully",
        "sku": {
            "id": sku.id,
            "sku_code": sku.sku_code,
            "designer_id": sku.designer_id,
            "product_name": sku.product_name,
            "category": sku.category,
            "colour": sku.colour,
            "size": sku.size,
            "mrp": sku.mrp,
            "selling_price": sku.selling_price,
            "stocking_location": warehouse.name,
            "fast_delivery_eligible": sku.fast_delivery_eligible,
            "returnable": sku.returnable,
            "qa_status": sku.qa_status,
            "live_status": sku.live_status
        }
    }
@app.get("/skus")
def get_skus(search: Optional[str] = Query(None),db: Session = Depends(get_db)):
    query = db.query(SKU)
    if search:
        search_value = f"%{search}%"
        query = query.filter(
            or_(
                SKU.sku_code.ilike(search_value),
                SKU.product_name.ilike(search_value),
                SKU.category.ilike(search_value),
                SKU.colour.ilike(search_value)
            )
        )
    skus = query.order_by(SKU.id.desc()).all()
    result = []
    for sku in skus:
        available = sum(
            inventory.available_qty
            for inventory in sku.inventory
        )
        reserved = sum(
            inventory.reserved_qty
            for inventory in sku.inventory
        )
        sold = sum(
            inventory.sold_qty
            for inventory in sku.inventory
        )
        result.append({
            "id": sku.id,
            "sku_code": sku.sku_code,
            "product_name": sku.product_name,
            "designer_id": sku.designer_id,
            "designer": sku.designer.brand if sku.designer else None,
            "category": sku.category,
            "colour": sku.colour,
            "size": sku.size,
            "mrp": sku.mrp,
            "selling_price": sku.selling_price,
            "qa_status": sku.qa_status,
            "live_status": sku.live_status,
            "returnable": sku.returnable,
            "fast_delivery_eligible": sku.fast_delivery_eligible,
            "available": available,
            "reserved": reserved,
            "sold": sold
        })
    return result
@app.get("/skus/{sku_id}")
def get_sku(sku_id: int,db: Session = Depends(get_db)):
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404,detail="SKU not found")
    available = sum(
        i.available_qty for i in sku.inventory
    )
    reserved = sum(
        i.reserved_qty for i in sku.inventory
    )
    sold = sum(
        i.sold_qty for i in sku.inventory
    )
    return {
        "id": sku.id,
        "sku_code": sku.sku_code,
        "product_name": sku.product_name,
        "designer": sku.designer.brand if sku.designer else None,
        "category": sku.category,
        "colour": sku.colour,
        "size": sku.size,
        "mrp": sku.mrp,
        "selling_price": sku.selling_price,
        "qa_status": sku.qa_status,
        "live_status": sku.live_status,
        "returnable": sku.returnable,
        "fast_delivery_eligible": sku.fast_delivery_eligible,
        "available": available,
        "reserved": reserved,
        "sold": sold
    }
@app.get("/designers/{designer_id}/skus")
def get_designer_skus(designer_id: int,db: Session = Depends(get_db)):
    designer = db.query(Designer).filter(Designer.id == designer_id).first()
    if not designer:
        raise HTTPException(status_code=404,detail="Designer not found")
    skus = db.query(SKU).filter(SKU.designer_id == designer_id).all()
    return [
        {
            "id": sku.id,
            "sku_code": sku.sku_code,
            "product_name": sku.product_name,
            "category": sku.category,
            "colour": sku.colour,
            "size": sku.size,
            "mrp": sku.mrp,
            "selling_price": sku.selling_price,
            "qa_status": sku.qa_status,
            "live_status": sku.live_status
        }
        for sku in skus
    ]
@app.put("/skus/{sku_id}/price")
def update_sku_price(sku_id: int,data: SKUPriceUpdate,db: Session = Depends(get_db)):
    if data.new_price < 0:
        raise HTTPException(status_code=400,detail="Price cannot be negative")
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404,detail="SKU not found")
    old_price = sku.selling_price
    sku.selling_price = data.new_price
    create_audit(
        db=db,
        action="PRICE_UPDATE",
        sku_id=sku.id,
        designer_id=sku.designer_id,
        old_value=str(old_price),
        new_value=str(data.new_price)
    )
    db.commit()
    db.refresh(sku)
    return {
        "message": "Price updated successfully",
        "sku_id": sku.id,
        "old_price": old_price,
        "new_price": sku.selling_price
    }
@app.put("/skus/{sku_id}/qa")
def update_qa_status(sku_id: int,data: QAUpdate,db: Session = Depends(get_db)):
    status = data.qa_status.upper()
    if status not in VALID_QA:
        raise HTTPException(status_code=400,detail=f"Invalid QA status. Use: {VALID_QA}")
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404,detail="SKU not found")
    old_status = sku.qa_status
    sku.qa_status = status
    if status != "APPROVED":
        sku.live_status = "NOT LIVE"
    create_audit(
        db=db,
        action="QA_STATUS_CHANGE",
        sku_id=sku.id,
        designer_id=sku.designer_id,
        old_value=old_status,
        new_value=status
    )
    db.commit()
    return {
        "message": "QA status updated",
        "sku_id": sku.id,
        "qa_status": sku.qa_status,
        "live_status": sku.live_status
    }
@app.put("/skus/{sku_id}/status")
def update_live_status(sku_id: int,data: LiveStatusUpdate,db: Session = Depends(get_db)):
    status = data.live_status.upper()
    if status not in VALID_LIVE_STATUS:
        raise HTTPException(status_code=400,detail=f"Invalid live status. Use: {VALID_LIVE_STATUS}")
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404,detail="SKU not found")
    if status == "LIVE":
        if sku.qa_status != "APPROVED":
            raise HTTPException(status_code=400,detail="SKU must be APPROVED by QA before going LIVE")
        designer = db.query(Designer).filter(Designer.id == sku.designer_id).first()
        if not designer or designer.stage not in ["LIVE", "ACTIVE"]:
            raise HTTPException(status_code=400,detail="Designer must be LIVE or ACTIVE")
    old_status = sku.live_status
    sku.live_status = status
    create_audit(
        db=db,
        action="LIVE_STATUS_CHANGE",
        sku_id=sku.id,
        designer_id=sku.designer_id,
        old_value=old_status,
        new_value=status
    )
    db.commit()
    return {
        "message": "Live status updated",
        "sku_id": sku.id,
        "old_status": old_status,
        "new_status": status
    }
@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    inventory = db.query(Inventory).all()
    return [
        {
            "id": i.id,
            "sku_id": i.sku_id,
            "sku_code": i.sku.sku_code if i.sku else None,
            "product_name": i.sku.product_name if i.sku else None,
            "warehouse_id": i.warehouse_id,
            "warehouse": i.warehouse.name if i.warehouse else None,
            "available_qty": i.available_qty,
            "reserved_qty": i.reserved_qty,
            "sold_qty": i.sold_qty
        }
        for i in inventory
    ]
@app.get("/skus/{sku_id}/inventory")
def get_sku_inventory(sku_id: int,db: Session = Depends(get_db)):
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404,detail="SKU not found")
    return [
        {
            "inventory_id": i.id,
            "warehouse_id": i.warehouse_id,
            "warehouse": i.warehouse.name if i.warehouse else None,
            "available_qty": i.available_qty,
            "reserved_qty": i.reserved_qty,
            "sold_qty": i.sold_qty
        }
        for i in sku.inventory
    ]
@app.put("/inventory/{inventory_id}")
def update_inventory(inventory_id: int,data: InventoryUpdate,db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404,detail="Inventory record not found")
    if data.available_qty is not None:
        if data.available_qty < 0:
            raise HTTPException(status_code=400,detail="Available quantity cannot be negative")
        inventory.available_qty = data.available_qty
    if data.reserved_qty is not None:
        if data.reserved_qty < 0:
            raise HTTPException(status_code=400,detail="Reserved quantity cannot be negative")
        inventory.reserved_qty = data.reserved_qty
    if data.sold_qty is not None:
        if data.sold_qty < 0:
            raise HTTPException(status_code=400,detail="Sold quantity cannot be negative")
        inventory.sold_qty = data.sold_qty
    db.commit()
    db.refresh(inventory)
    return {
        "message": "Inventory updated successfully",
        "inventory_id": inventory.id,
        "available_qty": inventory.available_qty,
        "reserved_qty": inventory.reserved_qty,
        "sold_qty": inventory.sold_qty
    }
@app.get("/dashboard/sku-summary")
def sku_summary(db: Session = Depends(get_db)):
    total_skus = db.query(SKU).count()
    live = db.query(SKU).filter(SKU.live_status == "LIVE").count()
    in_qa = db.query(SKU).filter(SKU.qa_status == "PENDING_QA").count()
    final_sale = db.query(SKU).filter(SKU.returnable == False).count()
    return {
        "skus": total_skus,
        "live": live,
        "in_qa": in_qa,
        "final_sale": final_sale
    }
@app.get("/audit-logs")
def get_audit_logs(sku_id: Optional[int] = None,designer_id: Optional[int] = None,db: Session = Depends(get_db)):
    query = db.query(AuditLog)
    if sku_id:
        query = query.filter(AuditLog.sku_id == sku_id)
    if designer_id:
        query = query.filter(AuditLog.designer_id == designer_id)
    logs = query.order_by(AuditLog.id.desc()).all()
    return [
        {
            "id": log.id,
            "sku_id": log.sku_id,
            "designer_id": log.designer_id,
            "action": log.action,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "changed_by": log.changed_by,
            "created_at": log.created_at
        }
        for log in logs
    ]
@app.delete("/skus/{sku_id}")
def delete_sku(sku_id: int, db: Session = Depends(get_db)):
    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404,detail="SKU not found")
    sku_code = sku.sku_code
    designer_id = sku.designer_id
    db.query(Inventory).filter(Inventory.sku_id == sku.id).delete(synchronize_session=False)
    create_audit(
        db=db,
        action="SKU_DELETED",
        sku_id=None,
        designer_id=designer_id,
        old_value=sku_code,
        new_value=None
    )
    db.delete(sku)
    db.commit()
    return {
        "message": "SKU deleted successfully",
        "sku_id": sku_id,
        "sku_code": sku_code
    }
@app.delete("/designers/{designer_id}")
def delete_designer(designer_id: int,db: Session = Depends(get_db)):
    designer = db.query(Designer).filter(Designer.id == designer_id).first()
    if not designer:
        raise HTTPException(status_code=404,detail="Designer not found")
    db.delete(designer)
    db.commit()
    return {
        "message": "Designer deleted successfully",
        "designer_id": designer_id
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )