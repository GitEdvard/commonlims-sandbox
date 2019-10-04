import os


def read_file(path):
    with open(path, 'r') as f:
        contents = f.read()
    return contents


def read_binary_file(path):
    with open(path, 'rb') as f:
        contents = f.read()
    return contents


def gemstone_csv_path():
    here_dir = os.path.dirname(__file__)
    sample_submission_path = os.path.join(here_dir, 'gemstones-samplesubmission.csv')
    return sample_submission_path


def gemstone_xlsx_path():
    here_dir = os.path.dirname(__file__)
    sample_submission_path = os.path.join(here_dir, 'gemstones-samplesubmission.xlsx')
    return sample_submission_path


def prep_samples_xlsx_path():
    here_dir = os.path.dirname(__file__)
    sample_submission_path = os.path.join(here_dir, 'samplesubmission_prep_samples.xlsx')
    return sample_submission_path


def read_gemstone_csv():
    return read_file(gemstone_csv_path())


def read_gemstone_xlsx():
    return read_binary_file(gemstone_xlsx_path())
