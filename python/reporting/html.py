"""Module docstring."""
from jinja2 import Environment
from pathlib import Path  # pylint: disable=wrong-import-order


def generate_dashboard(data):
    """Function docstring."""

    env = Environment(autoescape=True)

    template = env.from_string(
        '''
<html>
<head>
<title>SysClean Dashboard</title>
</head>
<body>

<h1>SysClean Dashboard</h1>

<p>Total reclaim:
{{ reclaimed_mb }} MB</p>

<p>Operations:
{{ operations }}</p>

<p>Failures:
{{ failures }}</p>

</body>
</html>
'''
    )

    html = template.render(**data)

    output = Path(
        "reports/dashboard.html"
    )

    output.write_text(html)  # pylint: disable=unspecified-encoding
