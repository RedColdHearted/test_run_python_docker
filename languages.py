import abc


class LanguageBaseHandler(abc.ABC):
    """Base language handler for docker run."""
    docker_image_name: str
    docker_container_name: str
    docker_run_command: str


class PythonHandler(LanguageBaseHandler):
    """Python handler that run in docker."""
    docker_image_name = "python_image"
    docker_container_name = "python_container"
    docker_run_command = "timeout {}.1s python -c '{}'"


class JavaScriptHandler(LanguageBaseHandler):
    """JavaScript handler that run in docker."""
    docker_image_name = "js_image"
    docker_container_name = "js_container"
    docker_run_command = "timeout {}.1s node -e '{}'"


class CSHandler(LanguageBaseHandler):
    """CSharp handler that run in docker."""
    docker_image_name = "cs_image"
    docker_container_name = "cs_container"
    docker_run_command = ...
