import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Identity,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Companies(Base):
    __tablename__ = "companies"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="companies_pkey"),
        UniqueConstraint("email", name="companies_email_key"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))


t_databasechangelog = Table(
    "databasechangelog",
    Base.metadata,
    Column("id", String(255), nullable=False),
    Column("author", String(255), nullable=False),
    Column("filename", String(255), nullable=False),
    Column("dateexecuted", DateTime, nullable=False),
    Column("orderexecuted", Integer, nullable=False),
    Column("exectype", String(10), nullable=False),
    Column("md5sum", String(35)),
    Column("description", String(255)),
    Column("comments", String(255)),
    Column("tag", String(255)),
    Column("liquibase", String(20)),
    Column("contexts", String(255)),
    Column("labels", String(255)),
    Column("deployment_id", String(10)),
)


class Databasechangeloglock(Base):
    __tablename__ = "databasechangeloglock"
    __table_args__ = (PrimaryKeyConstraint("id", name="databasechangeloglock_pkey"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    locked: Mapped[bool] = mapped_column(Boolean)
    lockgranted: Mapped[datetime.datetime | None] = mapped_column(DateTime)
    lockedby: Mapped[str | None] = mapped_column(String(255))


class Employees(Base):
    __tablename__ = "employees"
    __table_args__ = (PrimaryKeyConstraint("id", name="employees_pkey"),)

    id: Mapped[int] = mapped_column(
        Integer,
        Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer)
    priority: Mapped[str] = mapped_column(String(6))
    title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[str | None] = mapped_column(String(11))

    owner: Mapped["Users"] = relationship("Users", back_populates="tasks")
