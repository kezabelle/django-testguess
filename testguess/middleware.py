# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import namedtuple, OrderedDict
from functools import partial
from importlib import import_module
from tempfile import gettempdir
import logging
from django.core.urlresolvers import resolve
from django.utils.datetime_safe import datetime
import os
from django.conf import settings
from django.template.loader import render_to_string

try:
    from django.contrib.auth import get_user_model
    CAN_USE_CUSTOM_USERS = True
except ImportError:
    CAN_USE_CUSTOM_USERS = False
try:
    from model_mommy import mommy
    CAN_USE_MOMMY = True
except ImportError:
    CAN_USE_MOMMY = False
try:
    from html5lib import parse
    CAN_USE_HTML5LIB = True
except ImportError:
    CAN_USE_HTML5LIB = False

logger = logging.getLogger(__name__)
PathTestFile = namedtuple("PathTestFile", 'directory file')
PrepareResult = namedtuple("PrepareResult", 'project_root tree')


EMPTY_INIT_TEMPLATE = partial(render_to_string, template_name="testguess/empty_init.py")
TEST_TEMPLATE = partial(render_to_string, template_name='testguess/generated_class.py')
TEST_STATUS_CODE_TEMPLATE = partial(render_to_string, template_name='testguess/status_code.py')
TEST_REVERSE_TEMPLATE = partial(render_to_string, template_name='testguess/reverse_url.py')
TEST_HEADERS_TEMPLATE = partial(render_to_string, template_name='testguess/headers.py')
TEST_HTML5_OUTPUT_TEMPLATE = partial(render_to_string, template_name='testguess/html5.py')
TEST_JSON_OUTPUT_TEMPLATE = partial(render_to_string, template_name='testguess/json.py')
TEST_CONTEXT_DATA_TEMPLATE = partial(render_to_string, template_name='testguess/context_data.py')
TEST_CUSTOM_USER_TEMPLATE = partial(render_to_string, template_name='testguess/custom_user.py')
TEST_USER_TEMPLATE = partial(render_to_string, template_name='testguess/user.py')


class TestFileHandler(object):
    __slots__ = ('config', 'django_settings')

    def __init__(self, config, django_settings):
        assert hasattr(config, 'magic_number'), "Invalid config"
        self.config = config
        self.django_settings = django_settings

    def prepare(self, view_name):
        project_root = self.guess_project_directory(default=gettempdir)
        filenames = tuple(self.get_filenames(root_directory=project_root,
                                             view_name=view_name))
        if filenames is None:
            return None
        made_files = self.make_files(filenames=filenames)
        return PrepareResult(project_root=project_root, tree=made_files)

    def make_files(self, filenames):
        settings_obj = self.django_settings
        for directory, filename in filenames:
            if not os.path.exists(directory):
                perm = settings_obj.FILE_UPLOAD_DIRECTORY_PERMISSIONS or 0o750
                try:
                    os.makedirs(directory, perm)
                except os.error:
                    logger.error("Unable to create the following "
                                 "directory, halting preparation "
                                 "at: %s".format(directory), exc_info=1)
                    return None
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write(EMPTY_INIT_TEMPLATE())
        return filenames

    def guess_project_directory(self, default=None):
        settings_obj = self.django_settings
        guesses = ('TESTGUESS_ROOT', 'BASE_DIR', 'PROJECT_PATH',
                   'PROJECT_DIR', 'PROJECT_ROOT')
        for guess in guesses:
            resolved_guess = getattr(settings_obj, guess, None)
            if resolved_guess is not None:
                return resolved_guess
        has_media_root = getattr(settings_obj, 'MEDIA_ROOT', None) is not None
        has_static_root = getattr(settings_obj, 'STATIC_ROOT', None) is not None
        if has_static_root and has_media_root:
            media_root_parent = os.path.dirname(settings_obj.MEDIA_ROOT)
            static_root_parent = os.path.dirname(settings_obj.STATIC_ROOT)
            if media_root_parent == static_root_parent:
                # account for windows drives C:/ ...
                drive, path = os.path.splitdrive(static_root_parent)
                # if after trimming off separators, there is something, hope
                # for the best.
                if path.strip(os.sep) != '':
                    return static_root_parent
        has_settings_obj_module = getattr(settings_obj, 'SETTINGS_MODULE', None) is not None
        if has_settings_obj_module:
            # do not swallow ImportError so that it errors loudly.
            imported_file = import_module(settings_obj.SETTINGS_MODULE)
            path = os.path.dirname(imported_file.__file__)
            dirname = os.path.basename(path)
            # if the path ends with <project_name>/<project_name> then we want to
            # go up another directory to escape the config directory.
            if path.endswith(os.path.join(dirname, dirname)):
                return os.path.dirname(path)
            return path
        if default is not None and callable(default):
            default = default()
        return default

    def get_filenames(self, view_name, root_directory):
        segments = view_name.strip('.').split('.')
        app_root = os.path.join(root_directory, 'autoguessed')
        test_root = os.path.join(app_root, 'tests')
        init_file = '__init__.py'
        # output <path>/autoguessed/__init__.py
        yield PathTestFile(file=os.path.join(app_root, init_file),
                           directory=app_root)
        # output <path>/autoguessed/tests/__init__.py
        yield PathTestFile(file=os.path.join(test_root, init_file),
                           directory=test_root)
        path = None
        for length, segment in enumerate(segments, start=1):
            part = segments[0:length]
            path = os.path.join(*part)
            path_root = os.path.join(root_directory, 'autoguessed', 'tests', path)  # noqa
            # output <path>/autoguessed/tests/<path>/__init__.py
            yield PathTestFile(file=os.path.join(path_root, init_file),
                               directory=path_root)
        if path is not None:
            # output <path>/autoguessed<path>/test_<N>.py
            test_file = 'test_{}.py'.format(self.config.magic_number())
            test_root = os.path.join(test_root, path)
            yield PathTestFile(file=os.path.join(test_root, test_file),
                               directory=test_root)


