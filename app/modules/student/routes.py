from flask import render_template, redirect, request, url_for, make_response
from flask_login import current_user
from app.modules.teacher.forms import NewSubmissionForm
from . import student
from ._student import Student
from app.modules._classes import Submission
from app.decorators import required_access
from datetime import datetime
from app.google_storage import upload_blob
from app import db
from bson import ObjectId

@student.before_request
@required_access('Student')
def student_verification():
    # Required_access decorator already handled it
    pass


@student.route('/')
@student.route('/index')
@student.route('/dashboard')
def index():
    return render_template('student/dashboard.html', assignments=current_user.get_assignments())

@student.route('/submit/<class_id>/<assignment_id>', methods=["GET", "POST"])
def submit(class_id, assignment_id):
    form = NewSubmissionForm()
    assignment = db.classes.find_one({"assignments._id": ObjectId(assignment_id)}, {"_id": 0, "assignments": {"$elemMatch": {"_id": ObjectId(assignment_id)}}})["assignments"][0]
    full_name = current_user.first_name + " " +  current_user.last_name
    content = assignment["content"]
    estimated_time = assignment["estimated_time"]
    due_by = assignment["due_by"]
    if form.validate_on_submit():
        student = Student.get_by_id(current_user.ID)
        if request.files is not None:
            files = request.files.getlist(form.files.name)
            file_link_list = []
            for file_ in files:
                blob = upload_blob(file_.filename, file_)
                file_link_list.append(blob.media_link)
        submission = Submission(date_submitted=datetime.utcnow(), content=form.content.data, file_links=file_link_list)
        student.add_submission(current_user.ID, class_id, assignment_id, submission=submission) # need to replace IDs with current class and assignment ID
    return render_template('student/submission.html', form=form, class_id=class_id, assignment_id=assignment_id, full_name=full_name, 
                        content=content, estimated_time=estimated_time, due_by=due_by)

@student.route('/profile')
def profile():
    return render_template('student/profile.html')
    

@student.route('/assignments')
def assignments():
    return render_template('student/assignments.html', assignments=current_user.get_assignments())
