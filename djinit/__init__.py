#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
djinit: Divio's DjangoCMS Initializer

Usage:
    djinit <repo_name> -u <user> -p <pass> (-c | -r <remote>) [-o <organization> -s -m -P]
    djinit <repo_name> -i
    djinit (-h | --help)
    djinit --version

Options:
    -i --interactive            Interactive Mode
    -u --user=<user>            Github Username [nope: or Email (defaults to git-config's user.email)]
    -p --pass=<pass>            Github Password
    -c --create                 create github repo
    -r --remote=<remote>        Github Remote Link
    -o --org=<organization>     create repo on organization account
    -s --standardsite           install standardsite styles
    -m --make-init              make init
    -P --private                Make a private project
"""

import ask
import os
import re
from docopt import docopt
from pyrate.services import github
from random import choice

__version__ = '0.1.0'

DIVIO_DJANGO_TEMPLATE = 'git@github.com:divio/divio-django-template.git'
DIVIO_BOILERPLATE = 'git@github.com:divio/divio-boilerplate.git'
DIVO_STANDARDSITE = 'git@github.com:divio/divio-standardsite.git'
PUSHES = 4


def get_repo_owner(conf):
    if conf['github_org']:
        return conf['github_org']
    else:
        return conf['github_user']


def setup_cli(args):
    conf = dict()
    conf['project_name'] = args['<repo_name>']
    conf['github_pass'] = args['--pass']
    conf['github_org'] = args['--org']
    conf['project_private'] = args['--private']
    conf['github_user'] = args['--user']  # TODO: Improve, see example below
    conf['repo_owner'] = get_repo_owner(conf)
    conf['create_repo'] = args['--create']
    conf['standardsite'] = args['--standardsite']
    conf['make_init'] = args['--make-init']

    return conf
    #if args['--user']:
        #conf['github_user'] = args['--user']
    #else:
        #conf['github_user'] = os.popen('git config --global user.email').read().strip("\n")


def setup_interactive(args):
    ask.explain(True)
    conf = dict()
    conf['project_name'] = args['<repo_name>']
    conf['create_repo'] = ask.askBool("Do you want the script to create your Github repo?", default='y')

    if conf['create_repo']:
        conf['github_user'] = ask.ask("Please enter your Github username")
        conf['github_pass'] = ask.askPassword("Please enter your Github password")
        conf['github_org'] = ask.ask("If you want to create the repo on an organisation's account, "
                                     "enter its name now. Otherwise hit enter", default='')
        conf['project_private'] = ask.askBool("Should the repo be private?", default='y')
        conf['repo_owner'] = get_repo_owner(conf)

    else:
        print("Please create your repo on Github first then!")
        conf['project_name'] = ask.ask("Please enter the repo name")
        conf['repo_owner'] = ask.ask("Please enter the account name which the repo belongs to")
        if ask.askBool("Is this the repo's Github remote ssh url: git@github.com:" + conf['repo_owner'] + "/"
                       + conf['project_name'] + ".git?", default='y'):
            conf['github_remote'] = "git@github.com:" + conf['repo_owner'] + "/" + conf['project_name'] + ".git"

        else:
            conf['github_remote'] = ask.ask("Please enter your github remote ssh url:")

    conf['standardsite'] = ask.askBool("Do you want to add the standardsite styles and templates from "
                                       "divio-styleguide?", default='y')
    conf['make_init'] = ask.askBool("Do you want to create a virtualenv and run the makefile (make init)?", default='y')

    return conf


def setup(args):
    if args['--interactive']:
        conf = setup_interactive()
    else:
        conf = setup_cli(args)

    conf['pushes'] = PUSHES
    if conf['standardsite']:
        conf['pushes'] += 1

    if conf['create_repo']:
        h = github.GithubPyrate(conf['github_user'], conf['github_pass'])
        if conf['github_org']:
            r = h.create_repo(conf['project_name'], org_name=conf['github_org'], private=conf['project_private'])
        else:
            r = h.create_repo(conf['project_name'], private=conf['project_private'])

        try:
            conf['github_remote'] = r['ssh_url']
        except:
            raise Exception("Something went wrong.")
            # TODO: Improve

    return conf


def main():
    conf = setup(docopt(__doc__, version='djinit ' + __version__))

    versions = {}

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
    os.system('git clone ' + DIVIO_DJANGO_TEMPLATE + ' ' + pn + ' -q')
    versions['divio-django-template'] = \
        os.popen('cd ' + pn + ' && git log | head -1').read().strip('commit ').strip('\n')
    print("  OK")
    print("")

    # initializing git repo
    print("* Initializing Git repo")
    os.system("rm -rf " + pn + "/.git")
    os.system('cd ' + pn + ' && git init -q')
    os.system('cd ' + pn + ' && git remote add origin ' + conf['github_remote'])
    print("  OK")
    print("")

    # initial push to github
    print("* Initial Push to Github")
    os.system('cd ' + pn + ' && git add -A .')
    os.system('cd ' + pn + ' && git commit -m "djinit (1/' + str(conf['pushes'])
              + '): Initial commit" -m "push based on divio-django-template (divio/divio-django-template@'
              + str(versions['divio-django-template']) + ')" -q')
    os.system('cd ' + pn + ' && git push -u origin master -q')
    print("  OK")
    print("")

    # make temp dir
    os.system('mkdir ' + pn + '_tmp')

    # copying boilerplate
    print("* Copying files from Boilerplate")
    os.system('git clone ' + DIVIO_BOILERPLATE + ' ' + pn + '_tmp/bp -q')
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
              + str(versions['divio-boilerplate']) + ')" -q')
    os.system('cd ' + pn + ' && git push -u origin master -q')
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
    os.system('cd ' + pn + ' && git commit -m "djinit (3/' + str(conf['pushes']) + '): Set up Settings" -q')
    os.system('cd ' + pn + ' && git push -u origin master -q')
    print("  OK")
    print("")

    # adding standardsite styles and templates
    if conf['standardsite']:
        print("* Copying files from Standardsite")
        os.system('git clone ' + DIVO_STANDARDSITE + ' ' + pn + '_tmp/ss -q')
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
                  + str(versions['divio-standardsite']) + ')" -q')
        os.system('cd ' + pn + ' && git push -u origin master -q')
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
    os.system('cd ' + pn + ' && git commit -m "djinit (' + str(conf['pushes']) + '/' + str(conf['pushes']) +
              '): Cleanup" -q')
    os.system('cd ' + pn + ' && git push -u origin master -q')
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


if __name__ == '__main__':
    main()
