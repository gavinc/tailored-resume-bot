from db import add_submission, get_submission, list_submissions, update_submission, delete_submission

# SUBMISSIONS

def create_submission(**kwargs):
    add_submission(**kwargs)

def get_submission_by_id(sub_id):
    return get_submission(sub_id)

def list_all_submissions():
    return list_submissions()

def edit_submission(sub_id, **kwargs):
    update_submission(sub_id, **kwargs)

def remove_submission(sub_id):
    delete_submission(sub_id)

def set_submission_state(sub_id, state, reviewer_notes=None):
    update = {'state': state}
    if reviewer_notes is not None:
        update['reviewer_notes'] = reviewer_notes
    update_submission(sub_id, **update)
