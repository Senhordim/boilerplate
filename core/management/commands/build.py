"""Manager para mapear os models da app automatizando 
a criação dos templates customizados, das views, da APIRest e dos Forms.
"""

import os
import sys
import time
import platform
import fileinput
import traceback
import subprocess
from pathlib import Path
from optparse import make_option

# Pacote responsável por pegar a instância do models baseado no nome
from django.apps import apps
from django.utils import encoding
from django.utils.text import capfirst
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
# Importando os tipos de fields do Django
from django.db.models.fields import (BLANK_CHOICE_DASH, NOT_PROVIDED,
                                     AutoField, BigAutoField, BigIntegerField,
                                     BinaryField, BooleanField, CharField,
                                     CommaSeparatedIntegerField, DateField,
                                     DateTimeField, DecimalField,
                                     DurationField, EmailField, Empty, Field,
                                     FieldDoesNotExist, FilePathField,
                                     FloatField, GenericIPAddressField,
                                     IntegerField, IPAddressField,
                                     NullBooleanField, PositiveIntegerField,
                                     PositiveSmallIntegerField, SlugField,
                                     SmallIntegerField, TextField, TimeField,
                                     URLField, UUIDField)

from django.db.models import ManyToManyField
from django.urls import resolve, reverse
from django.utils.text import capfirst