# def getallkeys(data, parent=None):
#     for k, v in data.items():
#         if parent is not None:
#             squawk = [[k,], parent]
#         else:
#             squawk = [k,]
#         print(list(squawk))
#         yield squawk
#         if hasattr(v, 'items'):
#             for result in getallkeys(v, parent=[parent, k]):
#                 yield result

class GuessConfiguration(object):
    __slots__ = (
        'is_html5',
        'is_ajax',
        'is_authenticated',
        'has_context_data',
        'has_template_name',
        'has_get_params',
        'supports_model_mommy',
        'supports_custom_users',
        'supports_html5lib',
        'is_get',
        'is_post',
        'is_json',
    )

    def __init__(self, is_html5, is_ajax, is_authenticated, has_context_data,
                 has_template_name, has_get_params, is_get, is_post, is_json):
        assert not all((is_get, is_post)), "Cannot be both GET and POST"
        assert not all((is_html5, is_json)), "Cannot be both JSON and HTML"
        self.is_html5 = is_html5
        self.is_ajax = is_ajax
        self.is_authenticated = is_authenticated
        self.has_context_data = has_context_data
        self.has_template_name = has_template_name
        self.has_get_params = has_get_params
        self.supports_model_mommy = CAN_USE_MOMMY
        self.supports_custom_users = CAN_USE_CUSTOM_USERS
        self.supports_html5lib = CAN_USE_HTML5LIB
        self.is_get = is_get
        self.is_post = is_post
        self.is_json = is_json

    def magic_number(self):
        values = (getattr(self, attr) for attr in self.__slots__)
        ints = (int(value) for value in values
                if value is True or value is False)
        strs = (str(int_) for int_ in ints)
        bin_ = ''.join(strs)
        return bin_

    def items(self):
        out = OrderedDict((attr, getattr(self, attr))
                          for attr in self.__slots__)
        return out.items()


