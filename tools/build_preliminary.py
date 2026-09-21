"""Generate editable, source-traceable KiCad schematic. No PCB/fabrication claims."""
import json,re,uuid,math,pathlib,collections
P=pathlib.Path; OUT=P('hardware'); OUT.mkdir(exist_ok=True)
def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s))
def eff(size=1.0,extra=''):return f'(effects (font (size {size} {size})) {extra})'
def natural(s):return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)',s)]
libs={}; instances=[]; sheetlist=[]; audit=[]; pending=[]
footprints=json.loads((OUT/'footprint-map.json').read_text())
catalog=json.loads((OUT/'parts-catalog.json').read_text())
rootid=uid(); project='x86-som-preliminary'
class Sheet:
 def __init__(self,name,title,notes):
  self.name=name;self.title=title;self.id=uid();self.sheetid=uid();self.items=[];self.used=set();sheetlist.append(self)
  self.text(title,15,15,2.5)
  self.text('PRELIMINARY v0.1 - electrically incomplete; not for fabrication',15,21,1.5)
  for i,t in enumerate(notes):self.text(t,15,29+i*5,1.15)
 def text(self,s,x,y,size=1.0):self.items.append(f'(text {q(s)} (at {x} {y} 0) {eff(size,"(justify left)")} (uuid {q(uid())}))')
 def wire(self,x1,y1,x2,y2):self.items.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid {q(uid())}))')
 def label(self,s,x,y,angle=0):self.items.append(f'(global_label {q(s)} (shape bidirectional) (at {x} {y} {angle}) {eff(.9,"(justify left)" if angle==0 else "(justify right)")} (uuid {q(uid())}))')
 def nc(self,x,y):self.items.append(f'(no_connect (at {x} {y}) (uuid {q(uid())}))')
 def symbol(self,lib,ref,x,y,nets,unit=1,value=None):
  x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
  spec=libs[lib];u=spec['units'][unit-1];self.used.add(lib);iid=uid()
  val=value or spec['value'];h=u['height']
  props=f'(property "Reference" {q(ref)} (at {x} {y-5} 0) {eff(1.4)}) (property "Value" {q(val)} (at {x} {y-2} 0) {eff(1.2)})'
  props+=f'(property "Footprint" {q(footprints.get(lib,""))} (at {x} {y} 0) {eff(1,"hide")})'
  for key in ['Manufacturer','MPN','Datasheet','Status']:
   props+=f'(property {q(key)} {q(catalog.get(lib,{}).get(key,""))} (at {x} {y} 0) {eff(1,"hide")})'
  path=f'/{rootid}/{self.sheetid}'
  self.items.append(f'(symbol (lib_id {q("SOM:"+lib)}) (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid {q(iid)}) {props} (instances (project {q(project)} (path {q(path)} (reference {q(ref)}) (unit {unit})))))')
  seen=set()
  for p in u['pins']:
   px=x+p['x'];py=y-p['y'];net=nets.get(p['pin']);audit.append(dict(ref=ref,pin=p['pin'],name=p['name'],net=net,sheet=self.name,source=spec['source']))
   loc=(px,py)
   if loc in seen:continue
   seen.add(loc)
   if net=='NC':self.nc(px,py)
   elif net:
    end=px+(-10.16 if p['x']<0 else 10.16);self.wire(px,py,end,py);self.label(net,end,py,0 if p['x']<0 else 180)
   else:pending.append(dict(ref=ref,pin=p['pin'],name=p['name'],sheet=self.name))
 def part(self,kind,ref,value,x,y,a,b,source='Provisional value; see sheet notes'):
  self.symbol(kind,ref,x,y,{'1':a,'2':b},value=value)
 def save(self):
  definitions='\n'.join(libs[k]['sexp'].replace('(symbol '+q(k),'(symbol '+q('SOM:'+k),1) for k in sorted(self.used))
  s=f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(self.id)}) (paper "A2") (title_block (title {q(self.title)}) (rev "0.1-PRELIMINARY") (comment 1 "NOT FOR FABRICATION - see open-items.md")) (lib_symbols {definitions}) '+ '\n'.join(self.items)+')'
  (OUT/(self.name+'.kicad_sch')).write_text(s)
