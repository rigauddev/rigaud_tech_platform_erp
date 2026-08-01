import subprocess


def run_demo_action(action: str) -> None:
    subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            ".env.example",
            "exec",
            "backend",
            "python",
            "-m",
            "app.shared.demo.cli",
            action,
        ],
        check=True,
    )

