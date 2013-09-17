#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Important: For now pip install ask==0.0.6

"""
djinit: Divio's DjangoCMS Initializer

Usage:
    djinit <repo_name> -u <user> -p <pass> [-o <organization> -c -s -m -P -R <remote>]
    djinit <repo_name> -n -u <user> -p <pass> [-o <organization> -c -s -m -P -R <remote>]
    djinit <repo_name> -f -u <user> -p <pass> [-o <organization> -m -P -R <remote>]
    djinit <repo_name> -d -u <user> -p <pass> [-o <organization> -R <remote>]
    djinit (-h | --help)
    djinit --version

Options:
    -n                         Non-Interactive Mode
    -f                         Fast Mode (includes -c -s)
    -d                         Divio Mode (includes -c -s -m -P)
    -c                          create github repo
    -s                          install standarsite styles
    -m                          make init
    -u --user=<user>            Github Username [nope: or Email (defaults to git-config's user.email)]
    -p --pass=<pass>            Github Password
    -P --private                Make a private project
    -R --remote=<remote>        Github Remote Link
    -o --org=<organization>     create repo on organization account
"""
import os
from random import choice
import re
import ask
from docopt import docopt


def setup(args):
    conf = dict()
    conf['pushes'] = 4

    if args['-n'] or args['-f'] or args['-d']:
        conf['project_name'] = args['<repo_name>']
        conf['github_pass'] = args['--pass']
        conf['github_org'] = args['--org']
        conf['project_private'] = args['--private']
        conf['github_user'] = args['--user']

        #if args['--user']:
            #conf['github_user'] = args['--user']
        #else:
            #conf['github_user'] = os.popen('git config --global user.email').read().strip("\n")

        conf['repo_owner'] = get_repo_owner(conf)

        conf['create_repo'] = args['-c']
        conf['standardsite'] = args['-s']
        conf['make_init'] = args['-m']

        # Overrides for fast modes
        if args['-f'] or args['-d']:
            conf['standardsite'] = True
            conf['create_repo'] = True

        if args['-d']:
            conf['make_init'] = True
            conf['project_private'] = True

        if conf['create_repo']:
            conf = create_github_repo(conf)

    else:
        ask.explain(True)
        conf['create_repo'] = ask.askBool("Do you want the script to create your Github repo?", default='y')

        if conf['create_repo'] == 'y':
            conf['create_repo'] = True
        else:
            conf['create_repo'] = False

        if conf['create_repo']:
            conf['github_user'] = ask.ask("Please enter your Github username")
            conf['github_pass'] = ask.askPassword("Please enter your Github password")
            conf['github_org'] = ask.ask("If you want to create the repo on an organisation's account, "
                               "enter its name now. Otherwise hit enter", default='')
            conf['project_name'] = ask.ask("Please enter a name for the repo")
            conf['project_private'] = ask.askBool("Should the repo be private?", default='y')
            conf['repo_owner'] = get_repo_owner(conf)
            conf = create_github_repo(conf)

        else:
            print("Please create your repo on Github first then!")
            conf['project_name'] = ask.ask("Please enter the repo name")
            conf['repo_owner'] = ask.ask("Please enter the account name which the repo belongs to")
            i = ask.askBool("Is this the repo's Github remote: git@github.com:" + conf['repo_owner'] + "/"
                      + conf['project_name'] + ".git?", default='y')
            if i == 'y':
                conf['github_remote'] = "git@github.com:" + conf['repo_owner'] + "/" + conf['project_name'] + ".git"
            elif i == 'n':
                conf['github_remote'] = ask.ask("Please enter your github remote link:")

        if ask.askBool("Do you want to add the standardsite styles and templates from divio-styleguide?",
                       default='y') == 'y':
            conf['standardsite'] = True
            conf['pushes'] += 1
        else:
            conf['standardsite'] = False

        if ask.askBool("Do you want to create a virtualenv and run the makefile (make init)?", default='y') == 'y':
            conf['make_init'] = True
        else:
            conf['make_init'] = False

    return conf


