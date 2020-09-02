"""Management responsible for creating the deploy structure using Docker
"""

import os

from django.core.management.base import BaseCommand

from nuvols.core.management.commands.utils import Utils


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

    def __manage_nginx(self):
        """Method for configuring the Nginx server
        """

        try:
            Utils.show_message("Trabalhando na configuração do nginx")
            content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/nginx.txt"))
            content = content.replace("$sub_domain$", self.sub_domain_lower)
            content = content.replace("$project$", self.project_lower)
            if Utils.check_file(self.path_nginx) is False:
                with open(self.path_nginx, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            Utils.show_message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO nginx.py "
                               "sofreu alguma alteração: {}".format(e), error=True)

    def __manage_dockerfile(self):
        """Method for configuring the Dockerfile file
        """

        try:
            Utils.show_message("Trabalhando na configuração do Dockerfile")
            content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/Dockerfile.txt"))
            content = content.replace("$branch$", self.branch_lower)
            content = content.replace("$project$", self.project_lower)
            if Utils.check_file(self.path_dockerfile) is False:
                with open(self.path_dockerfile, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            Utils.show_message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO Dockerfile "
                               "sofreu alguma alteração: {}".format(e), error=True)

    def __manage_jenkisfile(self):
        """Method for configuring the o Jenkins file.
        """

        try:
            Utils.show_message("Trabalhando na configuração do Jenkinsfile")
            content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/Jenkinsfile.txt"))
            content = content.replace("$service_name$", self.service_name_lower)
            content = content.replace("$project$", self.project_lower)
            if Utils.check_file(self.path_jenkinsfile) is False:
                with open(self.path_jenkinsfile, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            Utils.show_message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO Jenkinsfile"
                               "sofreu alguma alteração: {}".format(e), error=True)

    def _manage_docker_compose(self):
        """Method to configure docker-compose.yml file
        """
        try:
            Utils.show_message("Trabalhando na configuração do docker-compose.yml")
            content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/docker-compose.txt"))
            content = content.replace("$sub_domain$", self.sub_domain_lower)
            content = content.replace("$project$", self.project_lower)
            content = content.replace("$service_name$", self.service_name_lower)
            if Utils.check_file(self.path_docker_compose) is False:
                with open(self.path_docker_compose, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            Utils.show_message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO "
                               "docker-compose.yml sofreu alguma alteração: "
                               "{}".format(e), error=True)

    def _manage_run(self):
        """Method to configure run.sh file
        """

        try:
            Utils.show_message("Trabalhando na configuração do run.sh")
            content = Utils.get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/run.txt"))
            content = content.replace("$project$", self.project_lower)
            if Utils.check_file(self.path_run) is False:
                with open(self.path_run, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            Utils.show_message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO run.sh "
                               "sofreu alguma alteração: {}".format(e), error=True)

    def handle(self, *args, **options):
        Utils.show_message("Gerando os arquivos do project para deploy")
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

        if Utils.contain_number(self.project) is False:
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
