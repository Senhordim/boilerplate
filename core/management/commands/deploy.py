"""Management responsible for creating the deploy structure using Docker
"""

import os
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manager to automate the generation of codes"

    def __init__(self):
        super().__init__()
        self.project = ""
        self.project_lower = ""
        self.sub_domain = ""
        self.sub_domain_lower = ""
        self.branch = ""
        self.branch_lower = ""
        self.service_name = ""
        self.service_name_lower = ""
        self.path_root = ""
        self.path_core = ""
        self.path_nginx = ""
        self.path_dockerfile = ""
        self.path_jenkinsfile = ""
        self.path_run = ""
        self.path_docker_compose = ""

    def add_arguments(self, parser):
        """Method for adding positional arguments (required) and optional arguments
        """

        parser.add_argument('project', type=str)
        parser.add_argument('sub_domain', type=str)
        parser.add_argument(
            '--branch',
            help='Passa o branch do project no git. Default = master',
        )
        parser.add_argument(
            '--service_name',
            help='Passa o nome do serviço dentro do docker-compose e '
                 'Jenkinsfile. Default = project',
        )

    def __message(self, message, error=False):
        """Method for displaying friendly messages on the flow of script execution on the terminal.

        Arguments:
            message {str} -- Message to be displayed on the terminal
            error {bool} -- Attribute that determines whether the message is an error,
                            being an error message the execution of the program is ended
        """
        if error:
            self.stdout.write(self.style.ERROR(message))
            sys.exit()
        else:
            self.stdout.write(self.style.SUCCESS(message))

    def __contain_number(self, text) -> bool:
        """Method to check the text passed as a parameter has numeric characters

        Arguments:
            text {String} -- Text to be validated

        Returns:
            bool -- True if there is any number in the text parameter
        """
        try:
            return any(character.isdigit() for character in text)
        except Exception as error:
            self.__message(f"Error in Contain Number: {error}", error=True)
            return False

    def __check_file(self, path):
        """Method to check if the file passed as a parameter exists

         Arguments:
             path {str} - Path to the file

         Returns:
             bool - True if the file exists and False if not.
        """

        try:
            return os.path.isfile(path)
        except Exception as e:
            self.__message(f"Error in check_file {e}", error=True)
            sys.exit()

    def __get_snippet(self, path):
        """Method to retrieve the value of the snippet file to be converted by merging with the values based on models
           from the Django project

        Arguments:
            path {str} - Absolute path to the optional file,
                         must be passed when the snippet path is in the same flutter directory

        Returns:
            str -- Text to be used to interpolate model data
        """

        try:
            if self.__check_file(path):
                with open(path) as arquivo:
                    return arquivo.read()
            self.__message("Arquivo não encontrado para captura.")
        except Exception as e:
            self.__message(e)
            return None

    def __manage_nginx(self):
        """Method for configuring the Nginx server
        """

        try:
            self.__message("Trabalhando na configuração do nginx")
            content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/nginx.txt"))
            content = content.replace("$sub_domain$", self.sub_domain_lower)
            content = content.replace("$project$", self.project_lower)
            if self.__check_file(self.path_nginx) is False:
                with open(self.path_nginx, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self.__message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO nginx.py "
                           "sofreu alguma alteração: {}".format(e))

    def __manage_dockerfile(self):
        """Method for configuring the Dockerfile file
        """

        try:
            self.__message("Trabalhando na configuração do Dockerfile")
            content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/Dockerfile.txt"))
            content = content.replace("$branch$", self.branch_lower)
            content = content.replace("$project$", self.project_lower)
            if self.__check_file(self.path_dockerfile) is False:
                with open(self.path_dockerfile, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self.__message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO Dockerfile "
                           "sofreu alguma alteração: {}".format(e))

    def __manage_jenkisfile(self):
        """Method for configuring the o Jenkins file.
        """

        try:
            self.__message("Trabalhando na configuração do Jenkinsfile")
            content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/Jenkinsfile.txt"))
            content = content.replace("$service_name$", self.service_name_lower)
            content = content.replace("$project$", self.project_lower)
            if self.__check_file(self.path_jenkinsfile) is False:
                with open(self.path_jenkinsfile, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self.__message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO Jenkinsfile"
                           "sofreu alguma alteração: {}".format(e))

    def _manage_docker_compose(self):
        """Method to configure docker-compose.yml file
        """
        try:
            self.__message("Trabalhando na configuração do docker-compose.yml")
            content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/docker-compose.txt"))
            content = content.replace("$sub_domain$", self.sub_domain_lower)
            content = content.replace("$project$", self.project_lower)
            content = content.replace("$service_name$", self.service_name_lower)
            if self.__check_file(self.path_docker_compose) is False:
                with open(self.path_docker_compose, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self.__message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO "
                           "docker-compose.yml sofreu alguma alteração: "
                           "{}".format(e))

    def _manage_run(self):
        """Method to configure run.sh file
        """

        try:
            self.__message("Trabalhando na configuração do run.sh")
            content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/run.txt"))
            content = content.replace("$project$", self.project_lower)
            if self.__check_file(self.path_run) is False:
                with open(self.path_run, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self.__message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO run.sh "
                           "sofreu alguma alteração: {}".format(e))

    def handle(self, *args, **options):
        self.__message("Gerando os arquivos do project para deploy")
        self.project = ''
        if options['project']:
            self.project = options['project']
            self.project_lower = self.project.lower()

        self.sub_domain = ''
        if options['sub_domain']:
            self.sub_domain = options['sub_domain']
            self.sub_domain_lower = self.sub_domain.lower()

        self.branch_lower = self.branch = 'master'
        if options['branch']:
            self.branch = options['branch']
            self.branch_lower = self.branch.lower()

        self.service_name_lower = self.service_name = self.project_lower
        if options['service_name']:
            self.service_name = options['service_name']
            self.service_name_lower = self.service_name.lower()

        if self.__contain_number(self.project) is False:
            self.project = self.project.strip()
            self.path_root = os.getcwd()
            self.path_core = os.path.join(self.path_root, "nuvols/core")
            self.path_nginx = os.path.join(self.path_root, "nginx.conf")
            self.path_dockerfile = os.path.join(self.path_root, "Dockerfile")
            self.path_jenkinsfile = os.path.join(self.path_root, "Jenkinsfile")
            self.path_run = os.path.join(self.path_root, "run.sh")
            self.path_docker_compose = os.path.join(self.path_root, "docker-compose.yml")
            self.__manage_nginx()
            self.__manage_dockerfile()
            self._manage_docker_compose()
            self.__manage_jenkisfile()
            self._manage_run()
