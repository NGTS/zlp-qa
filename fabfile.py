from fabric.api import *

env.use_ssh_config = True
env.hosts = ['ngtshead']

@task(default=True)
def deploy():
    '''
    Build the help pages and deploy to ngtshead
    '''
    build()
    copy_to_destination()

@task
def build():
    '''
    Build the help pages
    '''
    local('make -C help')


@task
def copy_to_destination():
    '''
    Deploy help pages to ngtshead
    '''
    with cd('/ngts/pipeline/qa'):
        run('mkdir -p help')
        put('help/build/*', 'help/')


@task
def copy_static_files():
    ''' Copy static files to ngtshead '''
    with cd('/ngts/pipeline/qa'):
        run('mkdir -p static')
        put('static/*', 'static/')
