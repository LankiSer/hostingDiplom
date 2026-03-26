from pathlib import Path


class FileStorage:
    def __init__(self, root: str) -> None:
        self.root = Path(root)

    def persist_source_reference(self, deployment_id: str, source_uri: str) -> str:
        deployment_dir = self.root / "deployments" / deployment_id
        deployment_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = deployment_dir / "source.txt"
        artifact_path.write_text(source_uri, encoding="utf-8")
        return artifact_path.as_posix()
