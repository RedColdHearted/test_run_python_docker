import abc


class LanguageBaseHandler(abc.ABC):
    """Base language handler for docker run."""
    docker_image_name: str
    docker_container_name: str
    docker_run_command: str


class PythonHandler(LanguageBaseHandler):
    """Python handle for docker."""
    docker_image_name = "python_image:latest"
    docker_container_name = "python_container"
    docker_run_command = "timeout {}.1s python -c '{}'"


class JavaScriptHandler(LanguageBaseHandler):
    """JavaScript handler for docker."""
    docker_image_name = "js_image:latest"
    docker_container_name = "js_container"
    docker_run_command = "timeout {}.1s node -e '{}'"


class CSHandler(LanguageBaseHandler):
    """CSharp handler for docker."""
    docker_image_name = "cs_image:latest"
    docker_container_name = "cs_container"
    # TODO: find a way to run cs code.
    docker_run_command = ...


class LanguagesManager:
    """Manager for language handlers."""
    language_handlers = {
        "python": PythonHandler,
        "javascript":  JavaScriptHandler,
        "cs": CSHandler,
    }

    def get_language_handler(
        self,
        handler_name: str,
    ) -> type[LanguageBaseHandler]:
        """Return a handler from mapper."""
        return self.language_handlers.get(handler_name.lower())
