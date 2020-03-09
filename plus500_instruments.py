import requests
import csv
import argparse
import time
import re
import os
from datetime import datetime


def parse_args():
    """
    Parses input arguments of the script.

    Returns
    -------
    argparse.Namespace
        parsed input arguments
    """
    parser = argparse.ArgumentParser()
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
    """
    with open(input_f_path, 'r') as in_f:
        content = in_f.read()    
    instruments = [x.strip() for x in content.split(',')]
    return instruments


def query_plus500_instruments(instruments, timeout=0):
    """
    Query each of the instrument for data from plus500 website.

    Parameters
    ----------
    instruments: list of str
        instruments to get the data for
    timeout: float
        timeout in seconds to wait between requests

    Returns
    -------
    dict
        keys are instrument names and values tuples of data
    """
    all_data = {}
    for instrument in instruments:
        print('Requesting data for instrument {}...'.format(instrument))
        response = requests.get('https://www.plus500.co.uk/Instruments/{}'.format(
                instrument), headers={'User-Agent': 'Mozilla/5.0'})
        if not response.ok:
            print('Could not fetch instrument {}, response status code {}'.format(
                    instrument, response.status_code))
            continue
        instrument_data = parse_response(response.text)
        if instrument_data:
            all_data[instrument] = instrument_data
        time.sleep(timeout)
    return all_data


def parse_response(response_content):
    """
    Parses sellers and buyers percents and calculate imbalance. If data
    are not found in the content None is returned.

    Parameters
    ----------
    response_content: str
        content of the response

    Returns
    -------
    tuple of floats or None
        percents of sellers, buyers and imbalance
    """
    sell_percent_match = re.search(r"UsersSellPercentage: '(\d+)'", response_content)
    buy_percent_match = re.search(r"UsersBuyPercentage: '(\d+)'", response_content)
    price_match = re.findall(r"SellPrice:\s*'(?P<price>[\d\.]+)'", response_content)
    if sell_percent_match and buy_percent_match and price_match:
        sell_percent = float(sell_percent_match.groups()[0])
        buy_percent = float(buy_percent_match.groups()[0])
        imbalance = buy_percent - sell_percent
        price = float(price_match[0])
        return buy_percent, sell_percent, imbalance, price
    return None


def output_data(all_data, output_dir):
    """
    Outputs data to CSV files in output directory. Data are appended to files
    if the files already exist, otherwise new files are created.
    Data are outputted to one file per instrument and one main file for
    current date of the scraping.

    Parameters
    ----------
    all_data: dict
        keys are instrument names and values are touples of data
        for the instrument
    output_dir: str
        path to output directory
    """
    def output_instrument_data(instrument, data):
        """ Outputs data for given instrument to csv file. """
        output_path = os.path.join(output_dir, 'plus500_{}.csv'.format(instrument))
        write_header = False if os.path.exists(output_path) else True
        with open(output_path, 'a', newline='') as csv_f:
            writer = csv.writer(csv_f)
            if write_header:
                writer.writerow(fieldnames)
            writer.writerow([date, instrument, *data])

    def output_main_file():
        """ Outputs all data to main csv for current scraping. """
        date = datetime.now().strftime("%y%m%d_%H%M")
        output_path = os.path.join(output_dir, 'plus500_{}.csv'.format(date))
        rows = [(key, *values) for key, values in all_data.items()]
        with open(output_path, 'w', newline='') as csv_f:
            writer = csv.writer(csv_f)
            writer.writerow(fieldnames[1:])
            writer.writerows(rows)

    print('Saving data to CSV files...')
    date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    fieldnames = ['timestamp', 'instrumentID', 'buyersPercentage',
            'sellersPercentage', 'imbalance', 'price']
    for instrument in all_data.keys():
        output_instrument_data(instrument, all_data[instrument])
    output_main_file()


def check_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


if __name__ == '__main__':
    args = parse_args()
    check_directory(args.output)
    instruments = read_input_instruments(args.input)
    all_data = query_plus500_instruments(instruments, timeout=0.5)
    output_data(all_data, args.output)
    print('Done')
    