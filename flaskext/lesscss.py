# -*- coding: utf-8 -*-
"""
    flaskext.lesscss
    ~~~~~~~~~~~~~

    A small Flask extension that makes it easy to use LessCSS with your Flask
    application.

    :copyright: (c) 2010 by Steve Losh.
    :license: MIT, see LICENSE for more details.
"""

import os, subprocess

def lesscss(app):
    @app.before_request
    def _render_less_css():
        if not hasattr(app, 'static_url_path'):
            from warnings import warn
            warn(DeprecationWarning('static_path is called '
                                    'static_url_path since Flask 0.7'),
                                    stacklevel=2)
        
            static_url_path = app.static_path
        
        else:
            static_url_path = app.static_url_path
        
        static_dir = app.root_path + app.static_url_path
        
        less_paths = []
        for path, subdirs, filenames in os.walk(static_dir):
            less_paths.extend([
                os.path.join(path, f)
                for f in filenames if os.path.splitext(f)[1] == '.less'
            ])
        
        css_base_path = static_dir + "/css"
        d = os.path.dirname(css_base_path)
        if not os.path.exists(d):
            os.makedirs(d)

        for less_path in less_paths:
            path_parts = os.path.splitext(less_path)[0].split('/')
            css_path = css_base_path + '/' + path_parts[len(path_parts) - 1] + '.css'
            if not os.path.isfile(css_path):
                css_mtime = -1
                open(css_path, 'w').close()
            else:
                css_mtime = os.path.getmtime(css_path)
            less_mtime = os.path.getmtime(less_path)
            if less_mtime >= css_mtime:
                app.logger.info("Compiling .less file: " + less_path)
                return_code = subprocess.call(['lessc', less_path, css_path], shell=False)
                if return_code == 0:
                    app.logger.info("lessc done with: " + less_path)
                else:
                    app.logger.info("lessc failed on: " + less_path)
                    os.remove(css_path)


