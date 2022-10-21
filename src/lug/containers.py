import uuid

from docker.errors import ImageNotFound, APIError, DockerException


class DockerContainer:
    """
    This class cannot be pickled by cloudpickle.
    """
    def __init__(self, docker_client=None, image_name_and_tag=None):
        self.container = None
        self.docker_client = docker_client
        self.image = None
        self.image_name_and_tag = image_name_and_tag
        self.container_name = f"lug-{uuid.uuid4()}"

    def __repr__(self):
        return str(f"<Lug DockerContainer {self.image_name_and_tag}>")

    def load_image(self, remote=False):
        try:
            self.image = self.docker_client.images.get(self.image_name_and_tag)
        except ImageNotFound:
            if not remote:
                self.image = self.docker_client.images.pull(self.image_name_and_tag)
        except (APIError, DockerException):
            if not remote:
                raise EnvironmentError(
                    'Unable to connect to Docker. Make sure you have Docker installed and that it is currently running.'
                )

    def signal_kill_handler(self, signum, frame):
        if self.container is not None:
            self.container.stop()
