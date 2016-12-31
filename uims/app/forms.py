#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField,SelectField,RadioField
from wtforms.validators import DataRequired,Length,Regexp,EqualTo
from .models import Course,Teacher,Ass_Template,Teach_Course
from flask_login import current_user

class LoginForm(FlaskForm):
    identity = SelectField(u'登录账号类型',validators=[DataRequired()],choices=[('student',u'学生'),('teacher',u'教师'),('ass_admin',u'考评管理员'),('sys_admin',u'系统管理员')])
    username = StringField(u'用户名',validators=[DataRequired()])
    password = PasswordField(u'密码',validators=[DataRequired()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录')

class Register(FlaskForm):
    identity = SelectField(u'登录账号类型',validators=[DataRequired()],choices=[('student',u'学生'),('teacher',u'教师'),('ass_admin',u'考评管理员'),('sys_admin',u'系统管理员')])
    user_num = StringField(u'用户名',validators=[DataRequired(),Length(8),Regexp('[0-9]{8}',0,u"用户名只能是8位数字")])
    user_name= StringField(u"姓名",validators=[DataRequired(),Length(1,32)])
    user_sex = RadioField(u"性别",validators=[DataRequired()],choices=[('1',u'男'),('0',u'女')])
    password = PasswordField(u'密码',validators=[DataRequired(),EqualTo("password2",message=u"两次密码不一致")])
    password2 = PasswordField(u"确认密码",validators=[DataRequired()])
    submit = SubmitField(u"注册")

class change_passwd(FlaskForm):
    old_passwd = PasswordField(u'旧密码',validators=[DataRequired()])
    new_passwd = PasswordField(u'新密码',validators=[DataRequired()])
    submit = SubmitField(u'修改')

class Student_profile(FlaskForm):
    user_name = StringField(u"姓名",validators=[DataRequired()])
    user_sex = RadioField(u"性别",validators=[DataRequired()],choices=[('1',u'男'),('0',u'女')])
    student_major = StringField(u"专业",validators=[DataRequired()])
    student_college = StringField(u"学院",validators=[DataRequired()])
    student_class = StringField(u"班级",validators=[DataRequired(),Regexp('[0-9]{2}',0,u"班级号是两位数字")])
    submit = SubmitField(u"修改")

class Admin_Student_profile(FlaskForm):
    user_name = StringField(u"姓名",validators=[DataRequired()])
    user_sex = RadioField(u"性别",validators=[DataRequired()],choices=[('1',u'男'),('0',u'女')])
    student_major = StringField(u"专业",validators=[DataRequired()])
    student_college = StringField(u"学院",validators=[DataRequired()])
    student_class = StringField(u"班级",validators=[DataRequired(),Regexp('[0-9]{2}',0,u"班级号是两位数字")])
    user_type = SelectField(u'修改角色',validators=[DataRequired()],choices=[('NULL',u'不修改'),('student',u'学生'),('teacher',u'教师'),('ass_admin',u'考评管理员'),('sys_admin',u'系统管理员')])
    submit = SubmitField(u"修改")

class Admin_profile(FlaskForm):
    user_name = StringField(u"姓名",validators=[DataRequired()])
    user_sex = RadioField(u"性别",validators=[DataRequired()],choices=[('1',u'男'),('0',u'女')])
    submit = SubmitField(u"修改")

class Admin_Admin_profile(FlaskForm):
    user_name = StringField(u"姓名",validators=[DataRequired()])
    user_sex = RadioField(u"性别",validators=[DataRequired()],choices=[('1',u'男'),('0',u'女')])
    user_type = SelectField(u'修改角色',validators=[DataRequired()],choices=[('NULL',u'不修改'),('student',u'学生'),('teacher',u'教师'),('ass_admin',u'考评管理员'),('sys_admin',u'系统管理员')])
    submit = SubmitField(u"修改")

class Teacher_profile(FlaskForm):
    user_name = StringField(u"姓名",validators=[DataRequired()])
    user_sex = RadioField(u"性别",validators=[DataRequired()],choices=[('1',u'男'),('0',u'女')])
    teacher_major = StringField(u"专业",validators=[DataRequired()])
    teacher_college = StringField(u"学院",validators=[DataRequired()])
    is_instructor = RadioField(u"辅导员",validators=[DataRequired()],choices=[('1',u'是'),('0',u'否')])
    submit = SubmitField(u"修改")

class Admin_Teacher_profile(FlaskForm):
    user_name = StringField(u"姓名",validators=[DataRequired()])
    user_sex = RadioField(u"性别",validators=[DataRequired()],choices=[('1',u'男'),('0',u'女')])
    teacher_major = StringField(u"专业",validators=[DataRequired()])
    teacher_college = StringField(u"学院",validators=[DataRequired()])
    is_instructor = RadioField(u"辅导员",validators=[DataRequired()],choices=[('1',u'是'),('0',u'否')])
    user_type = SelectField(u'修改角色',validators=[DataRequired()],choices=[('NULL',u'不修改'),('student',u'学生'),('teacher',u'教师'),('ass_admin',u'考评管理员'),('sys_admin',u'系统管理员')])
    submit = SubmitField(u"修改")

class New_Template(FlaskForm):
    template_name = StringField(u"模板名称",validators=[DataRequired()])
    problem_list = StringField(u"问题序号",validators=[DataRequired()])
    submit = SubmitField(u"新建模板")

class Create_Ass(FlaskForm):
    deliver_choice = []
    template_choice = []

    def __init__(self):
        super(Create_Ass,self).__init__()
        delivers = Teach_Course.query.all()
        templates = Ass_Template.query.all()

        for de in delivers:
            self.deliver_choice.append((str(de.id),de.teacher_name+'\t'+de.course_id))
        for te in templates:
            self.template_choice.append((str(te.id),str(te.id)))

    ass_name = StringField(u"评教活动名称",validators=[DataRequired()])
    deliver_id = SelectField(u"选择课程",choices=deliver_choice)
    start_time = StringField(u"开始时间(格式：06-12-12-12-30)")
    end_time = StringField(u"结束时间")
    template_id = SelectField(u"选择模板",choices=template_choice)
    submit = SubmitField(u"创建评教活动")

class Ass_result(FlaskForm):
    result = StringField(u"答案序列",validators=[DataRequired()])
    submit = SubmitField(u"提交")