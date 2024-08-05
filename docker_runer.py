import pathlib
import time

import docker
import docker.models
import docker.models.containers
import docker.models.images

from languages import LanguageBaseHandler
from utils import TestResult, TestCase
from errors import TestsError
from constants import TO_MUCH_TESTS_CASES_ERROR_MESSAGE


def build_docker_image(
    client: docker.client.DockerClient,
    dockerfile_path: pathlib.Path,
    image_tag: str,
) -> docker.models.images.Image:
    """Return a docker image from docker engine."""
    try:
        images = client.images.list(filters={"reference": image_tag})
        if len(images):
            image = images[0]
            return image
        image, _ = client.images.build(
            path=dockerfile_path,
            tag=image_tag,
        )
        return image
    except docker.errors.BuildError as e:
        print(f"Error building the Docker image: {e}")
        return None


def run_docker_container(
    client: docker.client.DockerClient,
    docker_image: docker.models.images.Image,
    docker_container_name: str,
) -> docker.models.containers.Container | None:
    """Return a docker container from docker engine."""
    try:
        containers = client.containers.list(
            filters={"name": docker_container_name},
        )
        if len(containers):
            container = containers[0]
            # container.restart() or some health check...
            return container
        # TODO: Add health check in future.
        container = client.containers.run(
            image=docker_image,
            name=docker_container_name,
            detach=True,
            security_opt=["no-new-privileges"],
            mem_limit="128m",  # 128 mb
            cpu_quota=15000,  # 15% of cpu
            network_disabled=True,
        )
        return container
    except docker.errors.ContainerError as e:
        print(f"Error starting the container: {e}")
        return None


def run_test_in_docker(
    container: docker.models.containers.Container,
    code_line: str,
    docker_run_command: str,
    timeout: int,
) -> tuple[str, int, float, float | None]:
    """Run a test in docker container."""
    start_time = time.perf_counter()
    exec_result = container.exec_run(
        docker_run_command.format(timeout, code_line)
    )
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
    language: type[LanguageBaseHandler],
    dockerfile_path: str = ".",
) -> list[TestResult]:
    """Run tests in docker container and return a result."""
    client = docker.from_env()
    docker_image = build_docker_image(
        client,
        dockerfile_path,
        image_tag=language.docker_image_name,
    )
    if docker_image is None:
        return
    container = run_docker_container(
        client,
        docker_image,
        docker_container_name=language.docker_container_name
    )

    if len(excepted_tets_result) > 10:
        raise TestsError(TO_MUCH_TESTS_CASES_ERROR_MESSAGE)

    tests_results = []

    for index, excepted_output in enumerate(excepted_tets_result):
        test_case = test_cases[index]
        output, exec_code, completed_time, memory_usage = run_test_in_docker(
            container,
            test_case.code_line,
            docker_run_command=language.docker_run_command,
            timeout=test_case.allocated_time,
        )
        order=index + 1,
        error_massage = None
        comparison = None
        status="Complete",

        if exec_code != 0:
            status="Error",
            error_massage=output,

        if excepted_output != output:
            status = "Fail"
            comparison = f"{excepted_tets_result[index]} != {output}",

        tests_results.append(
            TestResult(
                order=order,
                comparison=comparison,
                status=status,
                memory_usage=memory_usage,
                completed_time=completed_time,
                error_massage=error_massage,
            ),
        )
    return tests_results
