import pathlib,json,shutil,re
P=pathlib.Path;out=P('hardware');dest=out/'SOM.pretty';m=json.loads((out/'footprint-map.json').read_text());status=json.loads((out/'footprint-status.json').read_text())
def make(name,w,h,pads,desc):
 s=f'(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (descr {json.dumps(desc)}) (attr smd)\n'
 s+=f'(fp_text reference "REF**" (at 0 {-h/2-1.5}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))\n(fp_text value "{name}" (at 0 {h/2+1.5}) (layer "F.Fab") (effects (font (size .8 .8) (thickness .12))))\n'
 for layer,margin,width in [('F.Fab',0,.1),('F.CrtYd',.5,.05)]:s+=f'(fp_rect (start {-w/2-margin} {-h/2-margin}) (end {w/2+margin} {h/2+margin}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))\n'
 s+=f'(fp_circle (center {-w/2} {-h/2}) (end {-w/2+.25} {-h/2}) (stroke (width .15) (type default)) (fill none) (layer "F.SilkS"))\n'
 for n,x,y,a,b,shape,layers in pads:s+=f'(pad "{n}" smd {shape} (at {x:.5f} {y:.5f}) (size {a} {b}) (layers {layers}))\n'
 (dest/(name+'.kicad_mod')).write_text(s+')');return 'SOM:'+name
def qfn(n,ep,l,w,c):
 pads=[];side=n//4
 for i in range(side):
  t=(i-(side-1)/2)*.4
  for num,x,y,a,b in [(i+1,-c,t,l,w),(side+i+1,t,c,w,l),(2*side+i+1,c,-t,l,w),(3*side+i+1,-t,-c,w,l)]:pads.append((num,x,y,a,b,'rect','"F.Cu" "F.Paste" "F.Mask"'))
 pads.append((n+1,0,0,ep,ep,'rect','"F.Cu" "F.Mask"'))
 # Windowed paste avoids a single large solder deposit.
 sz=ep*.45
 for x in [-ep/4,ep/4]:
  for y in [-ep/4,ep/4]:pads.append(('',x,y,sz,sz,'rect','"F.Paste"'))
 return pads
m['ISL95866_reference']=make('Renesas_L52_6x6A_QFN52_EP4.7',6,6,qfn(52,4.7,.55,.2,2.875),'Renesas L52.6x6A Rev03 2026-05-28 recommended land pattern: 0.4 pitch; 0.55x0.20 pads; EP4.70; paste implementation chosen for assembly review')
status['ISL95866_reference']={'footprint':m['ISL95866_reference'],'status':'Copper land dimensions checked against manufacturer recommended pattern; package-to-device association donor-derived','source':'docs/reference/renesas-l52.pdf'}
m['I219_reference']=make('Intel_I219_QFN48_EP3',6,6,qfn(48,3,.6,.2,2.9),'Intel I219 Fig4-1 EP3x3; pitch0.4; leadwidth0.2. Peripheral land extension0.1 each end is engineering choice; paste4x1.35 from section13.3.2.4; thermal vias still needed')
status['I219_reference']={'footprint':m['I219_reference'],'status':'Corrected to manufacturer package: EP3x3 and0.4 pitch; land extension and thermal vias require assembly review','source':'docs/reference/i219.pdf pp41,254'}
rows='A B C D E F G H J K L M N P R T U V W Y AA AB'.split();pins=json.loads(P('research/ast-full-map.json').read_text());assert len(pins)==456
pads=[]
for p in pins:
 row,col=re.fullmatch('([A-Z]+)([0-9]+)',p['pin']).groups();pads.append((p['pin'],(int(col)-11.5)*.8,(rows.index(row)-10.5)*.8,.35,.35,'circle','"F.Cu" "F.Paste" "F.Mask"'))
m['AST2500_host_draft']=make('ASPEED_AST2500A2_GP_BGA456_19x19_P0.8',19,19,pads,'AST2500A2-GP package drawing PC00020 and top-view ball maps pp77-78,124; 456 balls; 19mm body;0.8 pitch. Copper diameter0.35 is provisional NSMD choice, not a manufacturer recommended land pattern.')
status['AST2500_host_draft']={'footprint':m['AST2500_host_draft'],'status':'456-ball occupancy and0.8 pitch checked against package; copper diameter0.35 remains provisional','source':'docs/reference/ast2500-datasheet.pdf pp77-78,124'}
for key,fp in {'L':'Inductor_SMD:L_Coilcraft_LPS4018','FUSE':'Fuse:Fuse_Littelfuse-NANO2-451_453','XTAL':'Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm','ABM8':'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm'}.items():
 folder,name=fp.split(':');shutil.copyfile(P('/usr/share/kicad/footprints')/(folder+'.pretty')/(name+'.kicad_mod'),dest/(name+'.kicad_mod'));m[key]='SOM:'+name;status[key]={'footprint':m[key],'status':'Specific package candidate; electrical rating/load capacitance not approved','source':fp}