def define(name,units,source,value=None,width=66.04):
 allpins=[];us=[];sx=[f'(symbol {q(name)} (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 5 0) {eff()}) (property "Value" {q(value or name)} (at 0 2 0) {eff()}) (property "Datasheet" {q(source)} (at 0 0 0) {eff(1,"hide")} )']
 for n,pins in enumerate(units,1):
  # Stack supply pins only when explicitly requested by same group.
  groups=[];by={}
  for p in pins:
   p=dict(p);key=p.get('stack',p['pin'])
   if key not in by:by[key]=len(groups);groups.append([])
   groups[by[key]].append(p)
  half=math.ceil(len(groups)/2);height=max(10.16,(half+1)*3.81);placed=[]
  body=f'(symbol {q(name+"_"+str(n)+"_1")} (rectangle (start {-width/2} 0) (end {width/2} {-height}) (stroke (width .254) (type default)) (fill (type background)))'
  # append pins within the unit definition
  # unit remains open after rectangle
  for k,group in enumerate(groups):
   side=-1 if k<half else 1;row=k if k<half else k-half;xx=side*(width/2+5.08);yy=-(row+1)*3.81
   for j,p in enumerate(group):
    p.update(x=xx,y=yy);placed.append(p);label=p['name'] if j==0 else p['name'];hide='hide' if j else ''
    typ=p.get('type','passive') if j==0 else 'passive';label=(p.get('stack')+' ['+str(len(group))+']') if len(group)>1 and j==0 else label
    body+=f'(pin {typ} line (at {xx} {yy} {0 if side<0 else 180}) (length 5.08) {hide} (name {q(label)} {eff(.95)}) (number {q(p["pin"])} {eff(.85)}))'
  body+=')';sx.append(body);us.append(dict(pins=placed,height=height));allpins+=placed
 sx.append(')');libs[name]=dict(sexp='\n'.join(sx),units=us,source=source,value=value or name)
 assert len({p['pin'] for p in allpins})==len(allpins),(name,'duplicate pins')
def pin(n,name,typ='passive',**kw):return dict(pin=str(n),name=name,type=typ,**kw)
# Standard two-terminal components, kept native/editable.
for kind in ['R','C','L','FUSE','XTAL']:
 define(kind,[[pin(1,'1'),pin(2,'2')]],'Conventional two-terminal symbol',width=10.16)
 # Replace the generic body by a conventional outline for R/C.
 if kind in ['R','C']:
  geom='(polyline (pts (xy -2.54 -3.81) (xy -5.08 -3.81)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy 2.54 -3.81) (xy 5.08 -3.81)) (stroke (width 0) (type default)) (fill (type none)))'
  if kind=='R':geom+='(rectangle (start -2.54 -5.08) (end 2.54 -2.54) (stroke (width .254) (type default)) (fill (type none)))'
  else:geom+=''.join(f'(polyline (pts (xy {x} -6.35) (xy {x} -1.27)) (stroke (width .254) (type default)) (fill (type none)))' for x in [-.635,.635])+ '(polyline (pts (xy -2.54 -3.81) (xy -.635 -3.81)) (stroke (width 0) (type default)) (fill (type none))) (polyline (pts (xy .635 -3.81) (xy 2.54 -3.81)) (stroke (width 0) (type default)) (fill (type none)))'
  libs[kind]['sexp']=re.sub(r'\(rectangle \(start .*?\(fill \(type background\)\)\)',geom,libs[kind]['sexp'],count=1)
# CPU complete source pin map; DDR4 interpretation of multiplexed pins explicit.
cpu=json.loads(P('research/cpu-pin-extraction.json').read_text())
for p in cpu:
 n=p['name']
 if n.startswith(('DDR0','DDR1')):
  if any(s in n for s in ['_MA[','_BA[','_RAS#','_CAS#','_WE#']):n=n.split('/')[-1]
  else:n=n.split('/')[0]
 p['original_name']=p['name'];p['name']=n
cpu_groups=collections.OrderedDict((k,[])for k in ['control','peg','ddr_a','ddr_b','display','power','unused'])
for p in cpu:
 n=p['name'];k='unused'
 if n.startswith(('VCC','VSS','VDDQ')) and n!='VCCST_PWRGD':k='power'
 elif n.startswith('DDR0'):k='ddr_a'
 elif n.startswith('DDR1'):k='ddr_b'
 elif n.startswith(('PEG_RX','PEG_TX','PEG_COMP')):k='peg'
 elif n.startswith(('DDI','EDP','DP_COMP','PROC_AUDIO')):k='display'
 elif p['page']==4 and not n.startswith(('NOA','MBP')):k='control'
 elif n=='DDR_VREF_CA':k='control'
 if k=='power' and not 'SENSE' in n:
  if n.startswith('VDDQ'):p['stack']='VDDQ'
  elif n.startswith('VCC_') and not n.startswith(('VCC_PLL','VCC_SENSE')):p['stack']='VCC'
  elif n.startswith('VSS'):p['stack']='VSS'
  else:p['stack']=n
  p['type']='power_in'
 cpu_groups[k].append(p)
