FROM python:3.12.4-slim

# Using python site-hooks to limit dangerous modules: https://docs.python.org/3/library/site.html
COPY restrict_modules.py /usr/local/lib/python3.12/restrict_modules.py
COPY restrict_modules_init.py /usr/local/lib/python3.12/site-packages/sitecustomize.py

RUN groupadd -r sandboxuser && useradd -r -g sandboxuser sandboxuser
USER sandboxuser

WORKDIR /tests_to_exec

COPY tests_to_exec /tests_to_exec

# Keep the container alive
CMD ["tail", "-f", "/dev/null"]