status['DDR4_SODIMM_260'].update(status='TE2309407 Rev5 PCB drawing checked:260contacts,0.5pitch,8.2rowspacing,0.3x1.75lands,3.5x4.6anchors; stock contact pad length corrected from1.7 to1.75',source='docs/reference/te-2309407.pdf sheet2')
f=dest/(m['DDR4_SODIMM_260'].split(':')[1]+'.kicad_mod');f.write_text(f.read_text().replace('(size 0.3 1.7)','(size 0.3 1.75)'))
# Preserve an honest socket envelope until solder-ball numbering mapping is verified.
f=dest/'CoffeeLake_LGA1151_PLACEMENT_ONLY.kicad_mod';s=f.read_text().replace('78','78');status['CoffeeLake_LGA1151'].update(manufacturer='Foxconn',mpn='PE115127-4041-01H',source='docs/reference/foxconn-lga1151.pdf sheet1',status='Manufacturer socket drawing obtained; 1151 socket solder-ball numbering map not yet verified. Padless envelope retained; do not route.')
status['Q370_draft'].update(status='Manufacturer confirms23x24 package; 874ball map recovered. Pitch/land dimensions unresolved; padless envelope retained.')
(out/'footprint-map.json').write_text(json.dumps(m,indent=2));(out/'footprint-status.json').write_text(json.dumps(status,indent=2))
catalog={
'CoffeeLake_LGA1151':('Foxconn','PE115127-4041-01H','docs/reference/foxconn-lga1151.pdf','Socket, CPU SKU separate; solder-ball mapping incomplete'),
'DDR4_SODIMM_260':('TE Connectivity','2309407-1','docs/reference/te-2309407.pdf','4mm standard orientation; 260contacts; gold flash; drawing verified'),
'EPS12V':('Molex','39-28-1083','https://www.molex.com/en-us/products/part-detail/39281083','Candidate header; EPS keying and numbering not yet verified'),
'Q370_draft':('Intel','FH82Q370','https://www.intel.com/content/www/us/en/products/sku/133282/intel-q370-chipset/specifications.html','Ordering suffix and land pattern unresolved'),
'AST2500_host_draft':('ASPEED','AST2500A2-GP','docs/reference/ast2500-datasheet.pdf','456balls;19x19;0.8mm'),
'ISL95866_reference':('Renesas','ISL95866HRZ-T','docs/reference/renesas-l52.pdf','Donor reference; obsolete; replacement not selected'),
'I219_reference':('Intel','WGI219LM','docs/reference/i219.pdf','Exact Q370-compatible stepping/order code still required'),
'TPS51200':('Texas Instruments','TPS51200DRCR','docs/reference/tps51200.pdf','DRC VSON10+EP; tape/reel'),
'L':('Coilcraft','LPS4018-472MRC','https://www.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum/lps/lps4018/lps4018-472/','4.7uH candidate; current/ripple check pending'),
'FUSE':('Littelfuse','0451015.MRL','https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1','15A package candidate only; system protection rating not approved'),
'XTAL':('Abracon','ABS07-32.768KHZ-7-T','https://abracon.com/Resonators/ABS07.pdf','7pF candidate; RTC load/startup check pending'),
'ABM8':('Abracon','ABM8-25.000MHZ-D2Y-T','https://abracon.com/Resonators/abm8.pdf','18pF candidate; oscillator validation required'),
'SPI_NOR_8':('Unselected','TBD','', 'Flash voltage/capacity and BIOS compatibility unresolved; do not buy a generic substitute'),
'R':('Unselected','TBD','','0603 template; exact value/tolerance/rating selects MPN'),
'C':('Unselected','TBD','','0603 template; bulk capacitance and DC bias may require larger package')}
cat={k:dict(zip(['Manufacturer','MPN','Datasheet','Status'],v),Footprint=m[k])for k,v in catalog.items()};(out/'parts-catalog.json').write_text(json.dumps(cat,indent=2))
# Add instance metadata and full ABM8 pin mapping to the generation source.
f=P('tools/build_preliminary.py');s=f.read_text();s=s.replace("rootid=uid(); project=", "catalog=json.loads((OUT/'parts-catalog.json').read_text())\nrootid=uid(); project=")
s=s.replace("path=f'/{rootid}/{self.sheetid}'", "for key in ['Manufacturer','MPN','Datasheet','Status']:\n   props+=f'(property {q(key)} {q(catalog.get(lib,{}).get(key,\"\"))} (at {x} {y} 0) {eff(1,\"hide\")})'\n  path=f'/{rootid}/{self.sheetid}'")
f.write_text(s)
f=P('tools/extra_circuits.py');s=f.read_text();s=s.replace("s.part('XTAL','Y2','25MHz / CL TBD',365,160,'HOST_XTAL_OUT','HOST_XTAL_IN')", "define('ABM8',[[pin(1,'XTAL1'),pin(2,'GND'),pin(3,'XTAL2'),pin(4,'GND')]],'Abracon ABM8 datasheet',value='ABM8-25.000MHZ-D2Y-T',width=10.16)\ns.symbol('ABM8','Y2',365,160,{'1':'HOST_XTAL_OUT','2':'GND','3':'HOST_XTAL_IN','4':'GND'})")
f.write_text(s)
