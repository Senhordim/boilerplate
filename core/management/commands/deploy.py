"""Manager para mapear os models da app automatizando 
a criação dos templates customizados, das views, da APIRest e dos Forms.
"""

import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Manager para automatizar a geração dos códigos"

    def add_arguments(self, parser):
        """Método inicial para informar quais parâmetros serão aceitos
        """

        parser.add_argument('projeto', type=str)
        parser.add_argument('subdominio', type=str)
        # parser.add_argument('branch', type=str)
        parser.add_argument(
            '--branch',
            help='Passa o branch do projeto no git. Default = master',
        )
        parser.add_argument(
            '--service_name',
            help='Passa o nome do servico dentro do docker-compose e '
                 'Jenkinsfile. Default = projeto',
        )
    """
    #################################################################
    Área dos método internos
    #################################################################    
    """

    def _contain_number(self, text):
        try:
            return any(character.isdigit() for character in text)
        except:
            return False

    def _get_size(self, path):
        """Método para verificar o tamanho de um determinado arquivo.
        
        Arguments:
            path {str} -- Caminho absoluto para o arquivo
        
        Returns:
            Tamanho do arquivo
        """

        try:
            return os.path.getsize(path)
        except Exception as e:
            self._message(e)
            return False
    
    def _check_dir(self, path):
        """Método para verificar se o diretório existe
        
        Arguments:
            path {str} -- Caminho do diretório
        
        Returns:
            Boolean -- Verdadeiro se existir o diretório e Falso se não.
        """

        try:
            return os.path.isdir(path)
        except Exception as e:
            self._message(e)
            return False

    def _check_file(self, path):
        """Método para verificar se o arquivo existe
        
        Arguments:
            path {str} -- Caminho para o arquivo
        
        Returns:
            Boolean -- Verdadeiro se existir o arquivo e False se não.
        """

        try:
            return os.path.isfile(path)
        except Exception as e:
            self._message(e)
            return False
    
    def _message(self, message):
        """Método para retornar mensagems ao prompt(Terminal)
        
        Arguments:
            message {str} -- Mensagem a ser exibida
        """

        self.stdout.write(self.style.SUCCESS(message))

    def _check_content(self, path, text_check):
        """Método para verificar se determinado texto existe 
        dentro de determinado arquivo
        
        Arguments:
            path {str} -- Caminho absoluto para o arquivo a ser analisado
            text_check {str} -- Texto a ser pesquisado dentro do arquivo
            informado
        
        Returns:
            Boolean -- Verdadeiro se o conteúdo for encontrado e False se não.
        """

        try:
            if self._check_file(path):
                with open(path) as arquivo:
                    content = arquivo.read()
                    return text_check in content
            self._message("Arquivo não encontrado para análise.")
        except Exception as e:
            self._message(e)
            return False

    def _get_snippet(self, path):
        """Método para recuperar o texto a ser utilizado na
        configuração do novo elemento
        
        Arguments:
            path {str} -- Caminho absoluto para o arquivo
        
        Returns:
            str -- Texto a ser utilizado para interpolar os dados do models
        """

        try:
            if self._check_file(path):
                with open(path) as arquivo:
                    return arquivo.read()
            self._message("Arquivo não encontrado para captura.")
        except Exception as e:
            self._message(e)
            return None


    """
    #################################################################
    Área dos nginx.conf
    #################################################################    
    """

    def _manage_nginx(self):
        """Método para configurar o nginx.
        """

        try:
            self._message("Trabalhando na configuração do nginx")
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/nginx.txt"))

            # Interpolando os dados
            content = content.replace("$subdominio$", self.subdominio_lower)
            content = content.replace("$projeto$", self.projeto_lower)

            # Verificando se o arquivo nginx.conf existe
            if self._check_file(self.path_nginx) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_nginx, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self._message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO nginx.py "
                          "sofreu alguma alteração: {}".format(e))

    """
        #################################################################
        Área dos Dockerfile
        #################################################################    
    """
    def _manage_dockerfile(self):
        """Método para configurar o Dockerfile.
        """

        try:
            self._message("Trabalhando na configuração do Dockerfile")
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/Dockerfile.txt"))

            # Interpolando os dados
            content = content.replace("$branch$", self.branch_lower)
            content = content.replace("$projeto$", self.projeto_lower)

            # Verificando se o arquivo Dockerfile existe
            if self._check_file(self.path_dockerfile) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_dockerfile, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self._message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO Dockerfile "
                          "sofreu alguma alteração: {}".format(e))

    """
    #################################################################
    Área do Jenkinsfile
    #################################################################    
    """

    def _manage_jenkisfile(self):
        """Método para configurar o Jenkinsfile.
        """

        try:
            self._message("Trabalhando na configuração do Jenkinsfile")
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/Jenkinsfile.txt"))

            # Interpolando os dados
            content = content.replace("$service_name$", self.service_name_lower)
            content = content.replace("$projeto$", self.projeto_lower)

            # Verificando se o arquivo Jenkinsfile existe
            if self._check_file(self.path_jenkinsfile) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_jenkinsfile, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self._message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO Jenkinsfile"
                          "sofreu alguma alteração: {}".format(e))

    """
    #################################################################
    Área do docker-compose
    #################################################################    
    """

    def _manage_docker_compose(self):
        """Método para configurar o docker-compose.yml.
        """

        try:
            self._message("Trabalhando na configuração do docker-compose.yml")
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/docker-compose.txt"))

            # Interpolando os dados
            content = content.replace("$subdominio$", self.subdominio_lower)
            content = content.replace("$projeto$", self.projeto_lower)
            content = content.replace("$service_name$", self.service_name_lower)

            # Verificando se o arquivo nginx.conf existe
            if self._check_file(self.path_docker_compose) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_docker_compose, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self._message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO "
                          "docker-compose.yml sofreu alguma alteração: "
                          "{}".format(e))

    """
    #################################################################
    Área do script run
    #################################################################    
    """

    def _manage_run(self):
        """Método para configurar o run.sh.
        """

        try:
            self._message("Trabalhando na configuração do run.sh")
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/deploy/run.txt"))

            # Interpolando os dados
            content = content.replace("$projeto$", self.projeto_lower)

            # Verificando se o arquivo nginx.conf existe
            if self._check_file(self.path_run) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_run, 'w') as arquivo:
                    arquivo.write(content)
                return

        except Exception as e:
            self._message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO run.sh "
                          "sofreu alguma alteração: {}".format(e))

    def handle(self, *args, **options):
        """Método invocado internamente pelo Command logo após a 
        validação da passagem de parâmetro.
        """

        # Verificando se o usuário passou o nome da app
        self._message("Gerando os arquivos do projeto para deploy")

        # Pegando a variavel projeto passada por parâmetro
        self.projeto = ''
        if options['projeto']:
            self.projeto = options['projeto']
            self.projeto_lower = self.projeto.lower()

        # Pegando a variavel subdominio passada por aparâmetro
        self.subdominio = ''
        if options['subdominio']:
            self.subdominio = options['subdominio']
            self.subdominio_lower = self.subdominio.lower()

        # Pegando a variavel branch passada por aparâmetro
        self.branch_lower = self.branch = 'master'
        if options['branch']:
            self.branch = options['branch']
            self.branch_lower = self.branch.lower()

        # Pegando a variavel service_name passada por aparâmetro
        self.service_name_lower = self.service_name = self.projeto_lower
        if options['service_name']:
            self.service_name = options['service_name']
            self.service_name_lower = self.service_name.lower()

        if (self._contain_number(self.projeto) is False):
            # Removendo os espaços em branco
            self.projeto = self.projeto.strip()

            # Pegando o diretório absoluto atual do projeto.
            self.path_root = os.getcwd()

            # Criando o path para a APP Core.
            self.path_core = os.path.join(self.path_root, "nuvols/core")

            # Criando o path para os forms baseado na App informada.
            self.path_nginx = os.path.join(self.path_root, "nginx.conf")
            self.path_dockerfile = os.path.join(self.path_root, "Dockerfile")
            self.path_jenkinsfile = os.path.join(self.path_root, "Jenkinsfile")
            self.path_run = os.path.join(self.path_root, "run.sh")
            self.path_docker_compose = os.path.join(self.path_root, "docker-compose.yml")
            self._manage_nginx()
            self._manage_dockerfile()
            self._manage_docker_compose()
            self._manage_jenkisfile()
            self._manage_run()

