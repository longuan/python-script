### 数据库课程大作业---UIMS管理系统

实现的功能比较少，主要有：

- 用户管理（用户登录验证，资料修改，管理员全局控制）
- 课程查看（数据库后台操作，前台显示）
- 评教系统（学生评价，教师查看自己的结果，管理员管理评教活动）

-------------

这是自己学flask以来第一个实践。给自己打3.5颗星。

flask+bootstrap+sqlalchemy+mysql

整个程序比较无脑，体力活居多，既然课程结束，自己也不想改了索性直接放上来，留给若干年后的自己看。。

------------------

## 使用flask开发

### url_for带参数

```py
from flask import url_for

@app.route('/')
def hello():
    return 'Hello'

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % name

# url_for('hello') 
# url_for('user_page', name='greyli') # 输出：/user/greyli
# url_for('user_page', name='peter') # 输出：/user/peter
# url_for('hello', num=2) # 输出：/?num=2
```


### flask集成的有click

```py
import click

@app.cli.command() # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.') # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop: # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') # 输出提示信息
```