# Split unused pins for readable units, and power by grouped supply.
cpu_units=[cpu_groups[k] for k in list(cpu_groups)[:-1]]+[cpu_groups['unused'][i:i+100]for i in range(0,len(cpu_groups['unused']),100)]
define('CoffeeLake_LGA1151',cpu_units,'H310M-S2P 2.0 Rev1.0 sheets 4-7; extracted 1151 pins',value='Coffee Lake-S / LGA1151')
# PCH use only reviewed functional pin names; unused GPIO aliases remain outside draft symbol.
pch=json.loads(P('research/pch-pin-extraction.json').read_text());pm={p['name']:p for p in pch};pb={p['pin']:p for p in pch}
def getpch(name):return dict(pm[name])
pch_ctrl_names=['CPUPWRGD','PLTRST_CPU#','PM_SYNC','PM_DOWN','PECI','THRMTRIP#','DRAM_RESET#','CLKOUT_CPUBCLK_P','CLKOUT_CPUBCLK_N','CLKOUT_CPUPCIBCLK_P','CLKOUT_CPUPCIBCLK_N','CLKOUT_CPUNSSC_P','CLKOUT_CPUNSSC_N']+[f'DMI{i}_{d}{s}'for i in range(4)for d in ['RX','TX']for s in ['P','N']]
pch_ctrl=[getpch(n)for n in pch_ctrl_names]
pch_pcie=[p for p in pch if re.fullmatch(r'PCIE\d+_(RX|TX)[NP]',p['name'])]
pch_boot=[getpch(n)for n in ['SPI0_CLK','SPI0_CS0#','SPI0_MISO','SPI0_MOSI','SPI0_IO2','SPI0_IO3','RTCX1','RTCX2','RTCRST#','SRTCRST#','RSMRST#','DSW_PWROK','SYS_PWROK','SYS_RESET#','CLKIN_XTAL']]
# Explicit aliases, verified against Intel ballout table.
for n,b in [('LAD0','BB39'),('LAD1','AW37'),('LAD2','AV37'),('LAD3','BA38'),('LFRAME#','BE38'),('SERIRQ','AW35'),('LPC_CLK','BB34'),('PLTRST#','AV29'),('PWRBTN#','BE46'),('SLP_S3#','BF42'),('SLP_S4#','BE42'),('SLP_S5#','BC42'),('SMBCLK','BE26'),('SMBDATA','BF26')]:
 if b in pb: pch_boot.append(pin(b,n))
# SMB pins corrected below from table, not assumed generic GPIO numbers.
for p in pch_boot:
 if p['name']=='SMBCLK':p['pin']='BE26'
 if p['name']=='SMBDATA':p['pin']='BF26'
pch_io=[p for p in pch if re.fullmatch(r'USB2[NP]_\d+',p['name'])]+[p for p in pch if re.fullmatch(r'CLKOUT_PCIE_[NP]\d+',p['name'])]
pch_power=[dict(p,stack=p['name'],type='power_in') for p in pch if p['name'].startswith(('VCC','VSS','DCPRTC'))]
# Do not conflate sense and internally generated supplies with external outputs.
for p in pch_power:
 if any(x in p['name'] for x in ['SENSE','DCPRTC','VCCDPHY','VCCDSW_1P05','VCCPHVLDO']):p['type']='passive'
define('Q370_draft',[pch_ctrl,pch_pcie,pch_boot,pch_io,pch_power],'Intel 337347-009 Table 11-1; partial functional symbol; remaining GPIO/HSIO omitted',value='Intel Q370 / draft pin subset')
# DIMM complete 260 contact map: 4 manually checked wrapped labels added.
dimm=json.loads(P('research/sodimm-pin-extraction.json').read_text())
dimm +=[pin(164,'VREFCA'),pin(257,'VPP1'),pin(259,'VPP2'),pin(258,'VTT')]
ds=[];dp=[]
for p in dimm:
 if p['name'].startswith(('VDD','VSS','VPP','VTT','VREF')):
  p=dict(p,stack=re.sub(r'\d+$','',p['name']) if p['name']!='VDDSPD' else p['name']);dp.append(p)
 else:ds.append(p)
