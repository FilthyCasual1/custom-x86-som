import xml.etree.ElementTree as E,re,json,pathlib,collections
P=pathlib.Path;ns={'x':'http://www.w3.org/1999/xhtml'};rows='A B C D E F G H J K L M N P R T U V W Y AA AB'.split()
def words(page):return [dict(t=w.text or '',x=(float(w.get('xMin'))+float(w.get('xMax')))/2,y=(float(w.get('yMin'))+float(w.get('yMax')))/2,h=float(w.get('yMax'))-float(w.get('yMin'))) for w in page.findall('.//x:word',ns)]
ast=[]
for ix,page in enumerate(E.parse('docs/text/ast-map-bbox.html').findall('.//x:page',ns)):
 ws=words(page);rs={w['t']:w['y'] for w in ws if w['t'] in rows and w['h']<10 and (100<w['x']<115 if ix==0 else w['x']>480)}
 cs={int(w['t']):w['x'] for w in ws if w['t'].isdigit() and w['y']<125 and (1<=int(w['t'])<=11 if ix==0 else 12<=int(w['t'])<=22)}
 print(ix,len(rs),cs)
 for row,y in rs.items():
  for col,x in cs.items():
   contents=sorted([w for w in ws if w['h']<10 and abs(w['x']-x)<17 and abs(w['y']-y)<14],key=lambda w:(round(w['y'],1),w['x']))
   name=''.join(w['t'] for w in contents)
   if name and name!='#N/A':ast.append({'pin':row+str(col),'name':name,'page':77+ix})
P('research/ast-full-map.json').write_text(json.dumps(ast,indent=2));print('AST',len(ast),len({x['pin']for x in ast}));print([p for p in ast if p['pin']in ['A1','AB22','L10','K10']])
# Ball names are left of ball numbers in three columns of Intel table.
pch=[]
for pg,page in enumerate(E.parse('docs/text/pch-map-bbox.html').findall('.//x:page',ns),102):
 ws=words(page)
 for w in ws:
  if not re.fullmatch('[A-HJ-NPRT-WY]{1,2}[1-9][0-9]?',w['t']):continue
  # Ball-number columns from word coordinates, reject signal text (e.g. GPD0).
  if not any(abs(w['x']-x)<12 for x in [245,380,518]):continue
  ls=[v for v in ws if 4<w['x']-v['x']<125 and abs(v['y']-w['y'])<3 and v!=w]
  name=' '.join(v['t']for v in sorted(ls,key=lambda v:v['x']))
  pch.append({'pin':w['t'],'name':name,'page':pg})
print('PCH',len(pch),len({p['pin']for p in pch}));P('research/pch-full-map.json').write_text(json.dumps(pch,indent=2))
