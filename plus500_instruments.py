import requests
import csv
import argparse


def parse_args():
    """
    Parses input arguments of the script.

    Returns
    -------
    argparse.Namespace
        parsed input arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
            help='If present, more information about processes will be printed.')
    parser.add_argument('-i', '--input', required=True, help='\
            Specifies path to input CSV with instruments IDs')
    parser.add_argument('-o', '--output', required=False, default='./outputs',
            help='Specifies path to output directory. (default is ./outputs)')
    args = parser.parse_args()
    return args


def read_input_instruments(input_f_path):
    """
    Reads input file for instruments names

    Parameters
    ----------
    input_f_path: str
        path to input file

    Returns
    -------
    list of str
        list of instrument names
    """"
    with open(input_f_path, 'r') as in_f:
        content = in_f.read()    
    instruments = [x.strip() for x in content.split(',')]
    return instruments


def query_plus500_instruments(instruments, timeout=1):
    pass


if __name__ == '__main__':
    args = parse_args()
    instruments = read_input_instruments(args.input)
    