from mako.template import Template
from datetime import datetime


with open('catcher/formatters/traceback.html', 'r') as f:
    str_template = f.read()

_template = Template(str_template, default_filters=['decode.utf8'], input_encoding='utf-8', output_encoding='utf-8')


class HTMLFormatter:
    def format(self, report, maxdepth=5) -> bytes:
        return _template.render(maxdepth=maxdepth, report=report, datetime=datetime)
