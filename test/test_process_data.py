from ..process_data import *
import pytest, subprocess, os


@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)

@pytest.fixture()
def parser():
    return get_argparser()


def compare_files_to_ref(ref, output_dir):

    root_dir, _, filenames = next(os.walk(output_dir))
    all_files = [os.path.join(root_dir, filename) for filename in filenames]
    

    with open(ref) as fh:
        ref_lines = set(fh)

    output_lines = set()
    for file_path in all_files:
        with open(file_path) as fh:
            output_lines.update(fh)

    assert output_lines == ref_lines


def test_process_data(parser, cleanup= True):
    
    args = parser.parse_args(['--articles-dir', 'testdata'])
    process_data(args)
    compare_files_to_ref('refs/processed.ref', 'testdata_processed')
    if cleanup:
        subprocess.run(('rm', '-fr', 'testdata_processed'))

    
def test_process_data_dump_only(parser, cleanup = True):
    args = parser.parse_args(['--articles-dir', 'testdata', '--dump-only'])
    process_data(args)
    compare_files_to_ref('refs/dumped.ref', 'testdata_processed')
    if cleanup:
        subprocess.run(('rm', '-fr', 'testdata_processed'))


def test_process_input_file(parser, cleanup = True):
    test_process_data_dump_only(parser, cleanup=False)
    root_dir, _, filenames = next(os.walk('testdata_processed'))
    all_files = [os.path.join(root_dir, filename) for filename in filenames]

    merged_input_file = 'testdata_processed/merged'
    with open(merged_input_file, 'w') as of:
        subprocess.run(('cat', *all_files), stdout = of)

    args = parser.parse_args(['--input-file', merged_input_file, '--output-part-size', '100'])
    process_data(args)
    compare_files_to_ref('refs/processed.ref', 'testdata_processed/merged_processed')
    if cleanup:
        subprocess.run(('rm', '-fr', 'testdata_processed'))
    

    