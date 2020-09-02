"""Manager to generate project documentation for the development team using the Sphinx package
"""

import os
import sys

from django.core.management.base import BaseCommand
from nuvols.core.settings import DOC_APPS


class Command(BaseCommand):
    help = """Manager responsible for generating documentation for the development team"""

    def __init__(self):
        super().__init__()
        self.projeto = None
        self.desenvolvedor = None
        self.path_root = os.getcwd()
        self.__docs_path = f"{self.path_root}/doc"

    def add_arguments(self, parser):
        parser.add_argument('projeto', type=str)
        parser.add_argument('desenvolvedor', type=str)

    @staticmethod
    def __title(string) -> str:
        try:
            string = string.replace('_', ' ').title()
        finally:
            return string

    def __get_snippet(self, path):
        """Method to retrieve the text to be used in
         new element configuration

         Arguments:
             path {str} - Absolute path to the file

         Returns:
             str - Text to be used to interpolate model data
        """

        try:
            if os.path.isfile(path):
                with open(path) as arquivo:
                    return arquivo.read()
            print("Arquivo não encontrado para captura.")
        except FileNotFoundError as e:
            self.__message(f"Erro no get_snippet {e}", error=True)

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

    def __parser_documentation(self):
        try:
            self.path_core = os.path.join(self.path_root, "nuvols/core")
            content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/config.txt"))

            content = content.replace("$project$", self.projeto.lower())
            content = content.replace("$Project$", self.__title(self.projeto))
            content = content.replace("$Desenvolvedor$", self.desenvolvedor)

            with open(f"{self.__docs_path}/source/conf.py", 'w') as arquivo:
                arquivo.write(content)

            __make_content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/make.txt"))

            with open(f"{self.__docs_path}/Makefile", 'w') as arquivo:
                arquivo.write(__make_content)

            __make_bat_content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/make_bat.txt"))

            with open(f"{self.__docs_path}/make.bat", 'w') as arquivo:
                arquivo.write(__make_bat_content)

            __modules_content = self.__get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/sphinx_doc/modules.txt"))

            __module_apps = ''
            for __app in DOC_APPS:
                __module_apps += f"   {__app}\n"

            __modules_content = __modules_content.replace("$App$", self.__title(self.projeto))
            __modules_content = __modules_content.replace("$Modules$", __module_apps)

            with open(f"{self.__docs_path}/source/modules.rst", 'w') as arquivo:
                arquivo.write(__modules_content)

            __rst_content = self.__get_snippet(
                os.path.join(self.path_core,
                             "management/commands/snippets/sphinx_doc/index_rst.txt")
            )

            with open(f"{self.__docs_path}/source/index.rst", "w") as arquivo:
                arquivo.write(__rst_content)

            for app in DOC_APPS:
                __content = self.__get_snippet(
                    os.path.join(self.path_core, "management/commands/snippets/sphinx_doc/rst.txt")
                )
                __content = __content.replace("$App$", app.title())
                __content = __content.replace("$app$", app)

                with open(f"{self.__docs_path}/source/{app.lower()}.rst", "w") as arquivo:
                    arquivo.write(__content)

            os.system("make --directory=doc html")

        except Exception as e:
            self.__message("OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO "
                           "docker-compose.yml sofreu alguma alteração: "
                           "{}".format(e))

    def handle(self, *args, **options):
        if not DOC_APPS:
            self.__message("É obrigatório a configuração no settings do projeto das DOC_APPS")
            return

        self.projeto = options['projeto'] or None
        self.desenvolvedor = options['desenvolvedor'] or None
        __path = self.path_root

        if self.projeto is not None and self.desenvolvedor is not None:
            try:
                os.makedirs(self.__docs_path)
                os.makedirs(f"{self.__docs_path}/build")
                os.makedirs(f"{self.__docs_path}/source")
                os.makedirs(f"{self.__docs_path}/source/_templates")
                os.makedirs(f"{self.__docs_path}/source/_static")
            except Exception as error:
                self.__message(f"Error in handle: {error}")
                pass
            
            self.__parser_documentation()
