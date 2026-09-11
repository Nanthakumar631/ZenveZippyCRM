from fastapi import FastAPI ,Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Integer,Column
from sqlalchemy import String,Boolean,Float,Date,DateTime,Time,ForeignKey,text,Text,UniqueConstraint
from sqlalchemy.orm import declarative_base,sessionmaker,Session
from typing import Optional
from datetime import datetime,date,time
from zoneinfo import ZoneInfo
DATABASE_URL = "mysql+pymysql://root:Snk%4026112000@127.0.0.1:3306/pet_management"
engine = create_engine( DATABASE_URL,echo=True,pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()
app = FastAPI(title= "Pet Management API",version= "1.0.0")
def yes_no_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value == "yes":
            return True
        if value == "no":
            return False
    raise HTTPException(status_code=422,detail="Value must be Yes or No")
def plan_response(obj):
    data = {k: v for k, v in obj.__dict__.items() if k != "_sa_instance_state"}
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = v.isoformat()
        elif isinstance(v, date):
            data[k] = v.isoformat()
    return data
def model_response(obj):
    data = {
        key: value
        for key, value in obj.__dict__.items()
        if key != "_sa_instance_state"
    }
    if "is_active" in data:
        data["is_active"] = "Yes" if data["is_active"] else "No"
    return data
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class PetParent(Base):
    __tablename__ = "pet_parents"
    id = Column(Integer , primary_key= True , index = True)
    full_name = Column(String(150), nullable = False)
    email = Column(String(100) , unique = True, nullable =False)
    phone = Column(String(30))
    city = Column(String(150))
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer,primary_key= True , index=True)
    parent_id = Column(Integer,ForeignKey("pet_parents.id"),nullable=False)
    name = Column(String(100),nullable = False)
    species = Column(String(100))
    breed = Column(String(100))
    gender = Column(String(20))
    weight_kg = Column(Float)
    is_active = Column(Boolean,default = True)
class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer , primary_key = True , index=True)
    pet_id = Column(Integer,ForeignKey("pets.id"),nullable=False)
    record_type = Column(String(100))
    title = Column(String(200))
    diagnosis = Column(String(500))
    record_date = Column(Date)
class Vaccination(Base):
    __tablename__ = "vaccinations"
    id=Column(Integer,primary_key=True , index=True)
    pet_id = Column(Integer,ForeignKey("pets.id"),nullable=False)
    vaccine_name = Column(String(200))
    administered_on = Column(Date)
    next_due_on = Column(Date)
    batch_number =Column(String(100))
class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer,primary_key=True , index=True)
    parent_id = Column(Integer,ForeignKey("pet_parents.id"),nullable=False)
    label = Column(String(100))
    contact_name = Column(String(150))
    line1 = Column(String(300))
    city = Column(String(100))
    pincode = Column(String(20))
    is_default =Column(Boolean,default=True)
class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    role = Column(String(100), nullable=False)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    qualification = Column(String(300))
    specializations = Column(String(500))
    pincode = Column(String(20))
    city = Column(String(150))
    phone = Column(String(30))
    experience_years = Column(Integer)
    consultation_fee = Column(Float)
    verification_status = Column(String(50), default="pending")
    is_active = Column(Boolean, default=True)
class ClinicHospital(Base):
    __tablename__ = "clinics_hospitals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    facility_type = Column(String(100))
    phone = Column(String(30))
    emergency_available = Column(Boolean, default=False)
    open_24x7 = Column(Boolean, default=False)
    verification_status = Column(String(50), default="pending")
    rating = Column(Float)
class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer,ForeignKey("doctors.id"),nullable=False)
    day_of_week = Column(String(20), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    consultation_type = Column(String(100))
    is_active = Column(Boolean, default=True)
class DoctorDocument(Base):
    __tablename__ = "doctor_documents"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer,ForeignKey("doctors.id"),nullable=False)
    document_type = Column(String(100), nullable=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    appointment_type = Column(String(100))
    status = Column(String(50), default="pending")
    payment_status = Column(String(50), default="pending")
    consultation_fee = Column(Float, default=0)
class Consultation(Base):
    __tablename__ = "consultations"
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=False)
    consultation_mode = Column(String(100))
    diagnosis = Column(String(500))
    follow_up_date = Column(Date)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Prescription(Base):
    __tablename__ = "prescriptions"
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    valid_until = Column(Date)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class ServiceProvider(Base):
    __tablename__ = "service_providers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    provider_type = Column(String(100))
    phone = Column(String(30))
    verification_status = Column(String(50), default="pending")
    rating = Column(Float)
    is_active = Column(Boolean, default=True)
class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    service_type = Column(String(100))
    price = Column(Float, default=0)
    duration_minutes = Column(Integer)
    home_service = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
class ServiceBooking(Base):
    __tablename__ = "service_bookings"
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("service_providers.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    price = Column(Float, default=0)
    status = Column(String(50), default="pending")
    payment_status = Column(String(50), default="pending")
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Float, default=0)
    mrp = Column(Float, default=0)
    discount_percent = Column(Float, default=0)
    pincode = Column(String(20))
    stock_quantity = Column(Integer, default=0)
    is_prescription_required = Column(Boolean, default=False)
    rating = Column(Float)
    is_active = Column(Boolean, default=True)
class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("seller_stores.id"), nullable=False)
    pincode = Column(String(20))
    inventory_source = Column(String(100))
    available_quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=0)
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(200), unique=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
class Brand(Base):
    __tablename__ = "brands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class SellerStore(Base):
    __tablename__ = "seller_stores"
    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(200), nullable=False)
    seller_type = Column(String(100))
    phone = Column(String(30))
    commission_rate = Column(Float, default=0)
    verification_status = Column(String(50), default="pending")
    rating = Column(Float)
    is_active = Column(Boolean, default=True)
class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    seller_id = Column(Integer, ForeignKey("seller_stores.id"), nullable=False)
    is_zenve_owned = Column(Boolean, default=False)
    contact_phone = Column(String(30))
    is_active = Column(Boolean, default=True)
class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
    updated_at = Column(DateTime,
    default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None),
    onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)
)
class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0)
    saved_for_later = Column(Boolean, default=False)
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(100), unique=True, nullable=False)
    total_amount = Column(Float, default=0)
    status = Column(String(50), default="pending")
    payment_status = Column(String(50), default="pending")
    placed_at = Column(DateTime, default=datetime.utcnow)
class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0)
    total_price = Column(Float, default=0)
    status = Column(String(50), default="CONFIRMED")
class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    tracking_number = Column(String(150))
    status = Column(String(50), default="pending")
    estimated_delivery = Column(Date)
    delivered_at = Column(DateTime)
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, default=0)
    gateway = Column(String(100))
    status = Column(String(50), default="pending")
    webhook_verified = Column(Boolean, default=False)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Refund(Base):
    __tablename__ = "refunds"
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    amount = Column(Float, default=0)
    reason = Column(String(500))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Payout(Base):
    __tablename__ = "payouts"
    id = Column(Integer, primary_key=True, index=True)
    payee_type = Column(String(100), nullable=False)
    payee_id = Column(Integer, nullable=False)
    amount = Column(Float, default=0)
    commission_amount = Column(Float, default=0)
    status = Column(String(50), default="pending")
class CommissionRule(Base):
    __tablename__ = "commission_rules"
    id = Column(Integer, primary_key=True, index=True)
    scope = Column(String(100), nullable=False)
    percentage = Column(Float, default=0)
    fixed_fee = Column(Float, default=0)
    effective_from = Column(Date)
    is_active = Column(Boolean, default=True)
class GPSLocation(Base):
    __tablename__ = "gps_locations"
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(100), nullable=False)
    city = Column(String(150))
    address = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    service_radius_km = Column(Float, default=0)
    is_primary = Column(Boolean, default=False)
class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String(100), nullable=False)
    rating = Column(Float)
    review_text = Column(String(1000))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    channel = Column(String(100))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class VendorMembershipPlan(Base):
    __tablename__ = "vendor_membership_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    credits = Column(Integer, default=0)
    price = Column(Float, default=0)
    sku_range = Column(String(100))
    duration_days = Column(Integer)
    is_active = Column(Boolean, default=True)
class PlanBenefit(Base):
    __tablename__ = "plan_benefits"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer,ForeignKey("vendor_membership_plans.id"),nullable=False)
    benefit = Column(String(300), nullable=False)
    value = Column(String(300))
class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    plan_id = Column(Integer,ForeignKey("vendor_membership_plans.id"),nullable=False)
    started_on = Column(Date)
    expires_on = Column(Date)
    status = Column(String(50), default="active")
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(300), nullable=False)
    category = Column(String(100))
    status = Column(String(50), default="open")
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class GeocodingCache(Base):
    __tablename__ = "geocoding_cache"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    formatted_address = Column(String(500))
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class RegionalManager(Base):
    __tablename__ = "regional_managers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    phone = Column(String(30))
    email = Column(String(100))
    region = Column(String(150))
    is_active = Column(Boolean, default=True)
class SalesManager(Base):
    __tablename__ = "sales_managers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    phone = Column(String(30))
    email = Column(String(100))
    region = Column(String(150))
    is_active = Column(Boolean, default=True)
class SalesExecutive(Base):
    __tablename__ = "sales_executives"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    phone = Column(String(30))
    email = Column(String(100))
    region = Column(String(150))
    city = Column(String(150))
    monthly_target = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
class PincodeCoverage(Base):
    __tablename__ = "pincode_coverages"
    id = Column(Integer, primary_key=True, index=True)
    executive_id = Column(Integer,ForeignKey("sales_executives.id"),nullable=False)
    pincode = Column(String(20), nullable=False)
    city = Column(String(150))
    state = Column(String(150))
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class ExecutiveTask(Base):
    __tablename__ = "executive_tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    task_type = Column(String(100))
    entity_type = Column(String(100))
    pincode = Column(String(20))
    priority = Column(String(50))
    status = Column(String(50), default="pending")
    due_date = Column(Date)
