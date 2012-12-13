from nltk.corpus import propbank
from nltk.corpus.reader.propbank import *
import csv
from util import *

business_baseforms = [
        'advise',
        'employ',
        'hire',
        'make',
        'produce',
        'acquire',
        'purchase',
        'market',
        'sell',
        'sponsor',
        'issue'
        ]

def rs_args(id, cache={}):
    if id in cache:
        return cache[id]

    print 'roleset %s (cache miss)' % id

    args = {}
    try:
        rs = propbank.roleset(id)
        roles = rs[0]
        for i, role in enumerate(roles.findall('role')):
            args['ARG'+role.attrib['n']] = role.attrib['descr']
    except ValueError as e:
        print e

    cache[id] = args

    return args

def get_instances(baseforms=None, instances_limit=None):
    instances = propbank.instances()[:instances_limit] if instances_limit else propbank.instances()
    instances = [i for i in instances if i.baseform in baseforms] if baseforms else instances
    return instances

def print_instances(instances):
    rscache = {}
    for idx,i in enumerate(instances):
        ctr(i.baseform)
        vprt('num',idx)
        vprt('fileid',i.fileid)
        vprt('sentnum',i.sentnum)
        vprt('wordnum',i.wordnum)
        vprt('roleset',i.roleset)
        args = rs_args(i.roleset, cache=rscache)
        infl = i.inflection
        vprt('inflection',infl)
        vprt('  form',infl.form)
        vprt('  tense',infl.tense)
        vprt('  aspect',infl.aspect)
        vprt('  person',infl.person)
        vprt('  voice',infl.voice)
        vprt('tagger',i.tagger)

        ctrs('sentence')
        if i.tree:
            print ' '.join(i.tree.leaves())
        else:
            print '<no tree>'

        ctrs('predicate')
        if isinstance(i.predicate, PropbankSplitTreePointer):
            print 'WARNING: PropbankSplitTreePointer'
            for tr in i.predicate.pieces:
                print tr
        else:
            vprt('wordnum',i.predicate.wordnum)
            vprt('height',i.predicate.height)
        if i.tree:
            vprt('word', ''.join(i.predicate.select(i.tree).leaves()))
            print i.predicate.select(i.tree)
        else:
            vprt('word','<no tree>')
        #vprt('parse_corpus',i.parse_corpus)

        for a in i.arguments:
            id = a[1]
            ctrs(id)
            if id in args:
                vprt('descr', args[a[1]])
                vprt('loc',a[0])
                if i.tree:
                    t = a[0].select(i.tree)
                    vprt('arg', ' '.join(t.leaves()))
                    print t
                else:
                    print '<no tree>'

        ctrs('tree')
        #vprt('tree leaves', i.tree.leaves())
        print i.tree
        print ''

def write_instances(instances, out_file='tmp.instances.csv', max_arg_num=10):
    ofile = open(out_file,'w')
    fieldnames = (
            'num',
            'baseform',
            'fileid',
            'tagger',
            'sentnum',
            'wordnum',
            'inflection',
            'sentence',
            'predicate',
            'roleset'
            )
    argnames = [('ARG%d_descr'%i, 'ARG%d'%i) for i in range(max_arg_num)]
    fieldnames += tuple([item for sublist in argnames for item in sublist])

    writer = csv.DictWriter(ofile, fieldnames=fieldnames)
    headers = dict((n,n) for n in fieldnames)
    writer.writerow(headers)

    rscache = {}
    for idx,i in enumerate(instances): 
        row = {}

        if not i.tree:
            print 'instance %d (%s, %s): WARNING:  skipping because no TB tree available' % (idx, i.baseform, i.fileid)
            continue

        row['num'] = idx
        row['baseform'] = i.baseform
        row['inflection'] = i.inflection
        row['predicate'] = ''.join(i.predicate.select(i.tree).leaves()) if i.tree else None
        row['fileid'] = i.fileid
        row['sentnum'] = i.sentnum
        row['wordnum'] = i.wordnum
        row['tagger'] = i.tagger
        row['sentence'] = ' '.join(i.tree.leaves()) if i.tree else None
        row['roleset'] = i.roleset

        args = rs_args(i.roleset, cache=rscache)

        for a in i.arguments:
            id = a[1]
            if id in args:
                row['%s_descr'%id] = args[a[1]]
                row[id] = ' '.join(a[0].select(i.tree).leaves()) if i.tree else None
            else:
                print 'instance %d (%s): WARNING:  %s not among known args!'%(idx,i.baseform,id)
                print '\t'+' '.join(a[0].select(i.tree).leaves()) if i.tree else ''
                print ''

        try:
            writer.writerow(row)
        except ValueError as e: 
            print 'instance %d: WARNING:  problem writing row'% idx
            print e

    ofile.close()

if __name__ == '__main__':

    print 'instances (retrieving)'
    #instances_limit = 1000
    instances_limit = None

    #baseforms = None
    baseforms = business_baseforms

    i = get_instances(baseforms=baseforms, instances_limit=instances_limit)

    #print 'instances (printing)'
    #print_instances(instances=i)

    print 'instances (writing)'
    write_instances(instances=i)



