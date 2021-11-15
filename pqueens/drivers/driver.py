import abc
import getpass
import os
import sys
import time

import pqueens.database.database as DB_module
from pqueens.external_geometry.external_geometry import ExternalGeometry


class Driver(metaclass=abc.ABCMeta):
    """
     Abstract base class for drivers in QUEENS.

    The driver manages simulation runs in QUEENS on local or remote computing resources
    with or without Singularity containers depending on the chosen CAE software (see also
    respective Wiki article on available CAE software).

    Args:
        base_settings (dict):      dictionary containing settings from base class for
                                   potential further use and completion in child classes

    Attributes:
        driver_name (str):         Name of the driver used for the analysis. The name is
                                   specified in the json-input file.
        experiment_name (str):     name of QUEENS experiment
        global_output_dir (str):   path to global output directory provided when launching
        port (int):                (only for remote scheduling with Singularity) port of
                                   remote resource for ssh port-forwarding to database
        database (obj):            database object
        experiment_dir (str):      path to QUEENS experiment directory
        scheduler_type (str):      type of scheduler chosen in QUEENS input file
        remote (bool):             flag for remote scheduling
        remote connect (str):      (only for remote scheduling) adress of remote
                                   computing resource
        singularity (bool):        flag for use of Singularity containers
        docker_image (str):        (only for use of Docker containers) name of Docker image
        num_procs (int):           number of processors for processing
        num_procs_post (int):      number of processors for post-processing
        direct_scheduling(bool):   flag for direct scheduling
        cluster_options (str):     (only for cluster schedulers Slurm and PBS) cluster options
        job_id (int):              job ID as provided in database within range [1, n_jobs]
        job (dict):                dictionary containing description of current job
        pid (int):                 unique process ID for subprocess
        simulation_input_t. (str): path to template for simulation input file
        executable (str):          path to main executable of respective CAE software
        custom_executable (str):   (if required) path to potential additional customized
                                   executable of respective CAE software
        cae_software_vers. (str):  (if required) version of CAE software
        result (np.array):         simulation result to be stored in database
        do_postprocessing (str):   string for identifying either local post-processing
                                   ('local') or remote post-processing ('remote') or 'None'
        postprocessor (str):       (only for post-processing) path to postprocessor of
                                   respective CAE software
        post_options (list):       (only for post-processing) list containing settings/options
                                   for post-processing
        post_file_name_prefix_lst (lst): List with unique prefix sequence to name the
                                         post-processed files by the post-processor
        postpostprocessor (obj):   instance of post-post class
        input_file (str):          path to input file
        input_file_2 (str):        path to second input file (not required for all drivers)
        case_run_script (str):     path to case run script (not required for all drivers)
        output_prefix (str):       output prefix (not required for all drivers)
        output_directory (str):    path to output directory (on remote computing resource for
                                   remote scheduling)
        local_output_dir (str):    (only for remote scheduling) path to local output directory
        output_file (str):         path to output file (not required for all drivers)
        control_file (str):        path to control file (not required for all drivers)
        log_file (str):            path to log file (not required for all drivers)
        error_file (str):          path to error file (not required for all drivers)

    Returns:
        driver (obj):         instance of driver class

    """

    def __init__(self, base_settings):
        self.driver_name = base_settings['driver_name']
        self.experiment_name = base_settings['experiment_name']
        self.global_output_dir = base_settings['global_output_dir']
        self.port = base_settings['port']
        self.database = base_settings['database']
        self.experiment_dir = base_settings['experiment_dir']
        self.scheduler_type = base_settings['scheduler_type']
        self.remote = base_settings['remote']
        self.remote_connect = base_settings['remote_connect']
        self.remote_python_cmd = base_settings['remote_python_cmd']
        self.singularity = base_settings['singularity']
        self.docker_image = base_settings['docker_image']
        self.num_procs = base_settings['num_procs']
        self.num_procs_post = base_settings['num_procs_post']
        self.direct_scheduling = base_settings['direct_scheduling']
        self.cluster_options = base_settings['cluster_options']
        self.batch = base_settings['batch']
        self.job_id = base_settings['job_id']
        self.job = base_settings['job']
        self.pid = None
        self.simulation_input_template = base_settings['simulation_input_template']
        self.executable = base_settings['executable']
        self.custom_executable = base_settings['custom_executable']
        self.cae_software_version = base_settings['cae_software_version']
        self.result = base_settings['result']

        self.do_postprocessing = base_settings['do_postprocessing']
        self.postprocessor = base_settings['postprocessor']
        self.post_options = base_settings['post_options']
        self.post_file_name_prefix_lst = base_settings['post_file_name_prefix_lst']

        self.do_postpostprocessing = base_settings['do_postpostprocessing']
        self.postpostprocessor = base_settings['postpostprocessor']
        self.error_file = base_settings['error_file']
        self.cae_output_streaming = base_settings['cae_output_streaming']

        self.input_file = base_settings['input_file']
        self.input_file_2 = base_settings['input_file_2']
        self.case_run_script = base_settings['case_run_script']
        self.output_prefix = base_settings['output_prefix']
        self.output_directory = base_settings['output_directory']
        self.local_output_dir = base_settings['local_output_dir']
        self.output_file = base_settings['output_file']
        self.control_file = base_settings['control_file']
        self.log_file = base_settings['log_file']
        self.error_file = base_settings['error_file']

    @classmethod
    def from_config_create_driver(
        cls,
        config,
        job_id,
        batch,
        driver_name,
        port=None,
        abs_path=None,
        workdir=None,
        cluster_options=None,
    ):
        """
        Create driver from problem description

        Args:
            config (dict):  Dictionary containing configuration from QUEENS input file
            job_id (int):   Job ID as provided in database within range [1, n_jobs]
            batch (int):    Job batch number (multiple batches possible)
            port (int):     Port for data forwarding from/to remote resource
            abs_path (str): Absolute path to post-post module on remote resource
            workdir (str):  Path to working directory on remote resource
            driver_name (str): Name of driver instance that should be realized

        Returns:
            driver (obj):   Driver object

        """
        from pqueens.drivers.baci_driver import BaciDriver
        from pqueens.post_post.post_post import PostPost

        # determine Driver class
        driver_dict = {
            'baci': BaciDriver,
        }

        # ---------------------------- CREATE BASE SETTINGS ---------------------------
        # initialize empty dictionary
        base_settings = {}

        # 1) general settings
        base_settings['experiment_name'] = config['global_settings'].get('experiment_name')
        base_settings['global_output_dir'] = config['global_settings'].get('output_dir')
        base_settings['driver_name'] = driver_name

        # 2) scheduler settings
        first = list(config['resources'])[0]
        scheduler_name = config['resources'][first]['scheduler']
        scheduler_options = config[scheduler_name]
        base_settings['scheduler_type'] = scheduler_options['scheduler_type']
        base_settings['experiment_dir'] = scheduler_options['experiment_dir']
        base_settings['docker_image'] = scheduler_options.get('docker_image')
        base_settings['num_procs'] = scheduler_options.get('num_procs', '1')
        base_settings['num_procs_post'] = scheduler_options.get('num_procs_post', '1')
        if scheduler_options.get('remote', False):
            base_settings['remote'] = True
            remote_options = scheduler_options['remote']
            base_settings['remote_connect'] = remote_options['connect']
            base_settings['remote_python_cmd'] = remote_options.get('python_cmd', 'python')
        else:
            base_settings['remote'] = False
            base_settings['remote_connect'] = None
            base_settings['remote_python_cmd'] = None
        base_settings['singularity'] = scheduler_options.get('singularity', False)

        # set flag for direct scheduling
        base_settings['direct_scheduling'] = False
        if not base_settings['singularity']:
            if (
                base_settings['scheduler_type'] == 'ecs_task'
                or base_settings['scheduler_type'] == 'nohup'
                or base_settings['scheduler_type'] == 'pbs'
                or base_settings['scheduler_type'] == 'slurm'
                or (base_settings['scheduler_type'] == 'standard' and base_settings['remote'])
            ):
                base_settings['direct_scheduling'] = True

        # get cluster options if required
        if base_settings['scheduler_type'] == 'pbs' or base_settings['scheduler_type'] == 'slurm':
            base_settings['cluster_options'] = cluster_options
        else:
            base_settings['cluster_options'] = None

        # 3) database settings
        base_settings['port'] = port
        base_settings['database'] = DB_module.database
        # 4) general driver settings

        # load correct driver settings
        driver_options = config[driver_name]['driver_params']
        base_settings['batch'] = batch
        base_settings['job_id'] = job_id
        base_settings['job'] = None
        base_settings['result'] = None
        base_settings['simulation_input_template'] = driver_options.get('input_template', None)
        base_settings['executable'] = driver_options['path_to_executable']
        base_settings['custom_executable'] = driver_options.get('custom_executable', None)
        base_settings['cae_software_version'] = driver_options.get('cae_software_version', None)

        # 5) driver settings for post-processing, if required
        base_settings['postprocessor'] = driver_options.get('path_to_postprocessor', None)
        if base_settings['postprocessor'] is not None:
            base_settings['post_file_name_prefix_lst'] = driver_options.get(
                'post_file_name_prefix_lst', None
            )
            base_settings['post_options'] = driver_options.get('post_process_options', None)
        else:
            base_settings['post_file_name_prefix_lst'] = None
            base_settings['post_options'] = None

        # determine whether post-processing needs to be done,
        # with the following prerequisite:
        # post-processor given and either no direct scheduling or direct
        # scheduling with post-processing options (e.g., post_drt_monitor)
        # further distinguish:
        # 1) local post-processing
        # 2) remote post-processing
        # 3) post-processing with Singularity container on cluster with Slurm or PBS
        if (base_settings['postprocessor'] is not None) and (
            (not base_settings['direct_scheduling']) or (base_settings['post_options'] is not None)
        ):
            if base_settings['remote'] and not base_settings['singularity']:
                base_settings['do_postprocessing'] = 'remote'
            elif base_settings['singularity'] and (
                base_settings['scheduler_type'] == 'pbs'
                or base_settings['scheduler_type'] == 'slurm'
            ):
                base_settings['do_postprocessing'] = 'cluster_sing'
            else:
                base_settings['do_postprocessing'] = 'local'
        else:
            base_settings['do_postprocessing'] = None

        # 6) driver settings for post-post-processing, if required, else set output
        #    streaming to 'stdout' for single simulation run
        base_settings['do_postpostprocessing'] = driver_options.get('post_post', None)
        if base_settings['do_postpostprocessing'] is not None:
            # TODO "hiding" a complete object in the base settings dict is unbelieveably ugly
            # and should be fixed ASAP
            base_settings['postpostprocessor'] = PostPost.from_config_create_post_post(
                config, driver_name=driver_name
            )
            base_settings['cae_output_streaming'] = False
        else:
            base_settings['postpostprocessor'] = None
            base_settings['cae_output_streaming'] = True

        # 7) initialize driver settings which are not required for all
        # specific drivers or only for remote scheduling, respectively
        base_settings['input_file_2'] = None
        base_settings['case_run_script'] = None
        base_settings['output_prefix'] = None
        base_settings['local_output_dir'] = None
        base_settings['output_file'] = None
        base_settings['control_file'] = None
        base_settings['log_file'] = None
        base_settings['error_file'] = None

        # 8) potentially generate an external external_geometry_obj object for input file
        # manipulation
        if config.get('external_geometry') is not None:
            external_geometry_obj = ExternalGeometry.from_config_create_external_geometry(config)
        else:
            external_geometry_obj = None
        base_settings["external_geometry_obj"] = external_geometry_obj

        # 9) get list of random field tuples: name, type
        model_name = config['method']['method_options'].get('model')
        parameter_name = config[model_name].get('parameters')
        if parameter_name is not None:
            random_fields = config[parameter_name].get("random_fields")
            if random_fields is not None:
                random_fields_lst = [
                    (name, value['external_definition']) for name, value in random_fields.items()
                ]
            else:
                random_fields_lst = None
            base_settings["random_fields_lst"] = random_fields_lst
        else:
            base_settings["random_fields_lst"] = None

        # generate specific driver class / base_settings are already set for this driver name
        if driver_name:
            driver_version = config[driver_name]['driver_type']
        else:
            driver_version = config['driver']['driver_type']

        driver_class = driver_dict[driver_version]
        driver = driver_class.from_config_create_driver(base_settings, workdir)

        return driver

    # ------ Core methods ----------------------------------------------------- #
    def pre_job_run_and_run_job(self):
        """
        Prepare and execute job run

        Returns:
            None

        """
        self.pre_job_run()
        self.run_job()

    def pre_job_run(self):
        """
        Prepare job run

        Returns:
            None

        """
        if self.job is None:
            self.initialize_job_in_db()
        self.prepare_input_files()

    def post_job_run(self):
        """
        Post-process (if required), post-post process (if required) and
        finalize job in database

        Returns:
            None

        """
        if self.do_postprocessing is not None:
            self.postprocess_job()
        if self.do_postpostprocessing is not None:
            self.postpostprocessing()
        else:
            # set result to "no" and load job from database, if there
            # has not been any post-post-processing before
            self.result = 'no post-post-processed result'
            if self.job is None:
                self.job = self.database.load(
                    self.experiment_name,
                    self.batch,
                    'jobs_' + self.driver_name,
                    {'id': self.job_id},
                )

        self.finalize_job_in_db()

    # ------ Base class methods ------------------------------------------------ #
    def initialize_job_in_db(self):
        """
        Initialize job in database

        Returns:
            None

        """
        # load job from database
        self.job = self.database.load(
            self.experiment_name,
            self.batch,
            'jobs_' + self.driver_name,
            {'id': self.job_id, 'expt_dir': self.experiment_dir, 'expt_name': self.experiment_name},
        )

        # set start time and store it in database
        start_time = time.time()
        self.job['start time'] = start_time

        # save start time in database to make it accessible for the second post-processing call
        self.database.save(
            self.job,
            self.experiment_name,
            'jobs_' + self.driver_name,
            str(self.batch),
            {'id': self.job_id, 'expt_dir': self.experiment_dir, 'expt_name': self.experiment_name},
        )

    def postpostprocessing(self):
        """
        Extract data of interest from post-processed files and save them to database

        Returns:
            None

        """

        # load job from database if existent
        if self.job is None:
            self.job = self.database.load(
                self.experiment_name, self.batch, 'jobs_' + self.driver_name, {'id': self.job_id},
            )

        # get (from the point of view of the location of the post-processed files)
        # "local" and "remote" output directory for this job ID, which is exactly
        # opposite to the general definition, with the latter effectively used
        # only in case of remote scheduling
        pp_local_output_dir = self.output_directory
        if self.remote and not self.singularity:
            pp_remote_output_dir = self.local_output_dir
            remote_connect = self.remote_connect
        else:
            pp_remote_output_dir = None
            remote_connect = None

        # only proceed if this job did not fail
        if self.job['status'] != "failed":
            # set security duplicate in case post_post did not catch an error
            self.result = None

            # call post-post-processing
            self.result = self.postpostprocessor.postpost_main(
                pp_local_output_dir, remote_connect, pp_remote_output_dir
            )

            # print obtained result to screen
            sys.stdout.write("Got result %s\n" % (self.result))

    def finalize_job_in_db(self):
        """
        Finalize job in database

        Returns:
            None

        """

        if self.result is None:
            self.job['result'] = None  # TODO: maybe we should better use a pandas format here
            self.job['status'] = 'failed'
            if not self.direct_scheduling:
                self.job['end time'] = time.time()
            self.database.save(
                self.job,
                self.experiment_name,
                'jobs_' + self.driver_name,
                str(self.batch),
                {
                    'id': self.job_id,
                    'expt_dir': self.experiment_dir,
                    'expt_name': self.experiment_name,
                },
            )
        else:
            self.job['result'] = self.result
            self.job['status'] = 'complete'
            if self.job['start time'] is not None and not self.direct_scheduling:
                self.job['end time'] = time.time()
                computing_time = self.job['end time'] - self.job['start time']
                sys.stdout.write(
                    'Successfully completed job {:d} (No. of proc.: {:d}, '
                    'computing time: {:08.2f} s).\n'.format(
                        self.job_id, self.num_procs, computing_time
                    )
                )
            self.database.save(
                self.job,
                self.experiment_name,
                'jobs_' + self.driver_name,
                str(self.batch),
                {
                    'id': self.job_id,
                    'expt_dir': self.experiment_dir,
                    'expt_name': self.experiment_name,
                },
            )

    # ---------------- COMMAND-ASSEMBLY METHODS ----------------------------------
    def assemble_nohup_run_cmd(self, run_cmd, log_file, err_file):
        """  Assemble command for nohup run

            Returns:
                nohup run command

        """
        command_list = [
            "nohup",
            run_cmd,
            ">",
            log_file,
            "2>",
            err_file,
            "< /dev/null &",
        ]

        return ' '.join(filter(None, command_list))

    def assemble_remote_run_cmd(self, run_cmd):
        """  Assemble command for remote (nohup) run

            Returns:
                remote (nohup) run command

        """
        command_list = [
            'ssh',
            self.remote_connect,
            '"cd',
            self.experiment_dir,
            ';',
            run_cmd,
            '"',
        ]

        return ' '.join(filter(None, command_list))

    def assemble_docker_run_cmd(self, run_cmd):
        """  Assemble command for run in Docker container

            Returns:
                Docker run command

        """
        command_list = [
            #            self.sudo,
            "docker run -i --rm --user='",
            str(os.geteuid()),
            "' -e USER='",
            getpass.getuser(),
            "' -v ",
            self.experiment_dir,
            ":",
            self.experiment_dir,
            " ",
            self.docker_image,
            " ",
            run_cmd,
        ]

        return ''.join(filter(None, command_list))

    def assemble_ecs_task_run_cmd(self, run_cmd):
        """  Assemble command for run as ECS task

            Returns:
                ECS task run command

        """
        command_list = [
            "aws ecs run-task ",
            "--cluster worker-queens-cluster ",
            "--task-definition docker-queens ",
            "--count 1 ",
            "--overrides '{ \"containerOverrides\": [ {\"name\": \"docker-queens-container\", ",
            "\"command\": [\"",
            run_cmd,
            "\"] } ] }'",
        ]

        return ''.join(filter(None, command_list))

    # ---------------- CHILD METHODS THAT NEED TO BE IMPLEMENTED ---------------
    @abc.abstractmethod
    def prepare_input_files(self):
        """
        Abstract method for preparing input file(s)

        Returns:
            None
        """
        pass

    @abc.abstractmethod
    def run_job(self):
        """
        Abstract method for running job

        Returns:
            None

        """
        pass

    @abc.abstractmethod
    def postprocess_job(self):
        """
        Abstract method for post-processing of job

        Returns:
            None

        """
        pass
