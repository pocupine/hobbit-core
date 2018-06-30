from contextlib import contextmanager
import os

import click
from jinja2 import Environment, FileSystemLoader, Template
from . import echo

SUFFIX = '.jinjia2'


@contextmanager
def chdir(dist):
    cwd = os.getcwd()
    echo('mkdir {}', (dist, ))
    os.makedirs(dist, exist_ok=True)
    os.chdir(dist)
    yield dist
    os.chdir(cwd)


@click.pass_context
def render_project(ctx, dist, tpl_path):
    jinjia_env = Environment(loader=FileSystemLoader(tpl_path))
    with chdir(dist):
        for fn in os.listdir(tpl_path):
            origin_path = os.path.join(tpl_path, fn)

            if os.path.isfile(origin_path) and not fn.endswith(SUFFIX):
                continue

            if os.path.isfile(origin_path):
                data = jinjia_env.get_template(fn).render(
                    ctx.obj['JINJIA_CONTEXT'])
                render_file(dist, fn[:-8], data)
                continue

            dir_name = Template(fn).render(ctx.obj['JINJIA_CONTEXT'])
            render_project(os.path.join(dist, dir_name),
                           os.path.join(tpl_path, fn))


@click.pass_context
def render_file(ctx, dist, fn, data):
    target = os.path.join(dist, fn)
    if os.path.isfile(fn) and not ctx.obj['FORCE']:
        echo('exists {}, ignore ...', (target, ))
        return

    echo('render {} ...', (target, ))

    with open(fn, 'w') as wf:
        wf.write(data)