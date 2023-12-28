import fastapi
import fastapi.security as _security
import jwt
import passlib
import passlib.hash as _hash
import sqlalchemy.orm as _orm
from sqlalchemy import and_

import database
import models
import schemas as schemas

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "myjwtsecret"


def create_database() -> None:
    database.Base.metadata.create_all(bind=database.engine)


def get_db() -> _orm.Session:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: _orm.Session) -> models.Users | None:
    return db.query(models.Users).filter(models.Users.email == email).first()  # type: ignore[no-any-return]


async def create_user(user: schemas.UserCreate, db: _orm.Session) -> models.Users:
    user_obj = models.Users(
        email=user.email,
        hashed_password=_hash.bcrypt.hash(user.hashed_password),
        name=user.name,
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


def verify_password(user: models.Users, password: str) -> bool:
    return passlib.hash.bcrypt.verify(password, user.hashed_password)  # type: ignore[no-any-return]


async def authenticate_user(
    email: str, password: str, db: _orm.Session
) -> models.Users | bool:
    user = await get_user_by_email(db=db, email=email)

    if not user:
        return False

    if not verify_password(user, password):
        return False

    return user


async def authenticate_company(
    email: str, password: str, db: _orm.Session
) -> models.Companies | bool:
    company = await get_company_by_email(email=email, db=db)

    if not company:
        return False

    if not verify_company_password(company, password):
        return False

    return company


async def create_token(user: models.Users | bool) -> dict:
    user_obj = schemas.User.from_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer", account_type="user")


async def get_current_user(
    db: _orm.Session = fastapi.Depends(get_db),
    token: str = fastapi.Depends(oauth2schema),
) -> schemas.User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(models.Users).get(payload["id"])
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid email or Password")

    return schemas.User.from_orm(user)  # type: ignore[no-any-return]


async def create_task(
    user: schemas.User,
    db: _orm.Session,
    task: schemas.TaskCreate,
) -> schemas.Task:
    task = models.Tasks(**task.dict(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return schemas.Task.from_orm(task)  # type: ignore[no-any-return]


async def get_tasks(user: schemas.User, db: _orm.Session) -> list:
    tasks = db.query(models.Tasks).filter_by(owner_id=user.id)

    return list(map(schemas.Task.from_orm, tasks))


async def _task_selector(
    task_id: int, user: schemas.User, db: _orm.Session
) -> models.Tasks:
    task = (
        db.query(
            models.Tasks,
        )
        .filter_by(owner_id=user.id)
        .filter(models.Tasks.id == task_id)
        .first()
    )

    if task is None:
        raise fastapi.HTTPException(status_code=404, detail="Task does not exist")

    return task  # type: ignore[no-any-return]


async def get_task(task_id: int, user: schemas.User, db: _orm.Session) -> schemas.Task:
    task = await _task_selector(task_id=task_id, user=user, db=db)

    return schemas.Task.from_orm(task)  # type: ignore[no-any-return]


async def delete_task(task_id: int, user: schemas.User, db: _orm.Session) -> None:
    task = await _task_selector(task_id, user, db)
    db.delete(task)
    db.commit()


async def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    user: schemas.User,
    db: _orm.Session,
) -> schemas.Task:
    task_db = await _task_selector(task_id, user, db)
    task_db.state = task.state
    task_db.title = task.title
    task_db.description = task.description
    task_db.priority = task.priority

    db.commit()
    db.refresh(task_db)

    return schemas.Task.from_orm(task_db)  # type: ignore[no-any-return]


async def update_password(
    user_id: int,
    changepassword: schemas.ChangePassword,
    user: schemas.User,
    db: _orm.Session,
) -> schemas.User:
    db_user = await get_user_by_email(user.email, db)

    if not verify_password(db_user, changepassword.password):  # type: ignore[arg-type]
        raise fastapi.HTTPException(status_code=401, detail="Invalid password")

    if changepassword.new_password != changepassword.confirm_password:
        raise fastapi.HTTPException(
            status_code=401,
            detail="The passwords are not the same",
        )

    hashed_password = _hash.bcrypt.hash(changepassword.new_password)

    user_db = db.query(models.Users).filter_by(id=user_id).first()
    user_db.hashed_password = hashed_password

    db.commit()
    db.refresh(user_db)

    return schemas.User.from_orm(user_db)  # type: ignore[no-any-return]


async def get_company_by_email(email: str, db: _orm.Session) -> models.Companies:
    return db.query(models.Companies).filter(models.Companies.email == email).first()  # type: ignore[no-any-return]


async def create_company(
    company: schemas.CompanyCreate, db: _orm.Session
) -> models.Companies:
    company_obj = models.Companies(
        email=company.email,
        hashed_password=_hash.bcrypt.hash(company.hashed_password),
        name=company.name,
    )
    db.add(company_obj)
    db.commit()
    db.refresh(company_obj)
    return company_obj


async def create_company_token(company: models.Companies | bool) -> dict:
    company_obj = schemas.Company.from_orm(company)
    token = jwt.encode(company_obj.dict(), JWT_SECRET)
    return dict(access_token=token, token_type="bearer", account_type="company")


def verify_company_password(company: models.Companies, password: str) -> bool:
    print(company, password, company.hashed_password)
    return passlib.hash.bcrypt.verify(password, company.hashed_password)  # type: ignore[no-any-return]


async def get_current_company(
    db: _orm.Session = fastapi.Depends(get_db),
    token: str = fastapi.Depends(oauth2schema),
) -> schemas.Company:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        company = db.query(models.Companies).get(payload["id"])
    except Exception:
        raise fastapi.HTTPException(status_code=401, detail="Invalid email or Password")

    return schemas.Company.from_orm(company)  # type: ignore[no-any-return]


async def get_all_company_data(db: _orm.Session) -> list[dict[str, int | str]]:
    companies = db.query(models.Companies).all()
    company_data = [{"id": company.id, "name": company.name} for company in companies]
    return company_data


async def get_employee_by_email(
    employee: schemas._EmployeeBase, db: _orm.Session
) -> models.Employees:
    return (  # type: ignore[no-any-return]
        db.query(models.Employees)
        .filter(
            and_(
                models.Employees.company_id == employee.company_id,
                models.Employees.user_email == employee.user_email,
            )
        )
        .first()
    )


async def create_employee(
    employee: schemas._EmployeeBase, db: _orm.Session
) -> models.Employees:
    employee_obj = models.Employees(
        company_id=employee.company_id,
        user_email=employee.user_email,
    )
    db.add(employee_obj)
    db.commit()
    db.refresh(employee_obj)
    return employee_obj


async def get_employees_tasks(company: schemas.Company, db: _orm.Session) -> list:
    employees_obj = (
        db.query(
            models.Employees,
        )
        .filter(models.Employees.company_id == company.id)
        .all()
    )

    employees_tasks = []
    for employee in employees_obj:
        user_obj = db.query(models.Users).filter_by(email=employee.user_email).first()
        tasks = db.query(models.Tasks).filter_by(owner_id=user_obj.id).all()
        name = ""
        if user_obj.name:
            name = user_obj.name
        employees_tasks.append({"id": employee.id, "name": name, "tasks": tasks})

    return employees_tasks
