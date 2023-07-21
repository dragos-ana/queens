"""Test BACI with RF materials."""

import pickle

import numpy as np
import pytest

from pqueens import run
from pqueens.utils import injector


def test_write_random_material_to_dat_dask(
    inputdir, tmp_path, third_party_inputs, baci_link_paths, expected_mean, expected_var
):
    """Test BACI with random field for material parameters."""
    dat_template = third_party_inputs / "baci_input_files" / "coarse_plate_dirichlet_template.dat"

    dat_file_preprocessed = tmp_path / "coarse_plate_dirichlet_template.dat"

    baci_release, post_ensight, _ = baci_link_paths

    dir_dict = {
        'baci_input': dat_template,
        'baci_input_preprocessed': dat_file_preprocessed,
        'post_ensight': post_ensight,
        'baci_release': baci_release,
    }
    template = inputdir / "baci_mc_random_field_ensight_template_dask.yml"
    input_file = tmp_path / "baci_mc_random_field_ensight.yml"
    injector.inject(dir_dict, template, input_file)

    run(input_file, tmp_path)

    experiment_name = "baci_mc_random_field_ensight_dask"
    result_file_name = experiment_name + ".pickle"

    result_file = tmp_path / result_file_name
    with open(result_file, 'rb') as handle:
        results = pickle.load(handle)

    # Check if we got the expected results
    np.testing.assert_array_almost_equal(results['mean'], expected_mean, decimal=8)
    np.testing.assert_array_almost_equal(results['var'], expected_var, decimal=8)


@pytest.fixture(name="expected_mean")
def fixture_expected_mean():
    """Reference samples mean."""
    result = np.array(
        [
            [2.5, 2.5],
            [2.27542528, 2.5],
            [2.27428635, 2.22656862],
            [2.5, 2.22772392],
            [2.04245122, 2.5],
            [2.04164592, 2.22472858],
            [1.79860357, 2.5],
            [1.79830412, 2.22378008],
            [1.54492736, 2.5],
            [1.5452743, 2.22368701],
            [1.28567445, 2.5],
            [1.28800082, 2.22558872],
            [1.02318291, 2.5],
            [1.0283711, 2.23195044],
            [0.76073754, 2.5],
            [0.7670636, 2.24251262],
            [0.50402426, 2.5],
            [0.50907063, 2.25313751],
            [0.25187233, 2.5],
            [0.25448458, 2.26029968],
            [0.0, 2.5],
            [0.0, 2.26275253],
            [2.27092854, 1.9728593],
            [2.5, 1.97541348],
            [2.03839469, 1.9674023],
            [1.79642685, 1.96230308],
            [1.54533629, 1.95929984],
            [1.29261879, 1.96000012],
            [1.04020502, 1.9673206],
            [0.78332263, 1.98227922],
            [0.52285496, 1.99953051],
            [0.26164692, 2.01170365],
            [0.0, 2.01580715],
            [2.26524019, 1.74077312],
            [2.5, 1.74448359],
            [2.03065077, 1.73143287],
            [1.79013093, 1.72045374],
            [1.54296251, 1.71219635],
            [1.29613845, 1.70936231],
            [1.05186313, 1.7134612],
            [0.80188278, 1.72536556],
            [0.54042576, 1.74154035],
            [0.27104907, 1.75400281],
            [0.0, 1.75820021],
            [2.25807595, 1.5200785],
            [2.5, 1.52418117],
            [2.01865919, 1.50864319],
            [1.77842156, 1.4934725],
            [1.53632224, 1.48045266],
            [1.29603271, 1.47324332],
            [1.05840707, 1.47196881],
            [0.81460243, 1.47606349],
            [0.55438262, 1.48401268],
            [0.27905914, 1.49115411],
            [0.0, 1.49356842],
            [2.25062052, 1.29374937],
            [2.5, 1.29755672],
            [2.00461102, 1.2827212],
            [1.76350443, 1.2675734],
            [1.5261848, 1.25397408],
            [1.29161922, 1.24494783],
            [1.05783292, 1.23937849],
            [0.81691742, 1.23540489],
            [0.55844751, 1.23265207],
            [0.28186242, 1.23106054],
            [0.0, 1.23033933],
            [2.2434907, 1.04873945],
            [2.5, 1.05205516],
            [1.99126629, 1.03988059],
            [1.74948597, 1.02906197],
            [1.51610649, 1.02023764],
            [1.28519126, 1.01422824],
            [1.05174202, 1.00842897],
            [0.80953254, 1.00011182],
            [0.55127612, 0.98955669],
            [0.27752144, 0.98024338],
            [0.0, 0.97645412],
            [2.23676658, 0.78498423],
            [2.5, 0.78765589],
            [1.98042369, 0.7789132],
            [1.73981611, 0.77424932],
            [1.51002089, 0.77317166],
            [1.28058485, 0.77375656],
            [1.04417984, 0.77179911],
            [0.79690741, 0.76394093],
            [0.53660518, 0.75081935],
            [0.26754677, 0.73792988],
            [0.0, 0.73259052],
            [2.23121341, 0.51204825],
            [2.5, 0.51354119],
            [1.97351344, 0.50977836],
            [1.73622322, 0.51116154],
            [1.50991213, 0.51661418],
            [1.28034349, 0.52283855],
            [1.03883525, 0.52524234],
            [0.78419026, 0.52047864],
            [0.52015544, 0.50919698],
            [0.2558121, 0.49725891],
            [0.0, 0.49231902],
            [2.22855544, 0.2461188],
            [2.5, 0.24613732],
            [1.97208536, 0.24749866],
            [1.73783799, 0.25177456],
            [1.51365308, 0.25799755],
            [1.28310414, 0.2640103],
            [1.0366136, 0.26704448],
            [0.77496517, 0.26490454],
            [0.5072641, 0.25817669],
            [0.24667418, 0.25117742],
            [0.0, 0.24842977],
            [2.22822158, 0.0],
            [2.5, 0.0],
            [1.97283038, 0.0],
            [1.73961786, 0.0],
            [1.51597516, 0.0],
            [1.28483963, 0.0],
            [1.0361793, 0.0],
            [0.77148831, 0.0],
            [0.50234967, 0.0],
            [0.24334292, 0.0],
            [0.0, 0.0],
        ]
    )
    return result


