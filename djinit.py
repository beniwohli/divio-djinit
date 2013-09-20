#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# djinit - Divio's Django CMS Initializer
# For Divio-Internal Use only. Usage:
#  python -c "$(curl -fsSL https://raw.github.com/Chive/playground/master/python/djinit.py)"
#
# Copyright (C) 2013 Kim Thoenen <kim@smuzey.ch>.  All Rights Reserved.

import os
from random import choice
import re
import ask


if __name__ == '__main__':
    DIVIO_DJANGO_TEMPLATE = 'git@github.com:divio/divio-django-template.git'
    DIVIO_BOILERPLATE = 'git@github.com:divio/divio-boilerplate.git'
    DIVO_STANDARDSITE = 'git@github.com:divio/divio-standardsite.git'
    versions = {}
    pushes = 4

    q = " -q"  # quiet flag for git commands

    os.system("clear")
    print("-----------------------------")
    print(" Divio DjangoCMS Initializer")
    print("-----------------------------")
    ask.explain(True)
    i = ask.askBool("Do you want the script to create your Github repo?", default='y')
    if i == 'y':
        try:
            from pyrate.services import github
        except ImportError:
            raise ImportError("Warning: Pyrate could not be found."
                              "Please install it and try again. (pip install pyrate -U)")

        github_user = ask.ask("Please enter your Github username")
        github_pass = ask.askPassword("Please enter your Github password")
        github_org = ask.ask("If you want to create the repo on an organisation's account, "
                           "enter its name now. Otherwise hit enter", default='')
        project_name = ask.ask("Please enter a name for the repo")
        project_private = ask.askBool("Should the repo be private?", default='y')
        if project_private == 'y':
            project_private = True

        elif project_private == 'n':
            project_private = False

        h = github.GithubPyrate(github_user, github_pass)
        if github_org:
            h.create_repo(project_name, org_name=github_org, private=project_private)
            repo_owner = github_org
        else:
            h.create_repo(project_name, private=project_private)
            repo_owner = github_user

        # TODO: check if it actually worked!
        github_remote = "git@github.com:" + repo_owner + "/" + project_name + ".git"

    elif i == 'n':
        print("Please create your repo on Github first then!")
        project_name = ask.ask("Please enter the repo name")
        repo_owner = ask.ask("Please enter the account name which the repo belongs to")
        i = ask.askBool("Is this the repo's Github remote: git@github.com:" + repo_owner + "/"
                  + project_name + ".git?", default='y')
        if i == 'y':
            github_remote = "git@github.com:" + repo_owner + "/" + project_name + ".git"
        elif i == 'n':
            github_remote = ask.ask("Please enter your github remote link:")

    i = ask.askBool("Do you want to add the standardsite styles and templates from divio-styleguide?", default='y')
    if i == 'y':
        standardsite = True
        pushes += 1
    elif i == 'n':
        standardsite = False

    i = ask.askBool("Do you want to create a virtualenv and run the makefile (make init)?", default='y')
    if i == 'y':
        minit = True
    elif i == 'n':
        minit = False

    print("")

    # for ease of use
    pn = project_name

    # cloning template
    print("* Cloning Divio Django Template")
    # print("* Cloning Divio Django Template...\t"),
    os.system('git clone ' + DIVIO_DJANGO_TEMPLATE + ' ' + pn + q)
    versions['divio-django-template'] = os.popen('cd ' + pn + ' && git log | head -1').read().strip("commit ").strip("\n")
    print("  OK")
    print("")

    # initializing git repo
    print("* Initializing Git repo")
    os.system('rm -rf ' + pn + '/.git')
    os.system('cd ' + pn + ' && git init' + q)
    os.system('cd ' + pn + ' && git remote add origin ' + github_remote)
    print("  OK")
    print("")

    # initial push to github
    print("* Initial Push to Github")
    os.system('cd ' + pn + ' && git add -A .')
    os.system('cd ' + pn + ' && git commit -m "djinit (1/' + str(pushes)
              + '): Initial commit" -m "push based on divio-django-template (divio/divio-django-template@'
              + str(versions['divio-django-template']) + ')"' + q)
    os.system('cd ' + pn + ' && git push -u origin master' + q)
    print("  OK")
    print("")

    # make temp dir
    os.system("mkdir " + pn + "_tmp")

    # copying boilerplate
    print("* Copying files from Boilerplate")
    os.system('git clone ' + DIVIO_BOILERPLATE + ' ' + pn + '_tmp/bp' + q)
    versions['divio-boilerplate'] = os.popen('cd ' + pn + '_tmp/bp && git log | head -1').read().strip("commit ").strip("\n")
    os.system('cp -r ' + pn + '_tmp/bp/private/sass ' + pn + '_tmp/bp/static ' +
              pn + '_tmp/bp/templates ' + pn + '_tmp/bp/config.rb ' + pn + '/')
    print("  OK")
    print("")

    # after boilerplate add push to github
    print("* Added Boilerplate Files, another push to Github")
    os.system('cd ' + pn + ' && git add -A .')
    os.system('cd ' + pn + ' && git commit -m "djinit (2/' + str(pushes)
              + '): Added boilerplate files" -m "push based on divio-boilerplate (divio/divio-boilerplate@'
              + str(versions['divio-boilerplate']) + ')"' + q)
    os.system('cd ' + pn + ' && git push -u origin master' + q)
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
        if 'SECRET_KEY' not in line and 'Run this on a console to get one' not in line and\
                        'from random import choice; print' not in line:
            f.write(line)

    key = re.escape("".join([choice("abcdefghijklmnopqrstuvwxyz0123456789^&*(-_=+)") for i in range(50)]))
    f.write("SECRET_KEY = '" + key + "'")

    f.close()
    print("  OK")
    print("")

    # move settings
    print("* Moving default settings")
    os.system('cd ' + pn + ' && mv deployment_default.py deployment.py')
    os.system('cd ' + pn + '/src && mv settings_server_dev_default.py settings_server_dev.py')
    print("  OK")
    print("")

    # after settings setup push to github
    print("* Set up Settings, another push to Github")
    os.system('cd ' + pn + ' && git add -A .')
    os.system('cd ' + pn + ' && git commit -m "djinit (3/' + str(pushes) + '): Set up Settings"' + q)
    os.system('cd ' + pn + ' && git push -u origin master' + q)
    print("  OK")
    print("")

    # adding standardsite styles and templates
    if standardsite:
        print("* Copying files from Standardsite")
        os.system('git clone ' + DIVO_STANDARDSITE + ' ' + pn + '_tmp/ss' + q)
        versions['divio-standardsite'] = os.popen('cd ' + pn + '_tmp/ss && git log | head -1').read().strip("commit ").strip("\n")
        os.system('cp ' + pn + '_tmp/ss/templates/standardsite.html ' + pn + '/templates')
        os.system('cp ' + pn + '_tmp/ss/sass/includes/_standardsite.scss ' + pn + '/sass/includes/')
        os.system('cp ' + pn + '_tmp/ss/sass/includes/_settings.scss ' + pn + '/sass/includes/')
        print("  OK")
        print("")

        # updating files for standardsite
        print("* Adding standardsite to cms templates")
        os.system("sed -i '' 's/CMS_TEMPLATES = \[/CMS_TEMPLATES = \[\'$'\n\t(\'standardsite.html\', "
                  "_(\'standardsite\')),/g' src/settings.py")
        os.system("sed -i '' 's/{% extends \"base.html\" %}/{% extends \"standardsite.html\" %}/g' "
                  "templates/fullwidth.html")
        os.system("sed -i '' 's/{% extends \"base.html\" %}/{% extends \"standardsite.html\" %}/g' "
                  "templates/sidebar_left.html")
        os.system("sed -i '' 's/{% extends \"base.html\" %}/{% extends \"standardsite.html\" %}/g' "
                  "templates/sidebar_right.html")
        print("  OK")
        print("")


        # after standardsite add push to github
        print("* Added Standardsite files, another push to Github")
        os.system('cd ' + pn + ' && git add -A .')
        os.system('cd ' + pn + ' && git commit -m "djinit (4/' + str(pushes) +
                  '): Added standardsite files" -m "push based on divio-standardsite (divio/divio-standardsite@'
                  + str(versions['divio-standardsite']) + ')"' + q)
        os.system('cd ' + pn + ' && git push -u origin master' + q)
        print("  OK")
        print("")

    # cleanup
    print("* Cleaning up")
    os.system('rm -rf ' + pn + '_tmp')
    os.system('rm ' + pn + '/project_init.sh')
    print("  OK")
    print("")


    # after cleanup push to github
    print("* Cleaned up, another push to Github")
    os.system('cd ' + pn + ' && git add -A .')
    os.system('cd ' + pn + ' && git commit -m "djinit (' + str(pushes) + '/' + str(pushes) + '): Cleanup"' + q)
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
