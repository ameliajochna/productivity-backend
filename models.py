from sqlalchemy import (
    ForeignKeyConstraint,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Companies(Base):
    __tablename__ = "companies"
    __table_args__ = (PrimaryKeyConstraint("id", name="companies_pkey"),)

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1
        ),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))


class Employees(Base):
    __tablename__ = "employees"
    __table_args__ = (PrimaryKeyConstraint("id", name="employees_pkey"),)

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            start=1,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    company_id: Mapped[int] = mapped_column(Integer)
    user_email: Mapped[str] = mapped_column(String(255))


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("email", name="users_email_key"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            start=91,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))

    tasks: Mapped[list["Tasks"]] = relationship("Tasks", back_populates="owner")


class Tasks(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        ForeignKeyConstraint(["owner_id"], ["users.id"], name="tasks_owner_id_fkey"),
        PrimaryKeyConstraint("id", name="tasks_pkey"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(
            start=542,
            increment=1,
            minvalue=1,
            maxvalue=2147483647,
            cycle=False,
            cache=1,
        ),
        primary_key=True,
    )
    owner_id: Mapped[int] = mapped_column(Integer)
    priority: Mapped[str] = mapped_column(String(6))
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[str | None] = mapped_column(String(11))

    owner: Mapped["Users"] = relationship("Users", back_populates="tasks")
