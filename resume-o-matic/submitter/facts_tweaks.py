from db import add_correction, get_corrections, delete_correction, update_correction

# CORRECTIONS

def list_corrections(context="global"):
    return get_corrections(context)

def create_correction(section, original_text, corrected_text, context="global"):
    add_correction(section, original_text, corrected_text, context)

def edit_correction(correction_id, section, original_text, corrected_text, context="global"):
    update_correction(correction_id, section, original_text, corrected_text, context)

def remove_correction(correction_id):
    delete_correction(correction_id)
