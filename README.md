Projeto Nuvols Core
==================================

Esse projeto tem como objetivo facilitar o desenvolvimento dos sistemas automatizando diversar tarefas realizadas pelos analistas/programadores.  

As funcionalidades desse projeto são:

1) Renderização automática dos templates HTML do CRUD.  
2) Geração dos templates HTML estáticos de cada App/Model.  
3) Geração das URL's.
4) Geração das views  
5) Geração da APIRest.  
6) Geração de um projeto mobile utilizando o Flutter.  
7) Geração de documentação de desenvolvimento baseado em DocStrings.  

Para que o projeto funcione corretamente devem ser seguidas as etapas a seguir.


1. Adicionar o core no INSTALLED_APPS do settings
    ```
        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',  
        
            'core',  
        
            '...',
        ]
    ```

2. Criar o virtualenv. `virtualenv env -p Python(Version: 2.7 ou 3)`  
3. Adicionar no diretório env/pythonx.x/lib/site-packages o arquivo .path apontando para o diretório desse projeto  
4. Ativar o virtualenv  
    3.1 Usuários Linux/Mac `. env/bin/activate`  
    3.2 Usuários Windows `env/Scripts/activate`  
5. Executar o comando `pip install -r requirements_dev.txt`

 
### Configurações para funcionamento do manager doc  
> Manage responsável por gerar a documentação baseado nos DocStrings.  

Adicionar no settings a lista abaixo  

```DOC_APPS = ['nome_da_app_1', 'nome_da_app_2']```

### Configurações para funcionamento do manager flutter  
> Manage responsável por gerar o projeto Flutter.

Adicionar no settings a lista abaixo

```FLUTTER_APPS = ['nome_da_app_1', 'nome_da_app_2']```

__________

## Executando os manager's  

### Doc  
> Manage responsável por gerar a documentação de desenvolvimento do sistema.

```python manage.py doc NOME_DO_PROJETO_DJANGO "NOME DO DESENVOLVEDOR"```

### Build
> Manage responsável por gerar os templates HTML, as views, configurar  as url's do projeto e gerar a APIRest. 

```python manage.py build NOME_DA_APP NOME_DO_MODEL```


### Flutter
> Manage responsável por gerar os templates HTML, as views, configurar  as url's do projeto e gerar a APIRest. 

Para gerar o projeto com todas as apps configuradas no FLUTTER_APPS  
```python manage.py flutter```

Para gerar os arquivos do Flutter de uma determinada App e seus models  
```python manage.py flutter --app NomeDaApp```

Para gerar os arquivos do Flutter de um determinado Model de uma App  
```python manage.py flutter --model NomeDaApp nome_do_model```

Para renderizar o arquivo main.dart -> Tela inicial do aplicativo flutter  
```python manage.py flutter --main```