define('DDR4_SODIMM_260',[ds,dp],'GL703GE Rev1A sheet19 connector symbol; no source-board DQ swaps copied',value='260-pin DDR4 SO-DIMM')
# Primary datasheet AST2500 interfaces used in this pass. Remaining supplies/DDR are explicit TODO.
astpairs={'L20':'PERST#','K21':'PEREFCLKP','K22':'PEREFCLKN','M21':'PERXP','M22':'PERXN','L21':'PETXP','L22':'PETXN','K20':'PEREXT','G21':'LAD0','G20':'LAD1','D22':'LAD2','E22':'LAD3','C22':'LCLK','F21':'LFRAME#','F22':'SERIRQ','G22':'LPCRST#','AB19':'FWSPICS0#','AA18':'FWSPICK','U17':'FWSPIMOSI','T18':'FWSPIMISO','U18':'SRST#','V18':'EXTRST#','W18':'CLKIN','K3':'ENTEST','A7':'USB2A_DP','A8':'USB2A_DN','B8':'USB2AVRES'}
astpins=[pin(b,n)for b,n in astpairs.items()]
define('AST2500_host_draft',[astpins],'ASPEED AST2500 A2 v1.6 pp52-53,58,68-69; partial symbol',value='AST2500 host/boot subset')
define('SPI_NOR_8',[[pin(1,'CS#'),pin(2,'DO_IO1'),pin(3,'WP#_IO2'),pin(4,'GND','power_in'),pin(5,'DI_IO0'),pin(6,'CLK'),pin(7,'HOLD#_IO3'),pin(8,'VCC','power_in')]],'Common SPI NOR 8-pin mapping; exact device/capacity/voltage not frozen',value='SPI NOR / capacity TBD')
define('TPS51200',[[pin(1,'REFIN'),pin(2,'VLDOIN','power_in'),pin(3,'VO','power_out'),pin(4,'PGND','power_in'),pin(5,'VOSNS'),pin(6,'REFOUT','output'),pin(7,'EN','input'),pin(8,'GND','power_in'),pin(9,'PGOOD','open_collector'),pin(10,'VIN','power_in'),pin(11,'EP','power_in')]],'TI TPS51200 pin table; DRC exposed pad',value='TPS51200DRC')
# Connector is exact EPS electrical pin numbering, physical footprint not selected.
define('EPS12V',[[pin(i,'GND' if i<=4 else '+12V')for i in range(1,9)]],'EPS12V 8-pin electrical convention; keying/footprint audit pending',value='EPS12V 8-pin')
# Net mapping
cpu_nets={}
for p in cpu:
 n=p['name'];net=None
 if n.startswith(('DDR0_','DDR1_')):
  ch='A' if n.startswith('DDR0') else 'B';s=n[5:];s=s.replace('MA[','A[').replace('CS#[','CS[').replace('PAR','PARITY');net=f'DDR_{ch}_{s}'
  if 'ECC' in s or re.match(r'DQS[NP]\[8\]',s):net='NC'
 elif n.startswith('DMI_'):
  m=re.match(r'DMI_(RX|TX)([PN])\[(\d+)\]',n)
  if m:net=f'DMI_CPU_{m[1]}_{m[3]}{m[2]}'
 elif n.startswith(('PEG_RX','PEG_TX')):
  m=re.match(r'PEG_(RX|TX)([PN])\[(\d+)\]',n);net=f'PEG_{m[1]}_{m[3]}{m[2]}'
 elif p in cpu_groups['power']:
  base=p.get('stack',n);net={'VSS':'GND','VCC':'CPU_VCORE','VCCGT':'CPU_VCCGT','VCCSA':'CPU_VCCSA','VCCIO':'CPU_VCCIO','VDDQ':'DDR_1V2'}.get(base,'CPU_'+base)
 elif n.startswith(('DDI','EDP','PROC_AUDIO')):net='CPU_'+n
 else:net={'BCLKP':'CPU_BCLK_P','BCLKN':'CPU_BCLK_N','PCI_BCLKP':'CPU_PEG_CLK_P','PCI_BCLKN':'CPU_PEG_CLK_N','CLK24P':'CPU_24M_P','CLK24N':'CPU_24M_N','PROCPWRGD':'CPU_PWRGD','RESET#':'CPU_RESET#','PECI':'PECI','PM_SYNC':'PM_SYNC','PM_DOWN':'PM_DOWN','THERMTRIP#':'THERMTRIP#','VIDALERT#':'CPU_SVID_ALERT#','VIDSCK':'CPU_SVID_CLK','VIDSOUT':'CPU_SVID_DATA','VCCST_PWRGD':'CPU_VCCST_PWRGD','PROCHOT#':'PROCHOT#','DDR_VTT_CNTL':'DDR_VTT_EN','DDR_VREF_CA':'DDR_VREFCA','PEG_COMP':'CPU_PEG_COMP','DP_COMP':'CPU_DP_COMP'}.get(n)
 cpu_nets[p['pin']]=net
pchnets={}
for p in pch_ctrl:
 n=p['name'];net={'CPUPWRGD':'CPU_PWRGD','PLTRST_CPU#':'CPU_RESET#','PM_SYNC':'PM_SYNC','PM_DOWN':'PM_DOWN','PECI':'PECI','THRMTRIP#':'THERMTRIP#','DRAM_RESET#':'DDR_RESET#','CLKOUT_CPUBCLK_P':'CPU_BCLK_P','CLKOUT_CPUBCLK_N':'CPU_BCLK_N','CLKOUT_CPUPCIBCLK_P':'CPU_PEG_CLK_P','CLKOUT_CPUPCIBCLK_N':'CPU_PEG_CLK_N','CLKOUT_CPUNSSC_P':'CPU_24M_P','CLKOUT_CPUNSSC_N':'CPU_24M_N'}.get(n)
 m=re.match(r'DMI(\d)_(RX|TX)([PN])',n)
 if m:net=f'DMI_CPU_{"TX" if m[2]=="RX" else "RX"}_{m[1]}{m[3]}'
 pchnets[p['pin']]=net
