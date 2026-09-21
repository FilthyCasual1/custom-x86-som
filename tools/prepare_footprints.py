import pathlib,json,shutil
p=pathlib.Path('hardware'); dest=p/'SOM.pretty';dest.mkdir(exist_ok=True)
stock={
'R':'Resistor_SMD:R_0603_1608Metric','C':'Capacitor_SMD:C_0603_1608Metric',
'DDR4_SODIMM_260':'Connector_PCBEdge:SODIMM-260_DDR4_H4.0-5.2_OrientationStd_Socket',
'TPS51200':'Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm',
'SPI_NOR_8':'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
'EPS12V':'Connector_Molex:Molex_Mini-Fit_Jr_5566-08A_2x04_P4.20mm_Vertical',
'I219_reference':'Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.4x4.4mm'}
m={};report={}
for lib,fp in stock.items():
 folder,name=fp.split(':');src=pathlib.Path('/usr/share/kicad/footprints')/(folder+'.pretty')/(name+'.kicad_mod')
 assert src.exists(),src
 shutil.copyfile(src,dest/src.name);m[lib]='SOM:'+name
 report[lib]={'footprint':m[lib],'status':'Stock KiCad footprint; exact purchased part and pad mapping require review','source':fp}
for lib,w,h in [('CoffeeLake_LGA1151',78,78),('Q370_draft',23,24),('AST2500_host_draft',23,23),('ISL95866_reference',6,6),('L',8,8),('FUSE',10,6),('XTAL',8,5)]:
 name=lib+'_PLACEMENT_ONLY';m[lib]='SOM:'+name
 s=f'''(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu")
 (descr "UNVERIFIED envelope only; no pads; replace before routing or fabrication")
 (attr smd exclude_from_pos_files exclude_from_bom)
 (fp_text reference "REF**" (at 0 {-h/2-2}) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))
 (fp_text value "{name}" (at 0 {h/2+2}) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))
 (fp_rect (start {-w/2} {-h/2}) (end {w/2} {h/2}) (stroke (width .15) (type default)) (fill none) (layer "F.Fab"))
 (fp_rect (start {-w/2-.5} {-h/2-.5}) (end {w/2+.5} {h/2+.5}) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))
 (fp_text user "NO PADS - ENVELOPE ONLY" (at 0 0) (layer "F.Fab") (effects (font (size .6 .6) (thickness .1)))))'''
 (dest/(name+'.kicad_mod')).write_text(s)
 report[lib]={'footprint':m[lib],'status':'Unverified placement-only envelope, NO PADS','assumed_envelope_mm':[w,h]}
(p/'footprint-map.json').write_text(json.dumps(m,indent=2));(p/'footprint-status.json').write_text(json.dumps(report,indent=2))
(p/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "SOM") (type "KiCad") (uri "${KIPRJMOD}/SOM.pretty") (options "") (descr "Stock candidates and clearly marked padless placement envelopes")))')
f=pathlib.Path('tools/build_preliminary.py');s=f.read_text();s=s.replace('rootid=uid(); project=',"footprints=json.loads((OUT/'footprint-map.json').read_text())\nrootid=uid(); project=")
s=s.replace('(property "Footprint" "" (at {x}', '(property "Footprint" {q(footprints.get(lib,""))} (at {x}')
f.write_text(s)
