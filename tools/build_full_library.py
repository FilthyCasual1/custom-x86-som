"""Generate complete pin-inventory symbols separately from the partial electrical schematic."""
import runpy,json,pathlib,re
P=pathlib.Path;g=runpy.run_path('tools/build_preliminary.py');define=g['define'];libs=g['libs'];q=g['q'];eff=g['eff'];cat=json.loads(P('hardware/parts-catalog.json').read_text())
for key,file,expected,name in [('Q370_draft','pch-full-map',874,'FH82Q370'),('AST2500_host_draft','ast-full-map',456,'AST2500A2_GP')]:
 pins=json.loads(P('research/'+file+'.json').read_text());assert len(pins)==expected and len({p['pin']for p in pins})==expected
 # Keep every individual supply ball accessible. No implicit global connections.
 pins=sorted(pins,key=lambda p:(re.sub('[0-9]','',p['pin']),int(re.search('[0-9]+',p['pin'])[0])))
 for p in pins:p['type']='passive'
 define(name,[pins[i:i+80]for i in range(0,len(pins),80)],cat[key]['Datasheet'],value=cat[key]['MPN']);cat[name]=cat[key]
entries=[];audit=[]
for key,spec in libs.items():
 if key=='AST2500_ddr_draft':continue
 meta=cat.get(key,{});s=spec['sexp'];insert=''
 for field in ['Manufacturer','MPN','Footprint','Status']:
  insert+=f'(property {q(field)} {q(meta.get(field,""))} (at 0 0 0) {eff(1,"hide")})\n'
 # Main project symbols keep compatibility names; complete inventory variants above are separate.
 s=s[:-1]+insert+')';entries.append(s)
 audit.append({'symbol':key,'pin_count':sum(len(u['pins'])for u in spec['units']),'units':len(spec['units']),**meta})
P('hardware/SOM_Full.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+'\n'.join(entries)+')')
P('hardware/library-inventory.json').write_text(json.dumps(audit,indent=2))
f=P('hardware/sym-lib-table');s=f.read_text();s=s[:-1]+' (lib (name "SOM_Full") (type "KiCad") (uri "${KIPRJMOD}/SOM_Full.kicad_sym") (options "") (descr "Full pin inventories with manufacturer and package status")))';f.write_text(s)
print('Library entries',len(entries));print([(x['symbol'],x['pin_count'])for x in audit if x['symbol']in ['CoffeeLake_LGA1151','FH82Q370','AST2500A2_GP']])
