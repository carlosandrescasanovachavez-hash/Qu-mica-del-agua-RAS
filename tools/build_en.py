"""Genera las versiones en inglés (en.html, bomba-de-calor-en.html) a partir de las páginas en español.
Uso: python3 tools/build_en.py   (desde la raíz del repositorio)
Las traducciones están en tools/es_en.json (texto español exacto -> inglés)."""
import json, re, os, sys
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pairs=json.load(open(os.path.join(root,'tools','es_en.json'),encoding='utf-8'))
keys=sorted(pairs,key=len,reverse=True)
def translate(s, page_pairs):
    for a,b in page_pairs: 
        if a not in s: raise SystemExit('No encontrado: '+a[:60])
        s=s.replace(a,b)
    # placeholders para no retraducir texto ya en inglés
    store=[]
    def hold(m):
        store.append(pairs[m.group(0)]); return '\x00%d\x00'%(len(store)-1)
    pat=re.compile('|'.join(re.escape(k) for k in keys))
    out=[];pos=0
    # reemplaza solo fuera de bloques <style>
    for m in re.finditer(r'<style>.*?</style>',s,flags=re.S):
        out.append(pat.sub(hold,s[pos:m.start()]));out.append(m.group(0));pos=m.end()
    out.append(pat.sub(hold,s[pos:]))
    s=''.join(out)
    return re.sub('\x00(\\d+)\x00',lambda m:store[int(m.group(1))],s)
def build(src,dst,page_pairs):
    s=open(os.path.join(root,src),encoding='utf-8').read()
    s=translate(s,page_pairs)
    # decimales con punto en el texto HTML (fuera de <script> y <style>)
    parts=re.split(r'(<script[^>]*>.*?</script>|<style>.*?</style>)',s,flags=re.S)
    for i in range(0,len(parts),2):
        parts[i]=re.sub(r'>([^<]*)<',lambda m:'>'+re.sub(r'(?<=\d),(?=\d)','.',m.group(1))+'<',parts[i])
    s=''.join(parts)
    open(os.path.join(root,dst),'w',encoding='utf-8').write(s)
    print('ok',dst)
COMMON=[('<html lang="es">','<html lang="en">'),]
build('index.html','en.html',COMMON+[
  ("'es-CL'","'en-US'"),
  ("const fmt=v=>String(v).replace('.',',');","const fmt=v=>String(v);"),
  ('src="bomba-de-calor.html"','src="bomba-de-calor-en.html"'),('href="bomba-de-calor.html"','href="bomba-de-calor-en.html"'),
  ('data-lang="es" class="on"','data-lang="es"'),('data-lang="en"','data-lang="en" class="on"'),
])
if os.path.exists(os.path.join(root,'bomba-de-calor.html')):
  build('bomba-de-calor.html','bomba-de-calor-en.html',COMMON+[('data-lang="es" class="on"','data-lang="es"'),('data-lang="en"','data-lang="en" class="on"'),('"es-CL"','"en-US"'),('href="./#bomba"','href="en.html#bomba"')]+[tuple(x) for x in json.load(open(os.path.join(root,'tools','es_en_bomba.json'),encoding='utf-8'))])
