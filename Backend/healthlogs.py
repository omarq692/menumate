def get_all_healthlogs(db):
    logs = list(db.healthlogs.find({}, {"_id": 0}))  # Hide MongoDB ObjectId
    return logs
