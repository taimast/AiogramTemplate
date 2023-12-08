from dataclasses import dataclass, field
from pathlib import Path

from fabric import Connection
from github import Github
from github import Repository
from invoke import Responder

from scripts.deploy.cli import cli, Action

BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / 'scripts'
key_responder = Responder(
    pattern=r".*Overwrite (y/n)?.*",
    response="n\n",
)
clone_responder = Responder(
    pattern=r".*Are you sure you want to continue connecting.*",
    response="yes\n",
)

always_yes_responder = Responder(
    pattern=r".*",
    response="yes\n",
)


@dataclass
class Deployer:
    github_token: str
    repo_name: str
    ip: str
    username: str = 'root'
    # key_filename: str
    repo_path_name: str = field(init=False)

    create_deploy_key_file: Path = field(default=Path(SCRIPTS_DIR / 'create_deploy_key.sh'))
    create_deploy_key_command: str = field(init=False)
    setup_docker_file: Path = field(default=Path(SCRIPTS_DIR / 'setup_docker.sh'))
    setup_docker_command: str = field(init=False)

    g: Github = field(init=False)
    repo: Repository = field(init=False)
    connection: Connection = field(init=False)

    def __post_init__(self):
        self.repo_path_name = self.repo_name.replace('_', '-')
        self.g = Github(self.github_token)
        self.repo = self.g.get_repo(f'taimast/{self.repo_name}')
        self.connection = Connection(
            host=f'{self.username}@{self.ip}',
            connect_kwargs={
                # "key_filename": self.key_filename
            }
        )
        if self.create_deploy_key_file.exists():
            self.create_deploy_key_command = self.create_deploy_key_file.read_text("utf-8").format(repo=self.repo_name)
        if self.setup_docker_file.exists():
            self.setup_docker_command = self.setup_docker_file.read_text("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def save_deploy_key(self, key: str):
        try:
            return self.repo.create_key('main', key)
        except Exception as e:
            print(e)

    def create_deploy_key(self):
        self.connection.run(
            self.create_deploy_key_command,
            pty=True,
            watchers=[key_responder],
        )
        key = self.connection.run(f'cat /root/.ssh/id_ed25519.pub').stdout.strip()
        print(f"Successfully created key: {key}")
        return key

    def clone_repo(self):
        self.connection.run(
            f'git clone {self.repo.ssh_url} /home/{self.repo_name}',
            pty=True,
            watchers=[clone_responder],
            warn=True
        )
        print(f"Successfully cloned repo: {self.repo_name}")

    def http_clone_repo(self):
        clone_url = self.repo.clone_url.replace('https://', f'https://taimast:{self.github_token}@')
        self.connection.run(
            f'git clone {clone_url} /home/{self.repo_name}',
            pty=True,
            watchers=[clone_responder],
            warn=True
        )
        print(f"Successfully cloned repo: {self.repo_name}")



    def pull_repo(self):
        self.connection.run(f'cd /home/{self.repo_name} && git pull')
        print(f"Successfully pulled repo: {self.repo_name}")

    def setup_docker(self):
        self.connection.run(
            self.setup_docker_command,
            pty=True,
            # watchers=[always_yes_responder],
        )
        print("Successfully setup docker")

    def deploy(self):
        key = self.create_deploy_key()
        self.save_deploy_key(key)
        self.clone_repo()
        self.pull_repo()
        self.setup_docker()

    def move_to_repo(self):
        self.connection.run(f'cd /home/{self.repo_name}')

    def _docker_compose(self, command: str):
        self.connection.run(f'docker compose -f /home/{self.repo_name}/docker-compose.yml {command}')

    def start_docker(self):
        self._docker_compose('up -d')
        print("Successfully started docker")

    def stop_docker(self):
        self._docker_compose('stop')
        print("Successfully stopped docker")

    def down_docker(self):
        self._docker_compose('down')
        print("Successfully downed docker")

    def restart_docker(self):
        self._docker_compose('restart')
        print("Successfully restarted docker")

    def build_docker(self):
        self._docker_compose('build')
        print("Successfully build docker")

    def rebuild_start_docker(self):
        self._docker_compose('stop')
        self._docker_compose('up -d --build')
        print("Successfully rebuilt docker")

    def down_build_start_docker(self):
        self._docker_compose('down')
        self._docker_compose('up -d --build')
        print("Successfully downed and rebuilt docker")

    def copy_config(self, config_path: str = f'{BASE_DIR}/config.yml'):
        self.connection.put(config_path, f'/home/{self.repo_name}/config.yml')
        print("Successfully copied config")


def main():
    args = cli()
    action: Action = Action(args.action)
    with Deployer(
            github_token=args.token,
            repo_name=args.repo,
            ip=args.ip,
            username=args.username,
    ) as deployer:
        if action == Action.PULL:
            deployer.pull_repo()
        else:
            getattr(deployer, action.value)()


if __name__ == '__main__':
    main()
