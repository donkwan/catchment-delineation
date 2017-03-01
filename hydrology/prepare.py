import sys
import os
import boto3
import requests
import io
import re

from bs4 import BeautifulSoup, SoupStrainer


def prepare_efs(region):
    """Prepare EFS"""
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = os.path.abspath("../instance/aws-credentials.ini")
    client = boto3.client('efs', region)

    # create file system
    response = client.create_file_system(
        CreationToken='string',
        PerformanceMode='generalPurpose'
    )

    response = client.create_mount_target(
        FileSystemId='fs-hydrodata',
        SubnetId=''
    )

    return response


def download_to_efs(stream, path):
    response = prepare_efs(path)

    # add download routine with stream
    return response


def download_to_local(stream, path):
    stream.write(path)


def main(dest, path):
    if dest == 'local':
        download = download_to_local
    elif dest == 'efs':
        download = download_to_efs

    # get list of zipped grid files
    r = requests.get('https://hydrosheds.cr.usgs.gov/datadownload.php')
    content = r.content.decode('utf-8')

    soup = BeautifulSoup(content, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href[-4:] != '.zip' or 'hydrodata' not in href:
            continue

        stream = requests.get(href, stream=True)

        response = download(stream, path)

def commandline_parser():
    """
        Parse the arguments passed in from the command line.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--destination', help='''Destination (local or efs).''')
    parser.add_argument('-p', '--path', help='''Path (local) or region (efs)''')

if __name__=='__main__':

    #parser = commandline_parser()
    #args = parser.parse_args()
    #main(args.destination, args.path)
    
    main('efs', 'us-west-2b')