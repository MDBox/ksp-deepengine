from os import environ

port = 8888
if environ.get('port') is not None and environ.get('port').isdigit():
	port = int(environ.get('port'))

c.NotebookApp.allow_credentials = True
c.NotebookApp.allow_origin = "*"

c.NotebookApp.ip = '*'
c.NotebookApp.port = port
c.NotebookApp.open_browser = False
c.NotebookApp.tornado_settings = {
    'headers': { 'Content-Security-Policy': "frame-ancestors 'self' *" }
}
c.NotebookApp.notebook_dir = '/root'
c.NotebookApp.allow_root = True

# Disable password
#c.NotebookApp.password_required = False
#c.NotebookApp.token = ''

c.NotebookApp.terminado_settings = {
    'shell_command': ['/bin/bash']
}

c.ContentsManager.checkpoints_kwargs = {
    'checkpoint_dir': '/tmp'
}
