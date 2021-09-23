"""
Test suite for remote BACI sumlations on the cluster in combination with the BACI ensight
 post-post-processor. No iterator is used, the model is called directly.
"""

import pickle
import pathlib
import numpy as np
import pytest
import json
from pqueens.utils import injector
from pqueens.utils.run_subprocess import run_subprocess
from pqueens.models.model import Model
from pqueens.database.mongodb import MongoDB


@pytest.mark.lnm_cluster
def test_cluster_postpost_ensight(
    inputdir, tmpdir, third_party_inputs, cluster_testsuite_settings, baci_cluster_paths
):
    """
    Integration test for clusters BACI runs with the postpost processor `post_post_ensight`.

    Args:
        inputdir (str): Path to the JSON input file
        tmpdir (str): Temporary directory in which the pytests are run
        third_party_inputs (str): Path to the BACI input files
        cluster_testsuite_settings (dict): Collection of cluster specific settings

    Returns:
        None

    """
    # unpack cluster settings needed for all cluster tests
    cluster = cluster_testsuite_settings["cluster"]
    cluster_user = cluster_testsuite_settings["cluster_user"]
    cluster_address = cluster_testsuite_settings["cluster_address"]
    cluster_bind = cluster_testsuite_settings["cluster_bind"]
    connect_to_resource = cluster_testsuite_settings["connect_to_resource"]
    cluster_queens_testing_folder = cluster_testsuite_settings["cluster_queens_testing_folder"]
    cluster_path_to_singularity = cluster_testsuite_settings["cluster_path_to_singularity"]
    scheduler_type = cluster_testsuite_settings["scheduler_type"]
    singularity_remote_ip = cluster_testsuite_settings["singularity_remote_ip"]

    path_to_executable = baci_cluster_paths["path_to_executable"]
    path_to_drt_monitor = baci_cluster_paths["path_to_drt_monitor"]
    path_to_drt_ensight = baci_cluster_paths["path_to_drt_ensight"]
    path_to_drt_monitor = baci_cluster_paths["path_to_drt_monitor"]
    path_to_post_processor = baci_cluster_paths["path_to_post_processor"]

    # unique experiment name
    experiment_name = cluster + "_remote_post_post_ensight"

    template = pathlib.Path(inputdir, "remote_baci_model_config.json")
    input_file = pathlib.Path(tmpdir, f"remote_baci_model_config.json")

    # specific folder for this test
    cluster_experiment_dir = cluster_queens_testing_folder.joinpath(experiment_name)

    baci_input_filename = "invaaa_ee.dat"
    third_party_input_file_local = pathlib.Path(
        third_party_inputs, "baci_input_files", baci_input_filename
    )
    path_to_input_file_cluster = cluster_experiment_dir.joinpath("input")
    input_file_cluster = path_to_input_file_cluster.joinpath(baci_input_filename)

    experiment_dir = cluster_experiment_dir.joinpath("output")

    command_string = f'mkdir -v -p {path_to_input_file_cluster}'
    returncode, pid, stdout, stderr = run_subprocess(
        command_string=command_string,
        subprocess_type='remote',
        remote_user=cluster_user,
        remote_address=cluster_address,
    )
    print(stdout)
    if returncode:
        raise Exception(stderr)

    command_string = f'mkdir -v -p {experiment_dir}'
    returncode, pid, stdout, stderr = run_subprocess(
        command_string=command_string,
        subprocess_type='remote',
        remote_user=cluster_user,
        remote_address=cluster_address,
    )
    print(stdout)
    if returncode:
        raise Exception(stderr)

    # copy input file to cluster
    command = ' '.join(
        [
            'scp',
            str(third_party_input_file_local),
            connect_to_resource + ':' + str(input_file_cluster),
        ]
    )
    returncode, pid, stdout, stderr = run_subprocess(command)
    print(stdout)
    if returncode:
        raise Exception(stderr)

    dir_dict = {
        'experiment_name': str(experiment_name),
        'path_to_singularity': str(cluster_path_to_singularity),
        'input_template': str(input_file_cluster),
        'path_to_executable': str(path_to_executable),
        'path_to_drt_monitor': str(path_to_drt_monitor),
        'path_to_drt_ensight': str(path_to_drt_ensight),
        'path_to_post_processor': str(path_to_post_processor),
        'experiment_dir': str(experiment_dir),
        'connect_to_resource': connect_to_resource,
        'cluster_bind': cluster_bind,
        'cluster': cluster,
        'scheduler_type': scheduler_type,
        'singularity_remote_ip': singularity_remote_ip,
    }

    injector.inject(dir_dict, template, input_file)
    arguments = ['--input=' + str(input_file), '--output=' + str(tmpdir)]

    # Patch the missing config arguments
    with open(str(input_file)) as f:
        config = json.load(f)
        global_settings = {
            "output_dir": str(tmpdir),
            "experiment_name": config["experiment_name"],
        }
        config["global_settings"] = global_settings
        config["input_file"] = str(input_file)

    # Add experimental coordinates to the database
    database = MongoDB.from_config_create_database(config, reset_database=True)
    experimental_data_dict = {"x1": [-16, 10], "x2": [7, 15], "x3": [0.63, 0.2]}
    database.save(experimental_data_dict, experiment_name, 'experimental_data', 1)

    # Create a BACI model for the benchmarks
    model = Model.from_config_create_model("model", config)

    # Evaluate the first batch
    samples = np.array([[0.2, 10], [0.3, 20], [0.45, 100]])
    model.update_model_from_sample_batch(samples)
    first_batch = np.array(model.evaluate()["mean"])

    # Evaluate a second batch
    # In order to make sure that no port is closed after one batch
    samples = np.array([[0.3, 20], [0.45, 100], [0.2, 10]])
    model.update_model_from_sample_batch(samples)
    second_batch = np.array(model.evaluate()["mean"][-3:])

    # Check results
    sample_result = np.array([-0.0006949830567464232, 0.0017958658281713724])
    np.testing.assert_array_equal(first_batch[0], sample_result)
    np.testing.assert_array_equal(second_batch[2], sample_result)

    sample_result = np.array([-0.0012194387381896377, 0.003230389906093478])
    np.testing.assert_array_equal(first_batch[1], sample_result)
    np.testing.assert_array_equal(second_batch[0], sample_result)

    sample_result = np.array([-0.004366828128695488, 0.0129017299041152])
    np.testing.assert_array_equal(first_batch[2], sample_result)
    np.testing.assert_array_equal(second_batch[1], sample_result)
