import xml.etree.ElementTree as E,re,json,collections,pathlib
ns={'x':'http://www.w3.org/1999/xhtml'}
root=E.parse('docs/text/cpu-bbox.html')
pins=[]
for page,p in enumerate(root.findall('.//x:page',ns),4):
 lines=[]
 for l in p.findall('.//x:line',ns):
  s=''.join(w.text or '' for w in l.findall('x:word',ns))
  lines.append(dict(s=s,**{k:float(v) for k,v in l.attrib.items()}))
 # Pin numbers often share a line with net labels. Use words, merging AW 23.
 words=[dict(s=w.text or '',**{k:float(v) for k,v in w.attrib.items()}) for w in p.findall('.//x:word',ns)]
 balls=[]
 for w in words:
  if re.fullmatch(r'[A-HJ-NPRT-WY]{1,2}[1-9][0-9]?',w['s']): balls.append(w)
  elif re.fullmatch(r'[A-HJ-NPRT-WY]{1,2}',w['s']):
   for v in words:
    if re.fullmatch(r'[1-9][0-9]?',v['s']) and abs(v['yMin']-w['yMin'])<.1 and 0<=v['xMin']-w['xMax']<2:
     balls.append(dict(w,s=w['s']+v['s'],xMax=v['xMax']))
 for l in lines:
  candidates=[]
  for b in balls:
   dy=l['yMin']-b['yMin']
   if not 1.5<dy<2.6:continue
   gap=min(abs(l['xMin']-b['xMax']),abs(b['xMin']-l['xMax']))
   if gap<9:candidates.append((gap,b))
  if candidates:
   b=min(candidates,key=lambda x:x[0])[1]
   if int(re.search(r'[0-9]+',b['s'])[0])>40: continue
   pins.append(dict(pin=b['s'],name=l['s'],page=page,x=l['xMin'],y=l['yMin']))
counts=collections.Counter(p['pin'] for p in pins)
print('PINS',len(pins),'UNIQUE',len(counts),'DUPES',[p for p in pins if counts[p['pin']]>1][:20])
pathlib.Path('research/cpu-pin-extraction.json').write_text(json.dumps(pins,indent=2))
print(collections.Counter(p['page'] for p in pins))
print('PEG',sum(p['name'].startswith('PEG_') for p in pins),'DDR',sum(p['name'].startswith('DDR') for p in pins))
