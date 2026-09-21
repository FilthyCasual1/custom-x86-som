"""Make a component staging board; not a proposed board outline or electrical signoff."""
import pcbnew as k,xml.etree.ElementTree as E,pathlib,json,re
p=pathlib.Path('hardware');r=E.parse(p/'x86-som-preliminary.xml').getroot();b=k.BOARD();fps={};nets={};missing=[]
rootid=re.search(r'\(uuid "([^"]+)"', (p/'x86-som-preliminary.kicad_sch').read_text()).group(1)
for net in r.findall('nets/net'):
 n=k.NETINFO_ITEM(b,net.get('name'));b.Add(n);nets[net.get('name')]=n
special={'U1':(70,70),'U2':(140,55),'U3':(180,55),'J1':(75,135),'J2':(75,165),'J3':(165,135),'J4':(165,165),'J10':(140,95),'U20':(180,95)}
i=0
for comp in r.findall('components/comp'):
 ref=comp.get('ref');name=comp.findtext('footprint').split(':')[1];f=k.FootprintLoad(str((p/'SOM.pretty').resolve()),name);assert f, name
 f.SetReference(ref);f.SetValue(comp.findtext('value'));f.SetFPID(k.LIB_ID('SOM',name))
 path=k.KIID_PATH()
 for v in [rootid]+comp.find('sheetpath').get('tstamps').strip('/').split('/')+[comp.findtext('tstamps').split()[0]]:path.push_back(k.KIID(v))
 f.SetPath(path)
 for prop in comp.findall('property'):
  if prop.get('name')=='Sheetfile':f.SetSheetfile(prop.get('value'))
  if prop.get('name')=='Sheetname':f.SetSheetname(prop.get('value'))
 if ref in special:x,y=special[ref]
 else:x,y=30+(i%12)*18,215+(i//12)*12;i+=1
 f.SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)));b.Add(f);fps[ref]=f
 for pad in f.Pads():
  for net in []:pass
for net in r.findall('nets/net'):
 for node in net.findall('node'):
  f=fps[node.get('ref')];matches=[pad for pad in f.Pads() if pad.GetNumber()==node.get('pin')]
  for pad in matches:pad.SetNet(nets[net.get('name')])
  if not matches:missing.append({'ref':node.get('ref'),'pin':node.get('pin'),'net':net.get('name')})
t=k.PCB_TEXT(b);t.SetText('COMPONENT STAGING ONLY - NO BOARD OUTLINE\nPadless envelopes marked PLACEMENT_ONLY must be replaced.\nCircuit incomplete; stock footprints are package candidates.');t.SetLayer(k.Dwgs_User);t.SetPosition(k.VECTOR2I(k.FromMM(30),k.FromMM(190)));t.SetTextSize(k.VECTOR2I(k.FromMM(1.4),k.FromMM(1.4)));b.Add(t)
k.SaveBoard(str(p/'x86-som-preliminary.kicad_pcb'),b)
loaded=k.LoadBoard(str(p/'x86-som-preliminary.kicad_pcb'));assert len(loaded.GetFootprints())==len(fps)
report={'components':len(fps),'padless_references':[ref for ref,f in fps.items() if len(list(f.Pads()))==0],'missing_pad_nodes':missing,'tracks':len(loaded.GetTracks()),'note':'Missing pads on placement envelopes are expected; not routing ready.'}
(p/'placement-validation.json').write_text(json.dumps(report,indent=2));print({key:value for key,value in report.items() if key!='missing_pad_nodes'});print('Missing pad nodes:',len(missing))
