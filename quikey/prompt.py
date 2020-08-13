from pick import pick

def show(db, action):
    keys = [x['key'] for x in db.all()]
    choice,_ = pick(keys, ("Select a phrase to %s" % action))
    return choice