class ExecutiveAlert(Base):
    __tablename__ = "executive_alerts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    severity = Column(String(50))
    entity_type = Column(String(100))
    pincode = Column(String(20))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class MonthlyPlan(Base):
    __tablename__ = "monthly_plans"
    id = Column(Integer, primary_key=True, index=True)
    executive_id = Column(Integer, ForeignKey("sales_executives.id"), nullable=False)
    month_key = Column(String(10), nullable=False)  
    month_label = Column(String(50))
    working_days = Column(Integer, default=0)
    daily_target = Column(Integer, default=0)
    total_doctors = Column(Integer, default=0)
    planning_method = Column(String(20), default="auto") 
    status = Column(String(30), default="Draft")
    submitted_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(String(150), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
    __table_args__ = (UniqueConstraint("executive_id", "month_key", name="uq_exec_month"),)
class PlanVisit(Base):
    __tablename__ = "plan_visits"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("monthly_plans.id"), nullable=False)
    executive_id = Column(Integer, ForeignKey("sales_executives.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    visit_time = Column(String(20), default="10:00 AM")
    status = Column(String(30), default="Planned")
    reschedule_reason = Column(String(200), nullable=True)
    rescheduled_from = Column(Date, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class VisitReport(Base):
    __tablename__ = "visit_reports"
    id = Column(Integer, primary_key=True, index=True)
    plan_visit_id = Column(Integer, ForeignKey("plan_visits.id"), nullable=False)
    executive_id = Column(Integer, ForeignKey("sales_executives.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    visit_date = Column(Date, nullable=False)
    visit_time = Column(String(20))
    location = Column(String(300))
    purpose = Column(String(150))
    products_discussed = Column(Text)
    notes = Column(Text)
    doctor_feedback = Column(Text)
    next_followup_date = Column(Date, nullable=True)
    next_action = Column(String(300))
    remarks = Column(Text)
    follow_up_required = Column(Boolean, default=True)
    status = Column(String(30), default="Draft")
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class ExecutiveSubmissionReport(Base):
    __tablename__ = "executive_submission_reports"
    id = Column(Integer, primary_key=True, index=True)
    executive_id = Column(Integer, ForeignKey("sales_executives.id"), nullable=False)
    executive_name = Column(String(100), nullable=True)
    employee_code = Column(String(50), nullable=True)
    region = Column(String(100), nullable=True)
    report_date = Column(Date, nullable=False)
    reporting_type = Column(String(50), default="Field")
    recipient_type = Column(String(50), default="both") 
    manager_id = Column(Integer, nullable=True)
    manager_name = Column(String(100), nullable=True)
    regional_manager_id = Column(Integer, nullable=True)
    regional_manager_name = Column(String(100), nullable=True)
    total_visits = Column(Integer, default=0)
    reported_visits = Column(Integer, default=0)
    summary_notes = Column(Text, nullable=True)
    visits_json = Column(Text, nullable=True)
    status = Column(String(50), default="Submitted")
    manager_remarks = Column(Text, nullable=True)
    regional_remarks = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
Base.metadata.create_all(bind=engine)
class PetParentCreate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
class PetParentResponse(PetParentCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
class PetCreate(BaseModel):
    parent_id: int
    name :str
    species: Optional[str] = None
    breed :Optional[str]=None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    is_active: str = "Yes"
class PetResponse(BaseModel):
    id:int
    class Config:
        from_attributes = True
class MedicalRecordCreate(BaseModel):
    pet_id: int
    record_type: Optional[str] = None
    title: Optional[str] = None
    diagnosis: Optional[str] = None
    record_date: Optional[date] = None
class VaccinationCreate(BaseModel):
    pet_id: int
    vaccine_name: str
    administered_on: Optional[date] = None
    next_due_on: Optional[date] = None
    batch_number: Optional[str] = None
class AddressCreate(BaseModel):
    parent_id: int
    label: Optional[str] = None
    contact_name: Optional[str] = None
    line1: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    is_default: bool = False
class UserRoleCreate(BaseModel):
    user_id: int
    role: str
class DoctorCreate(BaseModel):
    name: str
    qualification: Optional[str] = None
    specializations: Optional[str] = None
    pincode: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    verification_status: str = "pending"
    is_active: str = "Yes"
class ClinicHospitalCreate(BaseModel):
    name: str
    facility_type: Optional[str] = None
    phone: Optional[str] = None
    emergency_available: bool = False
    open_24x7: bool = False
    verification_status: str = "pending"
    rating: Optional[float] = None
class AvailabilitySlotCreate(BaseModel):
    doctor_id: int
    day_of_week: str
    start_time: time
    end_time: time
    consultation_type: Optional[str] = None
    is_active: str = "Yes"
class DoctorDocumentCreate(BaseModel):
    doctor_id: int
    document_type: str
    status: str = "pending"
class AppointmentCreate(BaseModel):
    pet_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    appointment_type: Optional[str] = None
    status: str = "pending"
    payment_status: str = "pending"
    consultation_fee: Optional[float] = 0
class ConsultationCreate(BaseModel):
    appointment_id: int
    consultation_mode: Optional[str] = None
    diagnosis: Optional[str] = None
    follow_up_date: Optional[date] = None
class PrescriptionCreate(BaseModel):
    doctor_id: int
    pet_id: int
    valid_until: Optional[date] = None
class ServiceProviderCreate(BaseModel):
    name: str
    provider_type: Optional[str] = None
    phone: Optional[str] = None
    verification_status: str = "pending"
    rating: Optional[float] = None
    is_active: str = "Yes"
class ServiceCreate(BaseModel):
    title: str
    service_type: Optional[str] = None
    price: Optional[float] = 0
    duration_minutes: Optional[int] = None
    home_service: bool = False
    is_active: str = "Yes"
class ServiceBookingCreate(BaseModel):
    service_id: int
    provider_id: int
    pet_id: int
    booking_date: date
    booking_time: time
    price: Optional[float] = 0
    status: str = "pending"
    payment_status: str = "pending"
class ProductCreate(BaseModel):
    name: str
    price: Optional[float] = 0
    mrp: Optional[float] = 0
    discount_percent: Optional[float] = 0
    pincode: Optional[str] = None
    stock_quantity: Optional[int] = 0
    is_prescription_required: bool = False
    rating: Optional[float] = None
    is_active: str = "Yes"
class InventoryCreate(BaseModel):
    product_id: int
    seller_id: int
    pincode: Optional[str] = None
    inventory_source: Optional[str] = None
    available_quantity: Optional[int] = 0
    reserved_quantity: Optional[int] = 0
    reorder_level: Optional[int] = 0
class CategoryCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    sort_order: Optional[int] = 0
    is_active: str = "Yes"
class BrandCreate(BaseModel):
    name: str
    is_active: str = "Yes"
class SellerStoreCreate(BaseModel):
    business_name: str
    seller_type: Optional[str] = None
    phone: Optional[str] = None
    commission_rate: Optional[float] = 0
    verification_status: str = "pending"
    rating: Optional[float] = None
    is_active: str = "Yes"
class WarehouseCreate(BaseModel):
    name: str
    seller_id: int
    is_zenve_owned: bool = False
    contact_phone: Optional[str] = None
    is_active: str = "Yes"
class CartCreate(BaseModel):
    user_id: int
class CartItemCreate(BaseModel):
    cart_id: int
    product_id: int
    quantity: int = 1
    price: Optional[float] = 0
    saved_for_later: bool = False
class OrderCreate(BaseModel):
    order_number: str
    total_amount: Optional[float] = 0
    status: str = "pending"
    payment_status: str = "pending"
class OrderItemCreate(BaseModel):
    order_id: int
    product_name: str
    quantity: int = 1
    unit_price: Optional[float] = 0
    total_price: Optional[float] = 0
    status: str = "CONFIRMED"
class DeliveryCreate(BaseModel):
    order_id: int
    tracking_number: Optional[str] = None
    status: str = "pending"
    estimated_delivery: Optional[date] = None
    delivered_at: Optional[datetime] = None
class PaymentCreate(BaseModel):
    order_id: int
    amount: Optional[float] = 0
    gateway: Optional[str] = None
    status: str = "pending"
    webhook_verified: bool = False
class RefundCreate(BaseModel):
    payment_id: int
    amount: Optional[float] = 0
    reason: Optional[str] = None
    status: str = "pending"
class PayoutCreate(BaseModel):
    payee_type: str
    payee_id: int
    amount: Optional[float] = 0
    commission_amount: Optional[float] = 0
    status: str = "pending"
class CommissionRuleCreate(BaseModel):
    scope: str
    percentage: Optional[float] = 0
    fixed_fee: Optional[float] = 0
    effective_from: Optional[date] = None
    is_active: str = "Yes"
class GPSLocationCreate(BaseModel):
    entity_type: str
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    service_radius_km: Optional[float] = 0
    is_primary: bool = False
class ReviewCreate(BaseModel):
    target_type: str
    rating: Optional[float] = None
    review_text: Optional[str] = None
    status: str = "pending"
class NotificationCreate(BaseModel):
    event_type: str
    title: str
    channel: Optional[str] = None
    is_read: bool = False
class VendorMembershipPlanCreate(BaseModel):
    name: str
    credits: Optional[int] = 0
    price: Optional[float] = 0
    sku_range: Optional[str] = None
    duration_days: Optional[int] = None
    is_active: str = "Yes"
class PlanBenefitCreate(BaseModel):
    plan_id: int
    benefit: str
    value: Optional[str] = None
class VendorCreate(BaseModel):
    user_id: int
    plan_id: int
    started_on: Optional[date] = None
    expires_on: Optional[date] = None
    status: str = "active"
class SupportTicketCreate(BaseModel):
    subject: str
    category: Optional[str] = None
    status: str = "open"
class GeocodingCacheCreate(BaseModel):
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None
class AuditLogCreate(BaseModel):
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
class RegionalManagerCreate(BaseModel):
    name: str
    code: str
    phone: Optional[str] = None
    email: Optional[str] = None
    region: Optional[str] = None
    is_active: str = "Yes"
class SalesManagerCreate(BaseModel):
    name: str
    code: str
    phone: Optional[str] = None
    email: Optional[str] = None
    region: Optional[str] = None
    is_active: str = "Yes"
class SalesExecutiveCreate(BaseModel):
    name: str
    code: str
    phone: Optional[str] = None
    email: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    monthly_target: Optional[float] = 0
    is_active: str = "Yes"
class PincodeCoverageCreate(BaseModel):
    executive_id: int
    pincode: str
    city: Optional[str] = None
    state: Optional[str] = None
class ExecutiveTaskCreate(BaseModel):
    title: str
    task_type: Optional[str] = None
    entity_type: Optional[str] = None
    pincode: Optional[str] = None
    priority: Optional[str] = None
    status: str = "pending"
    due_date: Optional[date] = None
class ExecutiveAlertCreate(BaseModel):
    title: str
    severity: Optional[str] = None
    entity_type: Optional[str] = None
    pincode: Optional[str] = None
    is_read: bool = False
class MonthlyPlanCreate(BaseModel):
    executive_id: int
    month_key: str
    month_label: Optional[str] = None
    working_days: int = 0
    daily_target: int = 0
    total_doctors: int = 0
    planning_method: str = "auto"
class MonthlyPlanUpdate(BaseModel):
    status: Optional[str] = None
    working_days: Optional[int] = None
    daily_target: Optional[int] = None
    total_doctors: Optional[int] = None
    planning_method: Optional[str] = None
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
class PlanVisitCreate(BaseModel):
    plan_id: int
    executive_id: int
    doctor_id: int
    scheduled_date: date
    visit_time: str = "10:00 AM"
    status: str = "Planned"
    reschedule_reason: Optional[str] = None
    rescheduled_from: Optional[date] = None
class PlanVisitUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    visit_time: Optional[str] = None
    status: Optional[str] = None
    reschedule_reason: Optional[str] = None
    rescheduled_from: Optional[date] = None
class VisitReportCreate(BaseModel):
    plan_visit_id: int
    executive_id: int
    doctor_id: int
    visit_date: date
    visit_time: Optional[str] = None
    location: Optional[str] = None
    purpose: Optional[str] = None
    products_discussed: Optional[str] = None
    notes: Optional[str] = None
    doctor_feedback: Optional[str] = None
    next_followup_date: Optional[date] = None
    next_action: Optional[str] = None
    remarks: Optional[str] = None
    follow_up_required: bool = True
    status: Optional[str] = None
    submitted_at: Optional[datetime] = None
class ExecutiveSubmissionReportCreate(BaseModel):
    executive_id: int
    executive_name: Optional[str] = None
    employee_code: Optional[str] = None
    region: Optional[str] = None
    report_date: date
    reporting_type: Optional[str] = "Field"
    recipient_type: Optional[str] = "both"
    manager_id: Optional[int] = None
    manager_name: Optional[str] = None
    regional_manager_id: Optional[int] = None
    regional_manager_name: Optional[str] = None
    total_visits: Optional[int] = 0
    reported_visits: Optional[int] = 0
    summary_notes: Optional[str] = None
    visits_json: Optional[str] = None
    status: Optional[str] = "Submitted"
class ExecutiveSubmissionReportUpdate(BaseModel):
    status: Optional[str] = None
    manager_remarks: Optional[str] = None
    regional_remarks: Optional[str] = None
    summary_notes: Optional[str] = None
class VisitReportUpdate(BaseModel):
    visit_date: Optional[date] = None
    visit_time: Optional[str] = None
    location: Optional[str] = None
    purpose: Optional[str] = None
    products_discussed: Optional[str] = None
    notes: Optional[str] = None
    doctor_feedback: Optional[str] = None
    next_followup_date: Optional[date] = None
    next_action: Optional[str] = None
    remarks: Optional[str] = None
    follow_up_required: Optional[bool] = None
    status: Optional[str] = None
    submitted_at: Optional[datetime] = None
class RejectBody(BaseModel):
    reason: str
    request_changes: bool = False
@app.get("/")
def home():
    return{"message":"Pet Management API is Running"}
@app.post("/pet-parents")
def create_pet_parent(
    data: PetParentCreate,
    db: Session = Depends(get_db)):
    parent = PetParent(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        city=data.city
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    return parent
@app.get("/pet-parents")
def get_pet_parent(db:Session=Depends(get_db)):
    return db.query(PetParent).all()
@app.get("/pet-parents/{parent_id}")
def get_pet_parent(
    parent_id: int,
    db: Session = Depends(get_db)):
    parent = db.query(PetParent).filter(PetParent.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404,detail="Pet parent not found")
    return parent
@app.put("/pet-parents/{parent_id}")
def update_petparent(parent_id: int,data: PetParentCreate,db: Session = Depends(get_db)):
    record = db.query(PetParent).filter(PetParent.id == parent_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="PetParent not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/pet-parents/{parent_id}")
def delete_petparent(parent_id: int,db: Session = Depends(get_db)):
    record = db.query(PetParent).filter(PetParent.id == parent_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="PetParent not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "PetParent deleted successfully",
            "id": parent_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/pets")
def create_pet(data: PetCreate,db: Session = Depends(get_db)):
    parent = db.query(PetParent).filter(
        PetParent.id == data.parent_id).first()
    if not parent:
        raise HTTPException(status_code=404,detail="Pet parent not found")
    pet = Pet(
        parent_id=data.parent_id,
        name=data.name,
        species=data.species,
        breed=data.breed,
        gender=data.gender,
        weight_kg=data.weight_kg,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return model_response(pet)
@app.get("/pets")
def get_pets(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(Pet).all()]
@app.get("/pets/{pet_id}")
def get_pet(pet_id: int,db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(
        Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=404,
            detail="Pet not found")
    return model_response(pet)
@app.put("/pets/{pet_id}")
def update_pet(pet_id: int,data: PetCreate,db: Session = Depends(get_db)):
    record = db.query(Pet).filter(Pet.id == pet_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Pet not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/pets/{pet_id}")
def delete_pet(pet_id: int,db: Session = Depends(get_db)):
    record = db.query(Pet).filter(Pet.id == pet_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Pet not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Pet deleted successfully",
            "id": pet_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/medical-records")
def create_medical_record(data: MedicalRecordCreate,db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(
        Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404,detail="Pet not found")
    record = MedicalRecord(
        pet_id=data.pet_id,
        record_type=data.record_type,
        title=data.title,
        diagnosis=data.diagnosis,
        record_date=data.record_date)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
@app.get("/medical-records")
def get_medical_records(
    db: Session = Depends(get_db)):
    return db.query(MedicalRecord).all()
@app.get("/medical-records/{medical_record_id}")
def get_medical_record_id(medical_record_id: int, db: Session = Depends(get_db)):
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == medical_record_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Medical record not found")
    return record
@app.put("/medical-records/{record_id}")
def update_medicalrecord(record_id: int,data: MedicalRecordCreate,db: Session = Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="MedicalRecord not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/medical-records/{record_id}")
def delete_medicalrecord(
    record_id: int,
    db: Session = Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="MedicalRecord not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "MedicalRecord deleted successfully",
            "id": record_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/vaccinations")
def create_vaccination(data:VaccinationCreate,db: Session =Depends(get_db)):
    pet = db.query(Pet).filter(
        Pet.id ==data.pet_id).first()
    if not pet:
        raise HTTPException(
            status_code=404,detail="Pet Not Found")
    vaccination = Vaccination(
        pet_id=data.pet_id,
        vaccine_name=data.vaccine_name,
        administered_on=data.administered_on,
        next_due_on=data.next_due_on,
        batch_number=data.batch_number
    )
    db.add(vaccination)
    db.commit()
    db.refresh(vaccination)
    return vaccination
@app.get("/vaccinations")
def get_vaccinations(db: Session = Depends(get_db)):
    return db.query(Vaccination).all()
@app.get("/vaccinations/{vaccination_id}")
def get_vaccination_id(vaccination_id: int, db: Session = Depends(get_db)):
    record = db.query(Vaccination).filter(
        Vaccination.id == vaccination_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Vaccination not found")
    return record
@app.put("/vaccinations/{vaccination_id}")
def update_vaccination(vaccination_id: int,data: VaccinationCreate,db: Session = Depends(get_db)):
    record = db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Vaccination not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/vaccinations/{vaccination_id}")
def delete_vaccination(vaccination_id: int,db: Session = Depends(get_db)):
    record = db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Vaccination not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Vaccination deleted successfully",
            "id": vaccination_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/addresses")
def create_address(data: AddressCreate,db: Session = Depends(get_db)):
    parent = db.query(PetParent).filter(
        PetParent.id == data.parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=404,detail="Pet parent not found")
    address = Address(
        parent_id=data.parent_id,
        label=data.label,
        contact_name=data.contact_name,
        line1=data.line1,
        city=data.city,
        pincode=data.pincode,
        is_default=data.is_default
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address
@app.get("/addresses")
def get_addresses(db: Session = Depends(get_db)):
    return db.query(Address).all()
@app.get("/addresses/{address_id}")
def get_address_id(address_id: int, db: Session = Depends(get_db)):
    record = db.query(Address).filter(Address.id == address_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Address not found")
    return record
@app.put("/addresses/{address_id}")
def update_address(address_id: int,data: AddressCreate,db: Session = Depends(get_db)):
    record = db.query(Address).filter(Address.id == address_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Address not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/addresses/{address_id}")
def delete_address(address_id: int,db: Session = Depends(get_db)):
    record = db.query(Address).filter(Address.id == address_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Address not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Address deleted successfully",
            "id": address_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/user-roles")
def create_user_role(data: UserRoleCreate,db: Session = Depends(get_db)):
    user_role = UserRole(
        user_id=data.user_id,
        role=data.role
        )
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role
@app.get("/user-roles")
def get_user_roles(db: Session = Depends(get_db)):
    return db.query(UserRole).all()
@app.get("/user-roles/{role_id}")
def get_role_id(role_id: int, db: Session = Depends(get_db)):
    record = db.query(UserRole).filter(
        UserRole.id == role_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="User role not found")
    return record
@app.put("/user-roles/{role_id}")
def update_userrole(role_id: int,data: UserRoleCreate,db: Session = Depends(get_db)):
    record = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="UserRole not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/user-roles/{role_id}")
def delete_userrole(role_id: int,db: Session = Depends(get_db)):
    record = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not record:
        raise HTTPException(
            status_code=404,
            detail="UserRole not found"
        )
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "UserRole deleted successfully",
            "id": role_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/doctors")
def create_doctor(data: DoctorCreate, db: Session = Depends(get_db)):
    doctor = Doctor(
        name=data.name,
        qualification=data.qualification,
        specializations=data.specializations,
        pincode=data.pincode,
        city=data.city,
        phone=data.phone,
        experience_years=data.experience_years,
        consultation_fee=data.consultation_fee,
        verification_status=data.verification_status,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return model_response(doctor)
@app.get("/doctors")
def get_doctors(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(Doctor).all()]
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int,db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404,detail="Doctor not found")
    return model_response(doctor)
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int,data: DoctorCreate,db: Session = Depends(get_db)):
    record = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Doctor not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int,db: Session = Depends(get_db)):
    record = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Doctor not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Doctor deleted successfully",
            "id": doctor_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/clinics-hospitals")
def create_clinic_hospital(data: ClinicHospitalCreate,db: Session = Depends(get_db)):
    facility = ClinicHospital(
        name=data.name,
        facility_type=data.facility_type,
        phone=data.phone,
        emergency_available=data.emergency_available,
        open_24x7=data.open_24x7,
        verification_status=data.verification_status,
        rating=data.rating
    )
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility
@app.get("/clinics-hospitals")
def get_clinics_hospitals(db: Session = Depends(get_db)):
    return db.query(ClinicHospital).all()
@app.get("/clinics-hospitals/{facility_id}")
def get_clinic_hospital(facility_id: int,db: Session = Depends(get_db)):
    facility = db.query(ClinicHospital).filter(
        ClinicHospital.id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404,detail="Clinic or hospital not found")
    return facility
@app.put("/clinics-hospitals/{facility_id}")
def update_clinichospital(facility_id: int,data: ClinicHospitalCreate,db: Session = Depends(get_db)):
    record = db.query(ClinicHospital).filter(ClinicHospital.id == facility_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="ClinicHospital not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/clinics-hospitals/{facility_id}")
def delete_clinichospital(facility_id: int,db: Session = Depends(get_db)):
    record = db.query(ClinicHospital).filter(ClinicHospital.id == facility_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="ClinicHospital not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "ClinicHospital deleted successfully",
            "id": facility_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/availability-slots")
def create_availability_slot(data: AvailabilitySlotCreate,db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404,detail="Doctor not found")
    slot = AvailabilitySlot(
        doctor_id=data.doctor_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        consultation_type=data.consultation_type,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return model_response(slot)
@app.get("/availability-slots")
def get_availability_slots(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(AvailabilitySlot).all()]
@app.get("/availability-slots/{slot_id}")
def get_availability_slot(slot_id: int,db: Session = Depends(get_db)):
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404,detail="Availability slot not found")
    return model_response(slot)
@app.put("/availability-slots/{slot_id}")
def update_availabilityslot(slot_id: int,data: AvailabilitySlotCreate,db: Session = Depends(get_db)):
    record = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="AvailabilitySlot not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/availability-slots/{slot_id}")
def delete_availabilityslot(slot_id: int,db: Session = Depends(get_db)):
    record = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="AvailabilitySlot not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "AvailabilitySlot deleted successfully",
            "id": slot_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/doctor-documents")
def create_doctor_document(data: DoctorDocumentCreate,db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404,detail="Doctor not found")
    document = DoctorDocument(
        doctor_id=data.doctor_id,
        document_type=data.document_type,
        status=data.status
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
@app.get("/doctor-documents")
def get_doctor_documents(db: Session = Depends(get_db)):
    return db.query(DoctorDocument).all()
@app.get("/doctor-documents/{document_id}")
def get_doctor_document(document_id: int,db: Session = Depends(get_db)):
    document = db.query(DoctorDocument).filter(
        DoctorDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404,detail="Doctor document not found")
    return document
@app.put("/doctor-documents/{document_id}")
def update_doctordocument(document_id: int,data: DoctorDocumentCreate,db: Session = Depends(get_db)):
    record = db.query(DoctorDocument).filter(DoctorDocument.id == document_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="DoctorDocument not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/doctor-documents/{document_id}")
def delete_doctordocument(document_id: int,db: Session = Depends(get_db)):
    record = db.query(DoctorDocument).filter(DoctorDocument.id == document_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="DoctorDocument not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "DoctorDocument deleted successfully",
            "id": document_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/appointments")
def create_appointment(data:AppointmentCreate,db:Session=Depends(get_db)):
    pet =db.query(Pet).filter(Pet.id==data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404 , detail= "Pet Not Found")
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404 , detail="Doctor Not Found")
    appointment = Appointment(
        pet_id = data.pet_id,
        doctor_id = data.doctor_id,
        appointment_date = data.appointment_date,
        appointment_time = data.appointment_time,
        appointment_type = data.appointment_type,
        status = data.status,
        payment_status = data.payment_status,
        consultation_fee=data.consultation_fee
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
@app.get("/appointments")
def get_appointments(db:Session=Depends(get_db)):
    return db.query(Appointment).all()
@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id :int,db:Session = Depends(get_db)):
    appointment =db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404 , detail="Appointment Not Found")
    return appointment
@app.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int,data: AppointmentCreate,db: Session = Depends(get_db)):
    record = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Appointment not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int,db: Session = Depends(get_db)):
    record = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Appointment not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Appointment deleted successfully",
            "id": appointment_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/consultations")
def create_consultation(data:ConsultationCreate,db:Session=Depends(get_db)):
    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404 , detail="Appointment Not Found")
    consultation = Consultation(
        appointment_id = data.appointment_id,
        consultation_mode = data.consultation_mode,
        diagnosis = data.diagnosis,
        follow_up_date = data.follow_up_date
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation
@app.get("/consultations")
def get_consultations(db:Session = Depends(get_db)):
    return db.query(Consultation).all()
@app.get("/consultations/{consultation_id}")
def get_consultation(consultation_id: int, db: Session = Depends(get_db)):
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    return consultation
@app.put("/consultations/{consultation_id}")
def update_consultation(consultation_id: int,data: ConsultationCreate,db: Session = Depends(get_db)):
    record = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Consultation not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/consultations/{consultation_id}")
def delete_consultation(consultation_id: int,db: Session = Depends(get_db)):
    record = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Consultation not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Consultation deleted successfully",
            "id": consultation_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/prescriptions")
def create_prescription(data: PrescriptionCreate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    prescription = Prescription(
        doctor_id=data.doctor_id,
        pet_id=data.pet_id,
        valid_until=data.valid_until
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return prescription
@app.get("/prescriptions")
def get_prescriptions(db:Session = Depends(get_db)):
    return db.query(Prescription).all()
@app.get("/prescriptions/{prescription_id}")
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription
@app.put("/prescriptions/{prescription_id}")
def update_prescription(prescription_id: int,data: PrescriptionCreate,db: Session = Depends(get_db)):
    record = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Prescription not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/prescriptions/{prescription_id}")
def delete_prescription(prescription_id: int,db: Session = Depends(get_db)):
    record = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Prescription not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Prescription deleted successfully",
            "id": prescription_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/service-providers")
def create_service_provider(data: ServiceProviderCreate,db: Session = Depends(get_db)):
    provider = ServiceProvider(
        name=data.name,
        provider_type=data.provider_type,
        phone=data.phone,
        verification_status=data.verification_status,
        rating=data.rating,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return model_response(provider)
@app.get("/service-providers")
def get_service_providers(db:Session = Depends(get_db)):
    return [model_response(item) for item in db.query(ServiceProvider).all()]
@app.get("/service-providers/{provider_id}")
def get_service_provider(provider_id:int , db:Session = Depends(get_db)):
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404 , detail="Provider Not Found")
    return model_response(provider)
@app.put("/service-providers/{provider_id}")
def update_serviceprovider(provider_id: int,data: ServiceProviderCreate,db: Session = Depends(get_db)):
    record = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="ServiceProvider not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/service-providers/{provider_id}")
def delete_serviceprovider(provider_id: int,db: Session = Depends(get_db)):
    record = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="ServiceProvider not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "ServiceProvider deleted successfully",
            "id": provider_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/services")
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(
        title=data.title,
        service_type=data.service_type,
        price=data.price,
        duration_minutes=data.duration_minutes,
        home_service=data.home_service,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return model_response(service)
@app.get("/services")
def get_services(db:Session = Depends(get_db)):
    return [model_response(item) for item in db.query(Service).all()]
@app.get("/services/{service_id}")
def get_service_id(service_id: int, db: Session = Depends(get_db)):
    record = db.query(Service).filter(Service.id == service_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Service not found")
    return record
@app.put("/services/{service_id}")
def update_service(service_id: int,data: ServiceCreate,db: Session = Depends(get_db)):
    record = db.query(Service).filter(Service.id == service_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Service not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/services/{service_id}")
def delete_service(service_id: int,db: Session = Depends(get_db)):
    record = db.query(Service).filter(Service.id == service_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Service not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Service deleted successfully",
            "id": service_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/service-bookings")
def create_service_booking(data: ServiceBookingCreate,db: Session = Depends(get_db)):
    try:
        service = db.query(Service).filter(
            Service.id == data.service_id).first()
        if not service:
            raise HTTPException(status_code=404,detail="Service not found")
        provider = db.query(ServiceProvider).filter(
            ServiceProvider.id == data.provider_id).first()
        if not provider:
            raise HTTPException(status_code=404,detail="Service provider not found")
        pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
        if not pet:
            raise HTTPException(status_code=404,detail="Pet not found")
        booking = ServiceBooking(
            service_id=data.service_id,
            provider_id=data.provider_id,
            pet_id=data.pet_id,
            booking_date=data.booking_date,
            booking_time=data.booking_time,
            price=data.price,
            status=data.status,
            payment_status=data.payment_status
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("ERROR:", str(e))
        raise HTTPException(status_code=500,detail=str(e))
@app.get("/service-bookings")
def get_service_bookings(db: Session = Depends(get_db)):
    return db.query(ServiceBooking).all()
@app.get("/service-bookings/{booking_id}")
def get_service_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(ServiceBooking).filter(
        ServiceBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Service booking not found")
    return booking
@app.put("/service-bookings/{booking_id}")
def update_servicebooking(booking_id: int,data: ServiceBookingCreate,db: Session = Depends(get_db)):
    record = db.query(ServiceBooking).filter(ServiceBooking.id == booking_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="ServiceBooking not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/service-bookings/{booking_id}")
def delete_servicebooking(booking_id: int,db: Session = Depends(get_db)):
    record = db.query(ServiceBooking).filter(ServiceBooking.id == booking_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="ServiceBooking not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "ServiceBooking deleted successfully",
            "id": booking_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/products")
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    product = Product(
        name=data.name,
        price=data.price,
        mrp=data.mrp,
        discount_percent=data.discount_percent,
        pincode=data.pincode,
        stock_quantity=data.stock_quantity,
        is_prescription_required=data.is_prescription_required,
        rating=data.rating,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return model_response(product)
@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(Product).all()]
@app.get("/products/{product_id}")
def get_product_id(product_id: int, db: Session = Depends(get_db)):
    record = db.query(Product).filter(Product.id == product_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Product not found")
    return record
@app.put("/products/{product_id}")
def update_product(product_id: int,data: ProductCreate,db: Session = Depends(get_db)):
    record = db.query(Product).filter(Product.id == product_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Product not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/products/{product_id}")
def delete_product(product_id: int,db: Session = Depends(get_db)):
    record = db.query(Product).filter(Product.id == product_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Product not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Product deleted successfully",
            "id": product_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/inventory")
def create_inventory(data: InventoryCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    seller = db.query(SellerStore).filter(SellerStore.id == data.seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller/store not found")
    inventory = Inventory(
        product_id=data.product_id,
        seller_id=data.seller_id,
        pincode=data.pincode,
        inventory_source=data.inventory_source,
        available_quantity=data.available_quantity,
        reserved_quantity=data.reserved_quantity,
        reorder_level=data.reorder_level
    )
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory
@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    return db.query(Inventory).all()
@app.get("/inventory/{inventory_id}")
def get_inventory_id(inventory_id: int, db: Session = Depends(get_db)):
    record = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Inventory not found")
    return record
@app.put("/inventory/{inventory_id}")
def update_inventory(inventory_id: int,data: InventoryCreate,db: Session = Depends(get_db)):
    record = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Inventory not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/inventory/{inventory_id}")
def delete_inventory(inventory_id: int,db: Session = Depends(get_db)):
    record = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Inventory not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Inventory deleted successfully",
            "id": inventory_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/categories")
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(
        name=data.name,
        slug=data.slug,
        sort_order=data.sort_order,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return model_response(category)
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(Category).all()]
@app.get("/categories/{category_id}")
def get_category_id(category_id: int, db: Session = Depends(get_db)):
    record = db.query(Category).filter(
        Category.id == category_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Category not found")
    return record
@app.put("/categories/{category_id}")
def update_category(category_id: int,data: CategoryCreate,db: Session = Depends(get_db)):
    record = db.query(Category).filter(Category.id == category_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Category not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/categories/{category_id}")
def delete_category(category_id: int,db: Session = Depends(get_db)):
    record = db.query(Category).filter(Category.id == category_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Category not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Category deleted successfully",
            "id": category_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/brands")
def create_brand(data: BrandCreate, db: Session = Depends(get_db)):
    brand = Brand(name=data.name,is_active=yes_no_to_bool(data.is_active))
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return model_response(brand)
@app.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(Brand).all()]
@app.get("/brands/{brand_id}")
def get_brand_id(brand_id: int, db: Session = Depends(get_db)):
    record = db.query(Brand).filter(
        Brand.id == brand_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Brand not found")
    return record
@app.put("/brands/{brand_id}")
def update_brand(brand_id: int,data: BrandCreate,db: Session = Depends(get_db)):
    record = db.query(Brand).filter(Brand.id == brand_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Brand not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/brands/{brand_id}")
def delete_brand(brand_id: int,db: Session = Depends(get_db)):
    record = db.query(Brand).filter(Brand.id == brand_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Brand not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Brand deleted successfully",
            "id": brand_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/seller-stores")
def create_seller_store(data: SellerStoreCreate, db: Session = Depends(get_db)):
    seller = SellerStore(
        business_name=data.business_name,
        seller_type=data.seller_type,
        phone=data.phone,
        commission_rate=data.commission_rate,
        verification_status=data.verification_status,
        rating=data.rating,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(seller)
    db.commit()
    db.refresh(seller)
    return model_response(seller)
@app.get("/seller-stores")
def get_seller_stores(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(SellerStore).all()]
@app.get("/seller-stores/{seller_id}")
def get_seller_id(seller_id: int, db: Session = Depends(get_db)):
    record = db.query(SellerStore).filter(SellerStore.id == seller_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Seller store not found")
    return record
@app.put("/seller-stores/{seller_id}")
def update_sellerstore(seller_id: int,data: SellerStoreCreate,db: Session = Depends(get_db)):
    record = db.query(SellerStore).filter(SellerStore.id == seller_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="SellerStore not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/seller-stores/{seller_id}")
def delete_sellerstore(seller_id: int,db: Session = Depends(get_db)):
    record = db.query(SellerStore).filter(SellerStore.id == seller_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="SellerStore not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "SellerStore deleted successfully",
            "id": seller_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/warehouses")
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db)):
    seller = db.query(SellerStore).filter(SellerStore.id == data.seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller/store not found")
    warehouse = Warehouse(
        name=data.name,
        seller_id=data.seller_id,
        is_zenve_owned=data.is_zenve_owned,
        contact_phone=data.contact_phone,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return model_response(warehouse)
@app.get("/warehouses")
def get_warehouses(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(Warehouse).all()]
@app.get("/warehouses/{warehouse_id}")
def get_warehouse_id(warehouse_id: int, db: Session = Depends(get_db)):
    record = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Warehouse not found")
    return record
@app.put("/warehouses/{warehouse_id}")
def update_warehouse(warehouse_id: int,data: WarehouseCreate,db: Session = Depends(get_db)):
    record = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Warehouse not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: int,db: Session = Depends(get_db)):
    record = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Warehouse not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Warehouse deleted successfully",
            "id": warehouse_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/carts")
def create_cart(data: CartCreate, db: Session = Depends(get_db)):
    cart = Cart(user_id=data.user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart
@app.get("/carts")
def get_carts(db: Session = Depends(get_db)):
    return db.query(Cart).all()
@app.get("/carts/{cart_id}")
def get_cart_id(cart_id: int, db: Session = Depends(get_db)):
    record = db.query(Cart).filter(Cart.id == cart_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Cart not found")
    return record
@app.put("/carts/{cart_id}")
def update_cart(cart_id: int,data: CartCreate,db: Session = Depends(get_db)):
    record = db.query(Cart).filter(Cart.id == cart_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Cart not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/carts/{cart_id}")
def delete_cart(cart_id: int,db: Session = Depends(get_db)):
    record = db.query(Cart).filter(Cart.id == cart_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Cart not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Cart deleted successfully",
            "id": cart_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/cart-items")
def create_cart_item(data: CartItemCreate, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.id == data.cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    cart_item = CartItem(
        cart_id=data.cart_id,
        product_id=data.product_id,
        quantity=data.quantity,
        price=data.price,
        saved_for_later=data.saved_for_later
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item
@app.get("/cart-items")
def get_cart_items(db: Session = Depends(get_db)):
    return db.query(CartItem).all()
@app.get("/cart-items/{cart_item_id}")
def get_cart_item_id(cart_item_id: int, db: Session = Depends(get_db)):
    record = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Cart item not found")
    return record
@app.put("/cart-items/{cart_item_id}")
def update_cartitem(cart_item_id: int,data: CartItemCreate,db: Session = Depends(get_db)):
    record = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="CartItem not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/cart-items/{cart_item_id}")
def delete_cartitem(cart_item_id: int,db: Session = Depends(get_db)):
    record = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="CartItem not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "CartItem deleted successfully",
            "id": cart_item_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/orders")
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    order = Order(
        order_number=data.order_number,
        total_amount=data.total_amount,
        status=data.status,
        payment_status=data.payment_status
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
@app.get("/orders")
def get_order(db :Session =Depends(get_db)):
    return db.query(Order).all()
@app.get("/orders/{order_id}")
def get_order_id(order_id: int, db: Session = Depends(get_db)):
    record = db.query(Order).filter(Order.id == order_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Order not found")
    return record
@app.put("/orders/{order_id}")
def update_order(order_id: int,data: OrderCreate,db: Session = Depends(get_db)):
    record = db.query(Order).filter(Order.id == order_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Order not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/orders/{order_id}")
def delete_order(order_id: int,db: Session = Depends(get_db)):
    record = db.query(Order).filter(Order.id == order_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Order not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Order deleted successfully",
            "id": order_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/order-items")
def create_order_item(data: OrderItemCreate , db : Session=Depends(get_db)):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        return HTTPException(status_code=404 , detail="order not found")
    item = OrderItem(
        order_id = data.order_id,
        product_name = data.product_name,
        quantity = data.quantity,
        unit_price = data.unit_price,
        total_price = data.total_price,
        status = data.status
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
@app.get("/order-items")
def get_order_items(db :Session = Depends(get_db)):
    return db.query(OrderItem).all()
@app.get("/order-items/{item_id}")
def get_item_id(item_id: int, db: Session = Depends(get_db)):
    record = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Order item not found")
    return record
@app.put("/order-items/{item_id}")
def update_orderitem(item_id: int,data: OrderItemCreate,db: Session = Depends(get_db)):
    record = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="OrderItem not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/order-items/{item_id}")
def delete_orderitem(item_id: int,db: Session = Depends(get_db)):
    record = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="OrderItem not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "OrderItem deleted successfully",
            "id": item_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/deliveries")
def create_delivery(data: DeliveryCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    delivery = Delivery(**data.model_dump())
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery
@app.get("/deliveries")
def get_deliveries(db: Session = Depends(get_db)):
    return db.query(Delivery).all()
@app.get("/deliveries/{delivery_id}")
def get_delivery_id(delivery_id: int, db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Delivery not found")
    return record
@app.put("/deliveries/{delivery_id}")
def update_delivery(delivery_id: int,data: DeliveryCreate,db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Delivery not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/deliveries/{delivery_id}")
def delete_delivery(delivery_id: int,db: Session = Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Delivery not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Delivery deleted successfully",
            "id": delivery_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/payments")
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404,detail="Order not found")
    payment = Payment(
        order_id=data.order_id,
        amount=data.amount,
        gateway=data.gateway,
        status=data.status,
        webhook_verified=data.webhook_verified
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
@app.get("/payments")
def get_payment(db:Session=Depends(get_db)):
    return db.query(Payment).all()
@app.get("/payments/{payment_id}")
def get_payment_id(payment_id: int, db: Session = Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == payment_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Payment not found")
    return record
@app.put("/payments/{payment_id}")
def update_payment(payment_id: int,data: PaymentCreate,db: Session = Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == payment_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Payment not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int,db: Session = Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == payment_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Payment not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Payment deleted successfully",
            "id": payment_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/refunds")
def create_refund(data: RefundCreate, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == data.payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    refund = Refund(**data.model_dump())
    db.add(refund)
    db.commit()
    db.refresh(refund)
    return refund
@app.get("/refunds")
def get_refunds(db: Session = Depends(get_db)):
    return db.query(Refund).all()
@app.get("/refunds/{refund_id}")
def get_refund_id(refund_id: int, db: Session = Depends(get_db)):
    record = db.query(Refund).filter(Refund.id == refund_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Refund not found")
    return record
@app.put("/refunds/{refund_id}")
def update_refund(refund_id: int,data: RefundCreate,db: Session = Depends(get_db)):
    record = db.query(Refund).filter(Refund.id == refund_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Refund not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/refunds/{refund_id}")
def delete_refund(refund_id: int,db: Session = Depends(get_db)):
    record = db.query(Refund).filter(Refund.id == refund_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Refund not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Refund deleted successfully",
            "id": refund_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/payouts")
def create_payout(data: PayoutCreate, db: Session = Depends(get_db)):
    payout = Payout(**data.model_dump())
    db.add(payout)
    db.commit()
    db.refresh(payout)
    return payout
@app.get("/payouts")
def get_payouts(db: Session = Depends(get_db)):
    return db.query(Payout).all()
@app.get("/payouts/{payout_id}")
def get_payout_id(payout_id: int, db: Session = Depends(get_db)):
    record = db.query(Payout).filter(Payout.id == payout_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Payout not found")
    return record
@app.put("/payouts/{payout_id}")
def update_payout(payout_id: int,data: PayoutCreate,db: Session = Depends(get_db)):
    record = db.query(Payout).filter(Payout.id == payout_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Payout not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/payouts/{payout_id}")
def delete_payout(payout_id: int,db: Session = Depends(get_db)):
    record = db.query(Payout).filter(Payout.id == payout_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Payout not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Payout deleted successfully",
            "id": payout_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/commission-rules")
def create_commission_rule(data: CommissionRuleCreate, db: Session = Depends(get_db)):
    rule_data = data.model_dump()
    rule_data["is_active"] = yes_no_to_bool(rule_data["is_active"])
    rule = CommissionRule(**rule_data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return model_response(rule)
@app.get("/commission-rules")
def get_commission_rules(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(CommissionRule).all()]
@app.get("/commission-rules/{rule_id}")
def get_rule_id(rule_id: int, db: Session = Depends(get_db)):
    record = db.query(CommissionRule).filter(
        CommissionRule.id == rule_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Commission rule not found")
    return model_response(record)
@app.put("/commission-rules/{rule_id}")
def update_commissionrule(rule_id: int,data: CommissionRuleCreate,db: Session = Depends(get_db)):
    record = db.query(CommissionRule).filter(CommissionRule.id == rule_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="CommissionRule not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/commission-rules/{rule_id}")
def delete_commissionrule(rule_id: int,db: Session = Depends(get_db)):
    record = db.query(CommissionRule).filter(CommissionRule.id == rule_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="CommissionRule not found" )
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "CommissionRule deleted successfully",
            "id": rule_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/gps-locations")
def create_gps_location(data: GPSLocationCreate,db: Session = Depends(get_db)):
    location = GPSLocation(**data.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location
@app.get("/gps-locations")
def get_gps_locations(db: Session = Depends(get_db)):
    return db.query(GPSLocation).all()
@app.get("/gps-locations/{location_id}")
def get_gps_location(location_id: int,db: Session = Depends(get_db)):
    location = db.query(GPSLocation).filter(GPSLocation.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404,detail="GPS location not found")
    return location
@app.put("/gps-locations/{location_id}")
def update_gpslocation(location_id: int,data: GPSLocationCreate,db: Session = Depends(get_db)):
    record = db.query(GPSLocation).filter(GPSLocation.id == location_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="GPSLocation not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/gps-locations/{location_id}")
def delete_gpslocation(location_id: int,db: Session = Depends(get_db)):
    record = db.query(GPSLocation).filter(GPSLocation.id == location_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="GPSLocation not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "GPSLocation deleted successfully",
            "id": location_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/reviews")
def create_review(data: ReviewCreate,db: Session = Depends(get_db)):
    review = Review(**data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
@app.get("/reviews")
def get_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()
@app.get("/reviews/{review_id}")
def get_review(review_id: int,db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404,detail="Review not found")
    return review
@app.put("/reviews/{review_id}")
def update_review(review_id: int,data: ReviewCreate,db: Session = Depends(get_db)):
    record = db.query(Review).filter(Review.id == review_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Review not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/reviews/{review_id}")
def delete_review(review_id: int,db: Session = Depends(get_db)):
    record = db.query(Review).filter(Review.id == review_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Review not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Review deleted successfully",
            "id": review_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/notifications")
def create_notification(data: NotificationCreate,db: Session = Depends(get_db)):
    notification = Notification(**data.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
@app.get("/notifications")
def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()
@app.get("/notifications/{notification_id}")
def get_notification(notification_id: int,db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404,detail="Notification not found")
    return notification
@app.put("/notifications/{notification_id}")
def update_notification(notification_id: int,data: NotificationCreate,db: Session = Depends(get_db)):
    record = db.query(Notification).filter(Notification.id == notification_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Notification not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int,db: Session = Depends(get_db)):
    record = db.query(Notification).filter(Notification.id == notification_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Notification not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Notification deleted successfully",
            "id": notification_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/vendor-membership-plans")
def create_vendor_membership_plan(data: VendorMembershipPlanCreate,db: Session = Depends(get_db)):
    plan_data = data.model_dump()
    plan_data["is_active"] = yes_no_to_bool(plan_data["is_active"])
    plan = VendorMembershipPlan(**plan_data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return model_response(plan)
@app.get("/vendor-membership-plans")
def get_vendor_membership_plans(db: Session = Depends(get_db)):
    return [model_response(item) for item in db.query(VendorMembershipPlan).all()]
@app.get("/vendor-membership-plans/{plan_id}")
def get_vendor_membership_plan(plan_id: int,db: Session = Depends(get_db)):
    plan = db.query(VendorMembershipPlan).filter(VendorMembershipPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404,detail="Vendor plan not found")
    return model_response(plan)
@app.put("/vendor-membership-plans/{plan_id}")
def update_vendor_membership_plan(plan_id: int,data: VendorMembershipPlanCreate,db: Session = Depends(get_db)):
    record = db.query(VendorMembershipPlan).filter(VendorMembershipPlan.id == plan_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="VendorVendorMembershipPlan not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/vendor-membership-plans/{plan_id}")
def delete_vendor_membership_plan(plan_id: int,db: Session = Depends(get_db)):
    record = db.query(VendorMembershipPlan).filter(VendorMembershipPlan.id == plan_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="VendorVendorMembershipPlan not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "VendorMembershipPlan deleted successfully",
            "id": plan_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/plan-benefits")
def create_plan_benefit(data: PlanBenefitCreate,db: Session = Depends(get_db)):
    plan = db.query(VendorMembershipPlan).filter(VendorMembershipPlan.id == data.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404,detail="Vendor plan not found")
    benefit = PlanBenefit(**data.model_dump())
    db.add(benefit)
    db.commit()
    db.refresh(benefit)
    return benefit
@app.get("/plan-benefits")
def get_plan_benefits(db: Session = Depends(get_db)):
    return db.query(PlanBenefit).all()
@app.get("/plan-benefits/{benefit_id}")
def get_plan_benefit(benefit_id: int,db: Session = Depends(get_db)):
    benefit = db.query(PlanBenefit).filter(PlanBenefit.id == benefit_id).first()
    if not benefit:
        raise HTTPException(status_code=404,detail="Plan benefit not found")
    return benefit
@app.put("/plan-benefits/{benefit_id}")
def update_planbenefit(benefit_id: int,data: PlanBenefitCreate,db: Session = Depends(get_db)):
    record = db.query(PlanBenefit).filter(PlanBenefit.id == benefit_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="PlanBenefit not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/plan-benefits/{benefit_id}")
def delete_planbenefit(benefit_id: int,db: Session = Depends(get_db)):
    record = db.query(PlanBenefit).filter(PlanBenefit.id == benefit_id).first()
    if not record:
        raise HTTPException( status_code=404,detail="PlanBenefit not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "PlanBenefit deleted successfully",
            "id": benefit_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/vendors")
def create_vendor(data: VendorCreate,db: Session = Depends(get_db)):
    plan = db.query(VendorMembershipPlan).filter(
        VendorMembershipPlan.id == data.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404,detail="Vendor plan not found")
    vendor = Vendor(**data.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor
@app.get("/vendors")
def get_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).all()
@app.get("/vendors/{vendor_id}")
def get_vendor(vendor_id: int,db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404,detail="Vendor not found")
    return vendor
@app.put("/vendors/{vendor_id}")
def update_vendor(vendor_id: int,data: VendorCreate,db: Session = Depends(get_db)):
    record = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Vendor not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e) )
@app.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int,db: Session = Depends(get_db)):
    record = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="Vendor not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Vendor deleted successfully",
            "id": vendor_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/support-tickets")
def create_support_ticket(data: SupportTicketCreate,db: Session = Depends(get_db)):
    ticket = SupportTicket(**data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
@app.get("/support-tickets")
def get_support_tickets(db: Session = Depends(get_db)):
    return db.query(SupportTicket).all()
@app.get("/support-tickets/{ticket_id}")
def get_support_ticket(ticket_id: int,db: Session = Depends(get_db)):
    ticket = db.query(SupportTicket).filter(
        SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404,detail="Support ticket not found")
    return ticket
@app.put("/support-tickets/{ticket_id}")
def update_supportticket(ticket_id: int,data: SupportTicketCreate,db: Session = Depends(get_db)):
    record = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="SupportTicket not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/support-tickets/{ticket_id}")
def delete_supportticket(ticket_id: int,db: Session = Depends(get_db)):
    record = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="SupportTicket not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "SupportTicket deleted successfully",
            "id": ticket_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/geocoding-cache")
def create_geocoding_cache(data: GeocodingCacheCreate,db: Session = Depends(get_db)):
    cache = GeocodingCache(**data.model_dump())
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache
@app.get("/geocoding-cache")
def get_geocoding_cache(db: Session = Depends(get_db)):
    return db.query(GeocodingCache).all()
@app.get("/geocoding-cache/{cache_id}")
def get_geocoding_cache_by_id(cache_id: int,db: Session = Depends(get_db)):
    cache = db.query(GeocodingCache).filter(
        GeocodingCache.id == cache_id).first()
    if not cache:
        raise HTTPException(status_code=404,detail="Geocoding cache not found")
    return cache
@app.put("/geocoding-cache/{cache_id}")
def update_geocodingcache(cache_id: int,data: GeocodingCacheCreate,db: Session = Depends(get_db)):
    record = db.query(GeocodingCache).filter(GeocodingCache.id == cache_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="GeocodingCache not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/geocoding-cache/{cache_id}")
def delete_geocodingcache(cache_id: int,db: Session = Depends(get_db)):
    record = db.query(GeocodingCache).filter(GeocodingCache.id == cache_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="GeocodingCache not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "GeocodingCache deleted successfully",
            "id": cache_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.post("/audit-logs")
def create_audit_log(data: AuditLogCreate,db: Session = Depends(get_db)):
    log = AuditLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
@app.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).all()
@app.get("/audit-logs/{log_id}")
def get_audit_log(log_id: int,db: Session = Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404,detail="Audit log not found")
    return log
@app.put("/audit-logs/{log_id}")
def update_auditlog(log_id: int,data: AuditLogCreate,db: Session = Depends(get_db)):
    record = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="AuditLog not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400,detail=str(e))
@app.delete("/audit-logs/{log_id}")
def delete_auditlog(log_id: int,db: Session = Depends(get_db)):
    record = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not record:
        raise HTTPException(status_code=404,detail="AuditLog not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "AuditLog deleted successfully",
            "id": log_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/regional-managers")
def create_regional_manager(data: RegionalManagerCreate,db: Session = Depends(get_db)):
    existing = db.query(RegionalManager).filter(RegionalManager.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400,detail="Regional manager code already exists")
    manager = RegionalManager(
        name=data.name,
        code=data.code,
        phone=data.phone,
        email=data.email,
        region=data.region,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return model_response(manager)
@app.get("/regional-managers")
def get_regional_managers(db: Session = Depends(get_db)):
    managers = db.query(RegionalManager).all()
    return [
        model_response(manager)
        for manager in managers
    ]
@app.get("/regional-managers/{manager_id}")
def get_regional_manager(manager_id: int,db: Session = Depends(get_db)):
    manager = db.query(RegionalManager).filter(RegionalManager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404,detail="Regional manager not found")
    return model_response(manager)
@app.put("/regional-managers/{manager_id}")
def update_regional_manager(manager_id: int,data: RegionalManagerCreate,db: Session = Depends(get_db)):
    manager = db.query(RegionalManager).filter(RegionalManager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404,detail="Regional manager not found")
    manager.name = data.name
    manager.code = data.code
    manager.phone = data.phone
    manager.email = data.email
    manager.region = data.region
    manager.is_active = yes_no_to_bool(data.is_active)
    db.commit()
    db.refresh(manager)
    return model_response(manager)
@app.delete("/regional-managers/{manager_id}")
def delete_regional_manager(manager_id: int,db: Session = Depends(get_db)):
    manager = db.query(RegionalManager).filter(RegionalManager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404,detail="Regional manager not found")
    db.delete(manager)
    db.commit()
    return {
        "message": "Regional manager deleted successfully",
        "id": manager_id
    }
@app.post("/sales-managers")
def create_sales_manager(data: SalesManagerCreate,db: Session = Depends(get_db)):
    existing = db.query(SalesManager).filter(SalesManager.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400,detail="Sales manager code already exists")
    manager = SalesManager(
        name=data.name,
        code=data.code,
        phone=data.phone,
        email=data.email,
        region=data.region,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    return model_response(manager)
@app.get("/sales-managers")
def get_sales_managers(db: Session = Depends(get_db)):
    managers = db.query(SalesManager).all()
    return [
        model_response(manager)
        for manager in managers
    ]
@app.get("/sales-managers/{manager_id}")
def get_sales_manager(manager_id: int,db: Session = Depends(get_db)):
    manager = db.query(SalesManager).filter(SalesManager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404,detail="Sales manager not found")
    return model_response(manager)
@app.put("/sales-managers/{manager_id}")
def update_sales_manager(manager_id: int,data: SalesManagerCreate,db: Session = Depends(get_db)):
    manager = db.query(SalesManager).filter(SalesManager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404,detail="Sales manager not found")
    manager.name = data.name
    manager.code = data.code
    manager.phone = data.phone
    manager.email = data.email
    manager.region = data.region
    manager.is_active = yes_no_to_bool(data.is_active)
    db.commit()
    db.refresh(manager)
    return model_response(manager)
@app.delete("/sales-managers/{manager_id}")
def delete_sales_manager(manager_id: int,db: Session = Depends(get_db)):
    manager = db.query(SalesManager).filter(SalesManager.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404,detail="Sales manager not found")
    db.delete(manager)
    db.commit()
    return {
        "message": "Sales manager deleted successfully",
        "id": manager_id
    }
@app.post("/sales-executives")
def create_sales_executive(data: SalesExecutiveCreate,db: Session = Depends(get_db)):
    executive = SalesExecutive(
        name=data.name,
        code=data.code,
        phone=data.phone,
        email=data.email,
        region=data.region,
        city=data.city,
        monthly_target=data.monthly_target,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(executive)
    db.commit()
    db.refresh(executive)
    return model_response(executive)
@app.get("/sales-executives")
def get_sales_executives(db: Session = Depends(get_db)):
    return [
        model_response(item)
        for item in db.query(SalesExecutive).all()
    ]
@app.get("/sales-executives/{executive_id}")
def get_sales_executive(executive_id: int,db: Session = Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == executive_id).first()
    if not executive:
        raise HTTPException(status_code=404,detail="Sales executive not found")
    return model_response(executive)
@app.put("/sales-executives/{executive_id}")
def update_sales_executive(executive_id: int,data: SalesExecutiveCreate,db: Session = Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == executive_id).first()
    if not executive:
        raise HTTPException( status_code=404, detail="Sales executive not found")
    update_data = data.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        update_data["is_active"] = yes_no_to_bool(
            update_data["is_active"]
        )
    for field, value in update_data.items():
        setattr(executive, field, value)
    db.commit()
    db.refresh(executive)
    return model_response(executive)
@app.delete("/sales-executives/{executive_id}")
def delete_sales_executive(executive_id: int,db: Session = Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == executive_id).first()
    if not executive:
        raise HTTPException(status_code=404,detail="Sales executive not found")
    db.delete(executive)
    db.commit()
    return {
        "message": "Sales executive deleted successfully",
        "id": executive_id
    }
@app.post("/pincode-coverages")
def create_pincode_coverage(data: PincodeCoverageCreate,db: Session = Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == data.executive_id).first()
    if not executive:
        raise HTTPException(status_code=404,detail="Sales executive not found")
    coverage = PincodeCoverage(
        executive_id=data.executive_id,
        pincode=data.pincode,
        city=data.city,
        state=data.state
    )
    db.add(coverage)
    db.commit()
    db.refresh(coverage)
    return coverage
@app.get("/pincode-coverages")
def get_pincode_coverages(db: Session = Depends(get_db)):
    return db.query(PincodeCoverage).all()
@app.get("/pincode-coverages/{coverage_id}")
def get_pincode_coverage(coverage_id: int,db: Session = Depends(get_db)):
    coverage = db.query(PincodeCoverage).filter(PincodeCoverage.id == coverage_id).first()
    if not coverage:
        raise HTTPException(status_code=404,detail="Pincode coverage not found")
    return coverage
@app.put("/pincode-coverages/{coverage_id}")
def update_pincode_coverage(coverage_id: int,data: PincodeCoverageCreate,db: Session = Depends(get_db)):
    coverage = db.query(PincodeCoverage).filter(PincodeCoverage.id == coverage_id).first()
    if not coverage:
        raise HTTPException(
            status_code=404,
            detail="Pincode coverage not found"
        )
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == data.executive_id).first()
    if not executive:
        raise HTTPException(status_code=404,detail="Sales executive not found")
    coverage.executive_id = data.executive_id
    coverage.pincode = data.pincode
    coverage.city = data.city
    coverage.state = data.state
    db.commit()
    db.refresh(coverage)
    return coverage
@app.delete("/pincode-coverages/{coverage_id}")
def delete_pincode_coverage(coverage_id: int,db: Session = Depends(get_db)):
    coverage = db.query(PincodeCoverage).filter(PincodeCoverage.id == coverage_id).first()
    if not coverage:
        raise HTTPException(status_code=404,detail="Pincode coverage not found")
    db.delete(coverage)
    db.commit()
    return {
        "message": "Pincode coverage deleted successfully",
        "id": coverage_id
    }
@app.post("/executive-tasks")
def create_executive_task(data: ExecutiveTaskCreate,db: Session = Depends(get_db)):
    task = ExecutiveTask(
        title=data.title,
        task_type=data.task_type,
        entity_type=data.entity_type,
        pincode=data.pincode,
        priority=data.priority,
        status=data.status,
        due_date=data.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
@app.get("/executive-tasks")
def get_executive_tasks(db: Session = Depends(get_db)):
    return db.query(ExecutiveTask).all()
@app.get("/executive-tasks/{task_id}")
def get_executive_task(task_id: int,db: Session = Depends(get_db)):
    task = db.query(ExecutiveTask).filter(ExecutiveTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404,detail="Executive task not found")
    return task
@app.put("/executive-tasks/{task_id}")
def update_executive_task(task_id: int,data: ExecutiveTaskCreate,db: Session = Depends(get_db)):
    task = db.query(ExecutiveTask).filter(ExecutiveTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Executive task not found"
        )
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task
@app.delete("/executive-tasks/{task_id}")
def delete_executive_task(task_id: int,db: Session = Depends(get_db)):
    task = db.query(ExecutiveTask).filter(ExecutiveTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404,detail="Executive task not found")
    db.delete(task)
    db.commit()
    return {
        "message": "Executive task deleted successfully",
        "id": task_id
    }
@app.post("/executive-alerts")
def create_executive_alert(data: ExecutiveAlertCreate,db: Session = Depends(get_db)):
    alert = ExecutiveAlert(
        title=data.title,
        severity=data.severity,
        entity_type=data.entity_type,
        pincode=data.pincode,
        is_read=data.is_read
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
@app.get("/executive-alerts")
def get_executive_alerts(db: Session = Depends(get_db)):
    return db.query(ExecutiveAlert).all()
@app.get("/executive-alerts/{alert_id}")
def get_executive_alert(alert_id: int,db: Session = Depends(get_db)):
    alert = db.query(ExecutiveAlert).filter(ExecutiveAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404,detail="Executive alert not found")
    return alert
@app.put("/executive-alerts/{alert_id}")
def update_executive_alert(alert_id: int,data: ExecutiveAlertCreate,db: Session = Depends(get_db)):
    alert = db.query(ExecutiveAlert).filter(ExecutiveAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404,detail="Executive alert not found")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert
@app.delete("/executive-alerts/{alert_id}")
def delete_executive_alert(alert_id: int,db: Session = Depends(get_db)):
    alert = db.query(ExecutiveAlert).filter(ExecutiveAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404,detail="Executive alert not found")
    db.delete(alert)
    db.commit()
    return {
        "message": "Executive alert deleted successfully",
        "id": alert_id
    }
@app.post("/monthly-plans")
def create_monthly_plan(data: MonthlyPlanCreate, db: Session = Depends(get_db)):
    plan = MonthlyPlan(**data.model_dump())
    db.add(plan)
    try:
        db.commit()
        db.refresh(plan)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return plan_response(plan)
@app.get("/monthly-plans")
def get_monthly_plans(
    executive_id: Optional[int] = None,
    month_key: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(MonthlyPlan)
    if executive_id is not None:
        q = q.filter(MonthlyPlan.executive_id == executive_id)
    if month_key is not None:
        q = q.filter(MonthlyPlan.month_key == month_key)
    if status is not None:
        q = q.filter(MonthlyPlan.status == status)
    return [plan_response(p) for p in q.all()]
@app.get("/monthly-plans/{plan_id}")
def get_monthly_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    return plan_response(plan)
@app.put("/monthly-plans/{plan_id}")
def update_monthly_plan(plan_id: int, data: MonthlyPlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(plan, field, value)
    try:
        db.commit()
        db.refresh(plan)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return plan_response(plan)
@app.delete("/monthly-plans/{plan_id}")
def delete_monthly_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    # Cascade delete associated visits
    db.query(PlanVisit).filter(PlanVisit.plan_id == plan_id).delete()
    db.delete(plan)
    db.commit()
    return {"message": "Monthly plan and visits deleted", "id": plan_id}
@app.post("/monthly-plans/{plan_id}/submit")
def submit_monthly_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    plan.status = "Submitted"
    plan.submitted_at = datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)
    db.commit()
    db.refresh(plan)
    return plan_response(plan)
def _normalize_approvers(existing_str: Optional[str], new_approver: Optional[str]) -> str:
    if not new_approver:
        return existing_str or "Manager"
    existing_items = [x.strip() for x in (existing_str or "").split(",") if x.strip()]    
    cleaned = []
    has_sales_mgr = any("(Sales Manager)" in x for x in existing_items + [new_approver])
    has_regional_mgr = any("(Regional Manager)" in x for x in existing_items + [new_approver])
    for item in existing_items:
        if (item == "Emily" or item == "Manager") and has_sales_mgr:
            continue
        if (item == "John" or item == "Manager") and has_regional_mgr:
            continue
        if item not in cleaned:
            cleaned.append(item)            
    if new_approver not in cleaned:
        cleaned.append(new_approver)
    return ", ".join(cleaned)
@app.post("/monthly-plans/{plan_id}/approve")
def approve_monthly_plan(plan_id: int,approved_by: Optional[str] = "Manager",db: Session = Depends(get_db),):
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    plan.status = "Approved"
    plan.approved_at = datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)
    plan.approved_by = _normalize_approvers(plan.approved_by, approved_by)
    plan.rejection_reason = None
    db.commit()
    db.refresh(plan)
    return plan_response(plan)
@app.post("/monthly-plans/{plan_id}/reject")
def reject_monthly_plan(plan_id: int, body: RejectBody, db: Session = Depends(get_db)):
    plan = db.query(MonthlyPlan).filter(MonthlyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Monthly plan not found")
    plan.status = "Draft" if body.request_changes else "Rejected"
    plan.rejection_reason = body.reason
    plan.approved_by = None
    plan.approved_at = None
    db.commit()
    db.refresh(plan)
    return plan_response(plan)
@app.post("/plan-visits")
def create_plan_visit(data: PlanVisitCreate, db: Session = Depends(get_db)):
    visit = PlanVisit(**data.model_dump())
    db.add(visit)
    try:
        db.commit()
        db.refresh(visit)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return plan_response(visit)
@app.post("/plan-visits/bulk")
def bulk_create_plan_visits(visits: list[PlanVisitCreate],db: Session = Depends(get_db),):
    objs = [PlanVisit(**v.model_dump()) for v in visits]
    db.bulk_save_objects(objs)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    if visits:
        plan_id = visits[0].plan_id
        exec_id = visits[0].executive_id
        rows = db.query(PlanVisit).filter(PlanVisit.plan_id == plan_id,PlanVisit.executive_id == exec_id,).all()
        return [plan_response(r) for r in rows]
    return []
@app.get("/plan-visits")
def get_plan_visits(
    plan_id: Optional[int] = None,
    executive_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(PlanVisit)
    if plan_id is not None:
        q = q.filter(PlanVisit.plan_id == plan_id)
    if executive_id is not None:
        q = q.filter(PlanVisit.executive_id == executive_id)
    if doctor_id is not None:
        q = q.filter(PlanVisit.doctor_id == doctor_id)
    if status:
        q = q.filter(PlanVisit.status == status)
    return [plan_response(v) for v in q.all()]
@app.get("/plan-visits/{visit_id}")
def get_plan_visit(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(PlanVisit).filter(PlanVisit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Plan visit not found")
    return plan_response(visit)
@app.put("/plan-visits/{visit_id}")
def update_plan_visit(visit_id: int, data: PlanVisitUpdate, db: Session = Depends(get_db)):
    visit = db.query(PlanVisit).filter(PlanVisit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Plan visit not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(visit, field, value)
    try:
        db.commit()
        db.refresh(visit)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return plan_response(visit)
@app.delete("/plan-visits/{visit_id}")
def delete_plan_visit(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(PlanVisit).filter(PlanVisit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Plan visit not found")
    db.delete(visit)
    db.commit()
    return {"message": "Plan visit deleted", "id": visit_id}
@app.post("/visit-reports")
def create_visit_report(data: VisitReportCreate, db: Session = Depends(get_db)):
    report = VisitReport(**data.model_dump())
    if data.status == "Submitted" and not report.submitted_at:
        report.submitted_at = datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)
    db.add(report)
    try:
        db.commit()
        db.refresh(report)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    if data.status == "Submitted":
        visit = db.query(PlanVisit).filter(PlanVisit.id == data.plan_visit_id).first()
        if visit:
            visit.status = "Completed"
            db.commit()
    return plan_response(report)
@app.get("/visit-reports")
def get_visit_reports(
    plan_visit_id: Optional[int] = None,
    executive_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(VisitReport)
    if plan_visit_id is not None:
        q = q.filter(VisitReport.plan_visit_id == plan_visit_id)
    if executive_id is not None:
        q = q.filter(VisitReport.executive_id == executive_id)
    if doctor_id is not None:
        q = q.filter(VisitReport.doctor_id == doctor_id)
    return [plan_response(r) for r in q.all()]
@app.get("/visit-reports/{report_id}")
def get_visit_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(VisitReport).filter(VisitReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Visit report not found")
    return plan_response(report)
@app.put("/visit-reports/{report_id}")
def update_visit_report(report_id: int, data: VisitReportUpdate, db: Session = Depends(get_db)):
    report = db.query(VisitReport).filter(VisitReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Visit report not found")
    updates = data.model_dump(exclude_unset=True)
    if updates.get("status") == "Submitted" and not report.submitted_at:
        updates["submitted_at"] = datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)
    for field, value in updates.items():
        setattr(report, field, value)
    try:
        db.commit()
        db.refresh(report)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    if updates.get("status") == "Submitted":
        visit = db.query(PlanVisit).filter(PlanVisit.id == report.plan_visit_id).first()
        if visit:
            visit.status = "Completed"
            db.commit()
    return plan_response(report)
@app.delete("/visit-reports/{report_id}")
def delete_visit_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(VisitReport).filter(VisitReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Visit report not found")
    db.delete(report)
    db.commit()
    return {"message": "Visit report deleted", "id": report_id}
@app.get("/plan-stats/{executive_id}")
def get_plan_stats(executive_id: int,month_key: Optional[str] = None,db: Session = Depends(get_db),):
    q = db.query(MonthlyPlan).filter(MonthlyPlan.executive_id == executive_id)
    if month_key:
        q = q.filter(MonthlyPlan.month_key == month_key)
    plan = q.order_by(MonthlyPlan.id.desc()).first()
    if not plan:
        return {"has_plan": False, "total_doctors": 0, "completed": 0, "pending": 0, "completion_pct": 0, "plan_status": None}
    visits = db.query(PlanVisit).filter(PlanVisit.plan_id == plan.id).all()
    total = len(visits)
    completed = sum(1 for v in visits if v.status == "Completed")
    pending = total - completed
    pct = round((completed / total * 100)) if total > 0 else 0
    return {
        "has_plan": True,
        "plan_id": plan.id,
        "month_key": plan.month_key,
        "month_label": plan.month_label,
        "total_doctors": plan.total_doctors,
        "working_days": plan.working_days,
        "daily_target": plan.daily_target,
        "planned_visits": total,
        "completed": completed,
        "pending": pending,
        "completion_pct": pct,
        "plan_status": plan.status,
    }
@app.post("/executive-submission-reports")
def create_submission_report(data: ExecutiveSubmissionReportCreate, db: Session = Depends(get_db)):
    report = ExecutiveSubmissionReport(**data.model_dump())
    db.add(report)
    try:
        db.commit()
        db.refresh(report)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return plan_response(report)
@app.get("/executive-submission-reports")
def get_submission_reports(
    executive_id: Optional[int] = None,
    for_role: Optional[str] = None,
    manager_id: Optional[int] = None,
    regional_manager_id: Optional[int] = None,
    report_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    q = db.query(ExecutiveSubmissionReport)
    if executive_id is not None:
        q = q.filter(ExecutiveSubmissionReport.executive_id == executive_id)
    if for_role == "manager":
        q = q.filter(ExecutiveSubmissionReport.recipient_type.in_(["manager", "both"]))
    elif for_role == "regional":
        q = q.filter(ExecutiveSubmissionReport.recipient_type.in_(["regional", "both"]))
    if manager_id is not None:
        q = q.filter(ExecutiveSubmissionReport.manager_id == manager_id)
    if regional_manager_id is not None:
        q = q.filter(ExecutiveSubmissionReport.regional_manager_id == regional_manager_id)
    if report_date is not None:
        q = q.filter(ExecutiveSubmissionReport.report_date == report_date)
    reports = q.order_by(ExecutiveSubmissionReport.id.desc()).all()
    return [plan_response(r) for r in reports]
@app.get("/executive-submission-reports/{report_id}")
def get_submission_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(ExecutiveSubmissionReport).filter(ExecutiveSubmissionReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Submission report not found")
    return plan_response(r)
@app.put("/executive-submission-reports/{report_id}")
def update_submission_report(report_id: int, data: ExecutiveSubmissionReportUpdate, db: Session = Depends(get_db)):
    r = db.query(ExecutiveSubmissionReport).filter(ExecutiveSubmissionReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Submission report not found")
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(r, k, v)
    r.reviewed_at = datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)
    db.commit()
    db.refresh(r)
    return plan_response(r)
@app.delete("/executive-submission-reports/{report_id}")
def delete_submission_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(ExecutiveSubmissionReport).filter(ExecutiveSubmissionReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Submission report not found")
    db.delete(r)
    db.commit()
    return {"message": "Submission report deleted", "id": report_id}
