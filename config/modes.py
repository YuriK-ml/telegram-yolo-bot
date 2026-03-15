# config/modes.py

def get_mode_label(mode):

    modes = {
        None: "Main menu",
        "english_test": "English test feedback",
        "age_detection": "Age detection",
        "object_detection": "Object detection",
        "teacher_chat": "Teacher communication"
    }

    return modes.get(mode, "Unknown mode")