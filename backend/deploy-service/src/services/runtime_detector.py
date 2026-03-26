from src.schemas.contracts import RuntimeDetectionRequest


class RuntimeDetector:
    def detect(self, payload: RuntimeDetectionRequest) -> dict[str, str]:
        runtime = "python"

        for file_name in payload.files:
            normalized = file_name.lower()
            if normalized.endswith("package.json") or "node" in normalized or "npm" in normalized:
                runtime = "node"
                break

        strategy = "docker-build"
        return {"runtime": runtime, "strategy": strategy}
