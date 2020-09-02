"""Manager para mapear os models da app automatizando 
a criação dos templates customizados, das views, da APIRest e dos Forms.
"""

import fileinput
import os
import sys
from pathlib import Path

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.urls import resolve, reverse
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = "Manager para automatizar a geração dos códigos"

    # Path do diretório onde a app core está instalada
    BASE_DIR = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    def __init__(self):
        super().__init__()
        self.path_root = os.getcwd()
        self.path_core = os.path.join(self.BASE_DIR, "core")
        self._snippet_index_view = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/index_view.txt"))
        self._snippet_crud_view = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/crud_views.txt"))
        self._snippet_crud_urls = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/crud_urls.txt"))
        self._snippet_index_template = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/indextemplate.txt"))
        self._snippet_detail_template = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/detailtemplate.txt"))
        self._snippet_list_template = self._get_snippet(Path(
            f"{self.path_core}/management/commands/snippets/django/listtemplate.txt"))
        self._snippet_update_template = self._get_snippet(Path(
            f"{self.path_core}/management/commands/snippets/django/updatetemplate.txt"))
        self._snippet_crud_modal_template = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/crud_form_modal.txt"))
        self._snippet_url = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/url.txt"))
        self._snippet_urls_imports = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/url_imports.txt"))
        self._snippet_modal_foreign_key = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/modal_form.txt"))
        self._snippet_api_router = self._get_snippet(
            Path(
                f"{self.path_core}/management/commands/snippets/django/api_router.txt"))
        self._snippet_api_routers = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/api_router_urls.txt"))
        self._snippet_api_view = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/api_view.txt"))
        self._snippet_api_urls = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/api_urls.txt"))
        self._snippet_serializer = self._get_snippet(Path(
            f"{self.path_core}/management/commands/snippets/django/serializer.txt"))
        self._snippet_serializer_url = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/serializer_urls.txt"))
        self._snippet_form = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/form.txt"))
        self._snippet_form_url = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/form_urls.txt"))
        self._snippet_create_template = self._get_snippet(
            Path(f"{self.path_core}/management/commands/snippets/django/createtemplate.txt"))
        self._snippet_delete_template = self._get_snippet(Path(
            f"{self.path_core}/management/commands/snippets/django/deletetemplate.txt"))

    def add_arguments(self, parser):
        """Método inicial para informar quais parâmetros serão aceitos
        """

        parser.add_argument('App', type=str)
        parser.add_argument('Model', type=str, nargs='?')

        parser.add_argument(
            '--templates',
            action='store_true',
            dest='templates',
            help='Criar apenas os Templates'
        )
        parser.add_argument(
            '--api',
            action='store_true',
            dest='api',
            help='Criar apenas a API'
        )
        parser.add_argument(
            '--urls',
            action='store_true',
            dest='url',
            help='Criar apenas as Urls'
        )
        parser.add_argument(
            '--forms',
            action='store_true',
            dest='forms',
            help='Criar apenas o Form'
        )
        parser.add_argument(
            '--views',
            action='store_true',
            dest='views',
            help='Criar apenas as Views (CRUD)'
        )
        parser.add_argument(
            '--parserhtml',
            action='store_true',
            dest='renderhtml',
            help='Renderirzar os fields do models para HTML'
        )
        parser.add_argument(
            '--format',
            action='store_true',
            dest='format',
            help='Aplicar PEP8 nos arquivos'
        )

    def _get_verbose_name(self, app_name=None, model_name=None):
        """Method get verbose name class

        Arguments:
            app_name String -- App Name lower()
            model_name String -- Model Name lower()

        Returns:
            String -- Verbose name model
        """

        try:
            if app_name is not None and model_name is not None:
                _model = ContentType.objects.get(
                    app_label=app_name.lower(), model=model_name.lower())
                return _model.model_class()._meta.verbose_name.title()
            if app_name is not None and model_name is None:
                __app_config = apps.get_app_config(app_name.lower())
                return __app_config.verbose_name.title() or app_name
        except Exception as error:
            self.__message(
                f"Ocorreu um erro ao executar _get_verbose_name o :{error}")
            return model_name.title()

    def _contain_number(self, text):
        try:
            return any(character.isdigit() for character in text)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
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
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
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
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
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
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
            return False

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

    def _check_content(self, path, text_check):
        """Método para verificar se determinado texto existe 
        dentro de determinado arquivo

        Arguments:
            path {str} -- Caminho absoluto para o arquivo a ser analisado
            text_check {str} -- Texto a ser pesquisado dentro do arquivo informado

        Returns:
            Boolean -- Verdadeiro se o conteúdo for encontrado e False se não.
        """

        try:
            if self._check_file(path):
                with open(path, 'r', encoding='utf-8') as arquivo:
                    content = arquivo.read()
                    return text_check in content
            self.__message("Arquivo não encontrado para análise.")
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error} no _check_content")
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
            if self._check_file(path):
                with open(path, 'r') as arquivo:
                    content = arquivo.read()
                    if "#FileLocked" in content:
                        print(
                            f"{'|' * 100}\nArquivo {path} travado para parser\n{'|' * 100}")
                        return True
                    return False
        except Exception as error:
            self.__message(
                f"Ocorreu o erro : {error} no __check_fil_is_locked")
            return True

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
                with open(path, 'r', encoding='utf-8') as arquivo:
                    return arquivo.read()
            self.__message("Arquivo não encontrado para captura.")
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
            return None

    def _get_model(self):
        """ Método para pegar a instancia 
        do models

        Returns:
            Instancia do Models or None
        """
        try:
            return apps.get_model(self.app, self.model)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
            return None

    def __convert_no_ascii_character_html_code(self, text: str):
        try:
            __list_uft = ["Á", "á", "Â", "â", "À", "à", "Å", "å",
                          "Ã", "ã", "Ä", "ä", "Æ", "æ", "É", "é",
                          "Ê", "ê", "È", "è", "Ë", "ë", "Ð", "ð",
                          "Í", "í", "Î", "î", "Ì", "ì", "Ï", "ï",
                          "Õ", "õ", "Ö", "ö", "Ú", "ú", "Û", "û",
                          "Ó", "ó", "Ô", "ô", "Ò", "ò", "Ø", "ø",
                          "Ù", "ù", "Ü", "ü", "Ç", "ç", "Ñ", "ñ",
                          "Ý", "ý", "“", "&lt;", "&gt;", "&", "®", "©"]
            __list_html = ["&Aacute;", "&aacute;", "&Acirc;", "&acirc;", "&Agrave;", "&agrave;", "&Aring;", "&aring;",
                           "&Atilde;", "&atilde;", "&Auml;", "&auml;", "&AElig;", "&aelig;", "&Eacute;", "&eacute;",
                           "&Ecirc;", "&ecirc;", "&Egrave;", "&egrave;", "&Euml;", "&Euml;", "&ETH;", "&eth;",
                           "&Iacute;", "&iacute;", "&Icirc;", "&icirc;", "&Igrave;", "&igrave;", "&Iuml;", "&iuml;",
                           "&Oacute;", "&oacute;", "&Ocirc;", "&ocirc;", "&Ograve;", "&ograve;", "&Oslash;", "&oslash;",
                           "&Otilde;", "&otilde;", "&Ouml;", "&ouml;", "&Uacute;", "&uacute;", "&Ucirc;", "&ucirc;",
                           "&Ugrave;", "&ugrave;", "&Uuml;", "&uuml;", "&Ccedil;", "&ccedil;", "&Ntilde;", "&ntilde;",
                           "&Yacute;", "&yacute;", "&quot;", "&lt;", "&gt;", "&amp;", "&reg;", "&copy;"]
            return text
        except Exception as error:
            self.__message(
                f"Ocorreu um erro ao chamar o __convert_no_ascii_character_html_code: {error}")
        return text

    def _apply_pep(self):
        """
        Método para aplicar as configurações da Pep8 ao documento.
        """
        try:
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_urls))
            os.system('isort {}'.format(self.path_urls))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
            pass
        try:
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_form))
            os.system('isort {}'.format(self.path_form))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
            pass
        try:
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_views))
            os.system('isort {}'.format(self.path_views))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
            pass
        try:
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_serializer))
            os.system('isort {}'.format(self.path_serializer))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")
            pass

    """
    #################################################################
    Área dos templates
    #################################################################    
    """

    def _manage_index_template(self):
        """Método para criar o template Inicial da APP
        """
        try:
            self.__message(
                "Trabalhando na configuração do template inicial da APP")
            path = Path(f"{self.path_template_dir}/index.html")
            if self.__check_file_is_locked(path):
                return
            content = self._snippet_index_template
            _title = self._get_verbose_name(
                app_name=self.app.lower())
            content = content.replace("$titlepage$", _title)
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _manage_detail_template(self):
        """Método para criar o template de Detail do model.
        """

        try:
            self.__message(
                "Trabalhando na configuração do template de Detalhamento.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_detail.html")
            if self.__check_file_is_locked(path):
                return
            content = self._snippet_detail_template
            _title = self._get_verbose_name(
                app_name=self.app.lower())
            content = content.replace("$title$", _title)
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _manage_list_template(self):
        """Método para criar o template de List do model.
        """
        try:
            self.__message(
                "Trabalhando na configuração do template de Listagem.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_list.html")
            if self.__check_file_is_locked(path):
                return
            content = self._snippet_list_template
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            content = content.replace("$title$", _title)
            content = content.replace("$label_count_item$", self.model)
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _manage_update_template(self):
        """Método para criar o template de Update do model.
        """
        try:
            self.__message(
                "Trabalhando na configuração do template de Atualização.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_update.html")
            if self.__check_file_is_locked(path):
                return
            content = self._snippet_update_template
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)

            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _manage_create_template(self):
        """Método para criar o template de Create do model.
        """
        try:
            self.__message(
                "Trabalhando na configuração do template de Criação.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_create.html")
            if self.__check_file_is_locked(path):
                return
            content = self._snippet_create_template
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _manage_delete_template(self):
        """Método para criar o template de Delete do model.
        """
        try:
            self.__message(
                "Trabalhando na configuração do template de Deleção.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_delete.html")
            if self.__check_file_is_locked(path):
                return
            content = self._snippet_delete_template
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$title$", _title)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _manage_templates(self):
        """Método pai para controlar a criação do templates
        """
        try:
            if self._check_dir(self.path_template_dir) is False:
                self.__message("Criando o diretório dos Templates")
                os.makedirs(self.path_template_dir)
            self._manage_index_template()
            self._manage_detail_template()
            self._manage_list_template()
            self._manage_create_template()
            self._manage_delete_template()
            self._manage_update_template()
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    """
    #################################################################
    Área da API DRF
    #################################################################    
    """

    def _manage_api_url(self):
        """Método para configuração das URLS da API
        """
        try:
            import pdb
            self.__message(
                "Trabalhando na configuração das Urls API do model {}".format(self.model))
            content = self._snippet_api_router
            content_urls = self._snippet_api_routers
            content = content.replace("$ModelName$", self.model)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            content_urls = content_urls.replace("$ModelName$", self.model)
            if self._check_file(self.path_urls) is False:
                with open(self.path_urls, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + content)
                return

            if self._check_content(self.path_urls, " {}ViewAPI".format(self.model)):
                self.__message(
                    "O model informado já possui urls da API configuradas.")
                return

            if self._check_content(self.path_urls, "router = routers.DefaultRouter()"):
                content = content.split("\n", 1)[1]
                content = content.replace(
                    'router = routers.DefaultRouter()', '\n')
                imports = 'router = routers.DefaultRouter()'
                with fileinput.FileInput(self.path_urls, inplace=True) as arquivo:
                    for line in arquivo:
                        print(line.replace(
                            imports, imports + '\n' + content), end='')

            elif self._check_content(self.path_urls, "app_name = \'{}\'".format(self.app)):
                app_name_url = "app_name = \'{}\'".format(self.app_lower)
                with fileinput.FileInput(self.path_urls, inplace=True) as arquivo:
                    for line in arquivo:
                        print(line.replace(
                            app_name_url, app_name_url + '\n' + content), end='')

            if self._check_content(self.path_urls, "from rest_framework import routers"):
                content_origin = content_urls.split("\n")
                content_urls = content_urls.split("\n")[3]
                arquivo = open(self.path_urls, "r", encoding='utf-8')
                data = []
                for line in arquivo:
                    if line.startswith('from .views import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + content_urls.split()[-1]
                        models += import_model
                        line = 'from .views import{}\n'.format(models)
                    data.append(line)
                arquivo.close()

                arquivo = open(self.path_urls, "w", encoding='utf-8')
                arquivo.writelines(data)
                arquivo.close()
            elif self._check_content(self.path_urls, "from .views import"):
                content_aux = content_urls.split("\n")[1]
                arquivo = open(self.path_urls, "r")
                data = []
                for line in arquivo:
                    if line.startswith('from .views import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + content_aux.split()[-1]
                        models += import_model
                        line = 'from .views import{}\n'.format(models)
                    data.append(line)
                arquivo.close()

                arquivo = open(self.path_urls, "w")
                arquivo.writelines(data)
                arquivo.close()
                if self._check_content(self.path_urls, "from django.urls import"):
                    imports = 'from django.urls import path, include'
                    with fileinput.FileInput(self.path_urls, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                imports, imports + '\n' + content_urls.split("\n")[0]), end='')
                else:
                    with open(self.path_urls, 'a', encoding='utf-8') as views:
                        views.write("\n")
                        views.write(content_urls)
            elif self._check_content(self.path_urls, "from django.urls import"):
                imports = 'from django.urls import path, include'
                with fileinput.FileInput(self.path_urls, inplace=True) as arquivo:
                    for line in arquivo:
                        print(line.replace(
                            imports, imports + '\n' + content_urls), end='')
            else:
                with open(self.path_urls, 'a', encoding='utf-8') as views:
                    views.write("\n")
                    views.write(content_urls)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error} no _manage_api_url")

    def _manage_api_view(self):
        """Método para configuração das Views da API
        """
        try:
            self.__message(
                "Trabalhando na configuração das Views da API do model {} ".format(self.model))
            content = self._snippet_api_view

            content_urls = self._snippet_api_urls
            content = content.replace("$ModelName$", self.model)
            content_urls = content_urls.replace("$ModelName$", self.model)
            if self._check_file(self.path_views) is False:
                with open(self.path_views, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + content)
                return

            if self._check_content(self.path_views, " {}ViewAPI".format(self.model)):
                self.__message(
                    "O model informado já possui views da API configurado.")
                return

            if self._check_content(self.path_views, self.model) is False:
                content_models = content_urls.split("\n")[5]
                arquivo = open(self.path_views, "r", encoding='utf-8')
                data = []
                for line in arquivo:
                    if line.startswith('from .models import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + content_models.split()[-1]
                        models += import_model
                        line = 'from .models import{}\n'.format(models)
                    data.append(line)
                arquivo.close()

                arquivo = open(self.path_views, "w", encoding='utf-8')
                arquivo.writelines(data)
                arquivo.close()
            else:
                content_urls = content_urls.rsplit("\n", 1)[0]

            if self._check_content(self.path_views, "from rest_framework.viewsets import ModelViewSet"):
                content_urls = content_urls.split("\n")[4]
                arquivo = open(self.path_views, "r", encoding='utf-8')
                data = []
                for line in arquivo:
                    if line.startswith('from .serializers import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + content_urls.split()[-1]
                        models += import_model
                        line = 'from .serializers import{}\n'.format(models)
                    data.append(line)
                arquivo.close()

                arquivo = open(self.path_views, "w", encoding='utf-8')
                arquivo.writelines(data)
                arquivo.close()
            elif self._check_content(self.path_views, "from nuvols.core.views"):
                imports = 'from nuvols.core.views import BaseListView, BaseDeleteView, BaseDetailView, BaseUpdateView, BaseCreateView, BaseTemplateView'
                imports_rest = '\n{}\n{}\n{}\n{}\n'.format(content_urls.split("\n")[0], content_urls.split("\n")[1],
                                                           content_urls.split("\n")[2], content_urls.split("\n")[3])
                with fileinput.FileInput(self.path_views, inplace=True) as arquivo:
                    for line in arquivo:
                        print(line.replace(
                            imports, imports + imports_rest + content_urls.split("\n")[4]), end='')
            else:
                with open(self.path_views, 'a', encoding='utf-8') as views:
                    views.write("\n")
                    views.write(content_urls)

            with open(self.path_views, 'a', encoding='utf-8') as api_views:
                api_views.write("\n")
                api_views.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _manage_serializer(self):
        """Método para configurar o serializer do model informado.
        """
        try:
            self.__message(
                "Trabalhando na configuração do Serializer do model {}".format(self.model))
            content = self._snippet_serializer
            content_urls = self._snippet_serializer_url
            content = content.replace("$ModelName$", self.model)
            content = content.replace("$ModelClass$", self.model)
            content_urls = content_urls.replace("$ModelName$", self.model)
            if self._check_file(self.path_serializer) is False:
                with open(self.path_serializer, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n\n' + content)
                return

            if self.__check_file_is_locked(self.path_serializer) is True:
                return

            if self._check_content(self.path_serializer, "class {}Serializer".format(self.model)):
                self.__message(
                    "O model informado já possui serializer configurado.")
                return

            if self._check_content(self.path_serializer, "from rest_framework.serializers import ModelSerializer"):
                content_urls = content_urls.split("\n")[1]
                arquivo = open(self.path_serializer, "r")
                data = []
                for line in arquivo:
                    if line.startswith('from .models import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + content_urls.split()[-1]
                        models += import_model
                        line = 'from .models import{}\n'.format(models)
                    data.append(line)
                arquivo.close()

                arquivo = open(self.path_serializer, "w", encoding='utf-8')
                arquivo.writelines(data)
                arquivo.close()
            else:
                with open(self.path_serializer, 'a', encoding='utf-8') as views:
                    views.write(content_urls)
            with open(self.path_serializer, 'a', encoding='utf-8') as urls:
                urls.write("\n")
                urls.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    """
    #################################################################
    Área dos Forms
    #################################################################    
    """

    def _manage_form(self):
        """Método para configurar o Form do model informado.
        """
        try:
            self.__message(
                "Trabalhando na configuração do Form do model {}".format(self.model))
            content = self._snippet_form
            content_urls = self._snippet_form_url
            content = content.replace("$ModelClass$", self.model)
            content_urls = content_urls.replace("$ModelClass$", self.model)

            if self._check_file(self.path_form) is False:
                with open(self.path_form, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            if self.__check_file_is_locked(self.path_form) is True:
                return

            if self._check_content(self.path_form, "class {}Form".format(self.model)):
                self.__message("O model informado já possui form configurado.")
                return

            if self._check_content(self.path_form, "from core.forms import BaseForm"):
                content_urls = content_urls.split("\n")[1]
                arquivo = open(self.path_form, "r", encoding='utf-8')
                data = []
                for line in arquivo:
                    if line.startswith('from .models import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + content_urls.split()[-1]
                        models += import_model
                        line = 'from .models import{}\n'.format(models)
                    data.append(line)
                arquivo.close()

                arquivo = open(self.path_form, "w", encoding='utf-8')
                arquivo.writelines(data)
                arquivo.close()
            else:
                with open(self.path_form, 'a', encoding='utf-8') as views:
                    views.write(content_urls)
            with open(self.path_form, 'a', encoding='utf-8') as form:
                form.write("\n")
                form.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    """
    #################################################################
    Área das Views
    #################################################################    
    """

    def _manage_views(self):
        """Método para configurar as Views para o model informado.
        """
        try:
            __snnipet_index_template = self._snippet_index_view
            self.__message(
                "Trabalhando na configuração das Views do model {}".format(self.model))
            content = self._snippet_crud_view
            content_urls = self._snippet_crud_urls
            content = content.replace("$ModelClass$", self.model)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            content_urls = content_urls.replace("$ModelClass$", self.model)
            _import_forms_modal = ""
            _model = self._get_model()
            try:
                if hasattr(_model._meta, 'fk_fields_modal') is True:
                    _forms = ""
                    for fk_name in _model._meta.fk_fields_modal:
                        _field = _model._meta.get_field(fk_name)
                        _field_name = str(_field.related_model).split("'")[1]
                        _field_split = _field_name.split(".")
                        _app_field = _field_split[0]
                        _model_field = _field_split[2]
                        if _app_field != self.app_lower:
                            _import_forms_modal += "\nfrom {}.forms import {}Form".format(
                                _app_field, _model_field)
                        _forms += "{s}context['form_{l}'] = {u}Form\n".format(
                            l=_model_field.lower(), u=_model_field, s=" " * 8)
                    modal_update = self._snippet_crud_modal_template
                    modal_update = modal_update.replace(
                        '$ModelClass$', "{}UpdateView".format(self.model))
                    modal_update = modal_update.replace(
                        '$FormsModal$', _forms.strip())
                    content = content.replace(
                        '$FormsModalUpdate$', modal_update)

                    modal_create = self._snippet_crud_modal_template
                    modal_create = modal_create.replace(
                        '$ModelClass$', "{}CreateView".format(self.model))
                    modal_create = modal_create.replace(
                        '$FormsModal$', _forms.strip())
                    content = content.replace(
                        '$FormsModalCreate$', modal_create)
                else:
                    content = content.replace('$FormsModalCreate$', "")
                    content = content.replace('$FormsModalUpdate$', "")
            except Exception as error:
                self.__message(f"Ocorreu o erro: {e}")

            try:
                if hasattr(_model._meta, 'fields_display') is True:
                    content = content.replace(
                        '$ListFields$', 'list_display = {}'.format(
                            _model._meta.fields_display))
                else:
                    content = content.replace('$ListFields$', "")
            except Exception as error:
                self.__message(f"Ocorreu o erro {error}")

            if self._check_content(self.path_views, "{}IndexTemplateView".format(self.app.title())) is False:
                __snnipet_index_template = __snnipet_index_template.replace(
                    "$AppClass$", self.app.title())
                __snnipet_index_template = __snnipet_index_template.replace(
                    "$app_name$", self.app_lower)
                content = __snnipet_index_template + content

            if self._check_file(self.path_views) is False:
                with open(self.path_views, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            if self._check_content(self.path_views, "class {}ListView".format(self.model)):
                self.__message(
                    "O model informado já possui as views configuradas.")
                return

            if self._check_content(self.path_views, "from nuvols.core.views"):
                content_models = content_urls.split("\n")[1]
                content_forms = content_urls.split("\n")[2]
                arquivo = open(self.path_views, "r", encoding='utf-8')
                data = []
                for line in arquivo:
                    if line.startswith('from .models import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + content_models.split()[-1]
                        models += import_model
                        line = 'from .models import{}\n'.format(models)
                    elif line.startswith('from .forms import'):
                        forms = line.split('import')[-1].rstrip()
                        import_form = ', ' + content_forms.split()[-1]
                        forms += import_form
                        line = 'from .forms import{}\n'.format(forms)
                    data.append(line)
                data.append(_import_forms_modal)
                arquivo.close()

                arquivo = open(self.path_views, "w", encoding='utf-8')
                arquivo.writelines(data)
                arquivo.close()
            else:
                with open(self.path_views, 'a', encoding='utf-8') as views:
                    views.write(content_urls)

            with open(self.path_views, 'a', encoding='utf-8') as views:
                views.write(_import_forms_modal)
                views.write("\n")
                views.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    """
    #################################################################
    Área das URLS
    #################################################################    
    """

    def _manage_url(self):
        """Método para configurar as URLS do model informado.
        """
        try:
            self.__message(
                "Trabalhando na configuração das Urls do model {}".format(self.model))
            content = self._snippet_url
            content_urls = self._snippet_urls_imports
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$app_title$", self.app_lower.title())
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$ModelClass$", self.model)
            content_urls = content_urls.replace("$ModelClass$", self.model)

            if self._check_content(self.path_urls, "{}IndexTemplateView".format(self.app.title())):
                content_urls = content_urls.replace(", $AppIndexTemplate$", "")
            else:
                content_urls = content_urls.replace(
                    "$AppIndexTemplate$", "{}IndexTemplateView".format(self.app.title()))
            if self._check_file(self.path_urls) is False:
                with open(self.path_urls, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            if self.__check_file_is_locked(self.path_urls) is True:
                return

            if self._check_content(self.path_urls, " {}ListView".format(self.model)):
                self.__message(
                    "O model informado já possui urls configuradas.")

            if self._check_content(self.path_urls, "from .views import"):
                content_urls = content_urls.split("\n")[1]
                arquivo = open(self.path_urls, "r", encoding='utf-8')
                data = []
                for line in arquivo:
                    if line.startswith('from .views import'):
                        models = line.split('import')[-1].rstrip()
                        import_model = ', ' + \
                                       content_urls.split(
                                           'import')[-1].rstrip()
                        models += import_model
                        line = 'from .views import{}\n'.format(models)
                    data.append(line)
                arquivo.close()

                arquivo = open(self.path_urls, "w", encoding='utf-8')
                arquivo.writelines(data)
                arquivo.close()
            else:
                with open(self.path_urls, 'a', encoding='utf-8') as views:
                    views.write(content_urls)

            if self._check_content(self.path_urls, "urlpatterns = ["):
                content = content.replace(
                    "urlpatterns = [", "urlpatterns += [")
                content = content.replace("path('api/{}/', include(router.urls)),\n    ".format(
                    self.app_lower), '')
                _url_index_page = "path('{}/', {}IndexTemplateView.as_view(), name='{}-index'),\n    ".format(
                    self.app_lower, self.app.title(), self.app_lower)
                content = content.replace(_url_index_page, "")

            if self._check_content(self.path_urls, "app_name = \'{}\'".format(self.app)):
                content = content.replace(
                    "app_name = \'{}\'".format(self.app), "")

            if self.__check_file_is_locked(self.path_urls) is True:
                return

            with open(self.path_urls, 'a', encoding='utf-8') as urls:
                urls.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error} no _manage_url")

    """
    #################################################################
    Área do parser do HTML
    #################################################################    
    """

    def _render_modal_foreign_key(self, model, app, model_lower, field_name):
        """
        Método para renderizar o Model respectivo da foreign key do model em questão.
        A possibilidade de adicionar um novo campo para a foreign key no próprio formulário
        """

        try:
            content = self._snippet_modal_foreign_key
            content = content.replace("$ModelName$", model)
            content = content.replace("$app_name$", app)
            content = content.replace("$model_name$", model_lower)
            content = content.replace("$field_name$", field_name)
            return content
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def _render_input(self, field):
        try:
            types = [
                'AutoField', 'BLANK_CHOICE_DASH', 'BigAutoField',
                'BigIntegerField', 'BinaryField', 'BooleanField',
                'CharField', 'CommaSeparatedIntegerField',
                'DateField', 'DateTimeField', 'DecimalField',
                'DurationField', 'EmailField', 'Empty', 'FileField',
                'Field', 'FieldDoesNotExist', 'FilePathField',
                'FloatField', 'GenericIPAddressField',
                'IPAddressField', 'IntegerField', 'FieldFile',
                'NOT_PROVIDED', 'NullBooleanField', 'ImageField',
                'PositiveIntegerField', 'PositiveSmallIntegerField',
                'SlugField', 'SmallIntegerField', 'TextField',
                'TimeField', 'URLField', 'UUIDField', 'ForeignKey',
                'OneToOneField', 'ManyToManyField', 'OptimizedImageField'
            ]
            _model = self._get_model()
            iten = {}
            iten["app"], iten["model"], iten["name"] = str(field).split('.')
            iten["tipo"] = (str(
                str(type(field)).split('.')[-1:])
                .replace("[\"", "").replace("\'>\"]", ""))
            if iten["tipo"] in types:
                if iten["tipo"] == 'BooleanField':
                    tag_result = "<div class='form-check col-md-6'>"
                else:
                    tag_result = "<div class='form-group col-md-6'>"
                required = 'required'
                if ((getattr(field, 'blank', None) is True) or
                        (getattr(field, 'null', None) is True)):
                    required = ''
                readonly = getattr(field, 'readonly', '')
                label = "{{{{ form.{}.label_tag }}}}".format(iten['name'])
                helptext = getattr(field, 'help_text', '')
                """ 
                #####################################################
                Tratando os tipos de campos
                #####################################################
                """
                if (iten.get("tipo") in ('ForeignKey', 'OneToOneField')):
                    tag_result += label
                    _foreign_key_field = "\n{{{{ form.{} }}}}".format(
                        iten['name'])
                    if hasattr(_model._meta, 'fk_fields_modal') is True:
                        if iten["name"] in _model._meta.fk_fields_modal:
                            _foreign_key_field = '\n<div class="input-group">'
                            _foreign_key_field += "{{{{ form.{} }}}}\n".format(
                                iten['name'])
                            _foreign_key_field += '{{% if form.{}.field.queryset.model|has_add_permission:request %}}<button type="button" class="btn btn-outline-secondary" data-toggle="modal" data-target="#form{}Modal">+</button>{{% endif %}}' \
                                .format(iten['name'], field.related_model._meta.object_name)
                            _foreign_key_field += '</div>'
                            self.html_modals += self._render_modal_foreign_key(
                                field.related_model._meta.object_name, iten['app'],
                                field.related_model._meta.model_name, iten['name'])
                    tag_result += _foreign_key_field

                elif iten["tipo"] == 'BooleanField':
                    tag_result += "{{{{ form.{} }}}}\n{}".format(
                        iten['name'], label)
                elif iten["tipo"] == 'ManyToManyField':
                    tag_result += "{}\n{{{{ form.{} }}}}".format(
                        label, iten['name'])
                else:
                    tag_result += "{}\n{{{{ form.{} }}}}".format(
                        label, iten['name'])
                """
                #####################################################
                Configurando os atributos do campo
                #####################################################
                """
                if readonly != '':
                    tag_result = tag_result.replace(
                        "class='", "class='form-control-plaintext ")
                if required != '':
                    tag_result += '\n<div class="invalid-feedback">Campo Requerido.</div>'
                if helptext != '':
                    tag_result += "\n<small class='form-text text-muted'>{{{{ form.{0}.help_text }}}}</small>\n".format(
                        iten['name'])
                tag_result += "{{% if form.{0}.errors  %}}{{{{ form.{0}.errors  }}}}{{% endif %}}".format(
                    iten['name'])
                tag_result += "</div>"
                return tag_result
            else:
                print('Campo {} desconhecido'.format(field))

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    """
    #################################################################
    Área dos templates HTML
    #################################################################    
    """

    def _manage_render_html(self):
        """Método para renderizar os campos do models 
        para tags HTML
        """
        try:
            model = self._get_model()
            if model == None:
                self.__message("Favor declarar a app no settings.", error=True)
            self._manage_templates()
            html_tag = ""
            self.html_modals = ""
            __fields = model._meta.fields + model._meta.many_to_many
            for field in iter(__fields):
                if str(field).split('.')[2] not in ('updated_on', 'created_on', 'deleted', 'enabled', 'id'):
                    html_tag += self._render_input(field)
            if html_tag != '':
                for temp in ['create', 'update']:
                    list_update_create = Path(
                        f"{self.path_template_dir}/{self.model_lower}_{temp}.html")
                    if self.__check_file_is_locked(list_update_create) is True:
                        continue
                    with fileinput.FileInput(list_update_create, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_PARSER_HTML-->",
                                BeautifulSoup(html_tag, 'html5lib').prettify().replace(
                                    "<html>", "").replace(
                                        "<head>", "").replace(
                                            "</head>", "").replace(
                                                "<body>", "").replace(
                                                    "</body>", "").replace(
                                                        "</html>", "").strip()).replace(
                                "$url_back$", '{}:{}-list'.format(
                                    self.app_lower, self.model_lower
                                )), end='')

                    with fileinput.FileInput(list_update_create, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_MODAL_HTML-->",
                                self.html_modals).replace(
                                "$url_back$", '{}:{}-list'.format(
                                    self.app_lower, self.model_lower
                                )), end='')
                try:
                    list_view = '{}:{}-list'.format(self.app_lower,
                                                    self.model_lower)
                    fields_display = resolve(
                        reverse(list_view)).func.view_class.list_display
                    thead = ''
                    tline = ''
                    for item in fields_display:
                        app_field = next(
                            (item_field for item_field in model._meta.fields if item == item_field.name), None)
                        if app_field is not None:
                            field_name = app_field.verbose_name.title(
                            ) if app_field.verbose_name else "Não Definido."
                            thead += f"<th>{field_name}</th>\n"
                            tline += '<td>{{{{ item.{} }}}}</td>\n'.format(
                                item.replace('__', '.'))
                    list_template = Path(
                        f"{self.path_template_dir}/{self.model_lower}_list.html")
                    list_template_content = self._get_snippet(list_template)
                    list_template_content = list_template_content.replace(
                        "<!--REPLACE_THEAD-->", thead)
                    list_template_content = list_template_content.replace(
                        "<!--REPLACE_TLINE-->", tline)
                    with open(list_template, 'w', encoding='utf-8') as list_file:
                        list_file.write(list_template_content)

                except Exception as error:
                    self.__message(f"Ocorreu o erro : {error}")
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}")

    def call_methods(self, options):
        """
        Função responsável por verificar as opções passadas por parametro 
        e chamar os métodos responsáveis.

        A Função foi criada para que não ocorrece a repetição de código
        """
        if options['templates']:
            self.__message("Trabalhando apenas os templates.")
            self._manage_templates()
            return
        elif options['api']:
            self.__message("Trabalhando apenas a api.")
            self._manage_serializer()
            self._manage_api_view()
            self._manage_api_url()
            self._apply_pep()
            return
        elif options['url']:
            self.__message("Trabalhando apenas as urls.")
            self._manage_url()
            self._manage_api_url()
            self._apply_pep()
            return
        elif options['forms']:
            self.__message("Trabalhando apenas os forms.")
            self._manage_form()
            self._apply_pep()
            return
        elif options['views']:
            self.__message("Trabalhando apenas as views.")
            self._manage_views()
        elif options['renderhtml']:
            self._manage_render_html()
            self._apply_pep()
            return
        elif options['format']:
            self._apply_pep()
            return
        else:
            self._manage_form()
            self._manage_views()
            self._manage_serializer()
            self._manage_url()
            self._manage_api_view()
            self._manage_api_url()
            self._manage_templates()
            self._manage_render_html()
            self._apply_pep()
            return

    def handle(self, *args, **options):
        """Método invocado internamente pelo Command logo após a 
        validação da passagem de parâmetro.
        """
        self.__message("Gerando os arquivos da app")
        app = options['App'] or None
        if (self._contain_number(app) is False):
            self.app = app.strip()
            self.path_root = os.getcwd()
            self.path_app = Path(f"{self.path_root}/{app}")
            self.path_core = Path(f"{self.BASE_DIR}/core")
            self.path_model = Path(f"{self.path_app}/models.py")
            self.path_form = Path(f"{self.path_app}/forms.py")
            self.path_views = Path(f"{self.path_app}/views.py")
            self.path_urls = Path(f"{self.path_app}/urls.py")
            self.path_serializer = Path(f"{self.path_app}/serializers.py")
            self.path_template_dir = Path(
                f"{self.path_app}/templates/{self.app}")
            self.path_app = Path(f"{self.path_root}/{app}")
            self.app_lower = app.lower()
            if self._check_dir(self.path_app) is False:
                self.__message("Diretório não encontrado.")
                return
            if apps.is_installed(self.app_lower) is False:
                self.__message(
                    "Você deve colocar sua app no INSTALLED_APPS do settings.")
                return
            self.app_instance = apps.get_app_config(self.app_lower)
            if options['Model']:
                model = options['Model'] or None
                if self._contain_number(model) is False:
                    self.model = model.strip()
                    if self._check_content(self.path_model, 'class {}'.format(self.model)) is False:
                        self.__message(
                            "Model informado não encontrado.")
                        return
                try:
                    # Verifica se o model está na app informada
                    # Se o model for abstract ela retornará uma exceção LookupError
                    self.app_instance.get_model(self.model)
                    self.__message(
                        "Gerando arquivos para o model {}".format(self.model))
                    self.model_lower = model.lower()
                    self.call_methods(options)
                except LookupError as error:
                    self.__message(f"Ocorreu o erro : {error}")
            else:
                for model in self.app_instance.get_models():
                    self.__message(
                        f"Gerando os arquivos para a app: {self.app}")
                    model = model.__name__
                    self.model = model.strip()
                    self.model_lower = model.lower()
                    self.call_methods(options)
                self.__message("Processo concluído.")
                return
