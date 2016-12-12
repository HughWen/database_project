#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Permission
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask import request, jsonify
from getContent import *
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.route('/topics/_add_numbers')
def add_numbers():
    torrent_id = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    if b ==3:
        id_num = 30 
    else:
        id_num = 100
    counter1 = get_tag_list(torrent_id, id_num)
    list1 = counter1.most_common(10)
    text_list = []
    for i in range(10):
        text_list.append(list1[i][0] + '\t' + str(list1[i][1]))
    text1 = list1[0][0] + '\t' + str(list1[0][1])
    text2 = list1[1][0] + '\t' + str(list1[1][1])
    text3 = list1[2][0] + '\t' + str(list1[2][1])
    text4 = list1[3][0] + '\t' + str(list1[3][1])
    text5 = list1[4][0] + '\t' + str(list1[4][1])
    text6 = list1[5][0] + '\t' + str(list1[4][1])
    text7 = list1[6][0] + '\t' + str(list1[4][1])
    text8 = list1[7][0] + '\t' + str(list1[4][1])
    text9 = list1[8][0] + '\t' + str(list1[4][1])
    text10 = list1[9][0] + '\t' + str(list1[4][1])

    return jsonify(result0=text_list[0], result1=text_list[1], result2=text_list[2], result3=text_list[3], result4=text_list[4],result5=text_list[5],
                   result6=text_list[6],result7=text_list[7],result8=text_list[8],result9=text_list[9]
    )

if __name__ == '__main__':
    manager.run()
