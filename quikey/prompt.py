from pick import pick

def show(db, action):
    keys = [x['key'] for x in db.all()]
    if not keys:
        return None
    choice,_ = pick(keys, ("Select a phrase to %s. Use CTRL+C to exit." % action))
    return choice