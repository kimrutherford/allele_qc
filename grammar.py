aa = 'GPAVLIMCFYWHKRQNEDST'
aa = aa + aa.lower()
aa = f'[{aa}]'

allowed_types = {
    frozenset({'amino_acid_mutation'}): 'amino_acid_mutation',
    frozenset({'partial_amino_acid_deletion'}): 'partial_amino_acid_deletion',
    frozenset({'amino_acid_mutation','partial_amino_acid_deletion'}): 'partial_amino_acid_deletion',
    frozenset({'amino_acid_insertion'}): 'amino_acid_insertion',
    frozenset({'amino_acid_insertion','partial_amino_acid_deletion'}): 'amino_acid_insertion_and_deletion',
    frozenset({'amino_acid_insertion','amino_acid_mutation'}): 'amino_acid_insertion_and_mutation',
    frozenset({'disruption'}): 'disruption',
    frozenset({'nonsense_mutation'}): 'nonsense_mutation',
    frozenset({'amino_acid_mutation','nonsense_mutation'}): 'amino_acid_deletion_and_mutation',
    frozenset({'unknown'}): 'unknwown',
}

modifications = [
    {
        'type': 'amino_acid_mutation',
        'rule_name': 'single_aa',
        'regex': f'(?<!{aa})({aa})(\d+)({aa})(?!{aa})',
        'apply_syntax': lambda g: ''.join(g).upper(),
        'check_invalid': lambda g: False
    },
    {
        'type': 'amino_acid_mutation',
        'rule_name': 'multiple_aa',
        # This is only valid for cases with two aminoacids or more (not to clash with amino_acid_insertion:usual)
        'regex': f'({aa}{aa}+)-?(\d+)-?({aa}+)(?!\d)',
        # We fix the case in which dashes are used for a single aa substitution: K-90-R
        'apply_syntax': lambda g: '-'.join(g).upper() if len(g[0])!=1 else ''.join(g).upper(),
        'check_invalid': lambda g: f'lengths don\'t match: {g[0]}-{g[2]}' if len(g[0]) != len(g[2]) else False
    },
    {
        'type': 'nonsense_mutation',
        'rule_name': 'stop_codon_text',
        'regex': f'({aa})(\d+)[^a-zA-Z0-9]*(?i:ochre|stop|amber|opal)',
        'apply_syntax': lambda g: ''.join(g).upper()+'*',
        'check_invalid': lambda g: False
    },
    {
        'type': 'nonsense_mutation',
        'rule_name': 'stop_codon_star',
        'regex': f'({aa})(\d+)(\*)',
        'apply_syntax': lambda g: ''.join(g[:2]).upper()+'*',
        'check_invalid': lambda g: False
    },
    # {
    #     'type': 'nonsense_mutation',
    #     'rule_name': 'stop_codon_aa_missing',
    #     'regex': f'({aa})(\d+)(\*)',
    #     'apply_syntax': lambda g: ''.join(g[:2]).upper()+'*',
    #     'check_invalid': lambda g: False
    # },
    {
        'type': 'partial_amino_acid_deletion',
        'rule_name': 'multiple_aa',
        'regex': f'(?<!{aa})(\d+)[-–](\d+)(?!{aa})(\s+Δaa)?',
        'apply_syntax': lambda g: '-'.join(g[:2]).upper(),
        'check_invalid': lambda g: False
    },
    {
        'type': 'partial_amino_acid_deletion',
        'rule_name': 'single_aa',
        'regex': f'(?<!{aa})(\d+)(?!{aa})(\s+Δaa)?',
        'apply_syntax': lambda g: g[0],
        'check_invalid': lambda g: False
    },
    {
        'type': 'amino_acid_insertion',
        'rule_name': 'usual',
        'regex': f'{aa}?(\d+)-?({aa}+)(?!\d)',
        # We fix the case in which dashes are used for a single aa substitution: K-90-R
        'apply_syntax': lambda g: '-'.join(g).upper(),
        'check_invalid': lambda g: False
    },
    {
        'type': 'unknown',
        'rule_name': 'empty',
        'regex': f'^$',
        'apply_syntax': lambda g: 'unknwown',
        'check_invalid': lambda g: False
    }
]