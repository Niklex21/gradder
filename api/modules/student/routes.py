import uuid
from datetime import datetime

from bson import ObjectId
from flask import abort, current_app, request
from flask_login import current_user

from api import db
from api import root_logger as logger
from api.classes import Student, Submission, User, Course, Assignment
from api.tools.decorators import required_access
from api.tools.factory import error, response
from api.tools.google_storage import download_blob, get_signed_url, upload_blob

from . import student


@student.before_request
@required_access(Student)
def student_verification():
    # Required_access decorator already handled it
    pass


@student.route("/submit/<string:class_id>/<string:assignment_id>", methods=["POST"])
def submit(class_id: str, assignment_id: str):
    """Submit work for an assignment

    Parameters
    ----------
    class_id : str
        The ID of the class for which the assignment was set
    assignment_id : str
        The ID of the assignment

    Returns
    -------
    dict
        The view response
    """
    assignment = db.courses.find_one(
        {"assignments._id": ObjectId(assignment_id)},
        {"_id": 0, "assignments": {"$elemMatch": {"_id": ObjectId(assignment_id)}}},
    )["assignments"][0]
    
    if assignment is not None:
        try:
            file_list = []
            files = request.files.getlist('files')
            if files[0].filename:
                for file_ in files:
                    filename = file_.filename
                    blob = upload_blob(
                        uuid.uuid4().hex + "." + file_.content_type.split("/")[-1], file_
                    )
                    file_list.append((blob.name, filename))
            
            submission = Submission(
                date_submitted=datetime.utcnow(),
                content=request.form['content'],
                filenames=file_list
            )
            
            current_user.add_submission(
                current_user.id, class_id, assignment_id, submission=submission
            )
        except KeyError:
            return error("Not all fields satisfied"), 400
        else:
            logger.info(f"Submission {submission.id} made")
            return response(["Submission was a success"]), 200
    else:
        return error("No assignment found"), 404



@student.route("/assignments", methods=["GET"])
def assignments():
    """Get all assignments for the signed in user

    Returns
    -------
    dict
        The view response
    """
    #print(list(map(lambda x: x.to_json(), current_user.get_assignments())))  
    logger.info(f"Accessed all assignments")
    return response(data={'assignments': list(map(lambda x: x.to_json(), current_user.get_assignments()))})

@student.route("/assignments/<string:class_id>/", methods=["GET"])
def assignments_by_class(class_id: str):
    """Get assignments for a specific class

    Parameters
    ----------
    class_id : str
        The ID of the class

    Returns
    -------
    dict
        The view response
    """

    course_assignments = Course.get_by_id(course_id).get_assignments()
    logger.info(f"All assignments from {class_id}.")
    return response(data={"assignments": list(map(lambda a: a.to_json(), course_assignments))})
    #return response(data={"assignments": list(map(lambda a: a.to_json(), course_assignments))})

    

# This could possibly instead just use /assignments/<string:assignment_id>/
# and then we could search through classes to find the assignment 
@student.route("/assignments/<string:class_id>/<string:assignment_id>/", methods=["GET"])
def assignment_by_id(class_id: str, assignment_id: str):
    """Get an assignment by its ID

    Parameters
    ----------
    class_id : str
        The ID of the class
    assignment_id : str
        The ID of the assignment

    Returns
    -------
    dict
        The view response
    """
    assignments = Course.get_by_id(class_id).get_assignments()
    assignment = list(filter(lambda a: str(a.ID) == assignment_id, assignments))[0]
    logger.info(f"All assignments from {class_id} with assignment id {assignment_id}.")
    return response(data={"assignment": assignment.to_json()})

    
