import uuid
import tempfile
import webbrowser
import os

from bson import ObjectId
from datetime import datetime

from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user

from app import db
from app.logger import logger
from app.modules.teacher.forms import NewSubmissionForm
from app.modules._classes import Submission
from app.decorators import required_access
from app.google_storage import upload_blob, get_signed_url, download_blob

from . import student
from ._student import Student


@student.before_request
@required_access("Student")
def student_verification():
    # Required_access decorator already handled it
    pass


@student.route("/")
@student.route("/index")
@student.route("/dashboard")
def index():
    return {
        "forms": {},
        "flashes": [],
        "data": {
            "assignments": [assignment.to_json() for assignment in current_user.get_assignments()]
        }
    } 


@student.route("/submit/<class_id>/<assignment_id>", methods=["GET", "POST"])
def submit(class_id, assignment_id):
    form = NewSubmissionForm()
    assignment = db.classes.find_one(
        {"assignments._id": ObjectId(assignment_id)},
        {"_id": 0, "assignments": {"$elemMatch": {"_id": ObjectId(assignment_id)}}},
    )["assignments"][0]
    full_name = current_user.first_name + " " + current_user.last_name
    content = assignment["content"]
    estimated_time = assignment["estimated_time"]
    due_by = assignment["due_by"]
    if form.validate_on_submit():
        student = Student.get_by_id(current_user.ID)
        file_list = []
        files = request.files.getlist(form.files.name)
        if files[0].filename:
            for file_ in files:
                filename = file_.filename
                blob = upload_blob(
                    uuid.uuid4().hex + "." + file_.content_type.split("/")[-1], file_
                )
                file_list.append((blob.name, filename))
        submission = Submission(
            date_submitted=datetime.utcnow(),
            content=form.content.data,
            filenames=file_list,
        )

        logger.info(f"Submission {form.title.data} made")

        student.add_submission(
            current_user.ID, class_id, assignment_id, submission=submission
        )  # need to replace IDs with current class and assignment ID
    return {
        "forms": {
            "submission": form.get_form_json()
        },
        "flashes": [],
        "data": {
            "class_id": class_id,
            "assignment_id": assignment_id,
            "full_name": full_name,
            "content": content,
            "estimated_time": estimated_time,
            "due_by": due_by
        }
    }


@student.route("/profile")
def profile():
    return render_template("student/profile.html")


@student.route("/assignments")
def assignments():
    print(list(map(lambda x: x.to_json(), current_user.get_assignments())))
    return {
        "forms": {},
        "flashes": [],
        "data": {
            "assignments": list(map(lambda x: x.to_json(), current_user.get_assignments()))
        }
    }

@student.route("/assignments/<string:class_id>", methods=["GET"])
def view_assignments_by_class_id(class_id: str):
    # Collect assignments from all classes
    class_ = Classes.get_by_id(class_id)
    class_assignments = class_.get_assignments()
    
    return {
        'forms': {},
        'flashes': [],
        'data': {
            'assignments': list(map(lambda a: a.to_json(), class_assignments))
        }
    }

@student.route("/assignments/<string:class_id>/<string:assignment_id>", methods=["GET", "POST"])
def view_assignment(class_id: str, assignment_id: str):
    # Find assignment in teacher's classes
    flashes = []
    class_ = Classes.get_by_id(class_id)
    assignments = class_.get_assignments()
    # TODO: Create custom error when assignment isn't found
    assignment = list(filter(lambda a: str(a.ID) == assignment_id, assignments))[0]

    return {
        'forms': {},
        'flashes': flashes,
        'data': {
            'assignment': assignment.to_json()
        }
    }

@student.route("/view_assignment/<filename>", methods=["GET", "POST"])
def view_file(filename):
    blob_url = get_signed_url(filename)
    webbrowser.open(blob_url, new=0)
    return {}
