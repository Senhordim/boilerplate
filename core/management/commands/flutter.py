import os
import sys
import json
import time
import traceback
from django.apps import apps
from django.core.management.base import BaseCommand

from nuvols.core.models import Base
from nuvols.core.settings import FLUTTER_APPS, SYSTEM_NAME, API_PATH


class AppModel:
    """Classe auxiliar para gerar os dados a serem utilizados nos métodos

    Arguments:
        path_flutter {String} -- Path do projeto Flutter
        app_name {String} -- Nome da App a ser mapeada

    Keyword Arguments:
        model_name {String} -- Nome do model a ser mapeado (default: {None})
    """

    try:
        def __init__(self, path_flutter, app_name, model_name=None):
            try:
                # Atribuindo o caminho do projeto Flutter
                self.path_flutter = path_flutter
                # Atributo para armazenar o generator dos models da App
                self.models = None

                # Atributo para armazenar o model informado
                self.model = None

                # Atributo para guardar o nome da App
                self.app_name = str(app_name).strip()
                self.app_name_lower = self.app_name.lower()

                # Recuperando a app informada
                self.app = apps.get_app_config(self.app_name_lower)

                # Atributo para guardar o nome do model
                self.model_name = str(model_name).strip()
                self.model_name_lower = self.model_name.lower()

                # Verificando se foi informado o nome do model
                if model_name is not None:
                    # Recuperando o model baseado no nome
                    self.model = self.app.get_model(self.model_name)
                else:
                    # Não foi informado o model
                    # Gerando os models dessa app
                    self.models = ((x, x.__name__.strip(),
                                    x.__name__.strip().lower()) for x in self.app.get_models())

            except Exception as error:
                raise error

        def get_path_app_dir(self):
            """Método para retornar o path da app no projeto Flutter

            Returns:
                String -- Caminho do diretório da app no projeto Flutter
            """
            try:
                return "{}/lib/apps/{}".format(
                    self.path_flutter, self.app_name_lower)
            except Exception as error:
                print(error)
                return None

        def get_path_app_model_dir(self):
            """Método para retornar o path do model no projeto Flutter

            Returns:
                String -- Caminho do diretório do model no projeto Flutter
            """
            try:
                return "{}/lib/apps/{}/{}".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
            except Exception as error:
                print(error)
                return None

        def get_path_pages_dir(self):
            """Método para retornar o path do diretório pages

            Returns:
                String -- Caminho do diretório pages no projeto Flutter
            """
            try:
                return "{}/lib/apps/{}/{}/pages".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
            except Exception as error:
                print(error)
                return None

        def get_path_files_pages(self):
            """Método para retornar os arquivos das páginas no projeto Flutter

            Returns:
                String's -- Caminho de cada arquivo das páginas na create, detail, index, list e update
            """
            try:
                __create = "{}/lib/apps/{}/{}/pages/create.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
                __detail = "{}/lib/apps/{}/{}/pages/detail.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
                __index = "{}/lib/apps/{}/{}/pages/index.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
                __list = "{}/lib/apps/{}/{}/pages/list.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
                __update = "{}/lib/apps/{}/{}/pages/update.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
                return __create, __detail, __index, __list, __update
            except Exception as error:
                print(error)
                return None

        def get_path_data_file(self):
            try:
                return "{}/lib/apps/{}/{}/data.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
            except Exception as error:
                print(error)
                return None

        def get_path_model_file(self):
            try:
                return "{}/lib/apps/{}/{}/model.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
            except Exception as error:
                print(error)
                return None

        def get_path_controller_file(self):
            """Método responsável por retornar o caminho para o arquivo controller.dart
            da app

            Returns:
                String -- Caminho do arquivo controller.dart
            """
            try:
                return "{}/lib/apps/{}/{}/controller.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
            except expression as identifier:
                print(error)
                return None

        def get_path_service_file(self):
            try:
                return "{}/lib/apps/{}/{}/service.dart".format(
                    self.path_flutter, self.app_name_lower,
                    self.model_name_lower
                )
            except Exception as error:
                print(error)
                return None

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
            print(f"Diretório Pages {self.get_path_pages_dir()}")
            print(f"Data {self.get_path_data_file()}")
            print(f"Model {self.get_path_model_file()}")
            print(f"Controller {self.get_path_controller_file()}")
            print(f"Service {self.get_path_service_file()}")
            c, d, i, l, u = self.get_path_files_pages()
            print("")
            print("Pages \nCreate: {}\nDetail: {}\nIndex: {}\nList: {}\nUpdate: {}".format(
                c, d, i, l, u
            ))

            print("Models (Generator)")
            if self.models is not None:
                for __model in self.models:
                    print("Model: {} Name: {} - {}".format(
                        __model[0], __model[1], __model[2]))
            else:
                print("None")

    except Exception as error:
        print(error)


