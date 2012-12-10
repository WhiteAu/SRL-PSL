from nltk.corpus import propbank
import csv

def vprt(nm,v): print '%-14s %s' % (nm+':',v)
def ctr(msg): print msg.center(80,'_')
def ctrs(msg): print msg.center(50,'_')

def rs_args(id):
    rs = propbank.roleset(id)
    args = {}
    roles = rs[0]
    for i, role in enumerate(roles.findall('role')):
        args['ARG'+role.attrib['n']] = role.attrib['descr']
    return args

def instance_example():
    for baseform in ['acquire','purchase']:
        for i in [i for i in propbank.instances()[:2000] if i.baseform == baseform][:3]:
            ctr(i.baseform)
            vprt('fileid',i.fileid)
            vprt('sentnum',i.sentnum)
            vprt('wordnum',i.wordnum)
            vprt('roleset',i.roleset)
            args = rs_args(i.roleset)
            vprt('inflection',i.inflection)
            vprt('tagger',i.tagger)

            ctrs('sentence')
            print ' '.join(i.tree.leaves())

            ctrs('predicate')
            vprt('wordnum',i.predicate.wordnum)
            vprt('height',i.predicate.height)
            vprt('word', ''.join(i.predicate.select(i.tree)))
            print i.predicate.select(i.tree)
            #vprt('parse_corpus',i.parse_corpus)

            for a in i.arguments:
                id = a[1]
                ctrs(id)
                if id in args:
                    vprt('descr', args[a[1]])
                    vprt('loc',a[0])
                    t = a[0].select(i.tree)
                    vprt('arg', ' '.join(t.leaves()))
                    print t

            ctrs('tree')
            #vprt('tree leaves', i.tree.leaves())
            print i.tree
            print ''

def write_instances(out_file='tmp.instances.psv', baseform=None, instances_limit=None, write_out_limit=None, max_arg_num=10):
    instances = propbank.instances()[:instances_limit] if instances_limit else propbank.instances()
    instances = [i for i in instances if i.baseform == baseform] if baseform else instances
    instances = instances[:write_out_limit] if write_out_limit else instances
    #instances = [i for i in instances if len(i.arguments) == min_args_num] if min_args_num else instances

    ofile = open(out_file,'w')
    fieldnames = ('baseform','inflection','predicate')
    argnames = [('ARG%d_descr'%i, 'ARG%d'%i) for i in range(max_arg_num)]
    fieldnames += tuple([item for sublist in argnames for item in sublist])
    writer = csv.DictWriter(ofile, fieldnames=fieldnames)
    headers = dict((n,n) for n in fieldnames)
    writer.writerow(headers)
    for i in instances: 
        row = {}

        row['baseform'] = i.baseform
        row['inflection'] = i.inflection
        row['predicate'] = ''.join(i.predicate.select(i.tree)) if i.tree else None

        args = rs_args(i.roleset)

        for a in i.arguments:
            id = a[1]
            if id in args:
                row['%s_descr'%id] = args[a[1]]
                row[id] = ' '.join(a[0].select(i.tree).leaves()) if i.tree else None

            print 'row (printing)'
            print row
            print 'row (writing'
            writer.writerow(row)

    ofile.close()

if __name__ == '__main__':
    #instanceExample()

    #write_instances(baseform='acquire', instances_limit=10000, write_out_limit=None, min_args_num=2)
    write_instances(baseform='acquire', instances_limit=10000, write_out_limit=None)
    #write_instances(baseform='acquire', instances_limit=None, write_out_limit=None, min_args_num=2)
    #write_instances(baseform='acquire', instances_limit=None, write_out_limit=None)



