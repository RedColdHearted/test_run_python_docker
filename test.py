
import pathlib
import time
import re

import docker
import docker.models
import docker.models.images

import utils



def convert_to_oneline(code: str) -> str:
    # Убираем начальные и конечные пробелы и переносы строк
    clean_code = code.strip()
    # Убираем все переносы строк и заменяем их точкой с запятой и пробелом
    clean_code = re.sub(r'\n', '; ', clean_code)
    # Убираем лишние пробелы, повторяющиеся пробелы и табуляции
    clean_code = re.sub(r'\s+', ' ', clean_code)
    return clean_code



def generate_exec_code_files(tests: list[list[str]]):
    for index, test in enumerate(tests):

        input_data_strings, solution_string, print_string = test
        code = input_data_strings + solution_string + print_string

        with open(
            f"./tests_to_exec/test{index}.py",
            'w+', encoding="UTF-8",
        ) as test_file:
            test_file.write(code)


def build_docker_image(
    client: docker.client.DockerClient,
    dockerfile_path: pathlib.Path,
    tag: str,
) -> docker.models.images.Image:
    try:
        images = client.images.list(filters={"reference": tag})
        if len(images):
            image = images[0]
            return image
        image, _ = client.images.build(
            path=dockerfile_path,
            tag=tag,
        )
        return image
    except docker.errors.BuildError as e:
        print(f"Error building the Docker image: {e}")
        return None


def run_docker_container(client: docker.client.DockerClient, image_tag):
    try:
        containers = client.containers.list(
            filters={"name": "python-container"},
        )
        if len(containers):
            container = containers[0]
            container.reload()
            return container
        container = client.containers.run(
            image_tag,
            name="python-container",
            detach=True,
            security_opt=["no-new-privileges"],
            mem_limit="128m",  # 128 mb
            cpu_quota=15000,  # 15% of cpu
            network_disabled=True,
        )
        # TODO: Add health check in future.
        return container
    except docker.errors.ContainerError as e:
        print(f"Error starting the container: {e}")
        return None


def run_test_in_docker(container, code_line: str, timeout=2):
    command = f"timeout {timeout}.1s python -c '{code_line}'"
    print(f"Running test: {command}")

    start_time = time.perf_counter()
    result = container.exec_run(command)
    end_time = time.perf_counter()

    print(f"result {result.output.decode()}")
    if result_time := round(end_time - start_time, 3) > timeout:
        return "Command timed out", 1, timeout, None
    memory_usage = container.stats(stream=False)["memory_stats"]["usage"]
    return (
        result.output.decode(),
        result.exit_code,
        result_time,
        memory_usage,  # round(memory_usage / (1024 * 1024), 1),
    )


def run_tests(code_lines: list[str], output_data: list[str]):
    client = docker.from_env()
    dockerfile_path = "."
    image_tag = "python_solving_image:latest"
    image = build_docker_image(
        client,
        dockerfile_path,
        image_tag,
    )
    if image is None:
        return
    container = run_docker_container(client, image_tag)
    if container is None:
        return

    if len(output_data) > 10:
        raise Exception("too much tests.")

    results = []

    for index, excepted_output in enumerate(output_data):
        print(code_lines)
        output, exec_code, timer, memory_usage = run_test_in_docker(
            container,
            code_lines,
        )
        if exec_code != 0:
            results.append(
                utils.TestResult(
                    order=index + 1,
                    status="Error",
                    error_massage=output,
                ),
            )
            continue
        if excepted_output != output:
            results.append(
                utils.TestResult(
                    order=index + 1,
                    status="Fail",
                    result=f"{output_data[index]} != {output}",
                    completed_time=timer,
                    used_memory=memory_usage,
                ),
            )
            continue
        results.append(
            utils.TestResult(
                order=index + 1,
                status="Complete",
                completed_time=timer,
                used_memory=memory_usage,
            ),
        )
    return results


if __name__ == "__main__":
    code = '''
    def fibonacci(n):
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n+1):
            a, b = b, a + b
        return b

    print(fibonacci(10))
    '''
    # one_line_code = convert_to_online(code)
    excepted_output = ["55\n"]

    results = run_tests(code, excepted_output)
    print(*results)
