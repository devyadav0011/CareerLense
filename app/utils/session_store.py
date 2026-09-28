import os
import json
import uuid
from flask import session, current_app

class SessionStore:
    """
    Server-side session store for CareerLense to prevent exceeding
    the 4KB client-side browser cookie limit when storing structured resumes,
    scoring breakdowns, and job match evaluations.
    """
    _memory_cache = {}

    @classmethod
    def _get_storage_dir(cls):
        try:
            path = os.path.join(current_app.instance_path, 'sessions')
        except Exception:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'instance', 'sessions')
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def get_sid(cls):
        sid = session.get('sid')
        if not sid:
            sid = uuid.uuid4().hex
            session['sid'] = sid
            session.modified = True
        return sid

    @classmethod
    def get_current_resume(cls):
        sid = session.get('sid')
        if sid:
            if sid in cls._memory_cache:
                return cls._memory_cache[sid]

            filepath = os.path.join(cls._get_storage_dir(), f"{sid}.json")
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        cls._memory_cache[sid] = data
                        return data
                except Exception:
                    pass

        # Fallback to cookie session if present
        return session.get('current_resume')

    @classmethod
    def set_current_resume(cls, resume_dict):
        sid = cls.get_sid()
        cls._memory_cache[sid] = resume_dict
        filepath = os.path.join(cls._get_storage_dir(), f"{sid}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(resume_dict, f, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def update_current_resume(cls, **kwargs):
        curr = cls.get_current_resume() or {}
        curr.update(kwargs)
        cls.set_current_resume(curr)
        return curr

    @classmethod
    def clear(cls):
        sid = session.get('sid')
        if sid:
            cls._memory_cache.pop(sid, None)
            try:
                filepath = os.path.join(cls._get_storage_dir(), f"{sid}.json")
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception:
                pass
            session.pop('sid', None)
        session.pop('current_resume', None)
        session.modified = True
