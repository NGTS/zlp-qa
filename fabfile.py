from fabric.api import *

env.use_ssh_config = True
env.hosts = ['ngtshead.astro']

@task(default=True)
def deploy():
    build()
    copy_to_destination()

@task
def build():
    local('make -C help')


@task
def copy_to_destination():
    with cd('/ngts/pipeline/qa'):
        run('mkdir -p help')
        put('help/build/*', 'help/')