class TestGuesser(object):
    __slots__ = (
        'config',
        'request',
        'response',
    )

    def __init__(self, config, request, response):
        assert hasattr(config, 'magic_number'), "Invalid config"
        self.config = config
        self.request = request
        self.response = response

    def is_valid(self):
        return self.config.magic_number() > 0

    def get_best_viewname(self, obj, default=None):
        has_app_name = getattr(obj, 'app_name', None) is not None
        has_url_name = getattr(obj, 'url_name', None) is not None
        has_view_name = getattr(obj, 'view_name', None) is not None
        has_func = getattr(obj, 'func', None) is not None
        if has_app_name and has_url_name:
            return '%s.%s' % (obj.app_name, obj.url_name)
        # no app:url but does have a dotted.string.to.function
        if not has_app_name and not has_url_name and has_view_name:
            return obj.view_name
        # wrapper is a ResolverMatch or a functools.partial, drill down ...
        if has_func:
            return self.get_best_viewname(obj=obj.func, default=default)

        if hasattr(obj, '__name__'):
            name = obj.__name__
        elif hasattr(obj, '__class__') and hasattr(obj.__class__, '__name__'):
            name = obj.__class__.__name__
        elif default is not None:
            name = default
        else:
            raise ValueError("Could not figure out a name for this view")

        module = None
        if hasattr(obj, '__module__'):
            module = obj.__module__
        elif hasattr(obj, '__class__') and hasattr(obj.__class__, '__module__'):
            module = obj.__class__.__module__

        if module is not None:
            return '%s.%s' % (module, name)
        return name

    def make_test(self, files):
        context = {
            'config': self.config,
            'when': datetime.utcnow(),
            'request': {
                'method': self.request.method,
                'path': self.request.path,
                'resolved': resolve(self.request.path),
            },
            'response': {
                'status_code': self.response.status_code,
                'headers': [v for k, v in self.response._headers.items()
                            if v[0] not in ('Last-Modified', 'Expires', 'Location')]
            },
            'setup': [],
        }

        if self.config.is_post:
            context['request']['data'] = dict(self.request.POST)
        elif self.config.is_get:
            context['request']['data'] = dict(self.request.GET)

        # Do anything necessary for authenticating users.
        if self.config.is_authenticated:
            context['request']['user'] = self.request.user

            if self.config.supports_custom_users:
                context['setup'].append(TEST_CUSTOM_USER_TEMPLATE(context=context))
            else:
                context['setup'].append(TEST_USER_TEMPLATE(context=context))

        status_code = TEST_STATUS_CODE_TEMPLATE(context=context)
        reversed = TEST_REVERSE_TEMPLATE(context=context)
        headers = TEST_HEADERS_TEMPLATE(context=context)
        tests_context = {
            'tests': {
                'status_code': status_code,
                'reverse': reversed,
                'headers': headers,
            }
        }

        # output the test for parsing as HTML5
        if self.config.is_html5 and self.config.supports_html5lib:
            tests_context['tests'].update({
                'html5': TEST_HTML5_OUTPUT_TEMPLATE(context=context)
            })
        if self.config.is_json:
            tests_context['tests'].update({
                'json': TEST_JSON_OUTPUT_TEMPLATE(context=context)
            })

        # output a test for checking the keys in the context.
        if self.config.has_context_data:
            context2 = context.copy()
            context2['response']['context_keys'] = sorted(set(
                self.response.context_data.keys()
            ))
            context_types = tuple(
                (k, type(v)) for k, v in self.response.context_data.items()
            )
            context_imports_parts = tuple(
                (k, t.__module__, t.__name__)
                for k, t in context_types
                if hasattr(t, '__module__') and hasattr(t, '__name__')
                and t.__name__ not in ('__proxy__',)
            )
            context_imports = sorted(
                (mod, name) for k, mod, name in context_imports_parts
                if mod != '__builtin__' and name != 'type'
            )
            context_instances = sorted(
                (k, name) for k, mod, name in context_imports_parts
            )
            context2['response']['context_value_imports'] = context_imports
            context2['response']['context_values'] = context_instances
            tests_context['tests'].update({
                'context_data': TEST_CONTEXT_DATA_TEMPLATE(context=context2)
            })
        context.update(tests_context)
        finalised = TEST_TEMPLATE(context=context)
        last = files.tree[-1]
        assert last.file.endswith('test_{}.py'.format(self.config.magic_number()))
        with open(last.file, 'w+') as f:
            f.write(finalised)
        return last, finalised

    def generate(self):
        match = resolve(self.request.path)
        view_name = self.get_best_viewname(match, default=match.url_name)
        test_filer = TestFileHandler(config=self.config,
                                     django_settings=settings)
        files = test_filer.prepare(view_name=view_name)
        test_itself = self.make_test(files)
        return 1


class GuessResponse(object):
    __slots__ = (
        'config_class',
        'guesser_class',
    )

    def __init__(self, config_class=None, guesser_class=None):
        # a config handler must accept the keyword arguments used in
        # `process_response` and a `magic_number` method
        self.config_class = config_class or GuessConfiguration
        # a test guesser must accept a config instance, request, response
        # and implement `is_valid` and `generate` methods.
        self.guesser_class = guesser_class or TestGuesser

    def process_response(self, request, response):
        not_in_testsuite = getattr(request, '_dont_enforce_csrf_checks', None) is None
        is_not_streaming = response.streaming is False
        is_not_servererror = response.status_code < 500
        if not_in_testsuite and is_not_streaming and is_not_servererror:
            config_handler = self.config_class
            test_guesser = self.guesser_class
            content = response.content.strip()
            html = content[0:15].lower() == '<!doctype html>'
            json_object = content.startswith('{') and content.endswith('}')
            json_array = content.startswith('[') and content.endswith(']')
            config = config_handler(
                is_html5=html,
                is_json=json_object or json_array,
                is_ajax=request.is_ajax(),
                is_authenticated=(hasattr(request, 'user') and
                                  request.user.is_authenticated()),
                has_context_data=hasattr(response, 'context_data'),
                has_template_name=hasattr(response, 'template_name'),
                has_get_params=len(request.GET) > 0,
                is_get=request.method == 'GET',
                is_post=request.method == 'POST',
            )
            guesser = test_guesser(config=config, request=request, response=response)
            if guesser.is_valid():
                guesser.generate()
        return response
