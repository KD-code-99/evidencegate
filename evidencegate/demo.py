"""Four fixed, owned sample revisions. No submitted source is executed."""
import json
from pathlib import Path
from .audit import audit, replay
from .packaging import verified_package
from .polynomial import extract, parse, evaluate, Unsupported

ROOT = Path(__file__).resolve().parents[1]
VARIABLES = ['units', 'unit_price', 'shipping']
CONTRACT = {'domain': 'integers', 'functions': [
    {'file': 'sampleapp/billing.py', 'function': 'invoice_total',
     'variables': VARIABLES, 'expected': 'units * unit_price + shipping'}]}
SCENARIOS = {
    'original': ('Original implementation', 'units * unit_price + shipping'),
    'wrong': ('A plausible but wrong refactor', 'units * (unit_price + shipping)'),
    'correct': ('An equivalent refactor', 'shipping + unit_price * units'),
    'unsupported': ('A change outside the checker language', 'round(units * unit_price + shipping)'),
}
CASES = [(1, 25, 0), (2, 40, 0), (5, 7, 0)]


def source(expression):
    return f'def invoice_total(units, unit_price, shipping):\n    return {expression}\n'


def prepare(state, scenario):
    if scenario not in SCENARIOS:
        raise ValueError('Choose one of the four sample revisions')
    workspace = Path(state) / scenario
    (workspace / 'sampleapp').mkdir(parents=True, exist_ok=True)
    title, expression = SCENARIOS[scenario]
    text = source(expression)
    (workspace / 'sampleapp' / 'billing.py').write_text(text, encoding='utf-8')
    (workspace / 'contracts.json').write_text(json.dumps(CONTRACT, indent=2), encoding='utf-8')
    rows = []
    try:
        polynomial = parse(extract(text, 'invoice_total', VARIABLES), VARIABLES)
        for point in CASES:
            actual = evaluate(polynomial, point)
            expected = point[0] * point[1] + point[2]
            rows.append({'arguments': dict(zip(VARIABLES, point)), 'expected': expected,
                         'actual': actual, 'passed': actual == expected})
    except Unsupported as error:
        # This fixed fixture's ordinary tests call a known round() expression.
        if scenario != 'unsupported':
            raise
        rows = [{'arguments': dict(zip(VARIABLES, p)), 'expected': p[0]*p[1],
                 'actual': round(p[0]*p[1]+p[2]), 'passed': True} for p in CASES]
    receipt = audit(workspace)
    (workspace / 'contract-receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    artifact = workspace / 'artifacts' / 'verified-billing.zip'
    # A previous package must not remain downloadable after a blocked check.
    if receipt['status'] != 'PASS' and artifact.exists():
        artifact.unlink()
    return {'scenario': scenario, 'title': title, 'source': text,
            'original_source': source(SCENARIOS['original'][1]),
            'ordinary_tests': {'passed': sum(r['passed'] for r in rows), 'total': len(rows), 'cases': rows},
            'receipt': receipt, 'replay': replay(workspace, receipt),
            'duo_execution': 'Pending an approved GitLab Duo project. This run is local.'}


def package(state, scenario):
    if scenario not in SCENARIOS:
        raise ValueError('Unknown revision')
    workspace = Path(state) / scenario
    receipt = json.loads((workspace / 'contract-receipt.json').read_text())
    return verified_package(workspace, receipt)
