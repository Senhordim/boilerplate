"""Manager para mapear os models da app automatizando 
a criação dos templates customizados, das views, da APIRest e dos Forms.
"""

import fileinput
import os
import time
import traceback
from optparse import make_option

# Pacote responsável por pegar a instância do models baseado no nome
from django.apps import apps
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
            return model_name.title()

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
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
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
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
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
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
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
            text_check {str} -- Texto a ser pesquisado dentro do arquivo informado

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
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
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
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
            return None

    def _get_model(self):
        """ Método para pegar a instancia 
        do models

        Returns:
            Instancia do Models or None
        """
        try:
            return apps.get_model(self.app, self.model)
        except:
            return None

    def _apply_pep(self):
        try:
            # Aplicando a PEP8 as URLs
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_urls))
            os.system('isort {}'.format(self.path_urls))
        except:
            pass
        try:
            # Aplicando a PEP8 as Forms
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_form))
            os.system('isort {}'.format(self.path_form))
        except:
            pass
        try:
            # Aplicando a PEP8 as Views
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_views))
            os.system('isort {}'.format(self.path_views))
        except:
            pass
        try:
            # Aplicando a PEP8 as Views
            os.system(
                'autopep8 --in-place --aggressive --aggressive {}'
                .format(self.path_serializer))
            os.system('isort {}'.format(self.path_serializer))
        except:
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
            self._message(
                "Trabalhando na configuração do template inicial da APP")
            path = os.path.join(self.path_template_dir, "index.html")
            if self._check_file(path):
                self._message("A app informada já possue o template inicial.")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/indextemplate.txt"))
            _title = self._get_verbose_name(
                app_name=self.app.lower())
            content = content.replace("$titlepage$", _title)
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w') as template:
                template.write(content)
        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    def _manage_detail_template(self):
        """Método para criar o template de Detail do model.
        """

        try:
            self._message(
                "Trabalhando na configuração do template de Detalhamento.")
            path = os.path.join(self.path_template_dir,
                                "{}_detail.html".format(self.model_lower))
            # Verificando se já existe o template
            if self._check_file(path):
                self._message(
                    "O model informado já possui o template de Detalhamento")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/detailtemplate.txt"))
            _title = self._get_verbose_name(
                app_name=self.app.lower())
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w') as template:
                template.write(content)
        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    def _manage_list_template(self):
        """Método para criar o template de List do model.
        """
        try:
            self._message("Trabalhando na configuração do template de Edição.")
            path = os.path.join(self.path_template_dir,
                                "{}_list.html".format(self.model_lower))
            # Verificando se já existe o template
            if self._check_file(path):
                self._message(
                    "O model informado já possui o template de Listagem")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/listtemplate.txt"))
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$label_count_item$", self.model)
            content = content.replace("$model_name$", self.model_lower)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w') as template:
                template.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    def _manage_update_template(self):
        """Método para criar o template de Update do model.
        """
        try:
            self._message("Trabalhando na configuração do template de Edição.")
            path = os.path.join(self.path_template_dir,
                                "{}_update.html".format(self.model_lower))
            # Verificando se já existe o template
            if self._check_file(path):
                self._message(
                    "O model informado já possui o template de Edição")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/updatetemplate.txt"))
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)

            with open(path, 'w') as template:
                template.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    def _manage_create_template(self):
        """Método para criar o template de Create do model.
        """
        try:
            self._message(
                "Trabalhando na configuração do template de Criação.")
            path = os.path.join(self.path_template_dir,
                                "{}_create.html".format(self.model_lower))
            # Verificando se já existe o template
            if self._check_file(path):
                self._message(
                    "O model informado já possui o template de Criação")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/createtemplate.txt"))
            _title = self._get_verbose_name(
                app_name=self.app.lower(), model_name=self.model_lower)
            # Interpolando o conteúdo
            content = content.replace("$title$", _title)
            content = content.replace("$app_name$", self.app_lower)
            with open(path, 'w') as template:
                template.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    def _manage_delete_template(self):
        """Método para criar o template de Delete do model.
        """

        try:
            self._message(
                "Trabalhando na configuração do template de Deleção.")
            path = os.path.join(self.path_template_dir,
                                "{}_delete.html".format(self.model_lower))
            # Verificando se já existe o template
            if self._check_file(path):
                self._message(
                    "O model informado já possui o template de Deleção.")
                return
            # Pegando o conteúdo do snippet para criar o template
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/deletetemplate.txt"))
            # Interpolando o conteúdo
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            with open(path, 'w') as template:
                template.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    def _manage_templates(self):
        """Método pai para controlar a criação do templates
        """

        try:
            self._message("Trabalhando na configuração dos templates.")
            if self._check_dir(self.path_template_dir) is False:
                self._message("Criando o diretório dos Templates")
                os.makedirs(self.path_template_dir)
            # Chamando método de criação do template Index da App
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
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    """
    #################################################################
    Área da API DRF
    #################################################################    
    """

    def _manage_api_url(self):
        """Método para configuração das URLS da API
        """

        try:
            self._message(
                "Trabalhando na configuração das Urls API do model {}".format(self.model))
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/api_router.txt"))
            content_urls = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/api_router_urls.txt"))
            # Interpolando o conteúdo
            content = content.replace("$ModelName$", self.model)
            content = content.replace("$app_name$", self.app_lower)
            content = content.replace("$model_name$", self.model_lower)
            content_urls = content_urls.replace("$ModelName$", self.model)
            # Verificando se o arquivo urls.py existe
            if self._check_file(self.path_urls) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_urls, 'w') as arquivo:
                    arquivo.write(content_urls + content)
                return

            if self._check_content(self.path_urls, " {}ViewAPI".format(self.model)):
                # Já existe configuração de URL para a APP saindo da função
                self._message(
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
                arquivo = open(self.path_urls, "r")
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
                arquivo = open(self.path_urls, "w")
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
                    with open(self.path_urls, 'a') as views:
                        views.write("\n")
                        views.write(content_urls)
            elif self._check_content(self.path_urls, "from django.urls import"):
                imports = 'from django.urls import path, include'
                with fileinput.FileInput(self.path_urls, inplace=True) as arquivo:
                    for line in arquivo:
                        print(line.replace(
                            imports, imports + '\n' + content_urls), end='')
            else:
                with open(self.path_urls, 'a') as views:
                    views.write("\n")
                    views.write(content_urls)
        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
        # finally:
        #     # Aplicando a PEP8 ao arquivo
        #     os.system(
        #         'autopep8 --in-place --aggressive --aggressive {}'
        #         .format(self.path_urls))
        #     os.system('isort {}'.format(self.path_urls))

    def _manage_api_view(self):
        """Método para configuração das Views da API
        """
        try:
            self._message(
                "Trabalhando na configuração das Views da API do model {} ".format(self.model))
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/api_view.txt"))
            content_urls = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/api_urls.txt"))
            # Interpolando os dados
            content = content.replace("$ModelName$", self.model)
            content_urls = content_urls.replace("$ModelName$", self.model)
            # Verificando se o arquivo views.py existe
            if self._check_file(self.path_views) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_views, 'w') as arquivo:
                    arquivo.write(content_urls + content)
                return

            # Verificando se já tem a configuração do model
            if self._check_content(self.path_views, " {}ViewAPI".format(self.model)):
                self._message(
                    "O model informado já possui views da API configurado.")
                return

            # Verificando se já foi importado o model
            if not self._check_content(self.path_views, self.model):
                content_models = content_urls.split("\n")[5]
                # Abre o arquivo do form
                arquivo = open(self.path_views, "r")
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
                arquivo = open(self.path_views, "w")
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
                arquivo = open(self.path_views, "r")
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
                arquivo = open(self.path_views, "w")
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
                with open(self.path_views, 'a') as views:
                    views.write("\n")
                    views.write(content_urls)

            # Atualizando o conteúdo do arquivo.
            with open(self.path_views, 'a') as api_views:
                api_views.write("\n")
                api_views.write(content)
        except Exception as e:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
        # finally:
        #     # Aplicando a PEP8 ao arquivo
        #     os.system(
        #         'autopep8 --in-place --aggressive --aggressive {}'
        #         .format(self.path_views))
        #     os.system('isort {}'.format(self.path_views))

    def _manage_serializer(self):
        """Método para configurar o serializer do model informado.
        """
        try:
            self._message(
                "Trabalhando na configuração do Serializer do model {}".format(self.model))
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/serializer.txt"))
            content_urls = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/serializer_urls.txt"))
            # Interpolando os dados
            content = content.replace("$ModelName$", self.model)
            content = content.replace("$ModelClass$", self.model)
            content_urls = content_urls.replace("$ModelName$", self.model)
            # Verificando se o arquivo serializers.py existe
            if self._check_file(self.path_serializer) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_serializer, 'w') as arquivo:
                    arquivo.write(content_urls + '\n\n' + content)
                return

            # Verificando se já existe configuração no serializers para o Models informado
            if self._check_content(self.path_serializer, "class {}Serializer".format(self.model)):
                self._message(
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
                arquivo = open(self.path_serializer, "w")
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()
            else:
                with open(self.path_serializer, 'a') as views:
                    views.write(content_urls)
            # Atualizando o conteúdo do arquivo.
            with open(self.path_serializer, 'a') as urls:
                urls.write("\n")
                urls.write(content)
        except:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
        # finally:
        #     # Aplicando a PEP8 ao arquivo
        #     os.system(
        #         'autopep8 --in-place --aggressive --aggressive {}'
        #         .format(self.path_serializer))
        #     os.system('isort {}'.format(self.path_serializer))

    """
    #################################################################
    Área dos Forms
    #################################################################    
    """

    def _manage_form(self):
        """Método para configurar o Form do model informado.
        """
        try:
            self._message(
                "Trabalhando na configuração do Form do model {}".format(self.model))
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/form.txt"))
            # Recuperando o conteúdo do snippet das urls do form
            content_urls = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/form_urls.txt"))
            # Interpolando os dados
            content = content.replace("$ModelClass$", self.model)
            content_urls = content_urls.replace("$ModelClass$", self.model)

            # Verificando se o arquivo forms.py existe
            if self._check_file(self.path_form) is False:
                # Criando o arquivo com o conteúdo da interpolação
                with open(self.path_form, 'w') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            # Verificando se já existe configuração no forms para o Models informado
            if self._check_content(self.path_form, "class {}Form".format(self.model)):
                self._message("O model informado já possui form configurado.")
                return

            # Verificando se tem a importação do BaseForm
            if self._check_content(self.path_form, "from core.forms import BaseForm"):
                # Pega somente o import dos models
                content_urls = content_urls.split("\n")[1]
                # Abre o arquivo do form
                arquivo = open(self.path_form, "r")
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
                arquivo = open(self.path_form, "w")
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()
            else:
                with open(self.path_form, 'a') as views:
                    views.write(content_urls)
            # Atualizando o conteúdo do arquivo.
            with open(self.path_form, 'a') as form:
                form.write("\n")
                form.write(content)
        except:
            self._message(
                "OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO forms.py sofreu alguma alteração")
        # finally:
        #     # Aplicando a PEP8 ao arquivo
        #     os.system(
        #         'autopep8 --in-place --aggressive --aggressive {}'
        #         .format(self.path_form))
        #     os.system('isort {}'.format(self.path_form))

    """
    #################################################################
    Área das Views
    #################################################################    
    """

    def _manage_views(self):
        """Método para configurar as Views para o model informado.
        """
        __snnipet_index_template = self._get_snippet(os.path.join(
            self.path_core, "management/commands/snippets/django/index_view.txt"))

        try:
            self._message(
                "Trabalhando na configuração das Views do model {}".format(self.model))
            # Recuperando o conteúdo do snippet da view
            content = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/crud_views.txt"))
            # Recuperando o conteúdo do snippet das urls da view
            content_urls = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/crud_urls.txt"))
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
                            l=_model_field.lower(), u=_model_field, s=" "*8)
                    # Parser do form modal do update
                    modal_update = self._get_snippet(
                        os.path.join(
                            self.path_core,
                            "management/commands/snippets/django/crud_form_modal.txt"))
                    modal_update = modal_update.replace(
                        '$ModelClass$', "{}UpdateView".format(self.model))
                    modal_update = modal_update.replace(
                        '$FormsModal$', _forms.strip())
                    content = content.replace(
                        '$FormsModalUpdate$', modal_update)

                    # Parser do form modal do create
                    modal_create = self._get_snippet(
                        os.path.join(
                            self.path_core,
                            "management/commands/snippets/django/crud_form_modal.txt"))
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
                self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

            # Verificando se o models possui a configuração dos fields_display
            try:
                if hasattr(_model._meta, 'fields_display') is True:
                    content = content.replace(
                        '$ListFields$', 'list_display = {}'.format(
                            _model._meta.fields_display))
                else:
                    content = content.replace('$ListFields$', "")
            except Exception as error:
                self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

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
                with open(self.path_views, 'w') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            # Verificando se já existe configuração da views para o Models informado
            if self._check_content(self.path_views, "class {}ListView".format(self.model)):
                self._message(
                    "O model informado já possui as views configuradas.")
                return

            # Verificando se já tem os imports do core
            if self._check_content(self.path_views, "from nuvols.core.views"):
                # Pega somente o import dos models
                content_models = content_urls.split("\n")[1]
                # Pega somente o import dos forms
                content_forms = content_urls.split("\n")[2]
                # Abre o arquivo do form
                arquivo = open(self.path_views, "r")
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
                arquivo = open(self.path_views, "w")
                # escreve o arquivos com as linhas da variável auxiliar
                arquivo.writelines(data)
                # fecha o arquivo
                arquivo.close()

            else:
                with open(self.path_views, 'a') as views:
                    views.write(content_urls)

            # Atualizando o conteúdo do arquivo.
            with open(self.path_views, 'a') as views:
                views.write(_import_forms_modal)
                views.write("\n")
                views.write(content)

        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
        # finally:
        #     # Aplicando a PEP8 ao arquivo
        #     os.system(
        #         'autopep8 --in-place --aggressive --aggressive {}'
        #         .format(self.path_views))
        #     os.system('isort {}'.format(self.path_views))


    """
    #################################################################
    Área das URLS
    #################################################################    
    """

    def _manage_url(self):
        """Método para configurar as URLS do model informado.
        """
        try:
            self._message(
                "Trabalhando na configuração das Urls do model {}".format(self.model))
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/url.txt"))
            # Recuperando o conteúdo do snippet das urls da view
            content_urls = self._get_snippet(os.path.join(
                self.path_core, "management/commands/snippets/django/url_imports.txt"))
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
                with open(self.path_urls, 'w') as arquivo:
                    arquivo.write(content_urls + '\n' + content)
                return

            if self._check_content(self.path_urls, " {}ListView".format(self.model)):
                # Já existe configuração de URL para a APP saindo da função
                self._message("O model informado já possui urls configuradas.")
                return

            # Verificando se tem a importação do BaseForm
            if self._check_content(self.path_urls, "from .views import"):
                # Pega somente o import dos models
                content_urls = content_urls.split("\n")[1]
                # Abre o arquivo do form
                arquivo = open(self.path_urls, "r")
                # Variável que armazenará todas as linas do arquivo
                data = []
                for line in arquivo:
                    # Se for a linha que importa os models
                    if line.startswith('from .views import'):
                        # Pega os models já importados
                        models = line.split('import')[-1].rstrip()
                        # Pega o model que o usuário deseja
                        import_model = ', ' + \
                            content_urls.split('import')[-1].rstrip()
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
            else:
                with open(self.path_urls, 'a') as views:
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

            # Atualizando o conteúdo do arquivo.
            with open(self.path_urls, 'a') as urls:
                urls.write(content)
        except:
            self._message(
                "OCORREU UM ERRO, VERIFIQUE SE O ARQUIVO urls.py sofreu alguma alteração")

    """
    #################################################################
    Área do parser do HTML
    #################################################################    
    """

    def _render_modal_foreign_key(self, model, app, model_lower, field_name):
        """
        Método para renderizar o Model respectivo a foreign key do model em questão
        A possibilidade de adicionar um novo campo para a foreign key no próprio formulário
        """

        try:
            content = self._get_snippet(
                os.path.join(self.path_core, "management/commands/snippets/django/modal_form.txt"))
            # Interpolando o conteúdo
            content = content.replace("$ModelName$", model)
            content = content.replace("$app_name$", app)
            content = content.replace("$model_name$", model_lower)
            content = content.replace("$field_name$", field_name)
            return content
        except Exception as error:
            self._message(error)

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
                    # TODO Verificar como tratar os casos onde
                    # o campo é blank=False
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
                            _foreign_key_field += '{{% if form.{}.field.queryset.model|has_add_permission:request %}}<button type="button" class="btn btn-outline-secondary" data-toggle="modal" data-target="#form{}Modal">+</button>{{% endif %}}'\
                                .format(iten['name'], field.related_model._meta.object_name)
                            _foreign_key_field += '</div>'
                            # Cria o modal da foreign
                            self.html_modals += self._render_modal_foreign_key(
                                field.related_model._meta.object_name, iten['app'], field.related_model._meta.model_name, iten['name'])
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
                if readonly is not '':
                    tag_result = tag_result.replace(
                        "class='", "class='form-control-plaintext ")
                # Adicionando a classe obrigatorio aos campos required
                if required is not '':
                    tag_result += '\n<div class="invalid-feedback">Campo Obrigatorio.</div>'
                # Adicionando o HelpText no campo
                if helptext is not '':
                    tag_result += "\n<small class='form-text text-muted'>{}</small>\n".format(
                        helptext)
                tag_result += "{{% if form.{0}.errors  %}}{{{{ form.{0}.errors  }}}}{{% endif %}}".format(
                    iten['name'])
                tag_result += "</div>"
                return tag_result
            else:
                print('Campo {} desconhecido'.format(field))

        except Exception as error:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))
    """
    #################################################################
    Área dos templates HTML
    #################################################################    
    """

    def _manage_render_html(self):
        """Método para renderizar os campos do models 
        para tags HTML
        """
        self._message(
            "Trabalhando na configuração do parserhtml do model {}".format(self.model))
        try:
            # Rercuperando uma instancia do models informado
            model = self._get_model()
            if model == None:
                self._message("Favor declarar a app no settings.")
                return
            self._manage_templates()
            html_tag = ""
            self.html_modals = ""
            # Percorrendo os campos/atributos do models
            __fields = model._meta.fields + model._meta.many_to_many
            for field in iter(__fields):
                if str(field).split('.')[2] not in ('updated_on', 'created_on', 'deleted', 'enabled', 'id'):
                    html_tag += self._render_input(field)
            if html_tag is not '':
                # Pegando os templates create e update do Model informado
                for temp in ['create', 'update']:
                    list_update_create = os.path.join(
                        self.path_template_dir, "{}_{}.html".format(
                            self.model_lower, temp))
                    # Adiciona os forms no arquivo
                    with fileinput.FileInput(list_update_create, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_PARSER_HTML-->",
                                html_tag).replace(
                                    "$url_back$", '{}:{}-list'.format(
                                        self.app_lower, self.model_lower
                                    ) ), end='')
                    # Adiciona os modais das foreign keys
                    with fileinput.FileInput(list_update_create, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_MODAL_HTML-->",
                                self.html_modals).replace(
                                    "$url_back$", '{}:{}-list'.format(
                                        self.app_lower, self.model_lower
                                    ) ), end='')

                # Parser do template list
                try:
                    list_view = '{}:{}-list'.format(self.app_lower,
                                                    self.model_lower)
                    fields_display = resolve(reverse(list_view)
                                             ).func.view_class.list_display
                    thead = ''
                    tline = ''
                    for item in fields_display:
                        app_field = next(
                            (item_field for item_field in model._meta.fields if item == item_field.name), None)
                        if app_field is not None:
                            field_name = app_field.verbose_name.title(
                            ) if app_field.verbose_name else "Não Definido."
                            thead += '<th>{}</th>\n'.format(field_name)
                            tline += '<td>{{{{ item.{} }}}}</td>\n'.format(
                                item.replace('__', '.'))
                    list_template = os.path.join(
                        self.path_template_dir, "{}_list.html".format(
                            self.model_lower))
                    with fileinput.FileInput(list_template, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_THEAD-->",
                                thead), end='')
                    with fileinput.FileInput(list_template, inplace=True) as arquivo:
                        for line in arquivo:
                            print(line.replace(
                                "<!--REPLACE_TLINE-->",
                                tline), end='')
                except:
                    pass
        except:
            self.stdout.write(self.style.ERROR(traceback.format_exc().splitlines()))

    '''
    Função responsável por verificar as opções passadas por parametro 
    e chamar os métodos responsáveis.

    A Função foi criada para que não ocorrece a repetição de código
    '''

    def call_methods(self, options):
        # Verificando se foram passados parâmetros opcionais
        if options['templates']:
            self._message("Trabalhando apenas os templates.")
            self._manage_templates()
            return
        elif options['api']:
            self._message("Trabalhando apenas a api.")
            # Chamando o método para tratar o serializer
            self._manage_serializer()
            # Chamando o método para tratar as views da API
            self._manage_api_view()
            # Chamado o método para tratar as urls da API
            self._manage_api_url()
            self._apply_pep()
            return
        elif options['url']:
            self._message("Trabalhando apenas as urls.")
            # Chamando o método para tratar as urls
            self._manage_url()
            # Chamado o método para tratar as urls da API
            self._manage_api_url()
            self._apply_pep()
            return
        elif options['forms']:
            self._message("Trabalhando apenas os forms.")
            # Chamando o método para tratar os form
            self._manage_form()
            self._apply_pep()
            return
        elif options['views']:
            self._message("Trabalhando apenas as views.")
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
        self._message("Gerando os arquivos da app")
        # Pagando o nome da App passada por parâmetro
        app = options['App'] or None
        if (self._contain_number(app) is False):
            # Removendo os espaços em branco
            self.app = app.strip()
            # Pegando o diretório absoluto atual do projeto.
            self.path_root = os.getcwd()
            # Criando o path para a APP informada.
            self.path_app = os.path.join(self.path_root, app)
            # Criando o path para a APP Core.
            self.path_core = os.path.join(self.BASE_DIR, "core")
            # Criando o path para os models baseado no App informada.
            self.path_model = os.path.join(self.path_app, "models.py")
            # Criando o path para os forms baseado na App informada.
            self.path_form = os.path.join(self.path_app, "forms.py")
            # Criando o path para as views baseado na App informada.
            self.path_views = os.path.join(self.path_app, "views.py")
            # Criando o path para as urls baseado na App informada.
            self.path_urls = os.path.join(self.path_app, "urls.py")
            # Criando o path para os serializers baseado na App informada.
            self.path_serializer = os.path.join(
                self.path_app, "serializers.py")
            # Criando o path para o diretório dos templates baseado na App informada.
            self.path_template_dir = os.path.join(
                self.path_app, "templates", self.app)
            # Criando o path para a APP informada.
            self.path_app = os.path.join(self.path_root, app)
            # Convertendo os nomes para caracteres minúsculo.
            # para serem usado nos locais que necessitem dos nomes
            # em minúsculo.
            self.app_lower = app.lower()
            # Verificando se o diretório da App informada existe
            if self._check_dir(self.path_app) is False:
                self._message("Diretório não encontrado.")
                return
            # Verifica se app esta instalada, pois precisa dela
            # para recuperar as instancias dos models
            if apps.is_installed(self.app_lower) is False:
                self._message(
                    "Você deve colocar sua app no INSTALLED_APPS do settings.")
                return
            # Criando uma instancia da app
            self.app_instance = apps.get_app_config(self.app_lower)
            # Verificando se o usuário passou o nome do model
            if options['Model']:
                model = options['Model'] or None
                if (self._contain_number(model) is False):
                    # Removendo os espaços em branco
                    self.model = model.strip()
                    # Verificando se existe no models.py o Model informado
                    if self._check_content(self.path_model, 'class {}'.format(self.model)) is False:
                        self._message("Model informado não encontrado.")
                        return
                try:
                    # Verifica se o model está na app informada
                    # Se o model for abstract ela retornará uma exceção LookupError
                    self.app_instance.get_model(self.model)
                    self._message(
                        "Gerando arquivos para o model {}".format(self.model))
                    # Convertendo os nomes para caracteres minúsculo.
                    # para serem usado nos locais que necessitem dos nomes
                    # em minúsculo.
                    self.model_lower = model.lower()
                    self.call_methods(options)
                    self._message("Processo concluído.")
                except LookupError:
                    self._message(
                        "Esse model é abastrato. Não vão ser gerados os arquivos.")
            else:
                # recupera todos os models da app
                for model in self.app_instance.get_models():
                    model = model.__name__
                    # Removendo os espaços em branco
                    self.model = model.strip()
                    self._message(
                        "Gerando arquivos para o model {}".format(self.model))
                    # Convertendo os nomes para caracteres minúsculo.
                    # para serem usado nos locais que necessitem dos nomes
                    # em minúsculo.
                    self.model_lower = model.lower()
                    # Chama os métodos de geração de arquivos
                    self.call_methods(options)
                    self._message(
                        "Processo concluído para o model {}.".format(self.model))
                self._message("Processo concluído.")
                return
