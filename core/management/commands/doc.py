"""Manager gerar a documentação do projeto utilizando o Sphinx

python -m pip install Sphinx

"""

import os
from django.core.management.base import BaseCommand
from nuvols.core.settings import DOC_APPS

class Command(BaseCommand):
    help = "Manager para automatizar a geração dos códigos"

    def add_arguments(self, parser):
        """Método inicial para informar quais parâmetros serão aceitos
        """

        parser.add_argument('projeto', type=str)
        parser.add_argument('desenvolvedor', type=str)

    def __title(self, string):
        try:
            return string.replace('_', ' ').title()
        except:
            return string

    def __get_snippet(self, path):
        """Método para recuperar o texto a ser utilizado na
        configuração do novo elemento

        Arguments:
            path {str} -- Caminho absoluto para o arquivo

        Returns:
            str -- Texto a ser utilizado para interpolar os dados do models
        """

        try:
            if os.path.isfile(path):
                with open(path) as arquivo:
                    return arquivo.read()
            print("Arquivo não encontrado para captura.")
        except Exception as e:
            self.__message(f"Erro no get_snippet {e}")
            return None

    """
    #################################################################
    Área do docker-compose
    #################################################################    
    """

    def __message(self, message):
        """Método para retornar mensagems ao prompt(Terminal)

        Arguments:
            message {str} -- Mensagem a ser exibida
        """
        self.stdout.write(self.style.SUCCESS(message))

    def __parser_documentation(self):
        """Método para configurar o docker-compose.yml.
        """
        try:
            self.path_core = os.path.join(self.path_root, "nuvols/core")
            content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/config.txt"))

            # Interpolando os dados
            content = content.replace("$project$", self.projeto.lower())
            content = content.replace("$Project$", self.__title(self.projeto))
            content = content.replace("$Desenvolvedor$", self.desenvolvedor)

            # Criando o arquivo config.
            with open(f"{self.__docs_path}/source/conf.py", 'w') as arquivo:
                arquivo.write(content)

            # Criando o arquivo Makefile
            __make_content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/make.txt"))

            with open(f"{self.__docs_path}/Makefile", 'w') as arquivo:
                arquivo.write(__make_content)

            # Criando o arquivo make.bat
            __make_bat_content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/make_bat.txt"))

            with open(f"{self.__docs_path}/make.bat", 'w') as arquivo:
                arquivo.write(__make_bat_content)

            # Criando o arquivo modules.rst
            __modules_content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/modules.txt"))

            # Gerando todos os módulos
            __module_apps = ''
            for __app in DOC_APPS:
                __module_apps += f"   {__app}\n"

            __modules_content = __modules_content.replace("$App$", self.__title(self.projeto))
            __modules_content = __modules_content.replace("$Modules$", __module_apps)

            with open(f"{self.__docs_path}/source/modules.rst", 'w') as arquivo:
                arquivo.write(__modules_content)

            # Criando o arquivo index.rst
            __rst_content = self.__get_snippet(
                os.path.join(
                    self.path_core, 
                    "management/commands/snippets/sphinx_doc/index_rst.txt"
                )
            )

            with open(f"{self.__docs_path}/source/index.rst", "w") as arquivo:
                arquivo.write(__rst_content)

            # Criando os arquivos rst para gerar a documentação
            for app in DOC_APPS:
                __content = self.__get_snippet(
                    os.path.join(
                        self.path_core, 
                        "management/commands/snippets/sphinx_doc/rst.txt"
                    )
                )
                __content = __content.replace("$App$", app.title())
                __content = __content.replace("$app$", app)

                with open(f"{self.__docs_path}/source/{app.lower()}.rst", "w") as arquivo:
                    arquivo.write(__content)

            # Executando o comando make html no diretório doc
            os.system("make --directory=doc html")

        except Exception as e:
            self.__message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO "
                          "docker-compose.yml sofreu alguma alteração: "
                          "{}".format(e))

    def handle(self, *args, **options):
        """Método invocado internamente pelo Command logo após a 
        validação da passagem de parâmetro.
        """

        if DOC_APPS == []:
            self.__message("É obrigatório a configuração no settings do projeto das DOC_APPS")
            return

        self.projeto = options['projeto'] or None
        self.desenvolvedor = options['desenvolvedor'] or None
        __path = self.path_root = os.getcwd()

        # Verificando se o usuário passou o nome da app
        if self.projeto is not None and self.desenvolvedor is not None:
            try:
                # Criando o diretório do DOCS
                self.__docs_path = f"{__path}/doc"
                os.makedirs(self.__docs_path)
                os.makedirs(f"{self.__docs_path}/build")
                os.makedirs(f"{self.__docs_path}/source")
                os.makedirs(f"{self.__docs_path}/source/_templates")
                os.makedirs(f"{self.__docs_path}/source/_static")
            except:
                pass
            
            self.__parser_documentation()
