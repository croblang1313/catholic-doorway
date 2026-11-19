import json
s=open('server.js').read(); h=open('app.html').read()
open('worker.js','w').write(s.replace('__APP_HTML__', json.dumps(h)))
