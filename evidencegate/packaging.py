from pathlib import Path
import json
import zipfile
from .audit import replay


def verified_package(root, receipt):
    root = Path(root).resolve()
    verdict = replay(root, receipt)
    if not verdict['release_allowed']:
        raise ValueError('Packaging is blocked by the mathematical contract')
    artifact = root / 'artifacts' / 'verified-billing.zip'
    artifact.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(artifact, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in ('sampleapp/billing.py', 'contracts.json'):
            archive.write(root / name, name)
        archive.writestr('evidence/contract.json', json.dumps(receipt, indent=2))
    return artifact
