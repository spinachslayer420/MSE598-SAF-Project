import numbers
import numpy as np
import discretisedfield as df


def box_atlas(pmin, pmax, name):
    mif = f'# BoxAtlas for {name}_atlas\n'
    mif += f'Specify Oxs_BoxAtlas:{name}_atlas {{\n'
    mif += f'  xrange {{ {pmin[0]} {pmax[0]} }}\n'
    mif += f'  yrange {{ {pmin[1]} {pmax[1]} }}\n'
    mif += f'  zrange {{ {pmin[2]} {pmax[2]} }}\n'
    mif += f'  name {name}\n'
    mif += '}\n\n'

    return mif


def mif_atlas_vector_field(value, name, atlas='main_atlas'):
    mif = f'# {name}\n'
    mif += f'Specify Oxs_AtlasVectorField:{name} {{\n'
    mif += f'  atlas :{atlas}\n'
    mif += '  default_value {{{} {} {}}}\n'.format(*value['default'])
    mif += '  values {\n'
    for region, val in value.items():
        if region != 'default':
            mif += '    {} {{{} {} {}}}\n'.format(region, *val)
    mif += '  }'
    mif += '}\n\n'

    return mif


def mif_atlas_scalar_field(value, name, atlas='main_atlas'):
    mif = f'# {name}\n'
    mif += f'Specify Oxs_AtlasScalarField:{name} {{\n'
    mif += f'  atlas :{atlas}\n'
    mif += '  default_value {}\n'.format(value['default'])
    mif += '  values {\n'
    for region, val in value.items():
        if region != 'default':
            mif += f'    {region} {val}\n'
    mif += '  }'
    mif += '}\n\n'

    return mif


def setup_m0(field, name):
    if not isinstance(field, df.Field):
        msg = f'Cannot use {type(field)} for magnetisation.'
        raise TypeError(msg)
    if field.dim != 3:
        msg = f'Cannot use dim={field.dim} field for magnetisation'
        raise ValueError(msg)
    field.write(f'{name}.omf')
    mif = file_vector_field(f'{name}.omf', f'{name}', 'main_atlas')
    mif += vector_norm_scalar_field(f'{name}', f'{name}_norm')
    
    return mif, f'{name}', f'{name}_norm'


def file_vector_field(filename, name, atlas):
    mif = f'# {name} file\n'
    mif += f'Specify Oxs_FileVectorField:{name} {{\n'
    mif += f'  file {filename}\n'
    mif += f'  atlas :{atlas}\n'
    mif += '}\n\n'

    return mif


def vector_norm_scalar_field(field, name):
    mif = f'# {name}\n'
    mif += f'Specify Oxs_VecMagScalarField:{name} {{\n'
    mif += f'    field :{field}\n'
    mif += '}\n\n'

    return mif


def setup_scalar_parameter(parameter, name):
    if isinstance(parameter, df.Field):
        if parameter.dim != 1:
            msg = f'Cannot use dim={parameter.dim} for {name}.'
            raise ValueError(msg)

        parameter.write(f'{name}.ovf', extend_scalar=True)

        mif = file_vector_field(f'{name}.ovf', f'{name}', 'main_atlas')
        mif += vector_norm_scalar_field(f'{name}', f'{name}_norm')

        return mif, f'{name}_norm'

    elif isinstance(parameter, dict):
        if 'default' not in parameter.keys():
            parameter['default'] = 0

        mif = mif_atlas_scalar_field(parameter, f'{name}')

        return mif, f'{name}'

    elif isinstance(parameter, numbers.Real):
        return '', f'{parameter}'


def setup_vector_parameter(parameter, name):
    if isinstance(parameter, df.Field):
        if parameter.dim != 3:
            msg = 'Parameter must be a vector (dim=3) field.'
            raise ValueError(msg)
        parameter.write(f'{name}.ovf')
        mif = mif_file_vector_field(f'{name}.ovf', f'{name}')
        return mif, f'{name}'
    elif isinstance(parameter, dict):
        if 'default' not in parameter.keys():
            parameter['default'] = (0, 0, 0)
        mif = mif_atlas_vector_field(parameter, f'{name}')
        return mif, f'{name}'
    elif isinstance(parameter, (tuple, list, np.ndarray)):
        return '', '{{{} {} {}}}'.format(*parameter)
