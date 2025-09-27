from jinja2.sandbox import SandboxedEnvironment
from jinja2 import meta, Environment
from jinja2.exceptions import TemplateSyntaxError, UndefinedError
import json

# create a sandbox environment and register a small safe filter set if needed
# Create a sandbox environment and register a small safe filter/global set
sandbox_env = SandboxedEnvironment()
# example safe filter
sandbox_env.filters["tojson"] = lambda obj: json.dumps(obj, ensure_ascii=False)

# Whitelisted safe globals (iterators/utilities commonly used in templates)
ALLOWED_GLOBALS = {
    # Convert to list to avoid leaking lazy iterators across template contexts
    "range": lambda *args: list(range(*args)),
}

def find_undeclared_vars(src):
    env = Environment()
    ast = env.parse(src)
    return list(meta.find_undeclared_variables(ast))

def safe_render(template_source: str, values: dict) -> str:
    """
    Render template_source in a sandboxed environment.
    WARNING: SandboxedEnvironment mitigates many risks but DOES NOT guarantee 100% safety.
    """
    # Clear globals to be conservative, then re-register whitelisted ones
    sandbox_env.globals.clear()
    sandbox_env.globals.update(ALLOWED_GLOBALS)

    try:
        tmpl = sandbox_env.from_string(template_source)
        # ensure only simple types in values (str, int, float, bool, list, dict)
        safe_values = _sanitize_values(values)
        return tmpl.render(**safe_values)
    except TemplateSyntaxError as e:
        raise
    except UndefinedError as e:
        # variable missing - allow render with default empty string or raise
        raise
    except Exception:
        raise

def _sanitize_values(values):
    # shallow sanitize (you can expand)
    if not isinstance(values, dict):
        return {}
    out = {}
    for k, v in values.items():
        if isinstance(v, (str, int, float, bool, list, dict, type(None))):
            out[k] = v
        else:
            out[k] = str(v)
    return out
