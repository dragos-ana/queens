import os
import docker
import getpass
import time
from pqueens.drivers.driver import Driver
from pqueens.utils.aws_output_string_extractor import aws_extract


class BaciDriverDocker(Driver):
    """
    Driver to run BACI in Docker container

    Attributes:
        docker_image (str): Path to the docker image

    """

    def __init__(self, base_settings):
        # TODO dunder init should not be called with dict
        self.docker_version = base_settings['docker_version']
        self.docker_image = base_settings['docker_image']
        super(BaciDriverDocker, self).__init__(base_settings)

    @classmethod
    def from_config_create_driver(cls, config, base_settings, workdir=None):
        """ Create Driver from input file

        Args:
            config (dict):          Input options
            base_settings (dict):   Second dict with input options TODO should probably be removed

        Returns:
            driver (obj): BaciDriverDocker object

        """
        base_settings['address'] = 'localhost:27017'
        base_settings['docker_version'] = config['driver']['driver_type']
        base_settings['docker_image'] = config['driver']['driver_params']['docker_image']
        return cls(base_settings)

    def setup_dirs_and_files(self):
        """ Setup directory structure

            Args:
                driver_options (dict): Options dictionary

            Returns:
                None

        """
        # extract name of Docker image and potential sudo
        docker_image_list = self.docker_image.split()
        self.image_name = docker_image_list[0]
        if (len(docker_image_list)) == 2:
            self.sudo = docker_image_list[1]
        else:
            self.sudo = ''

        # define destination directory
        dest_dir = os.path.join(str(self.experiment_dir), str(self.job_id))

        self.output_directory = os.path.join(dest_dir, "output")
        if not os.path.isdir(self.output_directory):
            os.makedirs(self.output_directory)

        # create input file name
        input_string = str(self.experiment_name) + '_' + str(self.job_id) + '.dat'
        self.input_file = os.path.join(dest_dir, input_string)

        # create output file name
        output_string = str(self.experiment_name) + '_' + str(self.job_id)
        self.output_file = os.path.join(self.output_directory, output_string)

    def run_job(self):
        """ Actual method to run the job on computing machine
            using run_subprocess method from base class
        """
        # assemble BACI run command string
        self.baci_run_command_string = self.assemble_baci_run_command_string()

        # decide whether task-based run or direct run
        if self.docker_version == 'baci_docker_task':
            run_command_string = self.assemble_aws_run_task_command_string()
        else:
            # first alternative (used currently):
            # explicitly assemble run command for Docker container
            run_command_string = self.assemble_docker_run_command_string()

            # second alternative (not used currently): use Docker SDK
            # get Docker client
            # client = docker.from_env()

            # assemble volume map for docker container
            # volume_map = {self.experiment_dir: {'bind': self.experiment_dir, 'mode': 'rw'}}

            # run BACI in Docker container via SDK
            # stderr = client.containers.run(self.image_name,
            #                               self.baci_run_command_string,
            #                               remove=True,
            #                               volumes=volume_map,
            #                               stdout=False,
            #                               stderr=True)

        # run BACI in Docker container via subprocess
        #_, stderr, self.pid = self.run_subprocess(docker_run_command_string)
        stdout, stderr, self.pid = self.run_subprocess(run_command_string)

        # save AWS ARN and number of processes to database for task-based run
        if self.docker_version == 'baci_docker_task':
            self.job['aws_arn'] = aws_extract("taskArn", stdout)
            self.job['num_procs'] = self.num_procs
            self.database.save(self.job,
                               self.experiment_name,
                               'jobs',
                               str(self.batch),
                               {'id': self.job_id})
          
        # detection of failed jobs
        if stderr:
            self.result = None
            self.job['status'] = 'failed'

    def assemble_baci_run_command_string(self):
        """  Assemble BACI run command list

            Returns:
                list: command list to execute BACI

        """
        # set MPI command
        mpi_command = '/usr/lib64/openmpi/bin/mpirun --allow-run-as-root -np'

        command_list = [
            mpi_command,
            str(self.num_procs),
            self.executable,
            self.input_file,
            self.output_file,
        ]

        return ' '.join(filter(None, command_list))

    def assemble_aws_run_task_command_string(self):
        """  Assemble command list for BACI runin Docker container

            Returns:
                list: command list to execute BACI in Docker container

        """
        command_list = [
            "aws ecs run-task ",
            "--cluster worker-queens-cluster ",
            "--task-definition docker-queens ",
            "--count 1 ",
            "--overrides '{ \"containerOverrides\": [ {\"name\": \"docker-queens-container\", ",
            "\"command\": [\"",
            self.baci_run_command_string,
            "\"] } ] }'",
        ]

        return ''.join(filter(None, command_list))
    def assemble_docker_run_command_string(self):
        """  Assemble command list for BACI runin Docker container

            Returns:
                list: command list to execute BACI in Docker container

        """
        command_list = [
            self.sudo,
            " docker run -i --rm --user='",
            str(os.geteuid()),
            "' -e USER='",
            getpass.getuser(),
            "' -v ",
            self.experiment_dir,
            ":",
            self.experiment_dir,
            " ",
            self.image_name,
            " ",
            self.baci_run_command_string,
        ]

        return ''.join(filter(None, command_list))