def create_github_repo(conf):
    try:
        from pyrate.services import github
    except ImportError:
        raise ImportError("Warning: Pyrate could not be found."
                          "Please install it and try again. (pip install pyrate -U)")

    if conf['project_private'] == 'y':
        conf['project_private'] = True

    elif conf['project_private'] == 'n':
        conf['project_private'] = False

    h = github.GithubPyrate(conf['github_user'], conf['github_pass'])
    if conf['github_org']:
        r = h.create_repo(conf['project_name'], org_name=conf['github_org'], private=conf['project_private'])
    else:
        r = h.create_repo(conf['project_name'], private=conf['project_private'])

    #exit("Debug: " + str(r))

    #TODO: check if it actually worked!

    #if r['message'] == 'Validation Failed':
    #    exit("Error: " + str(r))

    conf['github_remote'] = "git@github.com:" + conf['repo_owner'] + "/" + conf['project_name'] + ".git"
    return conf


def get_repo_owner(conf):
    if conf['github_org']:
        return conf['github_org']
    else:
        return conf['github_user']

if __name__ == '__main__':
    conf = setup(docopt(__doc__, version='Djinit 0.0.1'))

    DIVIO_DJANGO_TEMPLATE = 'git@github.com:divio/divio-django-template.git'
    DIVIO_BOILERPLATE = 'git@github.com:divio/divio-boilerplate.git'
    DIVO_STANDARDSITE = 'git@github.com:divio/divio-standardsite.git'
    versions = {}

    q = " -q"  # quiet flag for git commands

    os.system("clear")
    print("-----------------------------")
    print(" Divio DjangoCMS Initializer")
    print("-----------------------------")


    print("")

    # for ease of use
    pn = conf['project_name']

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
    os.system('cd ' + pn + ' && git remote add origin ' + conf['github_remote'])
    print("  OK")
    print("")

    # initial push to github
    print("* Initial Push to Github")
    os.system('cd ' + pn + ' && git add -A .')
    os.system('cd ' + pn + ' && git commit -m "djinit (1/' + str(conf['pushes'])
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
    os.system('cd ' + pn + ' && git commit -m "djinit (2/' + str(conf['pushes'])
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
    os.system('cd ' + pn + ' && git commit -m "djinit (3/' + str(conf['pushes']) + '): Set up Settings"' + q)
    os.system('cd ' + pn + ' && git push -u origin master' + q)
    print("  OK")
    print("")

    # adding standardsite styles and templates
    if conf['standardsite']:
        print("* Copying files from Standardsite")
        os.system('git clone ' + DIVO_STANDARDSITE + ' ' + pn + '_tmp/ss' + q)
        versions['divio-standardsite'] = os.popen('cd ' + pn + '_tmp/ss && git log | head -1').read().strip("commit ").strip("\n")
        os.system('cp ' + pn + '_tmp/ss/templates/standardsite.html ' + pn + '/templates')
        os.system('cp ' + pn + '_tmp/ss/sass/includes/_standardsite.scss ' + pn + '/sass/includes/')
        os.system('cp ' + pn + '_tmp/ss/sass/includes/_settings.scss ' + pn + '/sass/includes/')
        print("  OK")
        print("")

        # after standardsite add push to github
        print("* Added Standardsite files, another push to Github")
        os.system('cd ' + pn + ' && git add -A .')
        os.system('cd ' + pn + ' && git commit -m "djinit (4/' + str(conf['pushes']) +
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
    os.system('cd ' + pn + ' && git commit -m "djinit (' + str(conf['pushes']) + '/' + str(conf['pushes']) + '): Cleanup"' + q)
    os.system('cd ' + pn + ' && git push -u origin master' + q)
    print("  OK")
    print("")

    if conf['make_init']:
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
    if conf['standardsite']:
        print("")
        print("don't forget to:")
        print("* add ('standardsite.html', _('standardsite')),"
              "within src/settings.py at CMS_TEMPLATES as first position")
        print("* change {% extend %} to standardsite.html instead of base.html within all selectable templates")