for p in pch_boot:
 n=p['name'];net={'SPI0_CLK':'HOST_SPI_CLK','SPI0_CS0#':'HOST_SPI_CS#','SPI0_MISO':'HOST_SPI_MISO','SPI0_MOSI':'HOST_SPI_MOSI','SPI0_IO2':'HOST_SPI_IO2','SPI0_IO3':'HOST_SPI_IO3','LPC_CLK':'LPC_CLK','CLKIN_XTAL':'PCH_XTAL_IN'}.get(n,n)
 pchnets[p['pin']]=net
# Provisional allocation uses controller1 lanes1-4 with lane1 sacrificed for GbE;
# controller2 lanes5-8 x1 (lane5 BMC); controller3 lanes9-12 x1; 13-24 = 3 x4.
for p in pch_pcie:
 m=re.match(r'PCIE(\d+)_(RX|TX)([PN])',p['name']);i=int(m[1]);d=m[2];pol=m[3]
 if i==6:net=f'BMC_{"TX" if d=="RX" else "RX"}_{pol}_PCH'
 elif i==5:net=f'HOST_LAN_{d}_{pol}'
 else:net=f'PCH_PCIE{i}_{d}_{pol}'
 pchnets[p['pin']]=net
for p in pch_io:
 n=p['name'];net='EXPORT_'+n
 if n in ['USB2P_1','USB2N_1']:net='BMC_USB_'+('P'if n=='USB2P_1'else'N')
 if n in ['CLKOUT_PCIE_P0','CLKOUT_PCIE_N0']:net='BMC_REFCLK_'+('P'if '_P' in n else'N')
 pchnets[p['pin']]=net
for p in pch_power:
 n=p['name'];pchnets[p['pin']]='GND' if n=='VSS' else 'PCH_'+n
