from datetime import datetime
from game.models import Session
from pandemic.celery import app

@app.task
def schedule_session_start(session_pk):
    from game.views import setup_session 
    session = Session.objects.get(session_hash=session_pk)
    if not session.has_started:
        session.has_started = True
        session.start_time = datetime.now()
        session.last_changed = datetime.now()
        session.save()
        setup_session(session)
