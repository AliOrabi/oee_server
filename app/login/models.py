from app import login_manager, stream_handler, file_handler
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger('flask.app')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean)

    sessions = db.relationship('UserSession', backref="user")
    activities = db.relationship('Activity', backref="user")
    jobs = db.relationship('Job', backref="user")

    def has_job(self):
        for job in self.jobs:
            if job.active:
                return True
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User '{self.username}' (ID {self.id})>"


class UserSession(db.Model):
    """ Manages user sessions for Android logins"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False)
    device_ip = db.Column(db.String)
    timestamp_login = db.Column(db.Integer)
    timestamp_logout = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    jobs = db.relationship('Job', backref="user_session")

    def __repr__(self):
        return f"<UserSession " \
               f"user_id:{self.user_id} " \
               f"device_ip:{self.device_ip} " \
               f"machine_id:{self.machine_id} " \
               f"(ID {self.id})> "


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_default_users():

    if User.query.filter_by(username="admin").first() is not None:
        return
    # noinspection PyArgumentList
    default_admin = User(username="admin", admin=True)
    default_admin.set_password("digitme2")

    if User.query.filter_by(username="user").first() is not None:
        return
    # noinspection PyArgumentList
    default_user = User(username="user", admin=False)
    default_user.set_password("1")

    db.session.add(default_admin)
    db.session.add(default_user)
    db.session.commit()
    logger.info(f"Created default users:\n{default_admin}\n{default_user}\n on first startup")