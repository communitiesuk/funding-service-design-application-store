from db import db
from db.models import Feedback

### NEXT, CREATE API ENDPOINTS
### BELOW MAY NEED AMENDING TO WORK CORRECTLY

def add_new_feedback(application_id, fund_id, round_id, section_id, feedback_json, status):
    new_feedback_row = Feedback(
        application_id = application_id,
        fund_id = fund_id,
        round_id = round_id,
        section_id = section_id,
        feedback_json = feedback_json,
        status = "NOT_STARTED"
        )   
    
    db.session.add(new_feedback_row)
    db.session.commit()

def get_feedback(application_id, section_id):
    return (
        db.session.query(Feedback)
        .filter(Feedback.application_id == application_id, Feedback.section_id == section_id)
        .one()
    )
