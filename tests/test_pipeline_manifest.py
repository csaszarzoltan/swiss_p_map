import json
from pathlib import Path

def test_manifest_structure():
    """Verify that the manifest.json file exists and adheres to the pipeline schema."""
    manifest_path = Path(".agent-pipeline/00_index/manifest.json")
    assert manifest_path.exists(), "manifest.json must exist in .agent-pipeline/00_index/"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "tasks" in data
    assert "SPEC-001" in data["tasks"]
    spec_001 = data["tasks"]["SPEC-001"]
    
    assert spec_001["status"] in ["PENDING_DEV", "READY_FOR_QA", "COMPLETED", "FAILED_QA", "NEEDS_HUMAN_REVIEW"]
    assert Path(spec_001["spec_path"]).exists(), f"Spec file not found at {spec_001['spec_path']}"
    assert Path(spec_001["e2e_test_path"]).exists(), f"E2E test file not found at {spec_001['e2e_test_path']}"