@pytest.fixture(name="expected_var")
def fixture_expected_var():
    """Reference samples var."""
    result = np.array(
        [
            [0.00000000e00, 0.00000000e00],
            [1.13152081e-05, 0.00000000e00],
            [3.65466914e-05, 7.14479892e-04],
            [0.00000000e00, 8.60723585e-04],
            [2.53894874e-04, 0.00000000e00],
            [9.75547084e-05, 4.72135318e-04],
            [2.70515614e-03, 0.00000000e00],
            [2.17297405e-03, 4.55390458e-04],
            [8.13459934e-03, 0.00000000e00],
            [7.76375452e-03, 6.28429500e-04],
            [1.09895392e-02, 0.00000000e00],
            [1.15301314e-02, 5.91762862e-04],
            [6.51162027e-03, 0.00000000e00],
            [7.60206473e-03, 2.49709595e-04],
            [9.53860429e-04, 0.00000000e00],
            [1.42351003e-03, 1.01339285e-05],
            [8.89810347e-05, 0.00000000e00],
            [2.89948730e-05, 6.44464970e-05],
            [3.32486933e-04, 0.00000000e00],
            [2.88055913e-04, 1.61000512e-04],
            [0.00000000e00, 0.00000000e00],
            [0.00000000e00, 1.87104625e-04],
            [1.63704289e-04, 3.92000055e-03],
            [0.00000000e00, 4.38984414e-03],
            [2.50236270e-05, 2.72901947e-03],
            [1.16791284e-03, 1.46158625e-03],
            [6.46917586e-03, 8.27980680e-04],
            [1.19459578e-02, 6.75591834e-04],
            [9.98526106e-03, 3.45667975e-04],
            [3.08411463e-03, 4.40290853e-06],
            [5.97110439e-05, 3.20705418e-04],
            [1.39110006e-04, 8.80517666e-04],
            [0.00000000e00, 1.08883686e-03],
            [3.31158818e-04, 1.05191177e-02],
            [0.00000000e00, 1.11102851e-02],
            [3.33214352e-04, 8.73173312e-03],
            [7.11125241e-04, 5.95022361e-03],
            [4.79535522e-03, 3.17416714e-03],
            [1.10814451e-02, 1.41955821e-03],
            [1.19722944e-02, 5.34590703e-04],
            [5.96855334e-03, 1.52075909e-04],
            [8.59655264e-04, 7.84556355e-04],
            [7.15837352e-06, 2.05268208e-03],
            [0.00000000e00, 2.61149194e-03],
            [4.68854594e-04, 1.86570760e-02],
            [0.00000000e00, 1.93066666e-02],
            [8.81452563e-04, 1.65610981e-02],
            [1.13223129e-03, 1.28019464e-02],
            [3.98421979e-03, 8.09475677e-03],
            [9.98358305e-03, 4.04120319e-03],
            [1.33135797e-02, 1.59854041e-03],
            [9.59561581e-03, 6.34427285e-04],
            [3.09505078e-03, 1.23004032e-03],
            [2.56920124e-04, 2.93087413e-03],
            [0.00000000e00, 3.81340953e-03],
            [6.88850480e-04, 2.56201863e-02],
            [0.00000000e00, 2.67606759e-02],
            [1.82047728e-03, 2.22657163e-02],
            [2.68923141e-03, 1.70337444e-02],
            [5.12808391e-03, 1.09821994e-02],
            [1.06131158e-02, 5.73674554e-03],
            [1.52929652e-02, 2.46557779e-03],
            [1.36249084e-02, 1.24093231e-03],
            [6.48768138e-03, 1.78234450e-03],
            [1.10984363e-03, 3.38551225e-03],
            [0.00000000e00, 4.27000639e-03],
            [1.27416606e-03, 2.92093270e-02],
            [0.00000000e00, 3.13096037e-02],
            [4.02680496e-03, 2.33042915e-02],
            [6.56441013e-03, 1.57946586e-02],
            [9.50089680e-03, 9.18190313e-03],
            [1.44596297e-02, 4.68128488e-03],
            [1.91047207e-02, 2.49840329e-03],
            [1.78220896e-02, 2.16597232e-03],
            [9.70748187e-03, 2.99030507e-03],
            [2.09715786e-03, 4.17780284e-03],
            [0.00000000e00, 4.75313136e-03],
            [2.57092367e-03, 2.43544472e-02],
            [0.00000000e00, 2.69715012e-02],
            [8.94578772e-03, 1.72479624e-02],
            [1.44984200e-02, 9.57222924e-03],
            [1.80588333e-02, 4.65622869e-03],
            [2.16434247e-02, 2.77175639e-03],
            [2.44488893e-02, 2.88398093e-03],
            [2.13975875e-02, 3.84130293e-03],
            [1.14128508e-02, 4.72255410e-03],
            [2.48798809e-03, 5.13309519e-03],
            [0.00000000e00, 5.24272371e-03],
            [4.57605144e-03, 1.09920878e-02],
            [0.00000000e00, 1.26652518e-02],
            [1.62431923e-02, 6.89361586e-03],
            [2.54151185e-02, 3.12708337e-03],
            [2.90899540e-02, 1.54331794e-03],
            [3.02840332e-02, 2.05370496e-03],
            [2.97570632e-02, 3.53681985e-03],
            [2.33051465e-02, 4.73555117e-03],
            [1.11034793e-02, 4.90195393e-03],
            [2.12867531e-03, 4.40417946e-03],
            [0.00000000e00, 4.15175268e-03],
            [6.35053066e-03, 1.67629447e-03],
            [0.00000000e00, 2.01238470e-03],
            [2.20539830e-02, 9.63796440e-04],
            [3.41692654e-02, 4.13882330e-04],
            [3.81719805e-02, 4.49953676e-04],
            [3.74216244e-02, 1.12704220e-03],
            [3.35018626e-02, 1.97474467e-03],
            [2.33161264e-02, 2.31925323e-03],
            [9.59124202e-03, 1.99981872e-03],
            [1.54242207e-03, 1.55865812e-03],
            [0.00000000e00, 1.40448613e-03],
            [6.97186161e-03, 0.00000000e00],
            [0.00000000e00, 0.00000000e00],
            [2.39362196e-02, 0.00000000e00],
            [3.72655138e-02, 0.00000000e00],
            [4.16603781e-02, 0.00000000e00],
            [4.02853059e-02, 0.00000000e00],
            [3.48149031e-02, 0.00000000e00],
            [2.28716688e-02, 0.00000000e00],
            [8.75510421e-03, 0.00000000e00],
            [1.29716317e-03, 0.00000000e00],
            [0.00000000e00, 0.00000000e00],
        ]
    )
    return result
