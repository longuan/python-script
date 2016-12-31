#coding:utf-8
from . import app,db
from flask import render_template,url_for,flash,redirect,request
from .forms import LoginForm,change_passwd,Student_profile,Admin_profile,Teacher_profile,\
                New_Template,Create_Ass,Ass_result,Register
from flask_login import login_required,login_user,current_user,logout_user
from .models import User,Course,Teach_Course,Course_Selected,Student,Ass_Template,Teacher,\
                        Ass_History,Ass_Student,Sys_Admin,Ass_Admin
from .utils import page_role,admin_required,profile_html,profile_form,ass_required,\
                            role_user,admin_profile_form
from collections import defaultdict
from .problems import problems


role_type = {
            'student': Student,
            'teacher': Teacher,
            'sys_admin': Sys_Admin,
            'ass_admin': Ass_Admin
}


@app.errorhandler(404)
def not_found(a):
    msg = "you are lost your way?"
    return render_template('404.html', title='page_not_found', msg=msg)

@app.route('/',methods=['POST','GET'])
@app.route('/index',methods=['POST','GET'])
@app.route('/login',methods=['POST','GET'])
def login():
    """
    主页就是登录
    """
    form = LoginForm()
    if form.validate_on_submit():
        uename = form.username.data
        passwd = form.password.data
        user1 = User.query.filter_by(user_num=uename).first()
        if user1 is not None and user1.vertify_password(passwd) and user1.type == form.identity.data:
            login_user(user1, form.remember_me.data)
            flash(u"登陆成功")
            return redirect(url_for('my_profile'))
            # return render_template('base.html',type=form.identity.data)
        flash(u'无效用户名密码')
    return render_template('index.html', form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        using = User.query.filter_by(user_num=form.user_num.data).first()
        if using is not None:
            flash(u"用户已存在，无法注册")
            return render_template('register.html',form=form)
        type = role_type[form.identity.data]
        new_user = type(user_num = form.user_num.data,
                        user_name = form.user_name.data,
                        password = form.password.data,
                        user_sex = int(form.user_sex.data)
            )
        db.session.add(new_user)
        flash(u"注册成功，请登录")
        return redirect(url_for('login'))

    return render_template('register.html',form=form)



@app.route('/myprofile')
@login_required
def my_profile():
    """
登陆之后跳转到此路由，根据登录用户不同显示不同页面
"""
    index_html = page_role[current_user.type]
    curr_profile_html = profile_html[current_user.type]
    return render_template(curr_profile_html,index_html=index_html,user=current_user,role_user=role_user)

@app.route('/changepasswd',methods=['GET','POST'])
@login_required
def change_my_passwd():
    """
    修改自己的密码
    """
    form = change_passwd()
    index_html = page_role[current_user.type]
    if form.validate_on_submit():
        oldpass = form.old_passwd.data
        newpass = form.new_passwd.data
        if oldpass and newpass:
            if current_user.vertify_password(oldpass):
                current_user.password = newpass
                db.session.add(current_user)
                flash(u"修改成功,请重新登录")
                return redirect(url_for('login'))
            flash(u"旧密码不正确")
    return render_template('changepasswd.html',index_html=index_html,form=form,name=u"修改密码")


@app.route('/showalluser')
@login_required
@admin_required
def show_all_user():
    """
    admin的专属路由，显示所有用户
    """
    users = User.query.all()
    return render_template('showalluser.html',users=users,role_user=role_user)


@app.route('/users/<int:user_num>')
@login_required
def user_info(user_num):
    """
    类似api，动态传入用户编号
    """
    index_html = page_role[current_user.type]
    user1 = User.query.filter_by(user_num=user_num).first_or_404()
    curr_profile_html = profile_html[user1.type]
    return render_template(curr_profile_html,index_html=index_html,user=user1,role_user=role_user)

@app.route('/users/<int:user_num>/courses')
@login_required
def student_courses(user_num):
    """
    显示某个学生所选的所有课程
    """
    result = []
    if current_user.type == 'student':
        # student = Student.query.filter_by(user_num=user_num).first()
        delivers = Course_Selected.query.filter_by(student_id=user_num).all()
        for deliver in delivers:
            ddic = {}
            ddic['course_grade'] = deliver.course_grade
            ddlivers = Teach_Course.query.filter_by(id=deliver.deliver_id).first()
            ddic['teacher_id'] = deliver.teacher_name
            ddic['course_id'] = ddlivers.course_id
            result.append(ddic)
        return render_template('studentcourse.html',course=result)
    if current_user.type == 'teacher':
        courses = Teach_Course.query.filter_by(teacher_id=current_user.user_num).all()
        for course in courses:
            ddic = {}
            ddic['course_id'] = Course.query.filter_by(course_name=course.course_id).first().id
            ddic['course_name'] = course.course_id
            result.append(ddic)
        return render_template('teachercourse.html',course=result)

@app.route('/changeownprofile',methods=['GET','POST'])
@login_required
def change_own_profile():
    """
    修改自己的资料
    """
    form = profile_form[current_user.type]()
    if form.validate_on_submit():
        if current_user.type == 'student':
            current_user.user_name = form.user_name.data
            current_user.user_sex = int(form.user_sex.data)
            current_user.student_college = form.student_college.data
            current_user.student_major = form.student_major.data
            current_user.student_class = form.student_class.data
        if current_user.type == 'teacher':
            current_user.user_name = form.user_name.data
            current_user.user_sex = int(form.user_sex.data)
            current_user.teacher_major = form.teacher_major.data
            current_user.teacher_college = form.teacher_college.data
            current_user.is_instructor = int(form.is_instructor.data)
        if current_user.type == 'sys_admin' or current_user.type == "ass_admin":
            current_user.user_name = form.user_name.data
            current_user.user_sex = int(form.user_sex.data)
        db.session.add(current_user)
        flash(u"修改成功")
        return redirect(url_for('my_profile'))
    index_html = page_role[current_user.type]
    return render_template('changepasswd.html',index_html=index_html,form=form,name=u"修改资料")

@app.route('/changeprofile/<int:user_num>',methods=['GET','POST'])
@login_required
@admin_required
def change_profile(user_num):
    """
    admin用此路由修改其他用户的资料
    """
    c_user1 = User.query.filter_by(user_num=user_num).first()
    form = admin_profile_form[c_user1.type]()
    if form.validate_on_submit():
        if form.user_type.data == 'NULL' or form.user_type.data == c_user1.type:
            if c_user1.type == 'student':
                c_user1.user_name = form.user_name.data
                c_user1.user_sex = int(form.user_sex.data)
                c_user1.student_college = form.student_college.data
                c_user1.student_major = form.student_major.data
                c_user1.student_class = form.student_class.data
            if c_user1.type == 'teacher':
                c_user1.user_name = form.user_name.data
                c_user1.user_sex = int(form.user_sex.data)
                c_user1.teacher_major = form.teacher_major.data
                c_user1.teacher_college = form.teacher_college.data
                c_user1.is_instructor = int(form.is_instructor.data)
            if c_user1.type == 'sys_admin' or c_user1.type == "ass_admin":
                c_user1.user_name = form.user_name.data
                c_user1.user_sex = int(form.user_sex.data)
            db.session.add(c_user1)
        flash(u"修改成功")
        return redirect(url_for('my_profile'))
    index_html = page_role[current_user.type]
    return render_template('changepasswd.html',index_html=index_html,form=form)

@app.route('/showallcourse')
@login_required
@admin_required
def show_all_course():
    """
    admin用此路由显示所有课程
    """
    courses = Course.query.all()
    return render_template('showallcourse.html',courses=courses)

@app.route('/course/<int:id>')
@login_required
def course_info(id):
    """
    动态传入课程ID显示信息
    """
    course = Course.query.filter_by(id=id).first()
    delivers = Teach_Course.query.filter_by(course_id=course.course_name).all()
    course_dic = defaultdict()
    index_html = page_role[current_user.type]
    for deliver in delivers:
        course_dic[deliver.teacher_id] = []
        for i in Course_Selected.query.filter_by(deliver_id=deliver.id).all():
            if i.student_id not in course_dic[deliver.teacher_id]:
                course_dic[deliver.teacher_id].append((i.teacher_name,i.student_id,i.student_name))
    return render_template('courseinfo.html',index_html=index_html,coursename=course.course_name,course_dic=course_dic)

@app.route('/templatelist')
@login_required
@ass_required
def all_template():
    """
    考评管理员可以在此看到所有模板
    """
    templates = Ass_Template.query.all()
    problem_template = []
    for i,template in enumerate(templates):
        problem_template.append(list())
        problem_template[i].append(template.template_name)
        for pp in list(template.problem_list):
            problem_template[i].append(problems[int(pp)]['main'])
    return render_template('templates.html',p=problem_template)

@app.route('/newtemplate',methods=['GET','POST'])
@login_required
@ass_required
def new_template():
    """
    新建模板
    """
    form = New_Template()
    if form.validate_on_submit():
        problem_list = form.problem_list.data
        template_name = form.template_name.data
        new_tem = Ass_Template( template_name=template_name,problem_list=problem_list)
        db.session.add(new_tem)
        flash(u"添加成功")
        return redirect(url_for('my_profile'))
    a = range(len(problems))
    result = list(zip(a,problems))
    return render_template('createtemplate.html',problems=result,form=form)

@app.route('/deletetemplate')
@login_required
@ass_required
def delete_template():
    """
    删除模板
    """
    pass


@app.route('/newass',methods=['GET','POST'])
@login_required
@ass_required
def create_ass():
    """
    创建评教活动
    """
    form = Create_Ass()
    templates = Ass_Template.query.all()
    if form.validate_on_submit():
        newass = Ass_History(ass_name=form.ass_name.data,
                             deliver_id=form.deliver_id.data,
                             template_id=form.template_id.data,
                             ass_start_time=form.start_time.data,
                             ass_end_time=form.end_time.data,
                             is_certain_teacher=False)
        db.session.add(newass)
        flash(u"创建成功")
        return redirect(url_for('my_profile'))
    return render_template('createass.html',form=form)



@app.route('/allass')
@login_required
@ass_required
def all_asses():
    """
    显示所有历史评教活动
    """
    all_score = {}
    all_history = Ass_History.query.all()
    for history in all_history:
        records = Ass_Student.query.filter_by(history_id=history.id)
        problem_answer = ""
        for reco in records:
            problem_answer += reco.answer_list.upper()
        if len(problem_answer) != 0:
            A_count = problem_answer.count('A')
            B_count = problem_answer.count('B')
            C_count = problem_answer.count('C')
            D_count = problem_answer.count('D')
            score = float(A_count*100+B_count*80+C_count*60+D_count*40)/len(problem_answer)
            all_score[history.id] = score
        else:
            all_score[history.id] = 0
    result = sorted(list(zip(all_score.values(),all_score.keys())))
    result = result[::-1]
    return render_template('allhistory.html',historys=all_history,all_score=all_score,result=result,lenresult=len(result))

@app.route('/studentassing')
@login_required
def student_ass_list():
    """
    学生对应的进行中评教活动
    """
    using_ass = [ history for history in Ass_History.query.all() if history.is_running()]
    xuanxiu_delivers = Course_Selected.query.filter_by(student_id=current_user.user_num).all()
    xuanxiu_deliver_id = set([x.deliver_id for x in xuanxiu_delivers])
    result = []
    for j in using_ass:
        if j.deliver_id in xuanxiu_deliver_id:
            result.append(j)
    return render_template('studentrunning.html',historys=result)


@app.route('/assing/<int:history_id>',methods=['GET','POST'])
@login_required
def student_ass(history_id):
    """
    学生在此路由进行评教
    """
    history = Ass_History.query.filter_by(id=history_id).first_or_404()
    form = Ass_result()

    problem_template = []
    template = Ass_Template.query.filter_by(id=history.template_id).first()
    for i,pp in enumerate(list(template.problem_list)):
        problem_template.append((i,problems[int(pp)]))
    old_answer_li = Ass_Student.query.filter_by(student_id=current_user.user_num).first()
    if old_answer_li is not None:
        old_answer_li = old_answer_li.answer_list
    if form.validate_on_submit():
        new_record = Ass_Student.query.filter_by(student_id = current_user.user_num,history_id = history.id).first()
        if new_record is None:
            new_record = Ass_Student(student_id = current_user.user_num,
                                    history_id = history.id,
                                    answer_list = form.result.data
                                    )
        else:
            new_record.answer_list = form.result.data
        db.session.add(new_record)
        flash(u"已完成")
        return redirect(url_for('my_profile'))
    return render_template('/studentass.html',problems=problem_template,form=form,old_answer=old_answer_li)


@app.route('/history/<int:id>')
@login_required
def history_info(id):
    """
    详细显示评教活动信息
    """
    records = Ass_Student.query.filter_by(history_id=id)
    problem_answer = ""
    index_html = page_role[current_user.type]
    for reco in records:
        problem_answer += reco.answer_list.upper()
    options = {}
    if len(problem_answer) != 0:
        A_count = problem_answer.count('A')
        B_count = problem_answer.count('B')
        C_count = problem_answer.count('C')
        D_count = problem_answer.count('D')
        A_percent = str((float(A_count)/len(problem_answer))*100)
        options['A'] = A_percent[:4]+'%'
        A_percent = str((float(B_count)/len(problem_answer))*100)
        options['B'] = A_percent[:4]+'%'
        A_percent = str((float(C_count)/len(problem_answer))*100)
        options['C'] = A_percent[:4]+'%'
        A_percent = str((float(D_count)/len(problem_answer))*100)
        options['D'] = A_percent[:5]+'%'
        score = float(A_count*100+B_count*80+C_count*60+D_count*40)/len(problem_answer)
    else:
        flash(u"尚无结果")
        return redirect(url_for('my_profile'))
    return render_template('historyinfo.html',index_html=index_html,records=records,options=options,score=score)

@app.route('/assresult')
@login_required
@ass_required
def ass_result():
    historys = [ history for history in Ass_History.query.all() if history.is_running() ]
    return render_template('assresult.html')

@app.route('/studenthistory')
@login_required
def student_history():
    """
    学生历史评教列表
    """
    end_ass = [ record for record in Ass_Student.query.filter_by(student_id=current_user.user_num).all() if record.is_ended]
    return render_template('studenthistorylist.html',historys=end_ass)

@app.route('/oldass/<int:ass_num>',methods=['GET','POST'])
@login_required
def old_ass(ass_num):
    """
    学生查看自己的历史评教信息
    """
    history_id = Ass_Student.query.filter_by(id=ass_num).first()
    history = history_id.history
    problem_template = []
    template = Ass_Template.query.filter_by(id=history.template_id).first()
    for i,pp in enumerate(list(template.problem_list)):
        problem_template.append((i,problems[int(pp)]))
    old_answer = Ass_Student.query.filter_by(student_id=current_user.user_num,history_id=ass_num).first().answer_list
    return render_template('/oldass.html',problems=problem_template,old_answer=old_answer)

@app.route('/teacherasslist')
@login_required
def teacher_ass_list():
    """
    某个教师的评教活动列表
    """
    end_history = [history for history in Ass_History.query.all() if history.is_ended()]
    delivers = Teach_Course.query.filter_by(teacher_id=current_user.user_num).all()
    deliver_ids = set([ x.id for x in delivers ])
    result = []
    for i in end_history:
        if i.deliver_id in deliver_ids:
            result.append(i)
    return render_template('teacherresult.html',historys=result)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You hav been logout.')
    return redirect(url_for('login'))