import csv
from util import *

def fb_to_pb_map(map_file):  
    """
    Read a mappings file.
    """
    f2p = {}
    f = open(map_file,'r')
    header=True
    for line in f:
        if header or line.strip()=='':
            header=False
            continue
        (fbr,pbr,fba,pba) = line.strip().split(',')
        if fbr not in f2p: 
            f2p[fbr]={}
            f2p[fbr]['PROPBANK_RELATION'] = pbr
        f2p[fbr][fba] = pba
    f.close()
    return f2p

def pb_instances(fb_dir, fbr, f2p):
    """
    Convert a FB instance file to a list of PB instances.
    """
    fb_file = '%s/%s.tsv'%(fb_dir,fbr)
    pb = []
    with open(fb_file,'r') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            pb.append({f2p[fbr][key]:value for (key,value) in row.iteritems() if key in f2p[fbr]})

    return pb


if __name__ == '__main__':
    f2p = fb_to_pb_map('FB_to_PB.csv')
    for fbr in ['acquisition']:
        ctr(fbr)
        pb = pb_instances('tmp.business_Freebase', fbr, f2p)
        print pb[:10]
