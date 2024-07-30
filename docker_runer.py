import pathlib
import time

import docker
import docker.models
import docker.models.containers
import docker.models.images

from utils import TestResult, TestCase
from exceptions import TestsError
from constants import TO_MUCH_TESTS_CASES_ERROR_MESSAGE


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


def run_docker_container(
    client: docker.client.DockerClient,
    image_tag: docker.models.Image,
    container_name: str,
) -> docker.models.containers.Container | None:
    try:
        containers = client.containers.list(
            filters={"name": container_name},
        )
        if len(containers):
            container = containers[0]
            # container.restart() or some health check...
            return container
        container = client.containers.run(
            image=image_tag,
            name=container_name,
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


def run_test_in_docker(
    container: docker.models.containers.Container,
    code_line: str,
    timeout: int,
) -> tuple[str, int, float, float | None]:
    command = f"timeout {timeout}.1s python -c '{code_line}'"

    start_time = time.perf_counter()
    exec_result = container.exec_run(command)
    end_time = time.perf_counter()

    if result_time := round(end_time - start_time, 3) > timeout:
        return "Test timed out", 1, timeout, None
    memory_usage = container.stats(stream=False)["memory_stats"]["usage"]
    return (
        exec_result.output.decode(),
        exec_result.exit_code,
        result_time,
        memory_usage,
    )


def run_tests(
    test_cases: list[TestCase],
    excepted_tets_result: list[str],
    # image_tag = "python_image:latest"
    image_tag: str,
    dockerfile_path: str = "."
) -> list[TestResult]:
    client = docker.from_env()
    image = build_docker_image(
        client,
        dockerfile_path,
        image_tag,
    )
    if image is None:
        return
    container = run_docker_container(client, image_tag)

    if len(excepted_tets_result) > 10:
        raise TestsError(TO_MUCH_TESTS_CASES_ERROR_MESSAGE)

    tests_results = []

    for index, excepted_output in enumerate(excepted_tets_result):
        test_case = test_cases[index]
        output, exec_code, timer, memory_usage = run_test_in_docker(
            container,
            test_case.code_line,
            timeout=test_case.allocated_time
        )
        if exec_code != 0:
            tests_results.append(
                TestResult(
                    order=index + 1,
                    status="Error",
                    error_massage=output,
                ),
            )
            continue
        if excepted_output != output:
            tests_results.append(
                TestResult(
                    order=index + 1,
                    status="Fail",
                    result=f"{excepted_tets_result[index]} != {output}",
                    completed_time=timer,
                    used_memory=memory_usage,
                ),
            )
            continue
        tests_results.append(
            TestResult(
                order=index + 1,
                status="Complete",
                completed_time=timer,
                used_memory=memory_usage,
            ),
        )
    return tests_results
