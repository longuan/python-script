#coding:utf-8

from functools import wraps
from flask import abort
from flask_login import current_user
from .forms import Admin_Student_profile,Admin_Teacher_profile,Admin_Admin_profile,\
                    Student_profile, Teacher_profile, Admin_profile

page_role = {
    'student': 'index_stu.html',
    'sys_admin': 'index_sys.html',
    'ass_admin': 'index_ass.html',
    'teacher': 'index_tea.html'
}

profile_html = {
    'student': 'profile_stu.html',
    'sys_admin': 'profile_sys.html',
    'ass_admin': 'profile_sys.html',
    'teacher': 'profile_tea.html'
}

admin_profile_form = {
    'student': Admin_Student_profile,
    'teacher': Admin_Teacher_profile,
    'sys_admin': Admin_Admin_profile,
    'ass_admin': Admin_Admin_profile
}

profile_form = {
    'student': Student_profile,
    'teacher': Teacher_profile,
    'sys_admin': Admin_profile,
    'ass_admin': Admin_profile
}

role_user = {
    'student': u"学生",
    'teacher': u"教师",
    'ass_admin': u"考评管理员",
    'sys_admin': u"系统管理员"
}


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if current_user.type != permission:
                abort(403)
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required('sys_admin')(f)

def ass_required(f):
    return permission_required('ass_admin')(f)

def teacher_required(f):
    return permission_required('teacher')(f)