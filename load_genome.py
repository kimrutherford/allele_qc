"""
Build a genome dictionary from several embl-format files.

The genome contains a dictionary in which the key is the systematic ID,
and the value is a dictionary of features with the feature_type as key.

{
    "3'UTR": SeqFeature,
    "CDS": SeqFeature,
    "peptide": string containing the peptide sequence (only for CDS features, generated by translating the CDS with BioPython),
    "5'UTR": SeqFeature,
    "contig": SeqRecord of the sequence where this gene is found (generated from one of the files passed as arguments)
}

The dictionary is stored in a pickle file, specified by the argument --output.
"""
import pickle
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature
import argparse
import json

genome: dict[str, dict[str, SeqFeature]] = dict()


class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


with open('config.json') as ins:
    config = json.load(ins)

filename2chromosome_dict = {v: k for k, v in config['chromosome2file'].items()}

parser = argparse.ArgumentParser(description=__doc__, formatter_class=Formatter)
parser.add_argument('files', metavar='N', type=str, nargs='+',
                    help='files to be read')
parser.add_argument('--format', default='embl', help='format of the files to be read (for Biopython)')
parser.add_argument('--output', default='data/genome.pickle', help='output file (using pickle)')
args = parser.parse_args()


for f in args.files:
    print('\033[0;32m reading: ' + f + '\033[0m')
    iterator = SeqIO.parse(f, args.format)
    contig = next(iterator)
    if next(iterator, None) is not None:
        raise ValueError(f'multiple sequences in file {f}')
    for feature in contig.features:
        feature: SeqFeature
        if 'systematic_id' not in feature.qualifiers:
            continue
        gene_id = feature.qualifiers['systematic_id'][0]
        feature_type = feature.type
        if feature_type in ['intron', 'misc_feature']:
            continue

        if gene_id not in genome:
            genome[gene_id] = dict()
            # assigned only once
            file_name = f.split('/')[-1].split('.')[0]
            # We set the id to the value in the filename2chromosome_dict
            contig.id = filename2chromosome_dict[file_name]
            genome[gene_id]['contig'] = contig

        if feature_type in genome[gene_id]:
            raise ValueError(f'several features of {feature_type} for {gene_id}')

        genome[gene_id][feature_type] = feature

        # if feature_type == 'CDS' and not any([('pseudogene' in prod or 'dubious' in prod) for prod in feature.qualifiers['product']]):
        if feature_type == 'CDS':
            cds_seq = feature.extract(contig).seq
            if gene_id.startswith(config['mitochondrial_prefix']):
                genome[gene_id]['peptide'] = cds_seq.translate(table=config['mitochondrial_table'])
            else:
                genome[gene_id]['peptide'] = cds_seq.translate()
            errors = list()
            if len(cds_seq) % 3 != 0:
                errors.append('CDS length not multiple of 3')
            if genome[gene_id]['peptide'][-1] != '*':
                errors.append('does not end with STOP codon')
            if genome[gene_id]['peptide'].count('*') > 1:
                errors.append('multiple stop codons')
            if len(errors):
                print(gene_id, ','.join(errors), str(feature.qualifiers['product']), sep='\t')


with open(args.output, 'wb') as out:
    pickle.dump(genome, out, pickle.HIGHEST_PROTOCOL)
