'''BDD step definitions for ebook conversion feature tests.'''

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

import pytest
from pytest_bdd import given, parsers, scenario, then, when

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'samples')


# --- Scenarios ---

@scenario('convert.feature', 'Convert EPUB to other formats')
def test_convert_epub_to_other_formats():
    pass


@scenario('convert.feature', 'Convert AZW3 to EPUB')
def test_convert_azw3_to_epub():
    pass


@scenario('convert.feature', 'Convert MOBI to EPUB')
def test_convert_mobi_to_epub():
    pass


@scenario('convert.feature', 'Show help message')
def test_show_help():
    pass


@scenario('convert.feature', 'Show version')
def test_show_version():
    pass


# --- Fixtures ---

@pytest.fixture
def conversion_context():
    '''Shared context for conversion steps.'''
    ctx = {'tmpdir': tempfile.mkdtemp(prefix='ebook_test_')}
    yield ctx
    shutil.rmtree(ctx['tmpdir'], ignore_errors=True)


@pytest.fixture
def cli_result():
    '''Shared context for CLI invocation results.'''
    return {}


# --- Given steps ---

@given(parsers.parse('an EPUB file "{filename}"'), target_fixture='conversion_context')
def given_epub_file(filename):
    src = os.path.join(SAMPLES_DIR, filename)
    assert os.path.exists(src), f'Sample file not found: {src}'
    ctx = {'tmpdir': tempfile.mkdtemp(prefix='ebook_test_')}
    ctx['input_file'] = src
    return ctx


@given(parsers.parse('an AZW3 file "{filename}"'), target_fixture='conversion_context')
def given_azw3_file(filename):
    src = os.path.join(SAMPLES_DIR, filename)
    assert os.path.exists(src), f'Sample file not found: {src}'
    ctx = {'tmpdir': tempfile.mkdtemp(prefix='ebook_test_')}
    ctx['input_file'] = src
    return ctx


@given(parsers.parse('a MOBI file from converting "{epub_file}"'), target_fixture='conversion_context')
def given_mobi_from_epub(epub_file):
    src = os.path.join(SAMPLES_DIR, epub_file)
    assert os.path.exists(src), f'Sample file not found: {src}'
    ctx = {'tmpdir': tempfile.mkdtemp(prefix='ebook_test_')}
    # First convert EPUB to MOBI
    mobi_path = os.path.join(ctx['tmpdir'], epub_file.replace('.epub', '.mobi'))
    result = subprocess.run(
        [sys.executable, '-m', 'calibre.ebooks.conversion.cli', src, mobi_path],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f'EPUB→MOBI pre-conversion failed: {result.stderr}'
    assert os.path.exists(mobi_path), f'MOBI file not created: {mobi_path}'
    ctx['input_file'] = mobi_path
    return ctx


# --- When steps ---

@when(parsers.parse('I convert it to "{output_format}" format'), target_fixture='cli_result')
def when_convert_to_format(conversion_context, output_format):
    input_file = conversion_context['input_file']
    base = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(conversion_context['tmpdir'], f'{base}.{output_format}')
    conversion_context['output_file'] = output_file
    result = subprocess.run(
        [sys.executable, '-m', 'calibre.ebooks.conversion.cli', input_file, output_file],
        capture_output=True, text=True, timeout=120,
    )
    return {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


@when(parsers.parse('I convert the MOBI to "{output_format}" format'), target_fixture='cli_result')
def when_convert_mobi_to_format(conversion_context, output_format):
    input_file = conversion_context['input_file']
    base = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(conversion_context['tmpdir'], f'{base}_from_mobi.{output_format}')
    conversion_context['output_file'] = output_file
    result = subprocess.run(
        [sys.executable, '-m', 'calibre.ebooks.conversion.cli', input_file, output_file],
        capture_output=True, text=True, timeout=120,
    )
    return {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


@when(parsers.parse('I run aphrael with "{args}"'), target_fixture='cli_result')
def when_run_with_args(args):
    result = subprocess.run(
        [sys.executable, '-m', 'calibre.ebooks.conversion.cli'] + args.split(),
        capture_output=True, text=True, timeout=30,
    )
    return {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}


# --- Then steps ---

@then('the output file should be created')
def then_output_created(conversion_context, cli_result):
    assert cli_result['returncode'] == 0, (
        f'Conversion failed (exit code {cli_result["returncode"]}):\n'
        f'stdout: {cli_result["stdout"][-500:]}\n'
        f'stderr: {cli_result["stderr"][-500:]}'
    )
    output_file = conversion_context['output_file']
    assert os.path.exists(output_file), f'Output file not found: {output_file}'
    assert os.path.getsize(output_file) > 0, f'Output file is empty: {output_file}'


@then(parsers.parse('the output file should be a valid "{output_format}" file'))
def then_valid_output(conversion_context, output_format):
    output_file = conversion_context['output_file']
    fmt = output_format.lower()
    if fmt == 'epub':
        # EPUB is a ZIP file with mimetype
        assert zipfile.is_zipfile(output_file), f'Not a valid ZIP/EPUB file: {output_file}'
        with zipfile.ZipFile(output_file) as zf:
            names = zf.namelist()
            assert 'mimetype' in names, f'EPUB missing mimetype entry: {names[:10]}'
            mimetype = zf.read('mimetype').decode('ascii').strip()
            assert mimetype == 'application/epub+zip', f'Wrong mimetype: {mimetype}'
    elif fmt in ('mobi', 'azw3'):
        # MOBI/AZW3 files start with PalmDB header (first 32 bytes contain name, then magic)
        with open(output_file, 'rb') as f:
            header = f.read(68)
            # PalmDB magic at offset 60: 'BOOKMOBI'
            assert header[60:68] == b'BOOKMOBI', (
                f'Not a valid MOBI/AZW3 file (missing BOOKMOBI magic): {header[60:68]!r}'
            )


@then('it should display usage information')
def then_display_usage(cli_result):
    combined = cli_result['stdout'] + cli_result['stderr']
    assert 'usage' in combined.lower() or 'convert an e-book' in combined.lower(), (
        f'Help output not found in:\n{combined[:1000]}'
    )


@then('it should display version information')
def then_display_version(cli_result):
    combined = cli_result['stdout'] + cli_result['stderr']
    # Should contain some version-like output
    assert combined.strip(), 'No version output produced'
