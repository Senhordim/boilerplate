import os
import sys
import yaml
import time
import platform
import subprocess
from pathlib import Path
from django.apps import apps
from django.core.management.base import BaseCommand
from enum import Enum
from nuvols.core.models import Base
from nuvols.core.settings import FLUTTER_APPS, SYSTEM_NAME, API_PATH


class StateManager(Enum):
    Provider = 1
    MobX = 2
    Cubit = 3


class AppModel:
    """Classe auxiliar para encapsular os métodos de acesso 
    aos snippets e templates, bem como os método e funções recorrentes

    Arguments:
        path_flutter {String} -- Path do projeto Flutter
        app_name {String} -- Nome da App a ser mapeada

    Keyword Arguments:
        model_name {String} -- Nome do model a ser mapeado (default: {None})
    """

    def __init__(self, path_flutter, app_name, model_name=None):
        try:
            self.path_flutter = path_flutter
            self.models = None
            self.model = None
            self.app_name = str(app_name).strip()
            self.app_name_lower = self.app_name.lower()
            self.app = apps.get_app_config(self.app_name_lower)
            self.model_name = str(model_name).strip()
            self.model_name_lower = self.model_name.lower()
            if model_name is not None:
                self.model = self.app.get_model(self.model_name)
            else:
                self.models = ((x, x.__name__.strip(),
                                x.__name__.strip().lower()) for x in self.app.get_models())
            self.operation_system = platform.system().lower()

        except Exception as error:
            raise error

    def __message(self, message, error=False):
        """Método para retornar mensagems ao prompt(Terminal)

        Arguments:
            message {str} -- Mensagem a ser exibida
        """
        if error:
            sys.stdout.write(message)
            sys.exit()
        else:
            sys.stdout.write(message)

    def get_path_app_dir(self):
        """Método para retornar o path da app no projeto Flutter

        Returns:
            String -- Caminho do diretório da app no projeto Flutter
        """
        try:
            return Path("{}/lib/apps/{}".format(self.path_flutter, self.app_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_app_dir: {error}", error=True)

    def get_path_app_model_dir(self):
        """Método para retornar o path do model no projeto Flutter

        Returns:
            String -- Caminho do diretório do model no projeto Flutter
        """
        try:
            return Path("{}/lib/apps/{}/{}".format(self.path_flutter, self.app_name_lower, self.model_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_app_model_dir {error}", error=True)

    def get_path_views_dir(self):
        """Método para retornar o path do diretório views

        Returns:
            String -- Caminho do diretório views no projeto Flutter
        """
        try:
            return Path("{}/lib/apps/{}/{}/views/".format(self.path_flutter, self.app_name_lower,
                                                          self.model_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_views_dir {error}", error=True)

    def get_path_files_views(self):
        """Método para retornar os arquivos das páginas no projeto Flutter

        Returns:
            String's -- Caminho de cada arquivo das páginas na create, detail, index, list e update
        """
        try:
            # TODO 1: Modificar para pages
            __create = Path("{}/lib/apps/{}/{}/views/create.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
            __detail = Path("{}/lib/apps/{}/{}/views/detail.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
            __index = Path("{}/lib/apps/{}/{}/views/index.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
            __list = Path("{}/lib/apps/{}/{}/views/list.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))
            __update = Path("{}/lib/apps/{}/{}/views/update.dart".format(
                self.path_flutter, self.app_name_lower, self.model_name_lower))

            return __create, __detail, __index, __list, __update
        except Exception as error:
            self.__message(f"Erro no get_path_files_views: {error}", error=True)

    def get_path_data_file(self):
        """Método para recuperar o caminho do arquivo data.dart

        Returns:
            String -- Caminho do arquivo data.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/data.dart".format(self.path_flutter, self.app_name_lower,
                                                             self.model_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_data_file: {error}", error=True)

    def get_path_model_file(self):
        """Método para recuperar o caminho do arquivo model.dart

        Returns:
            String -- Caminho do arquivo model.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/model.dart".format(self.path_flutter, self.app_name_lower,
                                                              self.model_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_model_file {error}", error=True)

    def get_path_controller_file(self):
        """Método para recuperar o caminho para o arquivo controller.dart
        da app

        Returns:
            String -- Caminho do arquivo controller.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/controller.dart".format(self.path_flutter, self.app_name_lower,
                                                                   self.model_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_controller_file {error}", error=True)

    def get_path_provider_file(self):
        """Método para recuperar o caminho para o arquivo provider.dart
        da app

        Returns:
            String -- Caminho do arquivo controller.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/provider.dart".format(self.path_flutter, self.app_name_lower,
                                                                 self.model_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_provider_file {error}", error=True)

    def get_path_service_file(self):
        """Método para recuperar o caminho do arquivo service.dart

        Returns:
            String -- Caminho do arquivo service.dart
        """
        try:
            return Path("{}/lib/apps/{}/{}/service.dart".format(self.path_flutter, self.app_name_lower,
                                                                self.model_name_lower))
        except Exception as error:
            self.__message(f"Erro no get_path_service_file {error}", error=True)

    def print_string(self):
        """Método para imprimir o object
        """
        print("App: {} Name: {} - {}".format(
            self.app, self.app_name, self.app_name_lower))
        print("Model: {} Name: {} - {}".format(
            self.model, self.model_name, self.model_name_lower))
        print("")
        print("Caminhos:")
        print(f"Diretório App {self.get_path_app_dir()}")
        print(f"Diretório Model {self.get_path_app_model_dir()}")
        print(f"Diretório views {self.get_path_views_dir()}")
        print(f"Data {self.get_path_data_file()}")
        print(f"Model {self.get_path_model_file()}")
        print(f"Controller {self.get_path_controller_file()}")
        print(f"Service {self.get_path_service_file()}")
        c, d, i, l, u = self.get_path_files_views()
        print("")
        print("views \nCreate: {}\nDetail: {}\nIndex: {}\nList: {}\nUpdate: {}".format(
            c, d, i, l, u
        ))

        print("Models (Generator)")
        if self.models is not None:
            for __model in self.models:
                print("Model: {} Name: {} - {}".format(__model[0], __model[1], __model[2]))
        else:
            print("None")

    def check_inherited_base(self, model):
        """ Método para verificar se o model herda de Base

        Returns:
            Bool -- True se herdar e False se não herdar
        """
        try:
            __instance = apps.get_app_config(self.app_name_lower)
            __model = __instance.get_model(model)
            return issubclass(__model, Base)
        except Exception as error:
            self.__message(f"Erro ao executar o método check_inherited_base: {error}")
            return False

    def get_app_model_name(self, title_case=False):
        """Método para retornar uma String com o nome da App e do Model no formato
        NomeAppNomeModel.

        Arguments:
            title_case {Boolean} -- Determina se o return deve ser NomeAppNomeModel ou nomeAppNomeModel

        Returns:
            String -- String no formato NomeAppModel ou nomeAppModel
        """
        try:
            if title_case is True:
                return f"{self.app_name.title()}{self.model_name}"
            return f"{self.app_name}{self.model_name}"
        except Exception as error:
            self.__message(f"Erro ao executar o método get_app_model_name: {error}")
            return None


class Command(BaseCommand):
    help = "Manager para automatizar a geração do app em Flutter"

    def __init__(self):
        super().__init__()
        self.path_root = os.getcwd()
        self.path_core = os.path.join(self.BASE_DIR, "core")
        self.operation_system = platform.system().lower()
        self.state_manager = StateManager.Provider
        self.state_manager_provider = True

        _path_project = os.getcwd()

        if self.operation_system == 'windows':
            self.project = os.getcwd().split("\\")[-1:][0]
            self.flutter_dir = "{}\\Flutter\\{}".format("\\".join(os.getcwd().split("\\")[:-2]), self.project.lower())
            self.project = self.project.replace("-", "").replace("_", "")
            self.flutter_project = '{}'.format(self.project)
            self.utils_dir = "{}\\lib\\utils\\".format(self.flutter_dir)
            self.ui_dir = "{}\\lib\\user_interface\\".format(self.flutter_dir)
            self.config_file = "{}\\lib\\utils\\config.dart".format(self.flutter_dir)
            self.util_file = "{}\\lib\\utils\\util.dart".format(self.flutter_dir)
            self.process_controller_file = "{}\\lib\\utils\\process.controller.dart".format(self.flutter_dir)
            self.process_provider_file = "{}\\lib\\utils\\process.provider.dart".format(self.flutter_dir)
            self.snippet_dir = "{}\\{}".format(self.path_core, "management\\commands\\snippets\\flutter\\")

            # Criando o path da APP de configuração
            self.app_configuration = "{}\\lib\\apps\\configuracao\\".format(self.flutter_dir)
            self.app_configuration_page_file = f"{self.app_configuration}\\index.page.dart"
            self.app_configuration_controller_file = f"{self.app_configuration}\\controller.dart"
            self.app_configuration_profile_file = f"{self.app_configuration}\\model.dart"

        else:
            self.project = _path_project.split("/")[-1:][0]
            self.project = self.project.replace("-", "").replace("_", "")
            self.flutter_dir = "{}/Flutter/{}".format("/".join(_path_project.split("/")[:-2]), self.project.lower())

            # Concatenando o nome do projeto Django com o prefixo flutter
            self.flutter_project = '{}'.format(self.project)
            self.utils_dir = "{}/lib/utils/".format(self.flutter_dir)
            self.ui_dir = "{}/lib/user_interface/".format(self.flutter_dir)
            self.config_file = "{}/lib/utils/config.dart".format(self.flutter_dir)
            self.util_file = "{}/lib/utils/util.dart".format(self.flutter_dir)
            self.process_controller_file = "{}/lib/utils/process.controller.dart".format(self.flutter_dir)
            self.snippet_dir = "{}/{}".format(self.path_core, "management/commands/snippets/flutter/")

            # Criando o path da APP de configuração
            self.app_configuration = "{}/lib/apps/configuracao/".format(self.flutter_dir)
            self.app_configuration_page_file = f"{self.app_configuration}/index.page.dart"
            self.app_configuration_controller_file = f"{self.app_configuration}/controller.dart"

        self.current_app_model = None

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    _tipos_originais = ['SmallAutoField', 'AutoField', 'BLANK_CHOICE_DASH', 'BigAutoField', 'BigIntegerField',
                        'BinaryField', 'BooleanField', 'CharField', 'CommaSeparatedIntegerField',
                        'DateField', 'DateTimeField', 'DecimalField', 'DurationField', 'EmailField', 'Empty',
                        'FileField', 'Field', 'FieldDoesNotExist', 'FilePathField', 'FloatField',
                        'GenericIPAddressField', 'IPAddressField', 'IntegerField', 'FieldFile',
                        'NOT_PROVIDED', 'NullBooleanField', 'ImageField', 'PositiveIntegerField',
                        'PositiveSmallIntegerField', 'SlugField', 'SmallIntegerField', 'TextField',
                        'TimeField', 'URLField', 'UUIDField', 'ForeignKey', 'OneToOneField']

    _tipos_flutter = ['int', 'int', 'BLANK_CHOICE_DASH', 'int', 'int', 'String',
                      'bool', 'String', 'String', 'DateTime', 'DateTime',
                      'double', 'int', 'String', 'String', 'String', 'String',
                      'String', 'String', 'double', 'String', 'String', 'int',
                      'String', 'String', 'bool', 'String', 'int', 'int',
                      'String', 'int', 'String', 'DateTime', 'String',
                      'String', 'int', 'int']

    _tipos_sqlite = ['INT', 'INT', 'BLANK_CHOICE_DASH', 'BIGINT', 'BIGINT', 'TEXT',
                     'BOOLEAN', 'TEXT', 'TEXT', 'DATE', 'DATETIME', 'DOUBLE',
                     'INT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT',
                     'FLOAT', 'TEXT', 'TEXT', 'INT', 'TEXT', 'TEXT', 'BOOLEAN',
                     'TEXT', 'INT', 'INT', 'TEXT', 'SMALLINT', 'TEXT',
                     'DATETIME', 'TEXT', 'TEXT', 'INT', 'INT']

    def add_arguments(self, parser):
        """Método inicial para informar quais parâmetros serão aceitos
        """

        parser.add_argument('App', type=str, nargs='?')
        parser.add_argument('Model', type=str, nargs='?')

        parser.add_argument(
            '--app',
            action='store_true',
            dest='app',
            help='Criar a App e seus models'
        )
        parser.add_argument(
            '--app_model',
            action='store_true',
            dest='app_model',
            help='Criar a App e o Model informado'
        )
        parser.add_argument(
            '--main',
            action='store_true',
            dest='main',
            help='Renderizar a main.dart'
        )
        parser.add_argument(
            '--yaml',
            action='store_true',
            dest='yaml',
            help='Refatorando o YAML'
        )
        parser.add_argument(
            '--build_mobx',
            action='store_true',
            dest='build_mobx',
            help='Gerar os arquivos do MobX'
        )
        parser.add_argument(
            '--init_provider',
            action='store_true',
            dest='init_provider',
            help='Gerar o projeto Flutter utilizando o Provider como gerencia de estado.'
        )
        parser.add_argument(
            '--init_mobx',
            action='store_true',
            dest='init_mobx',
            help='Gerar o projeto Flutter utilizando o MobX como gerencia de estado.'
        )
        parser.add_argument(
            '--init_cubit',
            action='store_true',
            dest='init_mobx',
            help='Gerar o projeto Flutter utilizando o Cubit como gerencia de estado.'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help='Limpar projeto flutter.'
        )

    """
    #################################################################
    Área dos método internos
    #################################################################
    """

    def __contain_number(self, text):
        """Método para verificar se nome exixtem Número

        Arguments:
            text {String} -- Nome a ser testado

        Returns:
            Boolean -- True se existir algum número no text
        """
        try:
            return any(character.isdigit() for character in text)
        except Exception as error:
            self.__message(f"Ocorreu um erro no Contain Number: {error}", error=True)
            return False

    def __check_dir(self, path):
        """Método para verificar se o diretório existe

        Arguments:
            path {str} -- Caminho do diretório

        Returns:
            Boolean -- Verdadeiro se existir o diretório e Falso se não.
        """

        try:
            return os.path.isdir(path)
        except Exception as error:
            self.__message(f"Ocorreu um erro no Check Dir: {error}", error=True)
            return False

    def __ignore_base_fields(self, field):
        """Método para verificar se o campo deve ser ignorado no parser

        Arguments:
            field {String} -- Nome do campo

        Returns:
            Boolean -- True se for para ser ignorado.
        """
        try:
            __ignore_fields = ['id', 'enabled', 'deleted', 'createdOn', 'created_on', 'updatedOn', 'updatedOn']
            return field in __ignore_fields
        except Exception as error:
            self.__message(f"Ocorreu um erro ao validar os campos do Base: {error}", error=True)

    def __message(self, message, error=False):
        """Método para retornar mensagems ao prompt(Terminal)

        Arguments:
            message {str} -- Mensagem a ser exibida
        """
        if error:
            self.stdout.write(self.style.ERROR(message))
            sys.exit()
        else:
            self.stdout.write(self.style.SUCCESS(message))

    def __to_camel_case(self, text, flutter=False):
        """Método para convert a váriavel de snake_case para camelCase

        Arguments:
            str {str} -- String convertida
        """
        try:
            components = text.split('_')
            if flutter is True:
                if len(components) == 1:
                    __string = components[0]
                    return "{}{}".format(__string[:1].lower(), __string[1:])
                return components[0] + ''.join(x.title() for x in components[1:])
            return components[0] + ''.join(x.title() for x in components[1:])
        except Exception as error:
            self.__message(f"Ocorreu um erro no Camel Case: {error}")
            return None

    def __get_snippet(self, path=None, file_name=None, state_manager=False):
        """Método para recuperar o texto a ser utilizado na
        configuração do novo elemento

        Arguments:
            path {str} -- Caminho absoluto para o arquivo opcional,
                          deve ser passado quando o path do snippet é no diretório flutter mesmo
            file_name {str} -- Nome do arquivo do snippet no formato XPTO.txt, deve ser passado em conjunto
                               com o state_manager=True para recuperar o snippet do state manage correto
            state_manager {bool} -- Valor para determinar se o snippet será recuperado levando em consideração
                                    o state_manager escolhido

        Returns:
            str -- Texto a ser utilizado para interpolar os dados do models
        """

        try:
            if file_name and state_manager is True:
                if self.state_manager == StateManager.Provider:
                    path = f"{self.snippet_dir}provider/"
                if self.state_manager == StateManager.MobX:
                    path = f"{self.snippet_dir}mobx/"
                if self.state_manager == StateManager.Cubit:
                    path = f"{self.snippet_dir}cubit/"
                path += file_name

            if os.path.isfile(path):
                with open(path, encoding='utf-8') as arquivo:
                    return arquivo.read()
        except Exception as e:
            self.__message(f"Erro no get_snippet {e}", error=True)
            sys.exit()

    def __check_file(self, path):
        """Método para verificar se o arquivo existe

        Arguments:
            path {str} -- Caminho para o arquivo

        Returns:
            Boolean -- Verdadeiro se existir o arquivo e False se não.
        """

        try:
            return os.path.isfile(path)
        except Exception as e:
            self.__message(f"Erro no check_file {e}", error=True)
            sys.exit()

    def __check_content(self, path, text_check):
        """Método para verificar se determinado texto existe
        dentro de determinado arquivo

        Arguments:
            path {str} -- Caminho absoluto para o arquivo a ser analisado
            text_check {str} -- Texto a ser pesquisado dentro do arquivo informado

        Returns:
            Boolean -- Verdadeiro se o conteúdo for encontrado e False se não.
        """

        try:
            if self.__check_file(path):
                with open(path) as arquivo:
                    content = arquivo.read()
                    return text_check in content
            self.__message("Arquivo não encontrado para análise.")
        except Exception as e:
            self.__message(e)
            return False

    def __check_file_is_locked(self, path):
        """ Método para verificar se o arquivo está travado
        evitando assim que seja parseado novamente

        Arguments:
            path {str} -- Caminho absoluto para o arquivo a ser analisado

        Returns:
            Boolean -- Verdadeiro se contiver a palavra #FileLocked
        """
        try:
            if self.__check_file(path):
                with open(path, encoding='utf-8') as arquivo:
                    content = arquivo.read()
                    return "#FileLocked" in content
        except Exception as error:
            self.__message(f"Ocorreu erro ao verificar se o arquivo está travado: {error}", error=True)
            return True

    """
    #################################################################
    Área para Criar o projeto Flutter
    #################################################################
    """

    def __init_flutter(self):
        try:
            if not self.__check_dir(self.flutter_dir):
                self.__message("Criando o projeto flutter.")
                __cmd_flutter_create = "flutter create --androidx {}".format(
                    self.flutter_dir)
                subprocess.call(__cmd_flutter_create, shell=True)
                self.__message("Projeto criado com sucesso.")
        except Exception as error:
            self.__message(f"Erro ao executar o init do Flutter: {error}", error=True)

    def __build_flutter(self):
        """
        Método para quando o usuário criar o protejo flutter serem
        chamados os métodos __add_packages, __replace_main e __build_mobx
        """
        try:
            if self.__check_dir(self.flutter_dir):
                self.__message("Atualizando o arquivo de dependências.")
                self.__add_packages()
                time.sleep(3)

                current_path = os.getcwd()
                os.chdir(self.flutter_dir)
                subprocess.run("flutter pub get", shell=True)
                os.chdir(current_path)
                time.sleep(3)

                self.__message("Atualizando o arquivo main.dart.")
                self.__replace_main()
                time.sleep(3)

                # TODO 2: Refatorar para utilizar o Enum para saber qual StateManager está sendo utilizado
                if self.state_manager_provider:
                    print("Gerando com Provider")
                    pass
                else:
                    print("Gerando com MobX")
                    self.__message("Gerando os arquivos controller.g.dart do MobX")
                    self.__build_mobx()
        except Exception as error:
            self.__message(f"Erro ao executar o __build_flutter: {error}", error=True)

    """
    #################################################################
    Área para métodos assincronos
    #################################################################
    """

    def __build_menu_home_page_itens(self):
        try:
            __itens_menu = ""
            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)
                __app = __current_app.app_name
                for model in __current_app.models:
                    __model = model[1]
                    __itens_menu += f"list.add(Itens(title: '{__model.title()}',icon: FontAwesomeIcons.folderOpen,uri: {__app.title()}{__model.title()}Views.{__model.title()}ListPage(),),);"
            return __itens_menu
        except Exception as error:
            self.__message(f"Ocorreu o erro {error} ao chamar o __build_menu_home_page_itens", error=True)

    def __register_provider(self):
        __register_provider = ""
        __import_provider = ""
        try:
            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)
                __app = __current_app.app_name
                for model in __current_app.models:
                    __import_provider += f"import 'apps/{__app.lower()}/{model[1].lower()}/provider.dart';\n"
                    __register_provider += f"ChangeNotifierProvider<{model[1].title()}Provider>(create: (_) => {model[1].title()}Provider(),),\n"

            __import_provider += f"import 'apps/auth/provider.dart';\n"
            __register_provider += f"ChangeNotifierProvider<SettingsProvider>(create: (_) => SettingsProvider(),),\n"
            __register_provider += f"ChangeNotifierProvider<AuthProvider>(create: (_) => AuthProvider(),),\n"
        except Exception as error:
            self.__message(f"Ocorreu o erro {error} ao chamar o __register_provider", error=True)
        return __import_provider, __register_provider

    def __mapping_all_application(self):
        try:
            __imports_views = ""
            __imports_controllers = ""
            __controllers_models = ""
            __list_views = ""
            __current_app = None

            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)
                __app = __current_app.app_name
                for model in __current_app.models:
                    __model = model[1]
                    __imports_views += "import 'apps/{}/{}/views/list.dart' as {}Views;\n".format(
                        __app, __model.lower(
                        ), f"{__app.title()}{__model}"
                    )
                    __list_views += "Itens(title: '{}', icon: FontAwesomeIcons.folderOpen, uri: {}.{}ListPage()),\n".format(
                        model[0]._meta.verbose_name, f"{__app.title()}{__model}", __model
                    )
                    __imports_controllers += f"import 'apps/{__app.lower()}/{__model.lower()}/controller.dart' as {__app.title()}{__model.title()}Controller;\n"
                    __controller_model = f"{__app.title()}{__model.title()}Controller.{__model}"
                    __controllers_models += f"getIt.registerSingleton<{__controller_model}Controller>({__controller_model}Controller(), instanceName: '{__app.title()}{__model.title()}Controller');\n    "

            return __imports_views, __imports_controllers, __controllers_models, __list_views

        except Exception as error:
            self.__message(f"Ocorreu um erro no Mapping All Application: {error}", error=True)

    def __indexpage_parser(self, app):
        """Método para criar a página index do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            __indexpage_file = Path(f"{app.get_path_views_dir()}/index.dart")

            if self.__check_file_is_locked(__indexpage_file):
                return

            if self.state_manager_provider:
                content = self.__get_snippet(
                    f"{self.snippet_dir}index_page.provider.txt")
            else:
                content = self.__get_snippet(f"{self.snippet_dir}index_page.txt")
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$project$", self.flutter_project.lower())

            with open(__indexpage_file, 'w', encoding='utf-8') as page:
                page.write(content)

        except Exception as error:
            self.__message(f"Ocorreu um erro ao gerar a página da Index {error}", error=True)

    def __listpage_parser(self, app):
        """Método para criar a página de listagem do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            __listpage_file = Path(f"{app.get_path_views_dir()}/list.dart")

            if self.__check_file_is_locked(__listpage_file):
                return

            # TODO 2: Refatorar para utilizar o Enum para saber qual StateManager está sendo utilizado
            if self.state_manager_provider:
                content = self.__get_snippet(f"{self.snippet_dir}list_page.provider.txt")
            else:
                content = self.__get_snippet(f"{self.snippet_dir}list_page.txt")

            content = content.replace("$App$", app.app_name)
            content = content.replace("$Model$", app.model_name_lower)
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$project$", self.flutter_project)

            with open(__listpage_file, 'w', encoding='utf-8') as page:
                page.write(content)

        except Exception as error:
            self.__message(f"Ocorreu um erro ao gerar a página da Listagem {error}", error=True)

    def __get_attributes_data(self, attribute, model_name, name, name_title):
        """
        Método para recuperar a estrutura dos atributos dos field 
        para as páginas de create e update

        Arguments:
            attibute {String} -- String com o tipo de atributo a ser rederizado

        Returns:
            String  -- Estrutura do atribute data
        """

        __attribute = ''
        try:
            if attribute == 'int':
                if f"id{model_name.lower()}" == name.lower():
                    __attribute = '{0}_{1}.id = int.tryParse(_{1}Form{2}.text ?? 0);\n'.format(
                        ' ' * 16, self.__to_camel_case(model_name, True), name_title)
                else:
                    __attribute = '{0}_{1}.{2} = int.tryParse(_{1}Form{3}.text ?? 0);\n'.format(
                        ' ' * 16, self.__to_camel_case(model_name, True), name, name_title)

            elif attribute == 'double':
                __attribute = '{0}_{1}.{2} = double.tryParse(_{1}Form{3}.text ?? 0.0);\n'.format(
                    ' ' * 16, self.__to_camel_case(model_name, True), name, name_title)

            elif attribute == 'bool':
                __attribute = '{0}_{1}.{2} = _{1}Form{3}.text ?? true;\n'.format(
                    ' ' * 16, self.__to_camel_case(model_name, True), name, name_title)

            elif attribute == 'DateTime':
                __attribute = '{0}_{1}.{2} = _{1}Form{3}.text != "" ?Util.convertDate(_{1}Form{3}.text): null;\n'.format(
                    ' ' * 16, self.__to_camel_case(model_name, True), name, name_title)

            else:
                __attribute = '{0}_{1}.{2} = _{1}Form{3}.text ?? "";\n'.format(
                    ' ' * 16, self.__to_camel_case(model_name, True), name, name_title)
        except Exception as error:
            self.__message(f"Ocorreu um erro ao executar o __get_attributes: {error}", error=True)
        finally:
            return __attribute

    def __get_controllers_data(self, attribute, model_name, name, name_title):
        """Método para construir a linha de comando responsável por recuperar os valores
        dos controller

        Arguments:
            attribute {String} -- String contendo o tipo do atributo que está sendo parseado

        Returns:
            String -- Linha contendo o comando dart para recuperar o valor do controller
        """
        __controllers_data = ''
        try:
            if attribute == 'int':
                if f"id{model_name.lower()}" == name.lower():
                    __controllers_data = '{0}_{1}.id = int.tryParse(_{1}Form{2}.text ?? 0);\n'.format(
                        ' ' * 6, self.__to_camel_case(model_name, True), name_title)
                else:
                    __controllers_data = '{0}_{1}.{2} = int.tryParse(_{1}Form{3}.text ?? 0);\n'.format(
                        ' ' * 6, self.__to_camel_case(model_name, True), name, name_title)
            elif attribute == 'double':
                __controllers_data = '{0}_{1}.{2} = double.tryParse(_{1}Form{3}.text ?? 0.0);\n'.format(
                    ' ' * 6, self.__to_camel_case(model_name, True), name, name_title
                )
            elif attribute == 'bool':
                __controllers_data = '{0}_{1}.{2} = _{1}Form{3}.text ?? true;\n'.format(
                    ' ' * 6, self.__to_camel_case(model_name, True), name, name_title)
            elif attribute == 'DateTime':
                __controllers_data = '{0}_{1}.{2} = _{1}Form{3}.text != ""? Util.convertDate(_{1}Form{3}.text) : null;\n'.format(
                    ' ' * 6, self.__to_camel_case(model_name, True), name, name_title)
            else:
                __controllers_data = '{0}_{1}.{2} = _{1}Form{3}.text;\n'.format(
                    ' ' * 6, self.__to_camel_case(model_name, True), name, name_title)
        except Exception as error:
            self.__message(f"Ocorreu um erro ao executar o __get_controller_data: {error}", error=True)
        finally:
            return __controllers_data

    def __create_update_page_parser(self, app, createpage=True):
        try:
            if createpage is True:
                __createpage_file = Path(f"{app.get_path_views_dir()}/create.dart")
                # TODO 2: Refatorar para utilizar o Enum para saber qual StateManager está sendo utilizado
                if self.state_manager_provider:
                    content = self.__get_snippet(f"{self.snippet_dir}create_page.provider.txt")
                else:
                    content = self.__get_snippet(f"{self.snippet_dir}create_page.txt")

                if self.__check_file_is_locked(__createpage_file):
                    return
            else:
                __createpage_file = Path(f"{app.get_path_views_dir()}/update.dart")
                # TODO 2: Refatorar para utilizar o Enum para saber qual StateManager está sendo utilizado
                if self.state_manager_provider:
                    content = self.__get_snippet("{self.snippet_dir}update_page.provider.txt")
                else:
                    content = self.__get_snippet(f"{self.snippet_dir}update_page.txt")

                if self.__check_file_is_locked(__createpage_file):
                    return

            content_form = self.__get_snippet(f"{self.snippet_dir}text_field.txt")

            content_attributes = ""
            text_fiels = ""
            attributes_data = ""
            clear_data = ""
            edited_attributes = ""
            get_controllers_data = ""

            for field in iter(app.model._meta.fields):
                __app, __model, __name = str(field).split('.')
                __nameTitle = self.__to_camel_case(__name.title())
                __name = self.__to_camel_case(__name.lower())

                if self.__ignore_base_fields(__name):
                    continue

                field_type = (str(str(type(field)).split('.')[-1:]).replace("[\"", "").replace("\'>\"]", ""))
                attribute = self._tipos_flutter[self._tipos_originais.index(field_type)]
                content_attributes += '  final _{0}Form{1} = TextEditingController();\n'.format(
                    self.__to_camel_case(app.model_name, True), __nameTitle)
                text_field = content_form
                controller = '_{}Form{}'.format(self.__to_camel_case(app.model_name, True), __nameTitle)
                text_field = text_field.replace("$controller$", controller)
                text_field = text_field.replace("$Field$", str(field.verbose_name).replace("R$", "R\$"))
                text_fiels += text_field

                attributes_data += self.__get_attributes_data(attribute, app.model_name, __name, __nameTitle)

                get_controllers_data += self.__get_controllers_data(attribute, app.model_name, __name, __nameTitle)

                clear_data += '    {}.clear();\n'.format(controller)

                if __name.startswith(f"id{app.model_name_lower}"):
                    __name = "id"

                edited_attributes += '      {}.text = _{}.{}.toString();\n'.format(
                    controller, self.__to_camel_case(app.model_name, True), __name)

            content = content.replace("$app$", app.app_name_lower)
            content = content.replace("$App$", app.app_name_lower)
            content = content.replace("$Model$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$model$", app.model_name_lower)
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$project$", self.flutter_project)
            content = content.replace("$Attributes$", content_attributes)
            content = content.replace("$Form$", text_fiels)
            content = content.replace("$AttributesData$", attributes_data)
            content = content.replace("$ClearData$", clear_data)
            content = content.replace("$EditedAttributes$", edited_attributes)
            content = content.replace("$GetValuesControllers$", get_controllers_data)

            with open(__createpage_file, 'w', encoding='utf-8') as page:
                page.write(content)

        except Exception as error:
            self.__message(
                f"Ocorreu um erro ao gerar a página da Create {error}", error=True)

    def __detailpage_parser(self, app):
        """Método para criar a página de detalhamento do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            __detailpage_file = Path(f"{app.get_path_views_dir()}/detail.dart")

            if self.__check_file_is_locked(__detailpage_file):
                return
            # TODO 2:
            if self.state_manager_provider:
                content = self.__get_snippet(f"{self.snippet_dir}detail_page.provider.txt")
            else:
                content = self.__get_snippet(f"{self.snippet_dir}detail_page.txt")
            content = content.replace("$App$", app.app_name)
            content = content.replace("$app$", app.app_name_lower)
            content = content.replace("$Model$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$model$", app.model_name_lower)
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$project$", self.flutter_project)

            with open(__detailpage_file, 'w', encoding='utf-8') as page:
                page.write(content)

        except Exception as error:
            self.__message(f"Ocorreu um erro ao gerar a página da Detail {error}", error=True)

    def __widget_parser(self, app):
        """Método para criar o widget do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            __widget_file = Path(f"{app.get_path_views_dir()}/widget.dart")

            if self.__check_file_is_locked(__widget_file):
                return

            content = self.__get_snippet(f"{self.snippet_dir}widget.txt")
            content = content.replace("$ModelClass$", app.model_name)

            with open(__widget_file, 'w', encoding='utf-8') as page:
                page.write(content)

        except Exception as error:
            self.__message(f"Ocorreu um erro ao gerar a página da Widget {error}", error=True)

    def __create_auth_application(self):
        """Método responsável por criar a app padrão de autenticação no projeto flutter

        Args:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            __data_snippet = self.__get_snippet(f"{self.snippet_dir}auth_data.txt")
            __model_snippet = self.__get_snippet(f"{self.snippet_dir}auth_model.txt")

            __auth_file = Path(f"{self.flutter_dir}/lib/apps/auth")
            if self.__check_dir(__auth_file):
                return None
            os.makedirs(__auth_file)

            __data_file = Path("{}/lib/apps/auth/data.dart".format(self.flutter_dir))
            __model_file = Path("{}/lib/apps/auth/model.dart".format(self.flutter_dir))
            __service_file = Path("{}/lib/apps/auth/service.dart".format(self.flutter_dir))

            with open(__data_file, 'w', encoding='utf-8') as data_file:
                data_file.write(__data_snippet)

            with open(__model_file, 'w', encoding='utf-8') as model_file:
                model_file.write(__model_snippet)

            if self.state_manager_provider:
                __snippet = self.__get_snippet(f"{self.snippet_dir}auth.provider.txt")
                __file = Path("{}/lib/apps/auth/provider.dart".format(self.flutter_dir))
                with open(__file, 'w', encoding='utf-8') as provider_file:
                    provider_file.write(__snippet)
                __service_snippet = self.__get_snippet(f"{self.snippet_dir}auth_service.provider.txt")
            else:
                __controller_snippet = self.__get_snippet(f"{self.snippet_dir}auth_controller.txt")
                __controller_file = Path("{}/lib/apps/auth/controller.dart".format(self.flutter_dir))
                with open(__controller_file, 'w', encoding='utf-8') as controller_file:
                    controller_file.write(__controller_snippet)
                __service_snippet = self.__get_snippet(f"{self.snippet_dir}auth_service.txt")

            with open(__service_file, 'w', encoding='utf-8') as service_file:
                service_file.write(__service_snippet)

        except Exception as error:
            self.__message(f"Ocorreu um erro ao gerar a app de autentição {error}", error=True)

    def __data_parser(self, app):
        """Método responsável por criar o arquivo de data baseado na App e no Models

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            __data_file = app.get_path_data_file()

            content = self.__get_snippet(f"{self.snippet_dir}data.txt")

            if self.__check_file_is_locked(__data_file):
                return

            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$modelClass$", app.model_name_lower)
            content = content.replace("$project$", self.flutter_project)

            with open(__data_file, 'w', encoding='utf-8') as data_helper:
                data_helper.write(content)

        except Exception as error:
            self.__message(f"Ocorreu um erro ao criar o DBHelper {error}", error=True)

    def __http_dio_request(self):
        """Método para criar a classe auxiliar de acesso HTTP
        """
        try:

            __dio_file = Path(f"{self.flutter_dir}/lib/utils/custom_dio.dart")
            content = self.__get_snippet(f"{self.snippet_dir}/custom_dio.txt")
            content = content.replace("$project$", self.flutter_project)
            with open(__dio_file, 'w', encoding='utf-8') as http_request:
                http_request.write(content)
        except Exception as error:
            self.__message(f"Ocorreu um erro ao criar o Dio Request {error}", error=True)

    def __controller_parser(self, app):
        """Método responsável por criar o arquivo controller do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            if app.model is None:
                return

            __controller_file = app.get_path_controller_file()

            if self.__check_file_is_locked(__controller_file):
                return

            content = self.__get_snippet(f"{self.snippet_dir}controller.txt")
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))

            if not self.__check_file(__controller_file):
                os.makedirs(__controller_file)

            with open(__controller_file, 'w', encoding='utf-8') as controller_file:
                controller_file.write(content)

        except Exception as error:
            self.__message(f"Erro ao executar o controller parser {error}", error=True)

    def __provider_parser(self, app):
        """Método responsável por criar o arquivo provider do Model

        Args:
            app {AppModel} -- Instância da class AppModel
        """
        try:
            if app.model is None:
                print("Informe o App")
                return
            __file = app.get_path_provider_file()

            if self.__check_file_is_locked(__file):
                print("Arquivo travado")
                return

            content = self.__get_snippet(f"{self.snippet_dir}provider.txt")
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))

            with open(__file, 'w', encoding='utf-8') as fileProvider:
                fileProvider.write(content)

        except Exception as error:
            self.__message(f"Erro ao executar o __provider_parser: {error}", error=True)

    def __service_parser(self, app):
        """Método responsável por criar o arquivo de service do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            if app.model is None:
                return

            __service_file = app.get_path_service_file()

            if self.__check_file_is_locked(__service_file):
                return

            # TODO 2:
            if self.state_manager_provider:
                content = self.__get_snippet(f"{self.snippet_dir}service.provider.txt")
            else:
                content = self.__get_snippet(f"{self.snippet_dir}service.txt")

            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$App$", app.app_name_lower)
            content = content.replace("$Model$", app.model_name_lower)
            content = content.replace("$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$project$", self.flutter_project)

            if not self.__check_file(__service_file):
                os.makedirs(__service_file)

            with open(__service_file, 'w', encoding='utf-8') as service_file:
                service_file.write(content)

        except Exception as error:
            self.__message(f"Erro no parser do service: {error}", error=True)

    def __model_parser(self, app):
        """ Método responsável por criar a classe de modelo do Model
        """
        try:
            if app.model is None:
                return

            content = self.__get_snippet(f"{self.snippet_dir}model.txt")
            content_atributes = ""
            content_string_return = ""
            content_from_json = ""
            content_to_map = ""
            content_constructor = ""

            __model_file = app.get_path_model_file()

            if self.__check_file_is_locked(__model_file):
                return

            for field in iter(app.model._meta.fields):
                __app, __model, __name = str(field).split('.')
                __name_dart = self.__to_camel_case(__name)

                if __name_dart in [f"id{app.model_name_lower}", "id"]:
                    continue

                field_type = (str(str(type(field)).split('.')[-1:])
                              .replace("[\"", "").replace("\'>\"]", ""))
                attribute = self._tipos_flutter[self._tipos_originais.index(field_type)]

                content_atributes += "{} {};\n  ".format(attribute, __name_dart)
                content_string_return += "{}: ${}\\n".format(__name_dart.upper(), __name_dart)

                content_constructor += "this.{},\n".format(__name_dart)

                if str(attribute) == "DateTime":
                    content_from_json += "{1} = Util.convertDate(json['{2}']) == null ? null:  Util.convertDate(json['{2}']);\n        ".format(
                        __model.lower(), __name_dart, __name)
                elif str(attribute) == "double":
                    content_from_json += "{1} = json['{2}'] == null ? null : double.parse(json['{2}']) ;\n        ".format(
                        __model.lower(), __name_dart, __name)
                elif str(attribute) == "bool":
                    if __name_dart.lower() == "enabled":
                        content_from_json += "{1} = json['{2}'] == null ? true : json['{2}'] ;\n        ".format(
                            __model.lower(), __name_dart, __name)
                    elif __name_dart.lower() == "deleted":
                        content_from_json += "{1} = json['{2}'] == null ? false : json['{2}'];\n        ".format(
                            __model.lower(), __name_dart, __name)
                    else:
                        content_from_json += "{1} = json['{2}'] == null ? true : json['{2}'];\n        ".format(
                            __model.lower(), __name_dart, __name)
                else:
                    if __name_dart.startswith("fk"):
                        content_from_json += "{1} = json['{2}'] == null ? 0 : json['{2}'];\n        ".format(
                            __model.lower(), __name_dart, __name)
                    else:
                        content_from_json += "{1} = json['{2}'] == null ? \"\" : json['{2}'];\n        ".format(
                            __model.lower(), __name_dart, __name)

                if str(field_type) == "DateTimeField":
                    if __name_dart in ('createdOn', 'updatedOn'):
                        content_to_map += "'{0}': this.{1}.toString(),\n        ".format(
                            __name, __name_dart)
                    else:
                        content_to_map += '\'{0}\': this.{1} != null? Util.stringDateTimeSplit(this.{1}, returnType: "dt"): null, \n'.format(
                            __name, __name_dart)
                    continue
                if str(field_type) == "DateField":
                    content_to_map += '\'{0}\': this.{1} != null ?Util.stringDateTimeSplit(this.{1}, returnType: "d"): null, \n'.format(
                        __name, __name_dart)
                    continue
                if str(field_type) == "TimeField":
                    content_to_map += '\'{0}\': this.{1} != null ?Util.stringDateTimeSplit(this.{1}, returnType: "t"): null, \n'.format(
                        __name, __name_dart)
                    continue
                if str(attribute) == "bool":
                    if __name_dart.lower() == "enabled":
                        content_to_map += "'{0}': this.{1} != null? this.{1}: true,\n        ".format(
                            __name, __name_dart)
                    elif __name_dart.lower() == "deleted":
                        content_to_map += "'{0}': this.{1} != null? this.{1}: false,\n        ".format(
                            __name, __name_dart)
                    else:
                        content_to_map += "'{0}': this.{1} != null? this.{1}: true,\n        ".format(
                            __name, __name_dart)
                    continue
                content_to_map += "'{0}': this.{1} != null? this.{1}: \"\",\n        ".format(
                    __name, __name_dart)

            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$AttributeClass$", content_atributes)
            content = content.replace("$StringReturn$", content_string_return)
            content = content.replace("$Model$", app.model_name_lower)
            content = content.replace("$ParserFromJson$", content_from_json)
            content = content.replace("$ParserToMap$", content_to_map)
            content = content.replace("$project$", self.flutter_project)
            content = content.replace("$ConstructorModelClass$", content_constructor)

            if not self.__check_file(__model_file):
                os.makedirs(__model_file)

            with open(__model_file, 'w', encoding='utf-8') as model_file:
                model_file.write(content)

        except Exception as error:
            self.__message(f"Erro ao realizar o parser do model: {error}", error=True)


    """
    #################################################################
    Área para gerar os códigos do MobX
    #################################################################
    """

    def __build_mobx(self):
        """
        Método para executar o comando de geração dos códigos do MobX
        """
        try:
            if self.state_manager_provider:
                return
            if self.__check_dir(self.flutter_dir):
                current_path = os.getcwd()
                os.chdir(self.flutter_dir)
                subprocess.run("flutter pub run build_runner build", shell=True)
                os.chdir(current_path)
                time.sleep(3)
        except Exception as error:
            self.__message(f"Erro ao realizar o build mobx: {error}", error=True)

    def __build_settings_controller(self):
        """
        Método para gerar o controller e a página de configuração da APP.
        """
        try:
            if not self.__check_dir(self.app_configuration):
                os.makedirs(self.app_configuration)

                _content_page = self.__get_snippet(file_name="settings_page.txt", state_manager=True)
                _content_controller = self.__get_snippet(file_name="settings.txt", state_manager=True)
                if self.state_manager == StateManager.Provider:
                    with open(self.app_configuration_profile_file, 'w', encoding='utf-8') as arquivo:
                        arquivo.write(_content_controller)

                elif self.state_manager ==StateManager.MobX:
                    with open(self.app_configuration_controller_file, 'w', encoding='utf-8') as arquivo:
                        arquivo.write(_content_controller)
                elif self.state_manager == StateManager.Cubit:
                    # TODO Cubit: Implementar settings para
                    pass

                with open(self.app_configuration_page_file, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(_content_page)

        except Exception as error:
            self.__message(f"Erro ao executar o __build_settings_controller: {error}", error=True)

    """
    #################################################################
    Área para adicionar os pacotes no puspec.yaml
    #################################################################
    """

    def __get_yaml_file(self):
        try:
            # TODO: Tentar recuperar o arquivo sem precisar verificar o S.O.
            if self.operation_system == 'windows':
                return f"{self.flutter_dir}\\pubspec.yaml"
            else:
                return f"{self.flutter_dir}/pubspec.yaml"
        except Exception as error:
            self.__message(f"Ocorreu um erro ao recuperar o arquivo Yaml:{error}", error=True)

    def __add_packages(self):
        """
        Método assincrono para alterar os pacotes do projeto
        """
        try:
            __path = self.__get_yaml_file()

            # TODO 2:
            if self.state_manager_provider:
                snippet = self.__get_snippet(f"{self.snippet_dir}yaml.provider.txt")
            else:
                snippet = self.__get_snippet(f"{self.snippet_dir}yaml.txt")

            snippet = snippet.replace("$AppPackage$", self.project.lower())
            snippet = snippet.replace("$AppDescription$", f"Projeto Flutter do sistema Django {self.project}")
            with open(__path, 'w', encoding='utf-8') as yaml_file:
                yaml_file.write(snippet)

        except Exception as error:
            self.__message(f"Erro ao adicionar os pacotes: {error}", error=True)

    """
    #################################################################
    Área para Criar os arquivos auxiliares do projeto
    #################################################################
    """

    def __create_utils(self):
        """
        Método para criar os arquivos úteis do projeto
        """
        try:
            if not self.__check_dir(self.utils_dir):
                os.makedirs(self.utils_dir)

            __config_snippet = self.__get_snippet(f"{self.snippet_dir}config.txt")

            __util_snippet = self.__get_snippet(f"{self.snippet_dir}util.txt")

            __controller_snippet = self.__get_snippet(file_name="process.txt", state_manager=True)

            if self.__check_file(self.config_file) is False:
                __config_snippet = __config_snippet.replace("$AppName$", SYSTEM_NAME)
                __config_snippet = __config_snippet.replace("$DjangoAPIPath$", API_PATH)
                with open(self.config_file, "w", encoding='utf-8') as config:
                    config.write(__config_snippet)
            else:
                if self.__check_file_is_locked(self.config_file) is False:
                    __config_snippet = __config_snippet.replace("$AppName$", SYSTEM_NAME)
                    __config_snippet = __config_snippet.replace("$DjangoAPIPath$", API_PATH)
                    with open(self.config_file, "w", encoding='utf-8') as config:
                        config.write(__config_snippet)

            if self.__check_file(self.util_file) is False:
                with open(self.util_file, "w", encoding='utf-8') as config:
                    config.write(__util_snippet)
            else:
                if self.__check_file_is_locked(self.util_file) is False:
                    with open(self.util_file, "w", encoding='utf-8') as config:
                        config.write(__util_snippet)

            if self.state_manager == StateManager.Provider:
                if self.__check_file(self.process_provider_file) is False:
                    with open(self.process_provider_file, "w", encoding='utf-8') as process_provider:
                        process_provider.write(__controller_snippet)
                else:
                    if self.__check_file_is_locked(self.process_provider_file) is False:
                        with open(self.process_provider_file, "w", encoding='utf-8') as process_provider:
                            process_provider.write(__controller_snippet)
            elif self.state_manager == StateManager.MobX:
                if self.__check_file(self.process_controller_file) is False:
                    with open(self.process_controller_file, "w", encoding='utf-8') as process_controller:
                        process_controller.write(__controller_snippet)
                else:
                    if self.__check_file_is_locked(self.process_controller_file) is False:
                        with open(self.process_controller_file, "w", encoding='utf-8') as process_controller:
                            process_controller.write(__controller_snippet)
            elif self.state_manager == StateManager.Cubit:
                pass

        except Exception as error:
            self.__message(f"Erro ao criar o arquivo utils {error}", error=True)

    """
    #################################################################
    Área para Criar a estrutura de diretórios
    #################################################################
    """

    def __create_user_interface_directories(self):
        """Método para criar a estrutura de diretórios UI
        """
        try:
            if not self.__check_dir(self.ui_dir):
                os.makedirs(self.ui_dir)

            for arquivo in ['widget', 'font']:
                __path = Path(f"{self.ui_dir}{arquivo}.dart")
                if arquivo == "font":
                    __snippet = self.__get_snippet(Path(f"{self.snippet_dir}ui_{ arquivo}.txt"))
                else:
                    __snippet = self.__get_snippet(file_name="ui_widget.txt", state_manager=True)
                if self.__check_file(__path) is False:
                    with open(__path, "w", encoding='utf-8') as arq:
                        arq.write(__snippet)
                else:
                    if self.__check_file_is_locked(__path) is False:
                        with open(__path, "w", encoding='utf-8') as arq:
                            arq.write(__snippet)

        except Exception as error:
            self.__message(f"Erro ao criar a estrutura de arquivos da UI {error}", error=True)

    def __create_source_from_model(self):
        """Método para criar as apps quando a App e Model forem informados
        """
        self.__message("Criando as apps baseado na App e no Model")
        try:
            self.__create_source(
                self.current_app_model.app_name,
                self.current_app_model.model_name
            )
        except Exception as error:
            self.__message(f"Erro ao executar o Create App From Model: {error}", error=True)

    def __create_source_from_generators(self):
        """
        Método para criar as apps quando apenas a App for informada
        """
        self.__message("Criando as apps baseado na App e nos Generators")
        try:
            for model in self.current_app_model.models:
                self.__create_source(self.current_app_model.app_name, model[1])
        except Exception as error:
            self.__message(f"Erro ao executar o Create Apps From Generators: {error}", error=True)

    def __create_source(self, app_name, model_name):
        """
        Método para criar a estrutura de diretórios da App/Models
        """
        try:
            if app_name is None:
                self.__message("É necessário passar a App")
                return

            if model_name is None:
                self.__message(f"É necessário passar o Model")
                return

            __source_class = AppModel(self.flutter_dir, app_name, model_name)

            __app_name = __source_class.app_name
            __model_name = __source_class.model_name
            __model = __source_class.model

            __model_dir = __source_class.get_path_app_model_dir()
            __views_dir = __source_class.get_path_views_dir()
            __data_file = __source_class.get_path_data_file()
            __model_file = __source_class.get_path_model_file()
            __service_file = __source_class.get_path_service_file()
            __controller_file = __source_class.get_path_controller_file()
            __provider_file = __source_class.get_path_provider_file()

            __views = __source_class.get_path_files_views()

            if not self.__check_dir(__model_dir):
                self.__message(f"Criando diretório source do {__app_name}.{__model_name}")
                os.makedirs(__model_dir)

            if not self.__check_dir(__views_dir):
                os.makedirs(__views_dir)

                if __views is not None:
                    with open(__views[0], 'w', encoding='utf-8') as pagina:
                        pagina.write(f"// Create Page {__app_name} {__model_name}")

                    with open(__views[1], 'w', encoding='utf-8') as pagina:
                        pagina.write(f"// Detail Page {__app_name} {__model_name}")

                    with open(__views[2], 'w', encoding='utf-8') as pagina:
                        pagina.write(f"// Index Page {__app_name} {__model_name}")

                    with open(__views[3], 'w', encoding='utf-8') as pagina:
                        pagina.write(f"// List Page {__app_name} {__model_name}")

                    with open(__views[4], 'w', encoding='utf-8') as pagina:
                        pagina.write(f"// Update Page {__app_name} {__model_name}")

            if not self.__check_file(__model_file):
                with open(__model_file, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(f"// Modelo do {__model_name}")

            if not self.__check_file(__data_file):
                with open(__data_file, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(f"// Persistência do {__model_name}")

            if not self.__check_file(__service_file):
                with open(__service_file, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(f"// Service do {__model_name}")

            if self.state_manager_provider:
                if not self.__check_file(__provider_file):
                    with open(__provider_file, 'w', encoding='utf-8') as arquivo:
                        arquivo.write(f"// Provider do {__model_name}")
            else:
                if not self.__check_file(__controller_file):
                    with open(__controller_file, 'w', encoding='utf-8') as arquivo:
                        arquivo.write(f"// Controller do {__model_name}")

            self.__create_update_page_parser(__source_class)
            self.__detailpage_parser(__source_class)
            self.__indexpage_parser(__source_class)
            self.__listpage_parser(__source_class)
            self.__widget_parser(__source_class)
            self.__create_update_page_parser(__source_class, False)
            self.__model_parser(__source_class)
            self.__data_parser(__source_class)
            self.__service_parser(__source_class)

            if self.state_manager_provider:
                self.__provider_parser(__source_class)
            else:
                self.__controller_parser(__source_class)

        except Exception as error:
            self.__message(f"Error ao executar source. \n {error}", error=True)

    """
    #################################################################
    Área para criar o localizations.dart, responsável por implementar
    internacionalização.
    #################################################################
    """

    def __localization_app(self):
        try:
            snippet = self.__get_snippet(f"{self.snippet_dir}localization.txt")

            path_localization = os.path.join(self.utils_dir, 'localization.dart')

            if self.__check_file_is_locked(path_localization):
                return

            with open(path_localization, 'w', encoding='utf-8') as localizations:
                localizations.write(snippet)

            __lang_dir = Path(f"{self.flutter_dir}/lang")
            __pt_br = Path(f"{self.flutter_dir}/lang/pt.json")
            __en_us = Path(f"{self.flutter_dir}/lang/en.json")

            if not self.__check_dir(__lang_dir):
                os.makedirs(__lang_dir)

            if not self.__check_file(__pt_br):
                snippet = self.__get_snippet(f"{self.snippet_dir}pt_language.txt")
                with open(__pt_br, 'w', encoding='utf-8') as pt_json:
                    pt_json.write(snippet)

            if not self.__check_file(__en_us):
                snippet = self.__get_snippet(f"{self.snippet_dir}en_language.txt")
                with open(__en_us, 'w', encoding='utf-8') as en_json:
                    en_json.write(snippet)

        except Exception as error:
            self.__message(f"Erro ao executar o localizations app. \n {error}", error=True)

    """
    #################################################################
    Área para alterar o Main.dart
    #################################################################
    """

    def __replace_main(self):
        """
        Método para atualizar o main conforme o Snippet
        """
        __imports = ""
        __list_itens = []
        try:
            # TODO 2
            if self.state_manager_provider:
                snippet = self.__get_snippet(f"{self.snippet_dir}main.provider.txt")
            else:
                snippet = self.__get_snippet(f"{self.snippet_dir}main.txt")

            path_maindart = Path(f"{self.flutter_dir}/lib/main.dart")
            if self.__check_file_is_locked(path_maindart):
                return

            __import_views, __import_controllers, __register_controller, __views = self.__mapping_all_application()

            __import_controllers += f"import 'apps/configuracao/model.dart';"
            __import_views += f"import 'apps/configuracao/index.page.dart';\n"
            __register_controller += "getIt.registerSingleton<SettingsController>(SettingsController());"

            if __import_views is None or __import_controllers is None:
                return

            snippet = snippet.replace('$project$', self.flutter_project)
            snippet = snippet.replace('$RegisterControllers$', __register_controller)
            snippet = snippet.replace('$ImportViews$', __import_views)
            # TODO 2:
            if self.state_manager_provider:
                __import, __register = self.__register_provider()
                snippet = snippet.replace('$ImportProvider$', __import)
                snippet = snippet.replace('$RegisterProviders$', __register)
            else:
                snippet = snippet.replace('$ImportController$', __import_controllers)
            snippet = snippet.replace('$Listviews$', __views)

            with open(path_maindart, 'w', encoding='utf-8') as main_dart:
                main_dart.write(snippet)

            path_homepage = Path(f"{self.flutter_dir}/lib/home.page.dart")
            if self.__check_file_is_locked(path_homepage):
                return
            __snippet_page = self.__get_snippet(
                f"{self.snippet_dir}home.page.provider.txt")
            __menu_home_page_itens = self.__build_menu_home_page_itens()

            __snippet_page = __snippet_page.replace("$ImportViews$", __import_views)
            __snippet_page = __snippet_page.replace("$ItenMenu$", __menu_home_page_itens)

            with open(path_homepage, 'w', encoding='utf-8') as home_page_dart:
                home_page_dart.write(__snippet_page)

        except Exception as error:
            self.__message("Error Replace Main \n{}".format(error), error=True)

    """
    Função responsável por verificar as opções passadas por parametro
    e chamar os métodos responsáveis.

    A Função foi criada para que não ocorra repetição de código
    """

    def call_methods(self, options):
        if options['main']:
            self.__replace_main()
            return
        elif options['yaml']:
            self.__add_packages()
            return
        elif options['build_mobx']:
            self.__build_mobx()
            return
        elif options['clear']:
            self.__clear_project()
            sys.exit()

        elif options['init_provider'] or options['init_mobx'] or options['init_cubit']:
            if options['init_provider']:
                self.state_manager = StateManager.Provider
            elif options['init_mobx']:
                self.state_manager = StateManager.MobX
            elif options['init_cubit']:
                self.state_manager = StateManager.Cubit
            else:
                sys.exit()

            print(self.snippet_dir)
            self.__init_flutter()
            self.__create_utils()
            self.__build_settings_controller()
            self.__localization_app()
            self.__create_user_interface_directories()
            self.__http_dio_request()
        #     self.__create_auth_application()
        #     self.__build_flutter()
        #     return
        else:
            self.__message(
                "É necessário passar pelo menos um dos parâmetros a seguir: --init_provider, --init_mobx, --init_cubit,"
                " --main, --yaml, --build_mobx", error=True)
            sys.exit()

    def handle(self, *args, **options):
        """Método invocado internamente pelo Command logo após a
        validação da passagem de parâmetro.
        """

        app = options['App'] or None
        model = options['Model'] or None

        if app is None and model is None and FLUTTER_APPS == []:
            self.__message(
                f"Você não configurou o FLUTTER_APPS no settings e também não informou uma APP para ser gerada.",
                error=True)
            return

        if app and model:
            if self.__contain_number(app) or self.__contain_number(model):
                self.__message(f"Nome da app ou do model contendo números")
                return

            self.current_app_model = AppModel(self.flutter_project, app, model)
            self.call_methods(options)

        if app and model is None:
            if self.__contain_number(app):
                self.__message(f"Nome da app contendo números", error=True)
                return

            self.current_app_model = AppModel(self.flutter_project, app)
            self.call_methods(options)

        if not FLUTTER_APPS:
            self.__message("Não foram informadas as APPS a serem mapeadas", error=True)
            return
        else:
            self.call_methods(options)
            for __app in FLUTTER_APPS:
                self.current_app_model = AppModel(self.flutter_project, __app)
                self.__create_source_from_generators()
            self.__build_mobx()

    def __clear_project(self, path=None):
        try:
            __path = path or f"{self.flutter_dir}"
            import shutil
            shutil.rmtree(__path)
        except Exception as error:
            self.__message(f"Ocorreu um erro ao executar o __clear_project: {error}")
