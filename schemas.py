import pydantic


class _UserBase(pydantic.BaseModel):
    email: str


class UserCreate(_UserBase):
    hashed_password: str
    name: str

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int

    class Config:
        orm_mode = True


class _TaskBase(pydantic.BaseModel):
    state: str
    title: str
    description: str
    priority: str


class TaskCreate(_TaskBase):
    pass


class Task(_TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class ChangePassword(_UserBase):
    email: str
    password: str
    new_password: str
    confirm_password: str


class _CompanyBase(pydantic.BaseModel):
    email: str


class CompanyCreate(_CompanyBase):
    hashed_password: str
    name: str

    class Config:
        orm_mode = True


class Company(_CompanyBase):
    id: int

    class Config:
        orm_mode = True


class _EmployeeBase(pydantic.BaseModel):
    company_id: int
    user_email: str


class ChatGPTRequest(pydantic.BaseModel):
    question: str


class ChatGPTResponse(pydantic.BaseModel):
    response: str
