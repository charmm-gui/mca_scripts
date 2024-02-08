#!/usr/bin/env python
import sys
import numpy as np
import pint


def print_data(data, labels):
    """interprets pairs of columns as value ± error

    labels.shape should be data.ndim
    """
    row_labels, col_labels = labels

    # print header
    output = [['', *col_labels]]
    for r_label, row in zip(row_labels, data):
        fields = [str(r_label)]
        for c_idx, _ in enumerate(col_labels):
            val, err = row[c_idx*2:c_idx*2+2]
            fields.append(f'{val:g} ± {err:g}')
        output.append(fields)

    col_len = [max(map(len, col)) for col in zip(*output)]
    row_fmt = '  '.join(f'{{:{cl}s}}' for cl in col_len)
    for row in output:
        print(row_fmt.format(*row))


u = pint.UnitRegistry()
q = u.Quantity

input_units = 'nm**2/ns'
if len(sys.argv) == 1:
    output_units = input_units
else:
    output_units = sys.argv[1]

factor = q(input_units).to(output_units).m

data = np.loadtxt('diffusion.dat')
labels = [
    ['PET', 'PEF'],             # row labels
    ['τ=2.0', 'τ=5.0', 'fit'],  # column labels
]

data *= factor
print('D =', output_units)
print_data(data, labels)
