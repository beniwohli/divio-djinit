#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# djinit - Divio's Django CMS Initializer
# For Divio-Internal Use only. Usage:
#  python -c "$(curl -fsSL https://raw.github.com/Chive/playground/master/python/djinit.py)"
#
# Copyright (C) 2013 Kim Thoenen <kim@smuzey.ch>.  All Rights Reserved.
from getpass import getpass

import os
from random import choice


if __name__ == '__main__':

    # Fix python 2.x
    try:
        input = raw_input
    except NameError:
        pass

    _pyrate = False

    DIVIO_DJANGO_TEMPLATE = 'git@github.com:divio/divio-django-template.git'
    DIVIO_BOILERPLATE = 'git@github.com:divio/divio-boilerplate.git'
    DIVO_STANDARDSITE = 'git@github.com:divio/divio-standardsite.git'

    q = " -q"  # quiet flag for git commands

    os.system("clear")
    print("-----------------------------")
    print(" Divio DjangoCMS Initializer")
    print("-----------------------------")
    while 1:
        i = input("Do you want the script to create your Github repo? (y/n)")
        if i == 'y':
            try:
                from pyrate.services import github
                _pyrate = True
            except ImportError:
                raise ImportError("Warning: Pyrate could not be found."
                                  "Please install it and try again. (pip install pyrate -U)")

            github_user = input("Please enter your Github username: ")
            github_pass = getpass("Please enter your Github password: ")
            github_org = input("If you want to create the repo on an organisation's account, "
                               "enter its name now. Otherwise hit enter: ")
            project_name = input("Please enter a name for the repo: ")
            while 1:
                project_private = input("Should the repo be private? (y/n) ")
                if project_private == 'y':
                    project_private = True
                    break

                elif project_private == 'n':
                    project_private = False
                    break

                print("invalid input")

            h = github.GithubPyrate(github_user, github_pass)
            if github_org:
                h.create_repo(project_name, org_name=github_org, private=project_private)
                repo_owner = github_org
            else:
                h.create_repo(project_name, private=project_private)
                repo_owner = github_user

            # TODO: check if it actually worked!
            github_remote = "git@github.com:" + repo_owner + "/" + project_name + ".git"
            break

        elif i == 'n':
            print("Please create your repo on Github first then!")
            project_name = input("Please enter the repo name: ")
            repo_owner = input("Please enter the account which the repo belongs to: ")
            while 1:
                i = input("Is this the repo's Github remote: git@github.com:" + repo_owner + "/" + project_name + ".git? (y/n) ")
                if i == 'y':
                    github_remote = "git@github.com:" + repo_owner + "/" + project_name + ".git"
                    break
                elif i == 'n':
                    github_remote = input("Please enter your github remote then: ")
                    break
                print("invalid input")
            break
        print("invalid input")

    while 1:
        i = input("Do you want to add the standardsite styles and templates from divio-styleguide? (y/n) ")
        if i == 'y':
            standardsite = True
            break
        elif i == 'n':
            standardsite = False
            break
        print("invalid input")

    while 1:
        i = input("Do you want to create a virtualenv and run the makefile (make init)? (y/n) ")
        if i == 'y':
            minit = True
            break
        elif i == 'n':
            minit = False
            break
        print("invalid input")

    print("")

    # for ease of use
    pn = project_name

    # cloning template
    print("* Cloning Divio Django Template")
    # print("* Cloning Divio Django Template...\t"),
    os.system('git clone ' + DIVIO_DJANGO_TEMPLATE + ' ' + pn + q)
    print("  OK")
    print("")

    # init-ing git repo
    print("* Initializing Git repo")
    os.system('rm -rf ' + pn + '/.git')
    os.system('cd ' + pn + ' && git init' + q)
    os.system('cd ' + pn + ' && git remote add origin ' + github_remote)
    print("  OK")
    print("")

    # copying boilerplate
    print("* Copying files from Boilerplate")
    os.system('git clone ' + DIVIO_BOILERPLATE + ' ' + pn + '_tmp/bp' + q)
    os.system('cd ' + pn + '_tmp/bp')
    os.system('cp -r ' + pn + '_tmp/bp/sass ' + pn + '_tmp/bp/static ' +
              pn + '_tmp/bp/templates ' + pn + '_tmp/bp/config.rb ' + pn + '/')
    print("  OK")
    print("")

    # adding secret key and removing exception
    print("* Generating super secret key")
    f = open(pn + "/src/settings.py", "r")
    lines = f.readlines()
    f.close()
    f = open(pn + "/src/settings.py", "w")
    for line in lines:
        # removing secret key and exception and comments concerning this
        if 'SECRET_KEY' not in line and 'Run this on a console to get one' not in line and 'from random import choice; print' not in line:
            f.write(line)

    key = ''.join([choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])
    f.write("SECRET_KEY = '" + key + "'")

    f.close()
    print("  OK")
    print("")

    # adding standardsite styles and templates
    if standardsite:
        print("* Copying files from Standardsite")
        os.system('git clone ' + DIVO_STANDARDSITE + ' ' + pn + '_tmp/ss' + q)
        os.system('cp ' + pn + '_tmp/ss/templates/standardsite.html ' + pn + '/templates')
        os.system('cp ' + pn + '_tmp/ss/sass/includes/_standardsite.scss ' + pn + '/sass/includes/')
        os.system('cp ' + pn + '_tmp/ss/sass/includes/_settings.scss ' + pn + '/sass/includes/')
        print("  OK")
        print("")

    # cleanup
    print("* Cleaning up")
    os.system('rm -rf ' + pn + '_tmp')
    print("  OK")
    print("")

    # push to github
    print("* Pushing local repo to Github")
    os.system('cd ' + pn + ' && git add .')
    os.system('cd ' + pn + ' && git commit -m "Initial commit (djinit)"' + q)
    os.system('cd ' + pn + ' && git push -u origin master' + q)
    print("  OK")
    print("")

    if minit:
        print("* Setting up virtual environment")
        os.system('cd ' + pn + ' && virtualenv --prompt="(' + pn + ')" env --no-site-packages -q')
        print("  OK")
        print("")

        print("* Make init")
        os.system('cd ' + pn + ' && source env/bin/activate && make init')
        print("  OK")
        print("")

    print("")
    print("")
    print("All done!")
    if standardsite:
        print("")
        print("don't forget to:")
        print("* add ('standardsite.html', _('standardsite')),"
              "within src/settings.py at CMS_TEMPLATES as first position")
        print("* change {% extend %} to standardsite.html instead of base.html within all selectable templates")
