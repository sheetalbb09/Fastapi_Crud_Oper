from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal

# ---------------------------------------------------
# FastAPI app
# ---------------------------------------------------
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to CRUD operations using FastAPI and PostgreSQL"}

# ---------------------------------------------------
# Database model
# ---------------------------------------------------
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    department = Column(String, index=True)

# Create the table
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------
# Pydantic schema
# ---------------------------------------------------
class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str

class EmployeeUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    department: str | None = None

# ---------------------------------------------------
# Dependency: database session
# ---------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------
# CRUD Routes
# ---------------------------------------------------

# Create
@app.post("/employees/")
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    new_emp = Employee(**emp.dict())
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp


# Read all
@app.get("/employees/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

# Read one
@app.get("/employees/{emp_id}")
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

# Update
@app.put("/employees/{emp_id}")
def update_employee(emp_id: int, emp_update: EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    for key, value in emp_update.dict(exclude_unset=True).items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)
    return emp

# Delete
@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted successfully"}
