"""Validate the module's documentation contract and render CWL Markdown."""
import argparse
from pathlib import Path
import yaml


def render(path):
    document = yaml.safe_load(path.read_text())
    assert document['cwlVersion'] == 'v1.2', path
    for field in ('s:softwareVersion', 's:codeRepository', 's:license', 's:author'):
        assert document.get(field), f'{path}: missing {field}'
    assert document['s:codeRepository'] == 'https://github.com/eoap/dask-app-package', path
    def check(value):
        if isinstance(value, dict):
            assert not ({'$import', '$include'} & value.keys()), f'{path}: external dependency'
            for child in value.values(): check(child)
        elif isinstance(value, list):
            for child in value: check(child)
    check(document)
    lines = [f'# {path.stem}', '', f"Repository: {document['s:codeRepository']}", '',
             f"Version: {document['s:softwareVersion']}", '', f"License: {document['s:license']}", '']
    for author in document['s:author']:
        assert author.get('s:name') and author.get('s:email'), f'{path}: incomplete author'
        lines.extend([f"Author: {author['s:name']} ({author['s:email']})", ''])
    for process in document.get('$graph', [document]):
        assert process.get('label') and process.get('doc'), f'{path}: missing process description'
        lines.extend([f"## {process['label']}", '', process['doc'], ''])
        for group in ('inputs', 'outputs'):
            lines.extend([f'### {group.capitalize()}', '', '| Name | Type | Description |', '| --- | --- | --- |'])
            ports = process.get(group, {})
            ports = ports.items() if isinstance(ports, dict) else ((p['id'], p) for p in ports)
            for name, port in ports:
                assert isinstance(port, dict) and port.get('type') and port.get('label') and port.get('doc'), f'{path}: undocumented {name}'
                description = port['doc'].replace('\n', ' ').replace('|', '\\|')
                kind = str(port['type']).replace('|', '\\|')
                lines.append(f'| {name} | `{kind}` | {description} |')
            lines.append('')
        requirements = process.get('requirements', {})
        schemas = requirements.get('SchemaDefRequirement', {}).get('types', []) if isinstance(requirements, dict) else []
        for schema in schemas:
            if "$import" in schema:
                lines.extend([f"Shared schema: {schema['$import']}", ""])
                continue
            lines.extend([f"### Type `{schema['name']}`", '', '```yaml', yaml.safe_dump(schema, sort_keys=False).rstrip(), '```', ''])
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate', action='store_true', help='Also validate isolated CWL with HTTP fetching disabled')
    parser.add_argument('--output', type=Path, default=Path('/tmp/stac-cwl-docs'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    for path in sorted((root / 'cwl-workflows').glob('*.cwl')):
        if path.name.startswith('.'): continue
        markdown = render(path)
        if args.validate:
            import requests
            import shutil
            import tempfile
            from cwltool.main import main
            from calrissian.main import add_custom_schema
            from calrissian.context import CalrissianLoadingContext
            original_request = requests.sessions.Session.request
            def blocked_request(session, method, url, **kwargs):
                raise RuntimeError('HTTP fetching disabled for standalone validation')
            requests.sessions.Session.request = blocked_request
            try:
                with tempfile.TemporaryDirectory() as isolated:
                    target_cwl = Path(isolated) / path.name
                    shutil.copy(path, target_cwl)
                    assert main(['--enable-ext', '--validate', str(target_cwl)], custom_schema_callback=add_custom_schema, loadingContext=CalrissianLoadingContext()) == 0, path
            finally:
                requests.sessions.Session.request = original_request
        target = args.output / path.relative_to(root).with_suffix('.md')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown)
        print(f'Validated and rendered {path.relative_to(root)}')
