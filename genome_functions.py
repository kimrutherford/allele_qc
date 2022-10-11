from Bio.SeqFeature import FeatureLocation
from Bio.Seq import reverse_complement
from Bio.GenBank import _FeatureConsumer


def get_nt_at_genome_position(pos: int, gene: dict, contig):
    genome_coord, strand = gene_coords2genome_coords(pos, gene)
    if strand == 1:
        return contig[genome_coord]
    return reverse_complement(contig[genome_coord])


def gene_coords2genome_coords(pos: int, gene: dict) -> str:
    loc: FeatureLocation
    if 'CDS' in gene:
        loc = gene['CDS'].location
    else:
        if len(gene) != 2:
            # Error, we cannot read this position
            raise ValueError('cannot read sequence, alternative splicing?')
        # The key is the one that is not 'contig'
        key = next(k for k in gene if k != 'contig')
        loc = gene[key].location

    # Passed coordinates are one-based

    if loc.strand == 1:
        pos = loc.start + (pos - 1)
    else:
        pos = loc.end - pos

    return pos, loc.strand


def get_feature_location_from_string(location_str: str) -> FeatureLocation:
    fc = _FeatureConsumer(use_fuzziness=False)
    # We need to initialize a dummy feature
    fc._cur_feature = FeatureLocation(1, 2, 1)
    fc.location(location_str)
    return fc._cur_feature.location


def get_sequence_from_location_string(genome, location_str):
    loc = get_feature_location_from_string(location_str)
    return loc.extract(genome)