class Command(BaseCommand):
    help = "Manager para automatizar a geração dos códigos"

    # Path do diretório onde a app core está instalada
    BASE_DIR = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    def __init__(self):
        super().__init__()
        # Pegando o diretório absoluto atual do projeto.
        self.path_root = os.getcwd()

        # Criando o path para a APP Core.
        self.path_core = os.path.join(self.BASE_DIR, "core")

        # Área para recuperar os Snippets para serem utilizados nos métodos
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
        # O argumento Model conta com um argumento a mais porque ele é opcional
        # caso o desenvolvedor queria gerar os arquivos para toda a app
        parser.add_argument('Model', type=str, nargs='?')

        # Parâmetro opcionais
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

    """
    #################################################################
    Área dos método internos
    #################################################################    
    """

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
                return apps.get_app_config(app_name.lower()).verbose_name.title() or app_name
        except Exception as error:
            self.__message(
                f"Ocorreu um erro ao executar _get_verbose_name o :{error}", error=True)
            return model_name.title()

    def _contain_number(self, text):
        try:
            return any(character.isdigit() for character in text)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
                with open(path, 'r', encoding='utf-8') as arquivo:
                    content = arquivo.read()
                    return "#FileLocked" in content
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
            self.__message("Arquivo não encontrado para captura.", error=True)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
            self.__message(f"Ocorreu o erro : {error}", error=True)
            return None

    def _apply_pep(self):
        """
        Método para aplicar as configurações da Pep8 ao documento.
        """
        try:
            # Aplicando a PEP8 as URLs
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_urls))
            os.system('isort {}'.format(self.path_urls))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)
            pass
        try:
            # Aplicando a PEP8 as Forms
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_form))
            os.system('isort {}'.format(self.path_form))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)
            pass
        try:
            # Aplicando a PEP8 as Views
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_views))
            os.system('isort {}'.format(self.path_views))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)
            pass
        try:
            # Aplicando a PEP8 as Views
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_serializer))
            os.system('isort {}'.format(self.path_serializer))
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)
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
            # Verificando se o arquivo está travado para novo parser
            if self.__check_file_is_locked(path):
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._snippet_index_template
            _title = self._get_verbose_name(
                app_name=self.app.lower())
            content = content.replace("$titlepage$", _title)
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_detail_template(self):
        """Método para criar o template de Detail do model.
        """

        try:
            self.__message(
                "Trabalhando na configuração do template de Detalhamento.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_detail.html")
            # Verificando se o arquivo está travado para novo parser
            if self.__check_file_is_locked(path):
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._snippet_detail_template
            _title = self._get_verbose_name(
                app_name=self.app.lower())
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_list_template(self):
        """Método para criar o template de List do model.
        """
        try:
            self.__message(
                "Trabalhando na configuração do template de Listagem.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_list.html")
            # Verificando se o arquivo está travado para novo parser
            if self.__check_file_is_locked(path):
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._snippet_list_template
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$label_count_item$", self.model)
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_update_template(self):
        """Método para criar o template de Update do model.
        """
        try:
            self.__message(
                "Trabalhando na configuração do template de Atualização.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_update.html")
            # Verificando se o arquivo está travado para novo parser
            if self.__check_file_is_locked(path):
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._snippet_update_template
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)

            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_create_template(self):
        """Método para criar o template de Create do model.
        """
        try:
            self.__message(
                "Trabalhando na configuração do template de Criação.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_create.html")
            # Verificando se o arquivo está travado para novo parser
            if self.__check_file_is_locked(path):
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._snippet_create_template
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_delete_template(self):
        """Método para criar o template de Delete do model.
        """

        try:
            self.__message(
                "Trabalhando na configuração do template de Deleção.")
            path = Path(
                f"{self.path_template_dir}/{self.model_lower}_delete.html")
            # Verificando se o arquivo está travado para novo parser
            if self.__check_file_is_locked(path):
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._snippet_delete_template
            # Interpolando o conteúdo
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            with open(path, 'w', encoding='utf-8') as template:
                template.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_templates(self):
        """Método pai para controlar a criação do templates
        """

        try:
            if self._check_dir(self.path_template_dir) is False:
                self.__message("Criando o diretório dos Templates")
                os.makedirs(self.path_template_dir)
            # Chamando método de criação do template Index da Ap
            self._manage_index_template()
            # Chamando método de criação do template de detalhe.
            self._manage_detail_template()
            # Chamando método de criação do template de listagem.
            self._manage_list_template()
            # Chamando método de criação do template de criação.
            self._manage_create_template()
            # Chamando método de criação do template de deleção.
            self._manage_delete_template()
            # Chamando método de criação do template de atualização.
            self._manage_update_template()
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    """
    #################################################################
    Área da API DRF
    #################################################################    
    """

    def _manage_api_url(self):
        """Método para configuração das URLS da API
        """

        try:
            self.__message(
                "Trabalhando na configuração das Urls API do model {}".format(self.model))
            content = self._snippet_api_router
            content_urls = self._snippet_api_routers

            # Interpolando o conteúdo
            content = content.replace("$ModelName$", self.model)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            content_urls = content_urls.replace("$ModelName$", self.model)
            # Verificando se o arquivo urls.py existe
            if self._check_file(self.path_urls) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_urls, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + content)
                return

            if self._check_content(self.path_urls, " {}ViewAPI".format(self.model)):
                # Já existe configuração de URL para a APP saindo da função
                self.__message(
                    "O model informado já possui urls da API configuradas.")
                return

            # Verificando se já existe o router = routers.DefaultRouter()
            if self._check_content(self.path_urls, "router = routers.DefaultRouter()"):
                content = content.split("\n", 1)[1]
                imports = 'router = routers.DefaultRouter()'
                with fileinput.FileInput(self.path_urls, inplace=True) as arquivo:
                    for line in arquivo:
                        print(line.replace(
                            imports, imports + '\n' + content), end='')

            elif self._check_content(self.path_urls, "app_name = \'{}\'".format(self.app)):
                # Atualizando arquivo com o novo conteúdo
                app_name_url = "app_name = \'{}\'".format(self.app_lower)
                with fileinput.FileInput(self.path_urls, inplace=True) as arquivo:
                    for line in arquivo:
                        print(line.replace(
                            app_name_url, app_name_url + '\n' + content), end='')

            # Verificando se tem a importação do rest_framework
            if self._check_content(self.path_urls, "from rest_framework import routers"):
                content_urls = content_urls.split("\n")[1]
                # Abre o arquivo do form
                arquivo = open(self.path_urls, "r", encoding='utf-8')
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .views import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deja
                        import_model = ', ' + content_urls.split()[-1]
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .views import{}\n'.format(models)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_urls, "w", encoding='utf-8')
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()
            elif self._check_content(self.path_urls, "from .views import"):
                content_aux = content_urls.split("\n")[1]
                # Abre o arquivo do form
                arquivo = open(self.path_urls, "r")
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .views import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deja
                        import_model = ', ' + content_aux.split()[-1]
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .views import{}\n'.format(models)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_urls, "w")
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
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
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_api_view(self):
        """Método para configuração das Views da API
        """
        try:
            self.__message(
                "Trabalhando na configuração das Views da API do model {} ".format(self.model))
            content = self._snippet_api_view

            content_urls = self._snippet_api_urls
            # Interpolando os dados
            content = content.replace("$ModelName$", self.model)
            content_urls = content_urls.replace("$ModelName$", self.model)
            # Verificando se o arquivo views.py existe
            if self._check_file(self.path_views) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_views, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + content)
                return

            # Verificando se já tem a configuração do model
            if self._check_content(self.path_views, " {}ViewAPI".format(self.model)):
                self.__message(
                    "O model informado já possui views da API configurado.")
                return

            # Verificando se já foi importado o model
            if not self._check_content(self.path_views, self.model):
                content_models = content_urls.split("\n")[5]
                # Abre o arquivo do form
                arquivo = open(self.path_views, "r", encoding='utf-8')
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .models import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deja
                        import_model = ', ' + content_models.split()[-1]
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .models import{}\n'.format(models)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_views, "w", encoding='utf-8')
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()
            else:
                # Remove ultima linha do snippet que é a importação do model
                content_urls = content_urls.rsplit("\n", 1)[0]

            # Verificando se tem a importação do rest_framework
            if self._check_content(self.path_views, "from rest_framework.viewsets import ModelViewSet"):
                content_urls = content_urls.split("\n")[4]
                # Abre o arquivo do form
                arquivo = open(self.path_views, "r", encoding='utf-8')
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .serializers import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deja
                        import_model = ', ' + content_urls.split()[-1]
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .serializers import{}\n'.format(models)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_views, "w", encoding='utf-8')
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
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

            # Atualizando o conteúdo do arquivo.
            with open(self.path_views, 'a', encoding='utf-8') as api_views:
                api_views.write("\n")
                api_views.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    def _manage_serializer(self):
        """Método para configurar o serializer do model informado.
        """
        try:
            self.__message(
                "Trabalhando na configuração do Serializer do model {}".format(self.model))
            content = self._snippet_serializer
            content_urls = self._snippet_serializer_url
            # Interpolando os dados
            content = content.replace("$ModelName$", self.model)
            content = content.replace("$ModelClass$", self.model)
            content_urls = content_urls.replace("$ModelName$", self.model)
            # Verificando se o arquivo serializers.py existe
            if self._check_file(self.path_serializer) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_serializer, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n\n' + content)
                return

            # Verificando se o arquivo está travado para não realizar o parser
            if self.__check_file_is_locked(self.path_serializer) is True:
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return

            # Verificando se já existe configuração no serializers para o Models informado
            if self._check_content(self.path_serializer, "class {}Serializer".format(self.model)):
                self.__message(
                    "O model informado já possui serializer configurado.")
                return

            # Verificando se tem a importação do ModelSerializer
            if self._check_content(self.path_serializer, "from rest_framework.serializers import ModelSerializer"):
                content_urls = content_urls.split("\n")[1]
                # Abre o arquivo
                arquivo = open(self.path_serializer, "r")
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .models import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deja
                        import_model = ', ' + content_urls.split()[-1]
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .models import{}\n'.format(models)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_serializer, "w", encoding='utf-8')
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()
            else:
                with open(self.path_serializer, 'a', encoding='utf-8') as views:
                    views.write(content_urls)
            # Atualizando o conteúdo do arquivo.
            with open(self.path_serializer, 'a', encoding='utf-8') as urls:
                urls.write("\n")
                urls.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

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
            # Recuperando o conteúdo do snippet das urls do form
            content_urls = self._snippet_form_url
            # Interpolando os dados
            content = content.replace("$ModelClass$", self.model)
            content_urls = content_urls.replace("$ModelClass$", self.model)

            # Verificando se o arquivo forms.py existe
            if self._check_file(self.path_form) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_form, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            # Verificando se o arquivo está travado para não realizar o parser
            if self.__check_file_is_locked(self.path_form) is True:
                print(
                    f"{'|'*100}\nArquivo {self.path_form} travado para parser\n{'|'*100}")
                return

            # Verificando se já existe configuração no forms para o Models informado
            if self._check_content(self.path_form, "class {}Form".format(self.model)):
                self.__message("O model informado já possui form configurado.")
                return

            # Verificando se tem a importação do BaseForm
            if self._check_content(self.path_form, "from core.forms import BaseForm"):
                # Pega somente o import dos models
                content_urls = content_urls.split("\n")[1]
                # Abre o arquivo do form
                arquivo = open(self.path_form, "r", encoding='utf-8')
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .models import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deja
                        import_model = ', ' + content_urls.split()[-1]
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .models import{}\n'.format(models)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_form, "w", encoding='utf-8')
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()
            else:
                with open(self.path_form, 'a', encoding='utf-8') as views:
                    views.write(content_urls)
            # Atualizando o conteúdo do arquivo.
            with open(self.path_form, 'a', encoding='utf-8') as form:
                form.write("\n")
                form.write(content)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

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
            # Recuperando o conteúdo do snippet da view
            content = self._snippet_crud_view
            # Recuperando o conteúdo do snippet das urls da view
            content_urls = self._snippet_crud_urls

            # Interpolando os dados
            content = content.replace("$ModelClass$", self.model)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            content_urls = content_urls.replace("$ModelClass$", self.model)

            _import_forms_modal = ""

            # Recuperando o objeto model para acessar os atributos
            _model = self._get_model()

            # Verificando se o o models possue a configuração dos fks_modal
            try:
                if hasattr(_model._meta, 'fk_fields_modal') is True:
                    _forms = ""
                    for fk_name in _model._meta.fk_fields_modal:
                        _field = _model._meta.get_field(fk_name)
                        _field_name = str(_field.related_model).split("'")[1]
                        _field_split = _field_name.split(".")
                        _app_field = _field_split[0]
                        _model_field = _field_split[2]
                        # Verificando se o nome da app é igual para não importar
                        if _app_field != self.app_lower:
                            _import_forms_modal += "\nfrom {}.forms import {}Form".format(
                                _app_field, _model_field)
                        _forms += "{s}context['form_{l}'] = {u}Form\n".format(
                            l=_model_field.lower(), u=_model_field, s=" " * 8)
                    # Parser do form modal do update
                    modal_update = self._snippet_crud_modal_template
                    modal_update = modal_update.replace(
                        '$ModelClass$', "{}UpdateView".format(self.model))
                    modal_update = modal_update.replace(
                        '$FormsModal$', _forms.strip())
                    content = content.replace(
                        '$FormsModalUpdate$', modal_update)

                    # Parser do form modal do create
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
                self.__message(f"Ocorreu o erro: {e}", error=True)

            # Verificando se o models possui a configuração dos fields_display
            try:
                if hasattr(_model._meta, 'fields_display') is True:
                    content = content.replace(
                        '$ListFields$', 'list_display = {}'.format(
                            _model._meta.fields_display))
                else:
                    content = content.replace('$ListFields$', "")
            except Exception as error:
                self.__message(f"Ocorreu o erro {error}")

            # Verificando se já existe a views do Index da app
            if self._check_content(self.path_views, "{}IndexTemplateView".format(self.app.title())) is False:
                __snnipet_index_template = __snnipet_index_template.replace(
                    "$AppClass$", self.app.title())
                __snnipet_index_template = __snnipet_index_template.replace(
                    "$app_name$", self.app_lower)
                content = __snnipet_index_template + content

            # Verificando se o arquivo views.py já existe
            if self._check_file(self.path_views) is False:
                # Caso o arquivo não exista ele a já adiciona o código inicial
                with open(self.path_views, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            # Verificando se já existe configuração da views para o Models informado
            if self._check_content(self.path_views, "class {}ListView".format(self.model)):
                self.__message(
                    "O model informado já possui as views configuradas.")
                return

            # Verificando se já tem os imports do core
            if self._check_content(self.path_views, "from nuvols.core.views"):
                # Pega somente o import dos models
                content_models = content_urls.split("\n")[1]
                # Pega somente o import dos forms
                content_forms = content_urls.split("\n")[2]
                # Abre o arquivo do form
                arquivo = open(self.path_views, "r", encoding='utf-8')
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .models import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deja
                        import_model = ', ' + content_models.split()[-1]
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .models import{}\n'.format(models)
                    elif line.startswith('from .forms import'):
                        # Pega os forms já importados
                        forms = line.split('import')[-1].rstrip()
                        # Pega o form que o usuário deja
                        import_form = ', ' + content_forms.split()[-1]
                        # Acrescenta o form no import dos forms
                        forms += import_form
                        # Cria linha com os importes antigos do form e com
                        # o novo desejado pelo usuário
                        line = 'from .forms import{}\n'.format(forms)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Adicionando os imports dos modais das foreingkeys
                data.append(_import_forms_modal)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_views, "w", encoding='utf-8')
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()

            else:
                with open(self.path_views, 'a', encoding='utf-8') as views:
                    views.write(content_urls)

            # Atualizando o conteúdo do arquivo.
            with open(self.path_views, 'a', encoding='utf-8') as views:
                views.write(_import_forms_modal)
                views.write("\n")
                views.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

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

            # Recuperando o conteúdo do snippet das urls da view
            content_urls = self._snippet_urls_imports

            # Interpolando os dados
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
            # Verificando se o arquivo de urls já existe
            if self._check_file(self.path_urls) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_urls, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            # Verificando se o arquivo está travado para não realizar o parser
            if self.__check_file_is_locked(self.path_urls) is True:
                print(
                    f"{'|'*100}\nArquivo {self.path_serializer} travado para parser\n{'|'*100}")
                return

            if self._check_content(self.path_urls, " {}ListView".format(self.model)):
                # Já existe configuração de URL para a APP saindo da função
                self.__message(
                    "O model informado já possui urls configuradas.")
                return

            # Verificando se tem a importação do BaseForm
            if self._check_content(self.path_urls, "from .views import"):
                # Pega somente o import dos models
                content_urls = content_urls.split("\n")[1]
                # Abre o arquivo do form
                arquivo = open(self.path_urls, "r", encoding='utf-8')
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .views import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deseja
                        import_model = ', ' + \
                                       content_urls.split(
                                           'import')[-1].rstrip()
                        # Acrescenta o model no import dos models
                        models += import_model
                        # Cria linha com os importes antigos do model e com
                        # o novo desejado pelo usuário
                        line = 'from .views import{}\n'.format(models)
                    # Salva as linhas na variável auxiliar
                    data.append(line)
                # Fecha o arquivo
                arquivo.close()
                # Abre o mesmo arquivos com modo de escrita
                arquivo = open(self.path_urls, "w", encoding='utf-8')
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()
            else:
                with open(self.path_urls, 'a', encoding='utf-8') as views:
                    views.write(content_urls)

            if self._check_content(self.path_urls, "urlpatterns = ["):
                # Verificando se no arquivo já existe uma configuração da URL
                content = content.replace(
                    "urlpatterns = [", "urlpatterns += [")
                # retira 4 espaços e o \n para não ficar com quebra de linha dentro das urls
                content = content.replace("path('api/{}/', include(router.urls)),\n    ".format(
                    self.app_lower), '')
                # Removendo a configuracao duplicada da url da página inicial
                _url_index_page = "path('{}/', {}IndexTemplateView.as_view(), name='{}-index'),\n    ".format(
                    self.app_lower, self.app.title(), self.app_lower)
                content = content.replace(_url_index_page, "")

            # Verificando se o arquivo já possui o app_name configurado
            if self._check_content(self.path_urls, "app_name = \'{}\'".format(self.app)):
                # Removendo a duplicidade do app_name
                content = content.replace(
                    "app_name = \'{}\'".format(self.app), "")

            # Verificando se o arquivo está travado para não realizar o parser
            if self.__check_file_is_locked(self.path_urls) is True:
                print(
                    f"{'|'*100}\nArquivo {self.path_urls} travado para parser\n{'|'*100}")
                return

            # Atualizando o conteúdo do arquivo.
            with open(self.path_urls, 'a', encoding='utf-8') as urls:
                urls.write(content)

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

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
            # Interpolando o conteúdo
            content = content.replace("$ModelName$", model)
            content = content.replace("$app_name$", app)
            content = content.replace("$model_name$", model_lower)
            content = content.replace("$field_name$", field_name)
            return content
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

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
            # print("Campo: {} Tipo: {}".format(iten.get("name"), iten.get("tipo")))
            # Verificando se o tipo de campos está nos tipos conhecidos
            if iten["tipo"] in types:
                # Criando a DIV para os campos de Checkbox
                if iten["tipo"] == 'BooleanField':
                    tag_result = "<div class='form-check col-md-6'>"
                # Criando a DIV form-group
                else:
                    tag_result = "<div class='form-group col-md-6'>"
                required = 'required'
                # Verificando se o campo aceita branco ou nulo para
                # retirar o parâmetro required da tag HTML
                if ((getattr(field, 'blank', None) is True) or
                        (getattr(field, 'null', None) is True)):
                    required = ''
                # Verificando se ele foi setado para readonly
                readonly = getattr(field, 'readonly', '')
                # Criando o Label do campo
                label = "{{{{ form.{}.label_tag }}}}".format(iten['name'])
                # Criando o HELP Text caso exista
                helptext = getattr(field, 'help_text', '')
                """ 
                #####################################################
                Tratando os tipos de campos
                #####################################################
                """
                # Tratando o campo do tipo ForeignKey
                # Adiciona o botão de adicionar um novo
                # Abre o modal para adicionar
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
                            # Cria o modal da foreign
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
                # Configurando para os campos do tipo readonly serem plain text
                if readonly != '':
                    tag_result = tag_result.replace(
                        "class='", "class='form-control-plaintext ")
                # Adicionando a classe obrigatorio aos campos required
                if required != '':
                    tag_result += '\n<div class="invalid-feedback">Campo Obrigatorio.</div>'
                # Adicionando o HelpText no campo
                if helptext != '':
                    tag_result += "\n<small class='form-text text-muted'>{}</small>\n".format(
                        helptext)
                tag_result += "{{% if form.{0}.errors  %}}{{{{ form.{0}.errors  }}}}{{% endif %}}".format(
                    iten['name'])
                tag_result += "</div>"
                return tag_result
            else:
                print('Campo {} desconhecido'.format(field))

        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

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
            # Rercuperando uma instancia do models informado
            model = self._get_model()
            if model == None:
                self.__message("Favor declarar a app no settings.", error=True)
                return
            self._manage_templates()
            html_tag = ""
            self.html_modals = ""
            # Percorrendo os campos/atributos do models
            __fields = model._meta.fields + model._meta.many_to_many
            for field in iter(__fields):
                if str(field).split('.')[2] not in ('updated_on', 'created_on', 'deleted', 'enabled', 'id'):
                    html_tag += self._render_input(field)
            if html_tag != '':
                # Pegando os templates create e update do Model informado
                for temp in ['create', 'update']:
                    list_update_create = Path(
                        f"{self.path_template_dir}/{self.model_lower}_{temp}.html")
                    # Verificando se o arquivo está travado para não realizar o parser
                    if self.__check_file_is_locked(list_update_create) is True:
                        print(
                            f"{'|'*100}\nArquivo {list_update_create} travado para parser\n{'|'*100}")
                        continue
                    # Adiciona os forms no arquivo
                    with fileinput.FileInput(list_update_create, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_PARSER_HTML-->",
                                html_tag).replace(
                                "$url_back$", '{}:{}-list'.format(
                                    self.app_lower, self.model_lower
                                )), end='')
                    # Adiciona os modais das foreign keys
                    with fileinput.FileInput(list_update_create, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_MODAL_HTML-->",
                                self.html_modals).replace(
                                "$url_back$", '{}:{}-list'.format(
                                    self.app_lower, self.model_lower
                                )), end='')

                # Parser do template list
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

                    # Recuperando o conteúdo o arquivo
                    list_template_content = self._get_snippet(list_template)
                    # Realizando o replace da TAG pelo conteúdo
                    list_template_content = list_template_content.replace(
                        "<!--REPLACE_THEAD-->", thead)
                    # Abrindo o arquivo para alterar o conteúdo
                    with open(list_template, 'w', encoding='utf-8') as list_file:
                        list_file.write(list_template_content)

                    with fileinput.FileInput(list_template, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_TLINE-->",
                                tline), end='')
                except Exception as error:
                    self.__message(f"Ocorreu o erro : {error}", error=True)
        except Exception as error:
            self.__message(f"Ocorreu o erro : {error}", error=True)

    '''
    Função responsável por verificar as opções passadas por parametro 
    e chamar os métodos responsáveis.

    A Função foi criada para que não ocorrece a repetição de código
    '''

    def call_methods(self, options):
        # Verificando se foram passados parâmetros opcionais
        if options['templates']:
            self.__message("Trabalhando apenas os templates.")
            self._manage_templates()
            return
        elif options['api']:
            self.__message("Trabalhando apenas a api.")
            # Chamando o método para tratar o serializer
            self._manage_serializer()
            # Chamando o método para tratar as views da API
            self._manage_api_view()
            # Chamado o método para tratar as urls da API
            self._manage_api_url()
            self._apply_pep()
            return
        elif options['url']:
            self.__message("Trabalhando apenas as urls.")
            # Chamando o método para tratar as urls
            self._manage_url()
            # Chamado o método para tratar as urls da API
            self._manage_api_url()
            self._apply_pep()
            return
        elif options['forms']:
            self.__message("Trabalhando apenas os forms.")
            # Chamando o método para tratar os form
            self._manage_form()
            self._apply_pep()
            return
        elif options['views']:
            self.__message("Trabalhando apenas as views.")
            # Chamando o método para tratar as views
            self._manage_views()
            self._apply_pep()
        elif options['renderhtml']:
            self._manage_render_html()
            return
        else:
            # Chamando o método para tratar os form
            self._manage_form()
            # Chamando o método para tratar as views
            self._manage_views()
            # Chamando o método para tratar o serializer
            self._manage_serializer()
            # Chamando o método para tratar as urls
            self._manage_url()
            # Chamando o método para tratar as views da API
            self._manage_api_view()
            # Chamado o método para tratar as urls da API
            self._manage_api_url()
            # Chamando o método para tratar os templates
            self._manage_templates()
            # Chamando o método para gerar os formulários
            self._manage_render_html()
            self._apply_pep()
            return

    def handle(self, *args, **options):
        """Método invocado internamente pelo Command logo após a 
        validação da passagem de parâmetro.
        """
        # Verificando se o usuário passou o nome da app
        self.__message("Gerando os arquivos da app")
        # Pagando o nome da App passada por parâmetro
        app = options['App'] or None
        if (self._contain_number(app) is False):
            # Removendo os espaços em branco
            self.app = app.strip()
            # Pegando o diretório absoluto atual do projeto.
            self.path_root = os.getcwd()
            # Criando o path para a APP informada.
            self.path_app = Path(f"{self.path_root}/{app}")
            # Criando o path para a APP Core.
            self.path_core = Path(f"{self.BASE_DIR}/core")
            # Criando o path para os models baseado no App informada.
            self.path_model = Path(f"{self.path_app}/models.py")
            # Criando o path para os forms baseado na App informada.
            self.path_form = Path(f"{self.path_app}/forms.py")
            # Criando o path para as views baseado na App informada.
            self.path_views = Path(f"{self.path_app}/views.py")
            # Criando o path para as urls baseado na App informada.
            self.path_urls = Path(f"{self.path_app}/urls.py")
            # Criando o path para os serializers baseado na App informada.
            self.path_serializer = Path(f"{self.path_app}/serializers.py")
            # Criando o path para o diretório dos templates baseado na App informada.
            self.path_template_dir = Path(
                f"{self.path_app}/templates/{self.app}")
            # Criando o path para a APP informada.
            self.path_app = Path(f"{self.path_root}/{app}")
            # Convertendo os nomes para caracteres minúsculo.
            # para serem usado nos locais que necessitem dos nomes
            # em minúsculo.
            self.app_lower = app.lower()
            # Verificando se o diretório da App informada existe
            if self._check_dir(self.path_app) is False:
                print(self.path_app)
                self.__message("Diretório não encontrado.", error=True)
                return
            # Verifica se app esta instalada, pois precisa dela
            # para recuperar as instancias dos models
            if apps.is_installed(self.app_lower) is False:
                self.__message(
                    "Você deve colocar sua app no INSTALLED_APPS do settings.", error=True)
                return
            # Criando uma instancia da app
            self.app_instance = apps.get_app_config(self.app_lower)
            # Verificando se o usuário passou o nome do model
            if options['Model']:
                model = options['Model'] or None
                if self._contain_number(model) is False:
                    # Removendo os espaços em branco
                    self.model = model.strip()
                    # Verificando se existe no models.py o Model informado
                    if self._check_content(self.path_model, 'class {}'.format(self.model)) is False:
                        self.__message(
                            "Model informado não encontrado.", error=True)
                        return
                try:
                    # Verifica se o model está na app informada
                    # Se o model for abstract ela retornará uma exceção LookupError
                    self.app_instance.get_model(self.model)
                    self.__message(
                        "Gerando arquivos para o model {}".format(self.model))
                    # Convertendo os nomes para caracteres minúsculo.
                    # para serem usado nos locais que necessitem dos nomes
                    # em minúsculo.
                    self.model_lower = model.lower()
                    self.call_methods(options)
                except LookupError as error:
                    self.__message(f"Ocorreu o erro : {error}", error=True)
            else:
                # recupera todos os models da app
                for model in self.app_instance.get_models():
                    self.__message(
                        f"Gerando os arquivos para a app: {self.app}")
                    model = model.__name__
                    # Removendo os espaços em branco
                    self.model = model.strip()
                    # Convertendo os nomes para caracteres minúsculo.
                    # para serem usado nos locais que necessitem dos nomes
                    # em minúsculo.
                    self.model_lower = model.lower()
                    # Chama os métodos de geração de arquivos
                    self.call_methods(options)
                self.__message("Processo concluído.")
                return