# Pages
s=Sheet('01_cpu_platform','CPU / Q370 DMI, clocks and sideband',['Sources: H310M-S2P sheets4-7; Intel 337347 ballout. CPU RX connects PCH TX and vice versa.','DMI is direct as in board reference; package coupling must be checked against the Coffee Lake design guide.'])
s.symbol('CoffeeLake_LGA1151','U1',110,60,cpu_nets,1);s.symbol('Q370_draft','U2',350,60,pchnets,1)
s.text('Open: platform pull networks, CPU strap aliases, debug termination and power-good sequencing.',20,335,1.4)
s=Sheet('02_cpu_peg','CPU PEG / two x8 carrier links',['Lanes0-7 -> PEG_A x8; lanes8-15 -> PEG_B x8. Connector contact numbers remain open.','CPU TX coupling shown below as 100nF candidates; validate placement/value against design guide.'])
s.symbol('CoffeeLake_LGA1151','U1',100,60,cpu_nets,2)
for i in range(16):
 for j,pol in enumerate('PN'):
  k=2*i+j;s.part('C',f'C{100+k}','100nF / provisional',310+(k//16)*130,65+(k%16)*15,f'PEG_TX_{i}{pol}',f'CARRIER_PEG_TX_{i}{pol}')
s.part('R','R100','24.9R 1%',100,225,'CPU_PEG_COMP','CPU_VCCIO');s.text('CFG[6:5] = 10 for 2x8. Physical strap aliases still require verification; do not guess pin mapping.',20,360,1.3)
for ch,unit in [('A',3),('B',4)]:
 s=Sheet('03_ddr_a' if ch=='A' else '04_ddr_b',f'DDR4 channel {ch} / two SO-DIMMs',[f'CPU pinout: H310M-S2P sheet5. 260-contact connector: GL703GE sheet19. Proposed 2DPC adaptation.','DQ kept logical 1:1, no donor-specific lane swaps. Clock/CS/CKE/ODT split two per socket; layout validation pending.'])
 s.symbol('CoffeeLake_LGA1151','U1',92,60,cpu_nets,unit)
 for slot,x in enumerate([280,470]):
  nets={}
  for p in ds:
   n=p['name'];net=None
   if re.fullmatch(r'DQ\d+',n):net=f'DDR_{ch}_DQ[{n[2:]}]'
   elif re.fullmatch(r'DQS#?\d+',n):net=f'DDR_{ch}_DQS{"N" if "#"in n else "P"}[{re.search(r"\d+",n)[0]}]'
   elif re.match(r'A\d',n):net=f'DDR_{ch}_A[{re.search(r"\d+",n)[0]}]'
   elif n in ['BA0','BA1','BG0','BG1']:net=f'DDR_{ch}_{n[:2]}[{n[-1]}]'
   elif n in ['S0#','S1#','CKE0','CKE1','ODT0','ODT1','CK0','CK0#','CK1','CK1#']:
    z=int(re.search(r'\d',n)[0])+2*slot;stem='CS'if n.startswith('S')else ('CKN'if '#'in n else'CKP')if n.startswith('CK')and not n.startswith('CKE')else re.sub(r'\d','',n);net=f'DDR_{ch}_{stem}[{z}]'
   elif n in ['ACT#','PARITY','ALERT#']:net=f'DDR_{ch}_{n}'
   elif n=='RESET#':net='DDR_RESET#'
   elif n=='SCL':net='SMBCLK'
   elif n=='SDA':net='SMBDATA'
   elif n=='EVENT#':net=f'DDR_{ch}_EVENT#'
   elif n.startswith('SA'):bit=int(n[-1]);addr=(0 if ch=='A'else 2)+slot;net='SPD_3V3'if(addr>>bit)&1 else'GND'
   elif n.startswith(('DM','CB','S2','S3')):net='NC'
   if n in ['DQS8','DQS#8']:net='NC'
   nets[p['pin']]=net
  s.symbol('DDR4_SODIMM_260',f'J{1+(0 if ch=="A"else 2)+slot}',x,60,nets,1)
 s.text('No ECC. Address/command termination and per-socket decoupling are not yet sized. SPD addresses 0x50-0x53.',20,385,1.2)
s=Sheet('05_memory_power','DDR4 supply interfaces, termination and socket power',['DDR_1V2 and DDR_VPP_2V5 regulators remain to size for four modules. VTT circuit follows TPS51200.','Shown capacitors are preliminary, not a complete PDN. Memory VREF_DQ handling still needs CPU guidance.'])
for i in range(4):
 nets={p['pin']:('GND'if p['name'].startswith('VSS')else'SPD_3V3'if p['name']=='VDDSPD'else'DDR_VPP_2V5'if p['name'].startswith('VPP')else'DDR_VTT'if p['name']=='VTT'else'DDR_VREFCA'if p['name']=='VREFCA'else'DDR_1V2')for p in dp}
 s.symbol('DDR4_SODIMM_260',f'J{i+1}',90+i*135,60,nets,2)
s.symbol('TPS51200','U10',115,135,{'1':'DDR_REFIN_0V6','2':'DDR_1V2','3':'DDR_VTT','4':'GND','5':'DDR_VTT','6':'DDR_VREFCA','7':'DDR_VTT_EN','8':'GND','9':'DDR_VTT_PGOOD','10':'AUX_3V3','11':'GND'})
for idx,(a,b,val) in enumerate([('DDR_VTT','GND','10uF'),('DDR_VTT','GND','10uF'),('DDR_VTT','GND','10uF'),('DDR_VREFCA','GND','100nF'),('AUX_3V3','GND','1uF'),('DDR_1V2','GND','10uF')]):s.part('C',f'C{200+idx}',val,300+(idx//3)*130,145+(idx%3)*30,a,b)
s.part('R','R201','2.2k / provisional',100,255,'SMBCLK','SPD_3V3');s.part('R','R202','2.2k / provisional',300,255,'SMBDATA','SPD_3V3')
s.part('R','R203','10k 0.1%',100,300,'DDR_1V2','DDR_REFIN_0V6');s.part('R','R204','10k 0.1%',300,300,'DDR_REFIN_0V6','GND')
s.part('C','C206','100nF',470,300,'DDR_REFIN_0V6','GND')
s.text('SPD_3V3 source/sleep-state policy is open. Shared PCH/BMC SMBus requires ownership and voltage review.',20,335,1.4)
s=Sheet('06_cpu_power','CPU rails and power-pin inventory',['All 1151 socket contacts are present across CPU units. Supply pins stack by rail; exact pins are in pin-audit.json.','No CPU VRM is claimed complete. ISL95866 donor sheets25-27 are retained for the next circuit transcription.'])
s.symbol('CoffeeLake_LGA1151','U1',150,60,cpu_nets,6)
s.text('Required: CPU_VCORE, VCCGT, VCCSA, VCCIO, VCCST/PLL and DDR_1V2.',20,250,1.5)
s.text('Open: VR controller order code, 4+2 vs other phase count, load line, current limit, inductors, MOSFETs, compensation.',20,260,1.3)
s.text('Do not connect every rail with similar voltage together: sequencing and isolation are part of the implementation.',20,270,1.3)
s=Sheet('07_cpu_display','CPU display and audio interface inventory',['Donor H310M-S2P sheet4. Display port selection and carrier connector allocation are not frozen.'])
s.symbol('CoffeeLake_LGA1151','U1',145,60,cpu_nets,5);s.part('R','R301','24.9R 1%',370,70,'CPU_DP_COMP','CPU_VCCIO')
for u in range(7,len(cpu_units)+1):
 s=Sheet(f'08_cpu_reserved_{u}','CPU remaining debug / reserved contacts',[f'CPU unit {u}; source donor sheets4-7. Deliberately unconnected pending strap/debug review.','An open pin here is unresolved, not permission to omit a required strap.'])
 s.symbol('CoffeeLake_LGA1151','U1',180,60,cpu_nets,u)
s=Sheet('09_pch_expansion','Q370 PCIe lane inventory / draft allocation',['Proposed only: PCIe lane5 (HSIO10) shared with GbE; lane6 AST2500; 1-4,7-12 ten native x1; 13-16,17-20,21-24 three x4.','Numbered allocation must be checked against HSIO mux figure and straps. Carrier switches and connector pins not yet drawn.'])
s.symbol('Q370_draft','U2',150,60,pchnets,2)
s.text('No SATA allocation in this PCIe-max draft. Adding SATA requires a new lane budget.',340,70,1.3)
s.text('PCH PCIe TX AC coupling remains to add for each external lane.',340,80,1.3)
s.text('I219 link must use the selected GbE mux lane; lane5 / HSIO10 selected per Intel Fig3-1; strap verification pending.',340,90,1.3)
s=Sheet('10_pch_boot','Q370 boot flash, LPC and reset interfaces',['Intel 337347 ballout, H310M-S2P sheets10-12 as topology reference only. GPIO aliases require an independent check.','Host flash 3.3V policy proposed. BMC BIOS recovery mux is not implemented; flash presently connects to PCH only.'])
s.symbol('Q370_draft','U2',130,60,pchnets,3)
s.symbol('SPI_NOR_8','U11',370,60,{'1':'HOST_SPI_CS#','2':'HOST_SPI_MISO','3':'HOST_SPI_IO2','4':'GND','5':'HOST_SPI_MOSI','6':'HOST_SPI_CLK','7':'HOST_SPI_IO3','8':'PCH_VCCSPI'})
s.part('C','C301','100nF',370,125,'PCH_VCCSPI','GND');s.part('R','R302','10k / provisional',370,155,'HOST_SPI_CS#','PCH_VCCSPI')
s.part('XTAL','Y1','32.768kHz / CL TBD',120,240,'RTCX1','RTCX2')
s.text('24MHz crystal/oscillator circuit, RTC battery/reset network and reset supervisor remain open.',20,330,1.4)
s.text('PWRBTN#, SLP_S3/4/5#, DSW_PWROK, RSMRST# and SYS_PWROK are interfaces, not a completed sequencer.',20,340,1.3)
s=Sheet('11_pch_usb_clocks','Q370 USB2 and PCIe clocks',['USB2 port1 goes to AST2500 USB-A virtual hub. Other USB2 ports are carrier interface candidates.','Clock output0 reserved for AST2500; remaining reference clocks require CLKREQ# ownership and fanout budget.'])
s.symbol('Q370_draft','U2',160,60,pchnets,4)
s=Sheet('12_pch_power','Q370 power-domain interface inventory',['Intel 337347 Table8-1 and ballout. Identical rail names stack all extracted power balls; pin audit lists them.','Internal outputs DCPRTC, VCCDPHY_1P24, VCCDSW_1P05 must not be treated as external supply inputs.'])
s.symbol('Q370_draft','U2',170,60,pchnets,5)
s.text('Primary/suspend and deep-sleep domains need separate enable-state review. Regulators/filter networks not implemented.',20,270,1.3)
s.text('VCCPHVLDO_1P8 wiring depends on internal/external 1.8V mode. Keep separate until mode is selected.',20,280,1.3)
s=Sheet('13_bmc_host','AST2500 host links, boot flash and reset',['AST2500 A2 v1.6 pp52-53,58,68-69; X11SCH-F block diagram corroborates PCIe + LPC + USB integration.','This is the host-interface subset. BMC power, DDR4, GPIO straps, management PHY and firmware are not complete.'])
astnets={b:({'PERST#':'PLTRST#','PEREFCLKP':'BMC_REFCLK_P','PEREFCLKN':'BMC_REFCLK_N','PERXP':'BMC_RX_P','PERXN':'BMC_RX_N','PETXP':'BMC_TX_P','PETXN':'BMC_TX_N','LCLK':'LPC_CLK','LPCRST#':'PLTRST#','FWSPICS0#':'BMC_SPI_CS#','FWSPICK':'BMC_SPI_CLK','FWSPIMOSI':'BMC_SPI_MOSI','FWSPIMISO':'BMC_SPI_MISO','USB2A_DP':'BMC_USB_P','USB2A_DN':'BMC_USB_N'}.get(n,n if n in ['LAD0','LAD1','LAD2','LAD3','LFRAME#','SERIRQ']else'BMC_'+n))for b,n in astpairs.items()}
s.symbol('AST2500_host_draft','U3',130,60,astnets)
s.symbol('SPI_NOR_8','U12',370,60,{'1':'BMC_SPI_CS#','2':'BMC_SPI_MISO','3':'BMC_FLASH_WP#','4':'GND','5':'BMC_SPI_MOSI','6':'BMC_SPI_CLK','7':'BMC_FLASH_HOLD#','8':'BMC_3V3'})
for i,(n,val)in enumerate([('BMC_PEREXT','200R 1%'),('BMC_ENTEST','10k')]):s.part('R',f'R{400+i}',val,130,170+i*25,n,'GND')
s.part('C','C401','100nF',370,120,'BMC_3V3','GND')
for j,n in enumerate(['BMC_FLASH_WP#','BMC_FLASH_HOLD#']):s.part('R',f'R{402+j}','10k / provisional',370,155+j*25,n,'BMC_3V3')
for i,(a,b) in enumerate([('BMC_RX_P_PCH','BMC_RX_P'),('BMC_RX_N_PCH','BMC_RX_N'),('BMC_TX_P','BMC_TX_P_PCH'),('BMC_TX_N','BMC_TX_N_PCH')]):s.part('C',f'C{410+i}','100nF / provisional',130+(i//2)*240,245+(i%2)*30,a,b)
s.text('CLKIN needs a 24MHz oscillator; SRST# must remain asserted >=1ms after power is stable.',20,345,1.3)
s.text('Flash pins are also boot straps; verify strap resistor requirements before adopting these pull-ups.',20,355,1.3)
s=Sheet('14_input_power','EPS12V input and unresolved regulator interfaces',['8-pin EPS input retained. External 12V must remain available for BMC standby if deriving all standby rails locally.','Protection and rail converters are not sized in this draft. No eFuse/MOSFET ratings are implied.'])
s.symbol('EPS12V','J10',100,60,{str(i):'GND'if i<=4 else'EPS_12V'for i in range(1,9)})
s.part('FUSE','F1','Fuse / rating TBD',300,60,'EPS_12V','VIN_12V_PROTECTED')
s.text('Next circuit transcription: donor ISL95866 sheets25-27; DDR regulator sheet29; VPP sheet30.',20,150,1.4)
s.text('Required independently checked rails: AUX_3V3, BMC_3V3/core/DDR, PCH domains, CPU domains, DDR_1V2/VPP.',20,162,1.3)
s.text('No fabrication footprint, regulator compensation, current budget or sequencing approval in v0.1.',20,174,1.3)
exec(P('tools/extra_circuits.py').read_text())
# Save all sheets and project-local symbol library.
for s in sheetlist:s.save()
(OUT/'SOM.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+'\n'.join(x['sexp']for x in libs.values())+')')
(OUT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "SOM") (type "KiCad") (uri "${KIPRJMOD}/SOM.kicad_sym") (options "") (descr "Preliminary source-based symbols")))')
items=[]
def txt(t,x,y,size=1.2):return f'(text {q(t)} (at {x} {y} 0) {eff(size,"(justify left)")} (uuid {q(uid())}))'
items +=[txt('CUSTOM x86 SOM / preliminary schematic v0.1',15,15,2.5),txt('Coffee Lake-S + Q370 + four DDR4 SO-DIMMs + AST2500',15,23,1.7),txt('SOURCE-BASED ELECTRICAL DRAFT - incomplete circuits are listed on each sheet',15,31,1.3)]
for i,s in enumerate(sheetlist):
 x=20+(i//7)*190;y=50+(i%7)*43
 items.append(f'(sheet (at {x} {y}) (size 165 25) (stroke (width .254) (type default)) (fill (color 0 0 0 0)) (uuid {q(s.sheetid)}) (property "Sheetname" {q(s.title)} (at {x} {y-1} 0) {eff(1.1,"(justify left)")}) (property "Sheetfile" {q(s.name+".kicad_sch")} (at {x} {y+26} 0) {eff(.9,"(justify left)")}) (instances (project {q(project)} (path {q("/"+rootid)} (page {q(i+2)})))))')
items.append(txt('Known omissions: CPU VRM / sequencer / BMC DDR+power+LAN / host PHY / full PDN / connector pinout / remaining PCH GPIO.',15,380,1.15))
(OUT/(project+'.kicad_sch')).write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {q(rootid)}) (paper "A2") (lib_symbols) '+ '\n'.join(items)+f' (sheet_instances (path "/" (page "1"))))')
(OUT/(project+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':project+'.kicad_pro','version':1},'schematic':{'legacy_lib_dir':'','legacy_lib_list':[]}},indent=2))
P('research/pin-audit.json').write_text(json.dumps(audit,indent=2));P('research/unconnected-pins.json').write_text(json.dumps(pending,indent=2))
print('Sheets',len(sheetlist)+1,'pin occurrences',len(audit),'unconnected',len(pending))
