import os

import fastapi
import fastapi.security as _security
import openai
import sqlalchemy.orm as _orm
from fastapi.middleware.cors import CORSMiddleware

import database
import models
import schemas
import services

models.Base.metadata.create_all(bind=database.engine)

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.route("/")


@app.post("/api/users")
async def create_user(
    user: schemas.UserCreate,
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    db_user = await services.get_user_by_email(user.email, db)
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail="Email already in use")

    user = await services.create_user(user, db)

    return await services.create_token(user)


@app.post("/api/token")
async def generate_token(
    type,
    form_data: _security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    if type == "user":
        user = await services.authenticate_user(form_data.username, form_data.password, db)

        if not user:
            raise fastapi.HTTPException(
                status_code=401,
                detail="Invalid email or password. Please try entering it again.",
            )

        return await services.create_token(user)

    if type == "company":
        company = await services.authenticate_company(form_data.username, form_data.password, db)

        if not company:
            raise fastapi.HTTPException(
                status_code=401,
                detail="Invalid email or password. Please try entering it again.",
            )

        return await services.create_company_token(company)


@app.get("/api/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(services.get_current_user)):
    return user


@app.post("/api/tasks", response_model=schemas.Task)
async def create_task(
    task: schemas.TaskCreate,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.create_task(user=user, db=db, task=task)


@app.get("/api/tasks", response_model=list[schemas.Task])
async def get_tasks(
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.get_tasks(user=user, db=db)


@app.get("/api/tasks/{task_id}", status_code=200)
async def get_task(
    task_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.get_task(task_id, user, db)


@app.delete("/api/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.delete_task(task_id, user, db)


@app.put("/api/tasks/{task_id}", status_code=200)
async def update_task(
    task_id: int,
    task: schemas.TaskCreate,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.update_task(task_id, task, user, db)


@app.put("/api/users/{user_id}", status_code=200)
async def update_password(
    user_id: int,
    changepassword: schemas.ChangePassword,
    user: schemas.User = fastapi.Depends(services.get_current_user),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.update_password(user_id, changepassword, user, db)


@app.post("/api/companies", status_code=200)
async def create_company(company: schemas.CompanyCreate, db: _orm.Session = fastapi.Depends(services.get_db)):
    db_company = await services.get_company_by_email(company.email, db)
    if db_company:
        raise fastapi.HTTPException(status_code=400, detail="Email already in use")

    company = await services.create_company(company, db)

    return await services.create_company_token(company)


@app.get("/api/companies/me", response_model=schemas.Company)
async def get_company(
    company: schemas.Company = fastapi.Depends(services.get_current_company),
):
    return company


@app.get("/api/companies/names")
async def get_all_companies(db: _orm.Session = fastapi.Depends(services.get_db)):
    return await services.get_all_company_data(db)


@app.post("/api/employees")
async def create_employee(employee: schemas._EmployeeBase, db: _orm.Session = fastapi.Depends(services.get_db)):
    db_employee = await services.get_employee_by_email(employee, db)
    if db_employee:
        raise fastapi.HTTPException(status_code=400, detail="Connection already made")

    return await services.create_employee(employee, db)


@app.get("/api/employees/tasks")
async def get_employees_tasks(
    company: schemas.Company = fastapi.Depends(services.get_current_company),
    db: _orm.Session = fastapi.Depends(services.get_db),
):
    return await services.get_employees_tasks(company, db)


api_key = os.environ["OPENAI_API_KEY"]
openai.api_key = api_key


@app.post("/ask_gpt", response_model=schemas.ChatGPTResponse)
async def ask_gpt(chatgpt_request: schemas.ChatGPTRequest):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=chatgpt_request.question,
            max_tokens=150,
        )

        return schemas.ChatGPTResponse(response=response["choices"][0]["text"])

    except Exception as e:
        return schemas.ChatGPTResponse(response=f"Error: {str(e)}")
