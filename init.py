import sys, os, shutil, io, zipfile, argparse
import requests
from bs4 import BeautifulSoup


def main(path, cellsize, overwrite, regions):

    if not os.path.exists(path):
        # make the directory, but only if the root path exists (e.g., if '/efs' exists)
        if os.path.exists(os.path.abspath(path.split('/')[0])):
            os.makedirs(path)
        else:
            print('Root path does not exist.')
            return

    # get list of zipped grid files
    r = requests.get('https://hydrosheds.cr.usgs.gov/datadownload.php')
    content = r.content.decode('utf-8')

    soup = BeautifulSoup(content, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if not all(x in href for x in ['hydrodata', '_dir_', '_%ss_' % cellsize, 'bil.zip']):
            continue
        
        zfname = os.path.split(href)[-1]
        outpath = os.path.join(path, os.path.splitext(zfname)[0])
        if os.path.exists(outpath):
            if overwrite:
                shutil.rmtree(outpath)
            else:
                continue
        
        # for testing only
        if regions and zfname[:2] not in regions:
            continue
    
        print('Getting %s' % zfname)

        response = requests.get(href)
        if response.ok:
            file = io.BytesIO(response.content)
            zf = zipfile.ZipFile(file)
            # leave in '.xml' in case that information might be useful in the future
            members = [n for n in zf.namelist() if n[-4:] not in ['.htm', '.pdf']]
            zf.extractall(outpath, members)
            
        print('...done!')

    print('Finished')
    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', default='./hydrodata', help='''Path (local) or region (efs)''')
    parser.add_argument('-c', '--cellsize', default=15, help='''Cell size in arc-seconds (3, 15 or 30)''')
    parser.add_argument('-o', '--overwrite', action='store_true', help='''Overwrite any existing folders''')
    parser.add_argument('-r', '--regions', nargs='+', default=False, help='''Regions to include, separated by a single space''')
    args = parser.parse_args()
    
    main(args.path, args.cellsize, args.overwrite, args.regions)