class Command(BaseCommand):
    help = "Manager para automatizar a geração do app em Flutter"

    def __init__(self):
        super().__init__()
        # //////////////////////////////////////////////
        # Criando a estrutura dos diretórios do projeto
        # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        # Pegando o diretório absoluto atual do projeto.
        self.path_root = os.getcwd()

        # Criando o path para a APP Core.
        self.path_core = os.path.join(self.BASE_DIR, "core")

        # Obtém o nome do projeto
        self.project = os.getcwd().split("/")[-1:][0]
        self.project = self.project.replace("-", "").replace("_", "")
        # Concatenando o nome do projeto Django com o prefixo flutter
        self.flutter_project = '{}'.format(self.project)
        self.flutter_dir = "{}/Flutter/{}".format(
            "/".join(os.getcwd().split("/")[:-2]), self.project.lower())
        self.utils_dir = "{}/lib/utils".format(self.flutter_dir)
        self.ui_dir = "{}/lib/user_interface".format(self.flutter_dir)
        self.config_file = "{}/lib/utils/config.dart".format(self.flutter_dir)
        self.util_file = "{}/lib/utils/util.dart".format(self.flutter_dir)
        self.snippet_dir = "{}/{}".format(
            self.path_core, "management/commands/snippets/flutter")

        # Criando o path da APP de configuração
        self.app_configuration = "{}/lib/apps/configuracao".format(
            self.flutter_dir)
        self.app_configuration_page_file = f"{self.app_configuration}/index.page.dart"
        self.app_configuration_controller_file = f"{self.app_configuration}/controller.dart"

        # //////////////////////////////////////////////
        # Fim da estrutura dos diretórios do projeto
        # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

        # Instanciando o object current_app_model como None
        self.current_app_model = None

    # Path do diretório onde a app core está instalada
    BASE_DIR = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    _tipos_originais = ['AutoField', 'BLANK_CHOICE_DASH',
                        'BigAutoField', 'BigIntegerField',
                        'BinaryField', 'BooleanField',
                        'CharField', 'CommaSeparatedIntegerField',
                        'DateField', 'DateTimeField', 'DecimalField',
                        'DurationField', 'EmailField', 'Empty',
                        'FileField', 'Field', 'FieldDoesNotExist',
                        'FilePathField', 'FloatField',
                        'GenericIPAddressField', 'IPAddressField',
                        'IntegerField', 'FieldFile',
                        'NOT_PROVIDED', 'NullBooleanField',
                        'ImageField', 'PositiveIntegerField',
                        'PositiveSmallIntegerField', 'SlugField',
                        'SmallIntegerField', 'TextField',
                        'TimeField', 'URLField', 'UUIDField',
                        'ForeignKey', 'OneToOneField']

    _tipos_flutter = ['int', 'BLANK_CHOICE_DASH', 'int', 'int', 'String',
                      'bool', 'String', 'String', 'DateTime', 'DateTime',
                      'double', 'int', 'String', 'String', 'String', 'String',
                      'String', 'String', 'double', 'String', 'String', 'int',
                      'String', 'String', 'bool', 'String', 'int', 'int',
                      'String', 'int', 'String', 'DateTime', 'String',
                      'String', 'int', 'int']

    _tipos_sqlite = ['INT', 'BLANK_CHOICE_DASH', 'BIGINT', 'BIGINT', 'TEXT',
                     'BOOLEAN', 'TEXT', 'TEXT', 'DATE', 'DATETIME', 'DOUBLE',
                     'INT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT', 'TEXT',
                     'FLOAT', 'TEXT', 'TEXT', 'INT', 'TEXT', 'TEXT', 'BOOLEAN',
                     'TEXT', 'INT', 'INT', 'TEXT', 'SMALLINT', 'TEXT',
                     'DATETIME', 'TEXT', 'TEXT', 'INT', 'INT']

    def add_arguments(self, parser):
        """Método inicial para informar quais parâmetros serão aceitos
        """

        parser.add_argument('App', type=str, nargs='?')
        # O argumento Model conta com um argumento a mais porque ele é opcional
        # caso o desenvolvedor queria gerar os arquivos para toda a app
        parser.add_argument('Model', type=str, nargs='?')

        # Parâmetro opcionais
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
            '--init',
            action='store_true',
            dest='init',
            help='Gerar o projeto Flutter e executar os métodos auxiliares.'
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
            self.__message(f"Ocorreu um erro no Contain Number: {error}")
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
            self.__message(f"Ocorreu um erro no Check Dir: {error}")
            return False

    def __ignore_base_fields(self, field):
        """Método para verificar se o campo deve ser ignorado no parser

        Arguments:
            field {String} -- Nome do campo

        Returns:
            Boolean -- True se for para ser ignorado.
        """
        try:
            __ignore_fields = ['id', 'enabled', 'deleted',
                               'createdOn', 'created_on',
                               'updatedOn', 'updatedOn']
            return field in __ignore_fields
        except Exception as error:
            self.__message(
                f"Ocorreu um erro ao validar os campos do Base: {error}")

    def __message(self, message, error=False):
        """Método para retornar mensagems ao prompt(Terminal)

        Arguments:
            message {str} -- Mensagem a ser exibida
        """
        if error:
            self.stdout.write(self.style.ERROR(message))
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
                # Criando o camel case do Flutter
                if len(components) == 1:
                    # Nome simples
                    __string = components[0]
                    return "{}{}".format(__string[:1].lower(), __string[1:])
                # Nome composto
                return components[0] + ''.join(x.title() for x in components[1:])
            return components[0] + ''.join(x.title() for x in components[1:])
        except Exception as error:
            self.__message(f"Ocorreu um erro no Camel Case: {error}")
            return None

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
            self.__message(e)
            return False

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
                with open(path) as arquivo:
                    content = arquivo.read()
                    return "#FileLocked" in content
        except Exception as e:
            self.__message(e)
            return true
    """
    #################################################################
    Área para Criar o projeto Flutter
    #################################################################
    """

    def __init_flutter(self):
        try:
            # Verifica se o projeto já foi criado
            if not self.__check_dir(self.flutter_dir):
                # Se não foi criado, cria o projeto flutter
                self.__message("Criando o projeto flutter.")
                __cmd_flutter_create = "flutter create --androidx {}".format(
                    self.flutter_dir)
                os.system(__cmd_flutter_create)
                self.__message("Projeto criado com sucesso.")
        except Exception as error:
            self.__message(f"Erro ao executar o init do Flutter: {e}")

    def __build_flutter(self):
        """
        Método para quando o usuário criar o protejo flutter serem
        chamados os métodos __add_packages, __replace_main e __build_mobx
        """
        try:
            if self.__check_dir(self.flutter_dir):
                #  Chamando os métodos auxiliares para geração do projeto flutter
                # Executando o método de atualização do Yaml
                self.__message("Atualizando o arquivo de dependências.")
                self.__add_packages()
                time.sleep(3)
                # Executando o flutter package get
                self.__message("Executando o flutter packages get.")
                __cmd_get_packages = "cd {};flutter pub get; cd ../{}".format(
                    self.flutter_dir, self.project)
                os.system(__cmd_get_packages)
                time.sleep(3)
                # Executando o main
                self.__message("Atualizando o arquivo main.dart.")
                self.__replace_main()
                time.sleep(3)
                # Executando o build_mox
                self.__message("Gerando os arquivos controller.g.dart do MobX")
                self.__build_mobx()
        except Exception as error:
            self.__message(f"Erro ao executar o __build_flutter: {error}")
        pass
    """
    #################################################################
    Área para métodos assincronos
    #################################################################
    """

    def __mapping_all_application(self):
        try:
            __imports_pages = ""
            __imports_controllers = ""
            __controllers_models = ""
            __list_pages = ""
            __current_app = None

            for app in FLUTTER_APPS:
                __current_app = AppModel(self.flutter_project, app)

                __app = __current_app.app_name
                # Percorrendo os models da App
                for model in __current_app.models:
                    __model = model[1]
                    __imports_pages += "import 'apps/{}/{}/pages/list.dart';\n".format(
                        __app, __model.lower()
                    )
                    __list_pages += "Itens(title: '{}', icon: FontAwesomeIcons.folderOpen, uri: {}ListPage()),\n".format(
                        model[0]._meta.verbose_name, __model
                    )
                    # Construindo os imports dos controller
                    # import 'apps/animal/especie/controller.dart';
                    __imports_controllers += f"import 'apps/{__app.lower()}/{__model.lower()}/controller.dart';\n"
                    # Construindo os registros dos controllers
                    __controllers_models += f"getIt.registerSingleton<{__model}Controller>({__model}Controller());\n"

            return __imports_pages, __imports_controllers, __controllers_models, __list_pages

        except Exception as error:
            self.__message(
                f"Ocorreu um erro no Mapping All Application: {error}")
            return None, None

    def __indexpage_parser(self, app):
        """Método para criar a página index do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            # Recuperando o arquivo a ser editado
            __indexpage_file = f"{app.get_path_pages_dir()}/index.dart"

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(__indexpage_file):
                return

            # Realizando replace dos dados
            content = self.__get_snippet(f"{self.snippet_dir}/index_page.txt")
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace(
                "$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace(
                "$project$", self.flutter_project.lower())

            with open(__indexpage_file, 'w') as page:
                page.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(
                f"Ocorreu um erro ao gerar a página da Index {error}")

    def __listpage_parser(self, app):
        """Método para criar a página de listagem do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            # Recuperando o arquivo a ser editado
            __listpage_file = f"{app.get_path_pages_dir()}/list.dart"

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(__listpage_file):
                return

            # Realizando replace dos dados
            content = self.__get_snippet(f"{self.snippet_dir}/list_page.txt")

            content = content.replace("$App$", app.app_name)
            content = content.replace("$Model$", app.model_name_lower)
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace(
                "$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$project$", self.flutter_project)

            with open(__listpage_file, 'w') as page:
                page.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(
                f"Ocorreu um erro ao gerar a página da Listagem {error}")

    def __create_update_page_parser(self, app, createpage=True):
        try:
            if createpage is True:
                # Recuperando o arquivo da página de criação
                __createpage_file = f"{app.get_path_pages_dir()}/create.dart"
                content = self.__get_snippet(
                    f"{self.snippet_dir}/create_page.txt")

                # Verificando se o arquivo está travado para parser
                if self.__check_file_is_locked(__createpage_file):
                    return
            else:
                # Recuperando o arquivo da página de edição
                __createpage_file = f"{app.get_path_pages_dir()}/update.dart"
                content = self.__get_snippet(
                    f"{self.snippet_dir}/update_page.txt")

                # Verificando se o arquivo está travado para parser
                if self.__check_file_is_locked(__createpage_file):
                    return

            # Pegando o conteúdo do Snippet do Form
            content_form = self.__get_snippet(
                f"{self.snippet_dir}/text_field.txt")

            # Criando os atributos da classe Flutter
            content_attributes = ""
            text_fiels = ""
            attributes_data = ''
            clear_data = ''
            edited_attributes = ''

            for field in iter(app.model._meta.fields):
                __app, __model, __name = str(field).split('.')
                __nameTitle = self.__to_camel_case(
                    __name.title())
                __name = self.__to_camel_case(__name.lower())

                # Verificando se o field deve ser ignorado
                if self.__ignore_base_fields(__name):
                    continue

                field_type = (str(str(type(field)).split('.')[-1:])
                              .replace("[\"", "").replace("\'>\"]", ""))
                attribute = self._tipos_flutter[
                    self._tipos_originais.index(field_type)]
                content_attributes += '  final _{0}Form{1} = TextEditingController();\n'.format(
                    self.__to_camel_case(app.model_name, True), __nameTitle)
                text_field = content_form
                controller = '_{}Form{}'.format(
                    self.__to_camel_case(app.model_name, True), __nameTitle)
                text_field = text_field.replace("$controller$", controller)
                text_field = text_field.replace("$Field$", str(
                    field.verbose_name).replace("R$", "R\$"))
                text_fiels += text_field
                if attribute == 'int':
                    attributes_data += '{2}_{0}.{1} = int.tryParse(_{0}Form{1}.text ?? 0);\n'.format(
                        self.__to_camel_case(app.model_name, True), __name, '   ' * 11)
                elif attribute == 'double':
                    attributes_data += '{2}_{0}.{1} = double.tryParse(_{0}Form{1}.text ?? 0.0);\n'.format(
                        self.__to_camel_case(app.model_name, True), __name, '   ' * 11)
                elif attribute == 'bool':
                    attributes_data += '{2}_{0}.{1} = _{0}Form{1}.text == "true";\n'.format(
                        self.__to_camel_case(app.model_name, True), __name, '   ' * 11)
                elif attribute == 'DateTime':
                    attributes_data += '{2}_{0}.{1} = Util.convertDate(_{0}Form{1}.text);\n'.format(
                        self.__to_camel_case(app.model_name, True), __name, '   ' * 11)
                else:
                    attributes_data += '{2}_{0}.{1} = _{0}Form{1}.text;\n'.format(
                        self.__to_camel_case(app.model_name, True), __name, '   ' * 11)
                clear_data += '            {}.clear();\n'.format(controller)
                edited_attributes += '      {}.text = _{}.{}.toString();\n'.format(
                    controller, self.__to_camel_case(app.model_name, True), __name)

            # Interpolando o conteúdo
            content = content.replace("$app$", app.app_name_lower)
            content = content.replace("$App$", app.app_name_lower)
            content = content.replace(
                "$Model$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$model$", app.model_name_lower)
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace(
                "$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$project$", self.flutter_project)
            content = content.replace("$Atributes$", content_attributes)
            content = content.replace("$Form$", text_fiels)
            content = content.replace("$AttributesData$", attributes_data)
            content = content.replace("$ClearData$", clear_data)
            content = content.replace("$EditedAttributes$", edited_attributes)

            with open(__createpage_file, 'w') as page:
                page.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(
                f"Ocorreu um erro ao gerar a página da Create {error}")

    def __detailpage_parser(self, app):
        """Método para criar a página de detalhamento do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            # Recuperando o arquivo a ser editado
            __detailpage_file = f"{app.get_path_pages_dir()}/detail.dart"

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(__detailpage_file):
                return

            # Realizando replace dos dados
            content = self.__get_snippet(f"{self.snippet_dir}/detail_page.txt")
            content = content.replace("$App$", app.app_name)
            content = content.replace("$app$", app.app_name_lower)
            content = content.replace(
                "$Model$", self.__to_camel_case(app.model_name, True))
            content = content.replace(
                "$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$model$", app.model_name_lower)
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$project$", self.flutter_project)

            with open(__detailpage_file, 'w') as page:
                page.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(
                f"Ocorreu um erro ao gerar a página da Detail {error}")

    def __data_parser(self, app):
        """Método responsável por criar o arquivo de data baseado na App e no Models

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            # Recuperando o arquivo data do model
            __data_file = app.get_path_data_file()

            # Recuperando o snippet
            content = self.__get_snippet(f"{self.snippet_dir}/data.txt")

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(__data_file):
                return

            # Criando os atributos da classe Flutter
            content_parameters = "  final String {0}Table = " \
                                 "'{0}Table';\n  ".format(app.model_name_lower)
            content_database = '"CREATE TABLE ${}Table ("\n'.format(
                app.model_name_lower)

            # Recuperando o model
            for field in iter(app.model._meta.fields):
                __app, __model, __name = str(field).split('.')
                __name = self.__to_camel_case(__name.lower())
                field_type = (str(str(type(field)).split('.')[-1:])
                              .replace("[\"", "").replace("\'>\"]", ""))
                attribute = self._tipos_flutter[self._tipos_originais.index(
                    field_type)]
                data_type = self._tipos_sqlite[self._tipos_originais.index(
                    field_type)]
                content_parameters += "final {0}Column = '{0}'" \
                                      ";\n  ".format(__name)
                if (__name == 'id'):
                    content_database += '{}"$idColumn INTEGER PRIMARY KEY,' \
                                        '"\n'.format(" " * 23)
                else:
                    content_database += '{2}"${0}Column {1},"\n'.format(
                        __name, data_type, " " * 23)

            content_database += '{}")"'.format(" " * 23)

            # Alterando o conteúdo do Snippet com dados do model
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$ParametersTable$", content_parameters)
            content = content.replace("$CreateTable$", content_database)
            content = content.replace("$Model$", app.model_name_lower)
            content = content.replace("$App$", app.app_name_lower)
            content = content.replace("$project$", self.flutter_project)

            with open(__data_file, 'w') as data_helper:
                data_helper.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(f"Ocorreu um erro ao criar o DBHelper {error}")

    def __http_dio_request(self):
        """Método para criar a classe auxiliar de acesso HTTP
        """
        try:
            __dio_file = f"{self.flutter_dir}/lib/utils/http_dio_request.dart"
            content = self.__get_snippet(
                os.path.join(self.path_core,
                             "management/commands/snippets/flutter/http_request_dio.txt"))
            content = content.replace("$project$", self.flutter_project)
            with open(__dio_file, 'w') as http_request:
                http_request.write(content)
        except Exception as error:
            self.__message(f"Ocorreu um erro ao criar o Dio Request {error}")

    def __controller_parser(self, app):
        """Método responsável por criar o arquivo controller do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            if app.model is None:
                return

            __controller_file = app.get_path_controller_file()

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(__controller_file):
                return

            # Recuperando o snnipet do controller
            content = self.__get_snippet(f"{self.snippet_dir}/controller.txt")
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace(
                "$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))

            # Verifiando se o arquivo existe
            if not self.__check_file(__controller_file):
                # Arquivo não existe, criando arquivo
                os.makedirs(__controller_file)

            # Escrevendo no arquivo
            with open(__controller_file, 'w') as controller_file:
                controller_file.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(f"Erro ao executar o controller parser {error}")

    def __service_parser(self, app):
        """Método responsável por criar o arquivo de service do Model

        Arguments:
            app {AppModel} -- Instância da classe AppModel
        """
        try:
            if app.model is None:
                return

            # Recuperando o arquivo Service
            __service_file = app.get_path_service_file()

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(__service_file):
                return

            content = self.__get_snippet(f"{self.snippet_dir}/service.txt")

            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$App$", app.app_name_lower)
            content = content.replace("$Model$", app.model_name_lower)
            content = content.replace(
                "$ModelClassCamelCase$", self.__to_camel_case(app.model_name, True))
            content = content.replace("$project$", self.flutter_project)

            # Verificando se o arquivo existe
            if not self.__check_file(__service_file):
                # Arquivo não existe, criando o arquivo
                os.makedirs(__service_file)

            # Abrindo o arquivo para escrever
            with open(__service_file, 'w') as service_file:
                # Escrevendo o conteúdo no arquivo e fechando o arquivo
                service_file.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(f"Erro no parser do service: {error}")

    def __model_parser(self, app):
        """ Método responsável por criar a classe de modelo do Model
        """
        try:
            if app.model is None:
                return

            content = self.__get_snippet(f"{self.snippet_dir}/model.txt")
            # Criando os atributos da classe Flutter
            content_atributes = ""
            content_string_return = ""
            content_from_json = ""
            content_to_map = ""

            # Recuperando o arquivo do model.dart
            __model_file = app.get_path_model_file()

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(__model_file):
                return

            # Recuperando o model
            for field in iter(app.model._meta.fields):
                __app, __model, __name = str(field).split('.')
                __name_dart = self.__to_camel_case(__name)
                field_type = (str(str(type(field)).split('.')[-1:])
                              .replace("[\"", "").replace("\'>\"]", ""))
                attribute = self._tipos_flutter[self._tipos_originais.index(
                    field_type)]
                content_atributes += "{} {};\n  ".format(
                    attribute, __name_dart)
                content_string_return += "{}: ${}\\n".format(
                    __name_dart.upper(), __name_dart)

                # Verificando se o campo é do tipo Datetime para fazer a conversão
                if str(attribute) == "DateTime":
                    content_from_json += "{1} = Util.convertDate(json['{2}']) ?? \"\";\n        ".format(
                        __model.lower(), __name_dart, __name)
                elif str(attribute) == "bool":
                    if __name_dart.lower() == "enabled":
                        content_from_json += "{1} = json['{2}'] ?? true;\n        ".format(
                            __model.lower(), __name_dart, __name)
                    elif __name_dart.lower() == "deleted":
                        content_from_json += "{1} = json['{2}'] ?? false;\n        ".format(
                            __model.lower(), __name_dart, __name)
                    else:
                        content_from_json += "{1} = json['{2}'] ?? true;\n        ".format(
                            __model.lower(), __name_dart, __name)
                else:
                    # Verificando se o campo é do tipo FK para retornar null caso o valor não venha da API
                    if __name_dart.startswith("fk"):
                        content_from_json += "{1} = json['{2}'] ?? 0;\n        ".format(
                            __model.lower(), __name_dart, __name)
                    else:
                        content_from_json += "{1} = json['{2}'] ?? \"\";\n        ".format(
                            __model.lower(), __name_dart, __name)

                # Tratando os dados do content_to_map usados na função Map
                # Verificando se o campo é do tipo DateTime
                if str(field_type) == "DateTimeField":
                    if __name_dart in ('createdOn', 'updatedOn'):
                        content_to_map += "'{0}': this.{1},\n        ".format(
                            __name, __name_dart)
                    else:
                        content_to_map += '\'{0}\': Util.stringDateTimeSplit(this.{1}, returnType: "dt"), \n'.format(
                            __name, __name_dart
                        )
                    continue
                if str(field_type) == "DateField":
                    content_to_map += '\'{0}\': Util.stringDateTimeSplit(this.{1}, returnType: "d"), \n'.format(
                        __name, __name_dart
                    )
                    continue
                if str(field_type) == "TimeField":
                    content_to_map += '\'{0}\': Util.stringDateTimeSplit(this.{1}, returnType: "t"), \n'.format(
                        __name, __name_dart
                    )
                    continue
                if str(attribute) == "bool":
                    if __name_dart.lower() == "enabled":
                        content_to_map += "'{0}': this.{1} ?? true,\n        ".format(
                            __name, __name_dart)
                    elif __name_dart.lower() == "deleted":
                        content_to_map += "'{0}': this.{1} ?? false,\n        ".format(
                            __name, __name_dart)
                    else:
                        content_to_map += "'{0}': this.{1} ?? true,\n        ".format(
                            __name, __name_dart)
                    continue
                content_to_map += "'{0}': this.{1} ?? \"\",\n        ".format(
                    __name, __name_dart)

            # Alterando o conteúdo do Snippet com dados do model
            content = content.replace("$ModelClass$", app.model_name)
            content = content.replace("$AttributeClass$", content_atributes)
            content = content.replace("$StringReturn$", content_string_return)
            content = content.replace("$Model$", app.model_name_lower)
            content = content.replace("$ParserFromJson$", content_from_json)
            content = content.replace("$ParserToMap$", content_to_map)
            content = content.replace("$project$", self.flutter_project)

            # Verificando se o arquivo existe
            if not self.__check_file(__model_file):
                # Arquivo não existe, criando o arquivo
                os.makedirs(__model_file)

            # Abrindo o arquivo para escrever
            with open(__model_file, 'w') as model_file:
                # Escrevendo o conteúdo no arquivo e fechando o arquivo
                model_file.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(f"Erro ao realizar o parser do model: {error}")

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
            # Executando o comando
            # flutter pub run build_runner build
            # no diretório do projeto Flutter
            # Verifica se o projeto já foi criado
            if self.__check_dir(self.flutter_dir):
                __command = "cd {};flutter pub run build_runner build; cd ../{}".format(
                    self.flutter_dir, self.project)
                os.system(__command)
        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(f"Erro ao realizar o parser do model: {error}")

    def __build_settings_controller(self):
        """
        Método para gerar o controller e a página de configuração da APP.
        """
        try:
            # Criando o diretório da app de configuração
            if not self.__check_dir(self.app_configuration):
                os.makedirs(self.app_configuration)

                _content_page = self.__get_snippet(
                    f"{self.snippet_dir}/settings_page.txt")
                _content_controller = self.__get_snippet(
                    f"{self.snippet_dir}/settings_controller.txt")

                # Abrindo o arquivo da página para escrever
                with open(self.app_configuration_page_file, 'w') as arquivo:
                    arquivo.write(_content_page)

                # Abrindo o arquivo da página para escrever
                with open(self.app_configuration_controller_file, 'w') as arquivo:
                    arquivo.write(_content_controller)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(f"Erro ao realizar o parser do model: {error}")

    """
    #################################################################
    Área para adicionar os pacotes no puspec.yaml
    #################################################################
    """

    def __add_packages(self):
        """
        Método assincrono para alterar os pacotes do projeto
        """
        import yaml
        try:
            __path = f"{self.flutter_dir}/pubspec.yaml"
            # Trabalhando com a geração do arquivo baseado no snippet
            snippet = self.__get_snippet(f"{self.snippet_dir}/yaml.txt")
            snippet = snippet.replace("$AppPackage$", self.project.lower())
            snippet = snippet.replace("$AppDescription$",
                                      f"Projeto Flutter do sistema Django {self.project}")
            with open(__path, 'w') as yaml_file:
                yaml_file.write(snippet)

        except Exception as error:
            self.__message(f"Erro ao adicionar os pacotes: {error}")

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

            if not self.__check_file(self.config_file):
                # Acessando o snippet do arquivo de configuração
                snippet = self.__get_snippet(f"{self.snippet_dir}/config.txt")
                snippet = snippet.replace("$AppName$", SYSTEM_NAME)
                snippet = snippet.replace("$DjangoAPIPath$", API_PATH)

                # Classe de configuração
                with open(self.config_file, "w") as config:
                    config.write(snippet)

            if not self.__check_file(self.util_file):
                # Acessando o snippet do arquivo de funções auxiliares
                snippet = self.__get_snippet(f"{self.snippet_dir}/util.txt")
                # Classe de configuração
                with open(self.util_file, "w") as config:
                    config.write(snippet)

        except Exception as error:
            self.__message(f"Erro ao criar o arquivo utils {error}")

    """
    #################################################################
    Área para Criar a estrutura de diretórios
    #################################################################
    """

    def __create_user_interface_directories(self):
        """Método para criar a estrutura de diretórios UI
        """
        try:
            # Criando o diretório user_interface
            if not self.__check_dir(self.ui_dir):
                os.makedirs(self.ui_dir)

                # Criando os subdiretórios do user_interface
                for arquivo in ['widget', 'font']:
                    arquivo_dart = f"{self.ui_dir}/{arquivo}.dart"
                    if not self.__check_file(arquivo_dart):
                        # Criando os arquivos
                        snippet = self.__get_snippet(
                            f"{self.snippet_dir}/ui_{arquivo}.txt")
                        with open(arquivo_dart, "w") as arq:
                            arq.write(snippet)

        except Exception as error:
            self.__message(
                f"Erro ao criar a estrutura de arquivos da UI {error}")

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
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(
                f"Erro ao executar o Create App From Model: {error}")

    def __create_source_from_generators(self):
        """
        Método para criar as apps quando apenas a App for informada
        """
        self.__message("Criando as apps baseado na App e nos Generators")
        try:
            for model in self.current_app_model.models:
                self.__create_source(
                    self.current_app_model.app_name,
                    model[1])
        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(
                f"Erro ao executar o Create Apps From Generators: {error}")

    def __create_source(self, app_name, model_name):
        """
        Método para criar a estrutura de diretórios da App/Models
        """
        try:
            # Verificando se o self.current_app_model está populado
            if app_name is None:
                self.__message("É necessário passar a App")
                return

            # Verificando se foi passado a App e um Model
            if model_name is None:
                self.__message(f"É necessário passar o Model")
                return

            __source_class = AppModel(self.flutter_dir, app_name, model_name)

            __app_name = __source_class.app_name
            __model_name = __source_class.model_name
            __model = __source_class.model

            # Recuperando os caminhos dos diretório e arquivos do Model
            __model_dir = __source_class.get_path_app_model_dir()
            __pages_dir = __source_class.get_path_pages_dir()
            __data_file = __source_class.get_path_data_file()
            __model_file = __source_class.get_path_model_file()
            __service_file = __source_class.get_path_service_file()
            __controller_file = __source_class.get_path_controller_file()

            __pages = __source_class.get_path_files_pages()

            # Verificando se o diretório base do Model já existe
            if not self.__check_dir(__model_dir):
                # Diretório inexistente
                self.__message(
                    f"Criando diretório source do {__app_name}.{__model_name}")
                os.makedirs(__model_dir)

            # Verificando se o diretório pages do Model já existe
            if not self.__check_dir(__pages_dir):
                # Diretório inexistente
                os.makedirs(__pages_dir)

                # Criando os arquivos dart das páginas
                if __pages is not None:
                    with open(__pages[0], 'w') as pagina:
                        pagina.write(
                            f"// Create Page {__app_name} {__model_name}")

                    with open(__pages[1], 'w') as pagina:
                        pagina.write(
                            f"// Detail Page {__app_name} {__model_name}")

                    with open(__pages[2], 'w') as pagina:
                        pagina.write(
                            f"// Index Page {__app_name} {__model_name}")

                    with open(__pages[3], 'w') as pagina:
                        pagina.write(
                            f"// List Page {__app_name} {__model_name}")

                    with open(__pages[4], 'w') as pagina:
                        pagina.write(
                            f"// Update Page {__app_name} {__model_name}")

            # Verificando se o arquivo model.dart já existe
            if not self.__check_file(__model_file):
                with open(__model_file, 'w') as arquivo:
                    arquivo.write(f"// Modelo do {__model_name}")

            # Verificando se o arquivo data.dart já existe
            if not self.__check_file(__data_file):
                with open(__data_file, 'w') as arquivo:
                    arquivo.write(f"// Persistência do {__model_name}")

            # Verificando se o arquivo service.dart já existe
            if not self.__check_file(__service_file):
                with open(__service_file, 'w') as arquivo:
                    arquivo.write(f"// Service do {__model_name}")

            # Verificando se o arquivo controller.dart já existe
            if not self.__check_file(__controller_file):
                with open(__controller_file, 'w') as arquivo:
                    arquivo.write(f"// Controller do {__model_name}")

            # Área do parser

            # Realizando o parser da página de criação
            self.__create_update_page_parser(__source_class)

            # Realizando o parser da página de detalhe
            self.__detailpage_parser(__source_class)

            # Realizando o parser da página index
            self.__indexpage_parser(__source_class)

            # Realizando o parser da página de listagem
            self.__listpage_parser(__source_class)

            # Realizando o parser da página de criação
            self.__create_update_page_parser(__source_class, False)

            # Realizando o parser do arquivo model.dart
            self.__model_parser(__source_class)

            # Realizando o parser do arquivo data.dart
            self.__data_parser(__source_class)

            # Realizando o parser do arquivo service.dart
            self.__service_parser(__source_class)

            # Realizando o parser do arquivo store.dart
            self.__controller_parser(__source_class)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message(f"Error ao executar source. \n {error}")
            raise error

    """
    #################################################################
    Área para criar o localizations.dart, responsável por implementar
    internacionalização.
    #################################################################
    """

    def __localization_app(self):
        try:
            # Acessando o snippet do localizations
            snippet = self.__get_snippet(
                f"{self.snippet_dir}/localization.txt")
            # Criando o arquivo.
            path_localization = os.path.join(
                self.utils_dir, 'localization.dart')

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(path_localization):
                return

            # Gravando no arquivo
            with open(path_localization, 'w') as localizations:
                localizations.write(snippet)

            # Adicionando os arquivos de pt.json e en.json no diretório lang
            #
            # Recuperando o caminho do diretório
            __lang_dir = os.path.join(self.flutter_dir, 'lang')
            # Verificando se existe o diretório
            if not self.__check_dir(__lang_dir):
                # Criando o diretório
                os.makedirs(__lang_dir)

            # Verificando se o arquivo do idioma pt_br exiate
            if not self.__check_file(f"{__lang_dir}/pt.json"):
                # Criando os arquivos JSON
                with open(f"{__lang_dir}/pt.json", 'w') as pt_json:
                    pt_json.write(
                        '{\n"chave_do_texto":"Texto em português"\n}')

            # Verificando se o arquivo do idioma en_us existe.
            if not self.__check_file(f"{__lang_dir}/en.json"):
                with open(f"{__lang_dir}/en.json", 'w') as en_json:
                    en_json.write('{\n"chave_do_texto":"Text in english"\n}')

        except Exception as error:
            self.__message(f"Erro ao executar o localizations app. \n {error}")

    """
    #################################################################
    Área para alterar o Main.dart
    #################################################################
    """

    def __replace_main(self):
        """
        Método para atualizar o main conforme o Snippet
        """
        try:
            __list_itens = []
            __imports = ""

            # Acessando o snippet do arquivo
            snippet = self.__get_snippet(f"{self.snippet_dir}/main.txt")

            # Recuperando o caminho do arquivo main.dart no projeto Flutter
            path_maindart = os.path.join(self.flutter_dir, 'lib/main.dart')

            # Verificando se o arquivo está travado para parser
            if self.__check_file_is_locked(path_maindart):
                return

            # Pegando os imports das pages e dos controller
            __import_pages, __import_controllers, __register_controller, __pages = self.__mapping_all_application()

            # Adicionando a APP configuracao ao import dos controllers das pages e ao register
            __import_controllers += f"import 'apps/configuracao/controller.dart';"
            __import_pages += f"import 'apps/configuracao/index.page.dart';\n"
            __register_controller += "getIt.registerSingleton<SettingsController>(SettingsController());"

            if __import_pages is None or __import_controllers is None:
                return

            snippet = snippet.replace('$project$', self.flutter_project)
            snippet = snippet.replace(
                '$RegisterControllers$', __register_controller)
            snippet = snippet.replace('$ImportPages$', __import_pages)
            snippet = snippet.replace(
                '$ImportController$', __import_controllers)
            snippet = snippet.replace('$ListPages$', __pages)

            # Alterando o conteúdo do arquivo main.dart original
            with open(path_maindart, 'w') as main_dart:
                main_dart.write(snippet)

        except Exception as error:
            self.stdout.write(self.style.ERROR(
                traceback.format_exc().splitlines()))
            self.__message("Error Replace Main \n{}".format(error))

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
        elif options['init']:
            # Criando o Projeto
            self.__init_flutter()

            # Invocando o método para criar a app de configuração
            self.__build_settings_controller()

            # Gerando o arquivo utils
            self.__create_utils()

            # Gerando a estrutura da UserInterface
            self.__create_user_interface_directories()

            # Gerando o class de acesso HTTP
            self.__http_dio_request()

            # Criando a app para gerenciar a internacionalização do projeto
            self.__localization_app()

            # Invocando os demais métodos de geração do projeto flutter
            self.__build_flutter()

            return
        else:
            self.__message(
                "É necessário passar pelo menos um dos parâmetros a seguir: --init, --main, --yaml, --build_mobx", error=True)
            sys.exit()

    def handle(self, *args, **options):
        """Método invocado internamente pelo Command logo após a
        validação da passagem de parâmetro.
        """

        # Verificando se o usuário informou a APP a ser mapeada
        app = options['App'] or None
        model = options['Model'] or None

        # Verificando se nenhum dos parâmetros necessários foi informado
        if app is None and model is None and FLUTTER_APPS == []:
            self.__message(
                f"Você não configurou o FLUTTER_APPS no settings e também não informou uma APP para ser gerada.", error=True)
            return

        # Foram informados a App e o Model
        if app and model:
            # Verificando se existem números nos nomes informados
            if (self.__contain_number(app) or self.__contain_number(model)):
                self.__message(f"Nome da app ou do model contendo números")
                return

            self.current_app_model = AppModel(self.flutter_project, app, model)
            self.call_methods(options)

        # Foi informado a App apenas
        if app and model is None:
            if (self.__contain_number(app)):
                self.__message(f"Nome da app contendo números", error=True)
                return

            self.current_app_model = AppModel(self.flutter_project, app)
            self.call_methods(options)

        # Verificando se as app foram configuradas na settings do Core
        if FLUTTER_APPS == []:
            self.__message(
                "Não foram informadas as APPS a serem mapeadas", error=True)
            return
        else:
            # Chamando os métodos únicos
            self.call_methods(options)
            for __app in FLUTTER_APPS:
                self.current_app_model = AppModel(self.flutter_project, __app)
                # Gerar as apps.
                self.__create_source_from_generators()
            # Chamando o build_mobx para as apps
            self.__build_mobx()

    def __clear_project(self, path=None):
        try:
            __path = path or f"{self.flutter_dir}"
            import shutil
            shutil.rmtree(__path)
        except Exception as error:
            self.__message(
                f"Ocorreu um erro ao executar o __clear_project: {error}")
