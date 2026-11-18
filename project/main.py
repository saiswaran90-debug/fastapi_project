from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse
import sqlite3


def get_connection():
    connection = sqlite3.connect("students.db")
    return connection


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    q = """
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        course TEXT NOT NULL,
        marks INTEGER NOT NULL,
        image TEXT,
        gender TEXT NOT NULL,
        status INTEGER
    )
    """
    cursor.execute(q)
    connection.commit()
    connection.close()


create_table()


class Student(BaseModel):
    name: str
    age: int = Field(gt=0, le=100)
    gender: str
    marks: int = Field(ge=0, le=100)
    course: str
    image: str
    status: int = Field(ge=0, le=1)


templates = Jinja2Templates(directory="templates")
app = FastAPI()


@app.get("/")
def home(req: Request):
    connection = get_connection()
    cursor = connection.cursor()

    q = """
    SELECT id, name, age, course, marks, image, gender, status
    FROM students
    """
    cursor.execute(q)
    students = cursor.fetchall()
    connection.close()

    return templates.TemplateResponse(
        request=req,
        name="home.html",
        context={"stds": students}
    )


@app.get("/students/add")
def send_std_form(req: Request):
    return templates.TemplateResponse(
        request=req,
        name="add_student.html",
        context={}
    )


@app.post("/students/add")
def create_std(
    name: str = Form(),
    age: int = Form(),
    gender: str = Form(),
    marks: int = Form(),
    course: str = Form(),
    image: str = Form(),
    status: int = Form()
):
    student = Student(
        name=name,
        age=age,
        gender=gender,
        marks=marks,
        course=course,
        image=image,
        status=status
    )

    values = (
        student.name,
        student.age,
        student.course,
        student.marks,
        student.image,
        student.gender,
        student.status
    )

    connection = get_connection()
    cursor = connection.cursor()

    q = """
    INSERT INTO students
    (name, age, course, marks, image, gender, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(q, values)
    connection.commit()
    connection.close()

    return RedirectResponse(url="/", status_code=303)


@app.get("/students/{student_id}")
def student_details(req: Request, student_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    q = """
    SELECT id, name, age, course, marks, image, gender, status
    FROM students
    WHERE id = ?
    """
    cursor.execute(q, (student_id,))
    student = cursor.fetchone()
    connection.close()

    return templates.TemplateResponse(
        request=req,
        name="student_details.html",
        context={"std": student}
    )


@app.post("/students/delete/{student_id}")
def delete_student(student_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    q = "DELETE FROM students WHERE id = ?"
    cursor.execute(q, (student_id,))
    connection.commit()
    connection.close()

    return RedirectResponse(url="/", status_code=303)


@app.get("/students/update/{student_id}")
def update_std(req: Request, student_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    q = "SELECT * FROM students WHERE id = ?"
    cursor.execute(q, (student_id,))
    student = cursor.fetchone()
    connection.close()

    return templates.TemplateResponse(
        request=req,
        name="update_std.html",
        context={"std": student}
    )


@app.post("/students/update/{student_id}")
def update_student(
    student_id: int,
    name: str = Form(),
    age: int = Form(),
    gender: str = Form(),
    marks: int = Form(),
    course: str = Form(),
    image: str = Form(),
    status: int = Form()
):
    student = Student(
        name=name,
        age=age,
        gender=gender,
        marks=marks,
        course=course,
        image=image,
        status=status
    )

    values = (
        student.name,
        student.age,
        student.course,
        student.marks,
        student.image,
        student.gender,
        student.status,
        student_id
    )

    connection = get_connection()
    cursor = connection.cursor()

    q = """
    UPDATE students
    SET
        name = ?,
        age = ?,
        course = ?,
        marks = ?,
        image = ?,
        gender = ?,
        status = ?
    WHERE id = ?
    """
    cursor.execute(q, values)
    connection.commit()
    connection.close()

    return RedirectResponse(url="/", status_code=303)