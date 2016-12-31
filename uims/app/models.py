#coding:utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager,db
from datetime import datetime


def init_db():
    pass

def init_user():
    admin1 = Sys_Admin(user_num="00000000",user_name=u"扫地僧",user_sex=1,password='cat')
    assadmin1 = Ass_Admin(user_num="22222222",user_name=u"金庸",user_sex=1,password='cat')

    student1 = Student(user_num="21142101",user_name=u"萧峰",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student2 = Student(user_num="21142102",user_name=u"段誉",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student3 = Student(user_num="21142103",user_name=u"虚竹",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student4 = Student(user_num="21142104",user_name=u"完颜阿骨打",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student5 = Student(user_num="21142110",user_name=u"阿朱",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student7 = Student(user_num="21142105",user_name=u"慕容复",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student8 = Student(user_num="21142106",user_name=u"王语嫣",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student9 = Student(user_num="21142107",user_name=u"鸠摩智",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student10 = Student(user_num="21142108",user_name=u"游坦之",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student11 = Student(user_num="21142109",user_name=u"木婉清",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student12 = Student(user_num="21142111",user_name=u"叶二娘",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student6 = Student(user_num="21142112",user_name=u"玄慈",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)


    teacher1 = Teacher(user_num="09002101",user_name=u"段延庆",user_sex=1,password='cat',
                       teacher_major=u"计算机",teacher_college=u"计算机",is_instructor=0)
    teacher2 = Teacher(user_num="09002102",user_name=u"萧远山",user_sex=1,password='cat',
                       teacher_major=u"计算机",teacher_college=u"计算机",is_instructor=0)
    teacher3 = Teacher(user_num="09002103",user_name=u"无崖子",user_sex=1,password='cat',
                       teacher_major=u"计算机",teacher_college=u"计算机",is_instructor=1)
    teacher4 = Teacher(user_num="09002104",user_name=u"天山童姥",user_sex=0,password='cat',
                       teacher_major=u"计算机",teacher_college=u"计算机",is_instructor=0)
    teacher5 = Teacher(user_num="09002105",user_name=u"李秋水",user_sex=0,password='cat',
                       teacher_major=u"计算机",teacher_college=u"计算机",is_instructor=0)
    teacher6 = Teacher(user_num="09002106",user_name=u"慕容博",user_sex=1,password='cat',
                       teacher_major=u"计算机",teacher_college=u"计算机",is_instructor=0)

    db.session.add_all([student1,student10,student11,student12,student2,student3,student4,student5,\
                                admin1,assadmin1,teacher1,teacher2,teacher3,teacher4,teacher5,teacher6,\
                                student6,student7,student8,student9])

def init_course():
    course1 = Course(course_name=u"数据结构",course_credit=4,course_college=u"计算机")
    course2 = Course(course_name=u"图形学",course_credit=4,course_college=u"计算机")
    course3 = Course(course_name=u"计算机组成原理",course_credit=4,course_college=u"计算机")
    course4 = Course(course_name=u"算法设计与分析",course_credit=4,course_college=u"计算机")

    student1 = Student(user_num="21142101",user_name=u"萧峰",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student2 = Student(user_num="21142102",user_name=u"段誉",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student3 = Student(user_num="21142103",user_name=u"虚竹",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student4 = Student(user_num="21142104",user_name=u"完颜阿骨打",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student5 = Student(user_num="21142110",user_name=u"阿朱",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student7 = Student(user_num="21142105",user_name=u"慕容复",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student8 = Student(user_num="21142106",user_name=u"王语嫣",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student9 = Student(user_num="21142107",user_name=u"鸠摩智",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student10 = Student(user_num="21142108",user_name=u"游坦之",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student11 = Student(user_num="21142109",user_name=u"木婉清",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student12 = Student(user_num="21142111",user_name=u"叶二娘",user_sex=0,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)
    student6 = Student(user_num="21142112",user_name=u"玄慈",user_sex=1,password='cat',
                       student_major=u"计算机",student_college=u"计算机",student_class=21)




    deliver1 = Teach_Course(teacher_id="09002101",course_id=course1.course_name)
    deliver2 = Teach_Course(teacher_id="09002102",course_id=course2.course_name)
    deliver3 = Teach_Course(teacher_id="09002103",course_id=course3.course_name)
    deliver4 = Teach_Course(teacher_id="09002104",course_id=course4.course_name)
    deliver5 = Teach_Course(teacher_id="09002105",course_id=course1.course_name)
    deliver6 = Teach_Course(teacher_id="09002106",course_id=course2.course_name)

    select1 = Course_Selected(deliver_id=deliver3.id,student_id=student1.user_num,course_grade=80)
    select2 = Course_Selected(deliver_id=deliver3.id,student_id=student2.user_num,course_grade=80)
    select3 = Course_Selected(deliver_id=deliver3.id,student_id=student3.user_num,course_grade=80)
    select4 = Course_Selected(deliver_id=deliver3.id,student_id=student4.user_num,course_grade=80)
    select5 = Course_Selected(deliver_id=deliver3.id,student_id=student5.user_num,course_grade=80)
    select6 = Course_Selected(deliver_id=deliver3.id,student_id=student6.user_num,course_grade=80)
    select7 = Course_Selected(deliver_id=deliver3.id,student_id=student7.user_num,course_grade=80)
    select8 = Course_Selected(deliver_id=deliver3.id,student_id=student8.user_num,course_grade=80)
    select9 = Course_Selected(deliver_id=deliver3.id,student_id=student9.user_num,course_grade=80)
    select10 = Course_Selected(deliver_id=deliver3.id,student_id=student10.user_num,course_grade=80)
    select11 = Course_Selected(deliver_id=deliver3.id,student_id=student11.user_num,course_grade=80)
    select12 = Course_Selected(deliver_id=deliver3.id,student_id=student12.user_num,course_grade=80)
    db.session.add_all([select1,select10,select11,select12,select2,select3,select4,select5,select6,select7,select8,select9])
    # db.session.add_all([deliver1,deliver2,deliver3,deliver4,deliver5,deliver6])
    # db.session.commit()

def init_select():
    """

    class Course_Selected(db.Model):
    __tablename__ = 'selected'
    id = db.Column(db.Integer,primary_key=True)
    deliver_id = db.Column(db.Integer,db.ForeignKey('delivers.id'))
    student_id = db.Column(db.String(8),db.ForeignKey('students.id'))
    course_grade = db.Column(db.Integer)
    """

    select1 = Course_Selected(deliver_id=1,student_id="21142101",course_grade=80)
    select2 = Course_Selected(deliver_id=1,student_id="21142102",course_grade=80)
    select3 = Course_Selected(deliver_id=1,student_id="21142103",course_grade=80)
    select4 = Course_Selected(deliver_id=1,student_id="21142104",course_grade=80)
    select5 = Course_Selected(deliver_id=1,student_id="21142105",course_grade=80)
    select6 = Course_Selected(deliver_id=1,student_id="21142106",course_grade=80)
    select7 = Course_Selected(deliver_id=1,student_id="21142107",course_grade=80)
    select8 = Course_Selected(deliver_id=1,student_id="21142108",course_grade=80)
    select9 = Course_Selected(deliver_id=1,student_id="21142109",course_grade=80)
    select10 = Course_Selected(deliver_id=1,student_id="21142111",course_grade=80)
    select11 = Course_Selected(deliver_id=1,student_id="21142110",course_grade=80)
    select12 = Course_Selected(deliver_id=1,student_id="21142112",course_grade=80)
    db.session.add_all([select1,select10,select11,select12,select2,select3,select4,select5,select6,select7,select8,select9])
    db.session.commit()



# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User', backref='role', lazy='dynamic')
#
#     def __repr__(self):
#         return "<Role %r>" % self.name

class User(UserMixin, db.Model):
    """
    用户表，存储所有用户基本信息
    """
    __tablename__ = 'users'
    user_num = db.Column(db.String(8), primary_key=True, index=True)
    user_pass_hash = db.Column(db.String(128))
    user_name = db.Column(db.Unicode(32),nullable=False)
    user_sex = db.Column(db.Boolean)
    # role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    type = db.Column(db.String(32))

    __mapper_args__ = {
       'polymorphic_identity':'users',
        'polymorphic_on':type
    }

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.user_pass_hash = generate_password_hash(password)

    def vertify_password(self, password):
        return check_password_hash(self.user_pass_hash, password)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

class Sys_Admin(User):
    """
    系统管理员表
    """
    __tablename__ = 'sys_admins'
    id = db.Column(db.String(8),db.ForeignKey('users.user_num'),primary_key=True)
    __mapper_args__ = {
       'polymorphic_identity':'sys_admin',
    }


class Student(User):
    """
    学生表，存储学生专业班级信息
    """
    __tablename__ = 'students'
    id = db.Column(db.String(8),db.ForeignKey('users.user_num'),primary_key=True)
    student_major = db.Column(db.Unicode(64))
    student_college = db.Column(db.Unicode(32))
    student_class = db.Column(db.String(2))
    __mapper_args__ = {
       'polymorphic_identity':'student',
    }

    @property
    def username(self):
        return User.query.filter_by(user_num=self.id).first().user_name

class Teacher(User):
    """
    教师表，存储教师专业以及是否是辅导员
    """
    __tablename__ = 'teachers'
    id = db.Column(db.String(8),db.ForeignKey('users.user_num'),primary_key=True)
    teacher_major = db.Column(db.Unicode(64))
    teacher_college = db.Column(db.Unicode(32))
    is_instructor = db.Column(db.Boolean)
    __mapper_args__ = {
        'polymorphic_identity': 'teacher',
    }


    @property
    def username(self):
        return User.query.filter_by(user_num=self.id).first().user_name

class Ass_Admin(User):
    """
    考评管理员
    """
    __tablename__ = 'ass_admins'
    id = db.Column(db.String(8), db.ForeignKey('users.user_num'),primary_key=True)
    __mapper_args__ = {
        'polymorphic_identity': 'ass_admin',
    }


class Course(db.Model):
    """
    课程表，存储所有课程信息
    """
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.Unicode(32),unique=True,index=True)
    course_credit = db.Column(db.Integer)
    course_college = db.Column(db.Unicode(32))

class Teach_Course(db.Model):
    """
    授课表，教师与课程对应关系
    """
    __tablename__ = 'delivers'
    id = db.Column(db.Integer,primary_key=True)
    teacher_id = db.Column(db.String(8),db.ForeignKey('teachers.id'))
    course_id = db.Column(db.Unicode(32),db.ForeignKey('courses.course_name'))

    @property
    def teacher_name(self):
        return User.query.filter_by(user_num=self.teacher_id).first().user_name

class Course_Selected(db.Model):
    """
    选课表，学生与授课对应关系
    """
    __tablename__ = 'selected'
    id = db.Column(db.Integer,primary_key=True)
    deliver_id = db.Column(db.Integer,db.ForeignKey('delivers.id'))
    student_id = db.Column(db.String(8),db.ForeignKey('students.id'))
    course_grade = db.Column(db.Integer)

    @property
    def student_name(self):
        return User.query.filter_by(user_num=self.student_id).first().user_name

    @property
    def teacher_name(self):
        teacher_id = Teach_Course.query.filter_by(id=self.deliver_id).first().teacher_id
        return User.query.filter_by(user_num=teacher_id).first().user_name

# class Ass_Problem(db.Model):
#     __tablename__ = 'problems'
#     id = db.Column(db.Integer,primary_key=True)
#     problem_main = db.Column(db.Unicode(128))
#     option_A = db.Column(db.Unicode(32))
#     option_B = db.Column(db.Unicode(32))
#     option_C = db.Column(db.Unicode(32))
#     option_D = db.Column(db.Unicode(32))


class Ass_Template(db.Model):
    """
    模板表，保存所有可选模板
    """
    __tablename__ = 'templates'
    id = db.Column(db.Integer,primary_key=True)
    template_name = db.Column(db.Unicode(32))
    problem_list = db.Column(db.String(32))

class Ass_History(db.Model):
    """
    评教历史表，保存所有评教历史
    """
    __tablename__ = 'historys'
    id = db.Column(db.Integer,primary_key=True)
    ass_name = db.Column(db.Unicode(128))
    deliver_id = db.Column(db.Integer,db.ForeignKey('delivers.id'))
    template_id = db.Column(db.Integer,db.ForeignKey('templates.id'))
    ass_start_time = db.Column(db.String(15))
    ass_end_time = db.Column(db.String(15))
    """
    dt = datetime.strptime("06/12/11/16/30/", "%y/%m/%d/%H/%M/")
    time = datetime.now()
    flag = dt>time
    """
    is_certain_teacher = db.Column(db.Boolean)

    @property
    def teacher_name(self):
        teacher_id = Teach_Course.query.filter_by(id=self.deliver_id).first().teacher_id
        return User.query.filter_by(user_num=teacher_id).first().user_name

    @property
    def course_name(self):
        return Teach_Course.query.filter_by(id=self.deliver_id).first().course_id

    def is_running(self):
        dt = datetime.strptime(self.ass_start_time,"%y-%m-%d-%H-%M")
        dtn = datetime.strptime(self.ass_end_time,"%y-%m-%d-%H-%M")
        return True if datetime.now() > dt and  dtn > datetime.now() else False

    def is_ended(self):
        dt = datetime.strptime(self.ass_start_time,"%y-%m-%d-%H-%M")
        dtn = datetime.strptime(self.ass_end_time,"%y-%m-%d-%H-%M")
        return True if dtn < datetime.now() else False

    @property
    def start_time(self):
        return datetime.strptime(self.ass_start_time,"%y-%m-%d-%H-%M")

    @property
    def end_time(self):
        return datetime.strptime(self.ass_end_time,"%y-%m-%d-%H-%M")


class Ass_Student(db.Model):
    """
    学生评教记录表
    """
    __tablename__ = 'records'
    id = db.Column(db.Integer,primary_key=True)
    student_id = db.Column(db.String(8),db.ForeignKey('students.id'),index=True)
    history_id = db.Column(db.Integer,db.ForeignKey('historys.id'))
    answer_list = db.Column(db.String(32))

    @property
    def student_name(self):
        return User.query.filter_by(user_num=self.student_id).first().user_name

    @property
    def is_ended(self):
        return Ass_History.query.filter_by(id=self.history_id).first().is_ended()

    @property
    def history(self):
        return Ass_History.query.filter_by(id=self.history_id).first()