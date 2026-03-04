from flask import Flask, jsonify, request
from flask_cors import CORS

import db

app = Flask(__name__)
CORS(app)

# Instructions:
# - Use the functions in backend/db.py in your implementation.
# - You are free to use additional data structures in your solution
# - You must define and tell your tutor one edge case you have devised and how you have addressed this



def _error(message="error"):
    # Spec: all errors return 404
    return jsonify({"error": message}), 404


def _to_number(v):
    """
    Convert to float if possible.
    Accepts int, float, numeric string.
    Rejects bool and non-numeric.
    """
    if v is None:
        return None
    if isinstance(v, bool):
        raise ValueError("bool is not valid mark")
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip()
        if s == "":
            raise ValueError("empty string")
        try:
            return float(s)
        except ValueError:
            pass
    raise ValueError("mark must be numeric")


def _validate_name_course(name, course):
    if not isinstance(name, str) or name.strip() == "":
        raise ValueError("Invalid or missing 'name'")
    if not isinstance(course, str) or course.strip() == "":
        raise ValueError("Invalid or missing 'course'")
    return name.strip(), course.strip()


def _validate_mark(mark, default_if_missing=None):
    """
    Mark rules:
    - If missing and default_if_missing provided -> use it (e.g., POST default 0)
    - If provided -> must be int and in [0, 100]
    """
    if mark is None:
        if default_if_missing is None:
            return None
        return default_if_missing

    m = _to_number(mark)
    if m < 0 or m > 100:
        raise ValueError("Invalid 'mark' (must be 0-100)")
    return m


@app.route("/students")
def get_students():
    """
    Route to fetch all students from the database
    return: Array of student objects
    """

    try:
        students = db.get_all_students()
        return jsonify(students), 200
    except Exception:
        return _error("Failed to fetch students")

    # TODO: replace with your implementation. This is a mock response
    return jsonify([
        {'course': 'COMP1531', 'id': 1, 'mark': 85, 'name': 'Alice Zhang'},
        {'course': 'COMP1531', 'id': 2, 'mark': 72, 'name': 'Bob Smith'}
    ]), 200



@app.route("/students", methods=["POST"])
def create_student():
    """
    Route to create a new student
    param name: The name of the student (from request body)
    param course: The course the student is enrolled in (from request body)
    param mark: The mark the student received (from request body)
    return: The created student if successful
    """

    try:
        # Getting the request body - replace with your implementation
        student_data = request.json
        if not isinstance(student_data, dict):
            return _error("Request body must be JSON object")

        name = student_data.get("name")
        course = student_data.get("course")
        mark = student_data.get("mark", None)  # optional

        name, course = _validate_name_course(name, course)
        mark = _validate_mark(mark, default_if_missing=0)

        created = db.insert_student(name, course, mark)
        return jsonify(created), 200
    except ValueError as e:
        return _error(str(e))
    except Exception:
        return _error("Failed to create student")




@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    """
    Route to update student details by id
    param name: The name of the student (from request body)
    param course: The course the student is enrolled in (from request body)
    param mark: The mark the student received (from request body)
    return: The updated student if successful
    """

    try:
        student_data = request.json
        if not isinstance(student_data, dict):
            return _error("Request body must be JSON object")

        # All optional on update
        name = student_data.get("name", None)
        course = student_data.get("course", None)
        mark = student_data.get("mark", None)

        # Validate only if provided
        if name is not None:
            if not isinstance(name, str) or name.strip() == "":
                return _error("Invalid 'name'")
            name = name.strip()

        if course is not None:
            if not isinstance(course, str) or course.strip() == "":
                return _error("Invalid 'course'")
            course = course.strip()

        if mark is not None:
            mark = _validate_mark(mark, default_if_missing=None)

        updated = db.update_student(student_id, name=name, course=course, mark=mark)
        if updated is None:
            return _error("Student not found")
        return jsonify(updated), 200

    except ValueError as e:
        return _error(str(e))
    except Exception:
        return _error("Failed to update student")


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """
    Route to delete student by id
    return: The deleted student
    """

    try:
        deleted = db.delete_student(student_id)
        if deleted is None:
            return _error("Student not found")
        return jsonify(deleted), 200
    except Exception:
        return _error("Failed to delete student")



@app.route("/stats")
def get_stats():
    """

    Route to show the stats of all student marks
    return: An object with the stats (count, average, min, max)
    """
    try:
        students = db.get_all_students()
        marks = [s.get("mark") for s in students if isinstance(s.get("mark"), (int, float))]

        if len(marks) == 0:
            return jsonify({"count": 0, "average": 0, "min": 0, "max": 0}), 200

        count = len(marks)
        avg = sum(marks) / count
        return jsonify(
            {
                "count": count,
                "average": avg,
                "min": min(marks),
                "max": max(marks),
            }
        ), 200
    except Exception:
        return _error("Failed to compute stats")



@app.route("/")
def health():
    """Health check."""
    return {"status": "ok"}


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)

