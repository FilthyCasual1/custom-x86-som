# Additional source-transcribed draft circuits. Executed by build_preliminary.py.
vr=json.loads(P('research/vrm-pin-extraction.json').read_text())
vr +=[pin(24,'VDD','power_in'),pin(32,'VDDP','power_in'),pin(53,'GND_EP','power_in')]
define('ISL95866_reference',[vr],'H310M-S2P 2.0 sheet25; populated options differ for ISL95856/ISL95866',value='ISL95866HRZ-T / donor reference')
s=Sheet('15_vrm_controller','CPU VR controller / source-based starting circuit',['Transcribed pinout and bias/bootstrap networks: H310M-S2P 2.0 sheet25. This does not constitute a complete VRM.','Donor contains ISL95856/ISL95866 population alternatives. Phase mapping, compensation and current sense remain open.'])
vnets={p['pin']:'VR_'+p['name']for p in vr}
vnets.update({'24':'VR_VDD_5V','32':'VR_VDDP_5V','53':'GND','44':'VR_VIN','5':'CPU_SVID_CLK','6':'CPU_SVID_ALERT#','7':'CPU_SVID_DATA','8':'CPU_VR_ENABLE','11':'CPU_VR_READY','4':'CPU_VR_HOT#','43':'SMBDATA','42':'SMBCLK','20':'CPU_VSS_SENSE','48':'CPU_VSSGT_SENSE'})
s.symbol('ISL95866_reference','U20',130,60,vnets)
for i,(a,b,val,kind) in enumerate([('AUX_5V','VR_VDD_5V','2.2R','R'),('AUX_5V','VR_VDDP_5V','2.2R','R'),('VIN_12V_PROTECTED','VR_VIN','2.2R','R'),('VR_VDD_5V','GND','1uF','C'),('VR_VDDP_5V','GND','1uF','C'),('VR_VIN','GND','1uF','C'),('VR_PROG','GND','2.87k 1% / donor','R')]):
 s.part(kind,f'{kind}{500+i}',val,330,65+i*28,a,b)
for i,phase in enumerate(['1_A','2_A','1_B']):
 s.part('R',f'R{520+i}','2.2R / donor',470,65+i*65,f'VR_BOOT{phase}',f'VR_BOOT{phase}_CAP')
 s.part('C',f'C{520+i}','220nF / donor',470,95+i*65,f'VR_BOOT{phase}_CAP',f'VR_PHASE{phase}')
s.text('UGATE/LGATE/PHASE are unconnected power-stage interfaces. Feedback/current-sense must be completed before power-on.',20,330,1.25)
s.text('CPU_VCORE and CPU_VCCGT are not generated in this draft. Donor sheets26-27 retain exact MOSFET/driver circuits.',20,340,1.25)
s.text('CPU SVID source pull-up/series networks and PSYS/IMON/NTC programming remain required.',20,350,1.25)
# I219: all package contacts plus exposed pad; external generation compatibility still open.
ih={1:'RSVD1_VCC3P3',2:'LANWAKE_N',3:'LAN_DISABLE_N',4:'VDD3P3',5:'VDD3P3_IN',6:'SVR_EN_N',7:'CTRL0P9',9:'XTAL_OUT',10:'XTAL_IN',12:'RBIAS',13:'MDI_PLUS0',14:'MDI_MINUS0',17:'MDI_PLUS1',18:'MDI_MINUS1',20:'MDI_PLUS2',21:'MDI_MINUS2',23:'MDI_PLUS3',24:'MDI_MINUS3',25:'LED2',26:'LED0',27:'LED1',28:'SMB_CLK',30:'TEST_EN',31:'SMB_DATA',32:'JTAG_TDI',33:'JTAG_TMS',34:'JTAG_TDO',35:'JTAG_TCK',36:'PE_RST_N',38:'PETp',39:'PETn',41:'PERp',42:'PERn',44:'PE_CLKP',45:'PE_CLKN',48:'CLK_REQ_N',49:'GND_EP'}
for k in [8,11,16,22,37,40,43,46,47]:ih[k]='VDD0P9'
for k in [15,19,29]:ih[k]='VDD3P3'
ip=[pin(k,v,stack=v) if v.startswith('VDD')else pin(k,v)for k,v in sorted(ih.items())]
define('I219_reference',[ip],'Intel I219 datasheet sections3.1.2-3.1.7 pp36-38; exposed ground pad',value='I219-LM / revision TBD')
s=Sheet('16_host_lan','Host GbE PHY / I219 reference circuit',['Intel I219 full datasheet pin tables. Exact I219-LM generation and Q370 compatibility must be selected before BOM freeze.','Uses PCH GbE on HSIO10 / PCIe lane5. This link consumes the shared lane; it is not an additional expansion root port.'])
nets={str(k):'HOST_'+v for k,v in ih.items()}
nets.update({'49':'GND','5':'LAN_AUX_3V3','6':'GND','7':'I219_SW_0V9','12':'I219_RBIAS','30':'I219_TEST_EN','36':'PLTRST#','38':'I219_TX_P','39':'I219_TX_N','41':'I219_RX_P','42':'I219_RX_N','44':'I219_REFCLK_P','45':'I219_REFCLK_N','28':'I219_SML_CLK','31':'I219_SML_DATA'})
s.symbol('I219_reference','U21',135,60,nets)
s.part('L','L600','4.7uH / Intel',365,70,'I219_SW_0V9','HOST_VDD0P9')
s.part('R','R600','3.01k 1%',365,100,'I219_RBIAS','GND');s.part('R','R601','1k',365,130,'I219_TEST_EN','GND')
define('ABM8',[[pin(1,'XTAL1'),pin(2,'GND'),pin(3,'XTAL2'),pin(4,'GND')]],'Abracon ABM8 datasheet',value='ABM8-25.000MHZ-D2Y-T',width=10.16)
s.symbol('ABM8','Y2',365,160,{'1':'HOST_XTAL_OUT','2':'GND','3':'HOST_XTAL_IN','4':'GND'})
for i,(a,b)in enumerate([('HOST_LAN_TX_P','I219_RX_P'),('HOST_LAN_TX_N','I219_RX_N'),('I219_TX_P','HOST_LAN_RX_P'),('I219_TX_N','HOST_LAN_RX_N')]):s.part('C',f'C{600+i}','100nF / provisional',130+(i//2)*235,225+(i%2)*30,a,b)
s.text('Open: LANPHYPC / LAN_DISABLE logic, SMLink wiring, source clock+CLKREQ, internal regulator caps and strap pull-ups.',20,320,1.25)
s.text('MDI pairs go to carrier magnetics/RJ45; no magnetics or termination network is included yet.',20,330,1.25)
# BMC DDR signal inventory from datasheet. Real package balls; no fictitious DRAM pinout.
a=P('docs/text/ast2500.txt').read_text().split('\f');ap=[]
for pg in [51,52]:
 for line in a[pg-1].splitlines():
  m=re.match(r'^\s*([A-Z]{1,2}[0-9]{1,2})\s+(M[A-Z0-9_/#]+)(?:\s|$)',line)
  if m:ap.append(pin(m[1],m[2]))
define('AST2500_ddr_draft',[ap],'AST2500 A2 v1.6 pp51-52; DDR3L/DDR4 multiplexing',value='AST2500 DDR / interface subset')
# Separate reference designator avoids pretending this is a second BMC part in the BOM:
# Merge into the existing BMC symbol as second unit, so U3 remains one physical device.
old=libs['AST2500_host_draft'];define('AST2500_host_draft',[astpins,ap],old['source']+'; DDR pp51-52',value=old['value'])
s=Sheet('17_bmc_ddr','AST2500 local DDR4 / pin-level interface',['AST2500 DDR4 x16 interface from full datasheet pp51-52. Exact DRAM part and footprint remain unselected.','MA14/MACT#, MBA aliases and required memory geometry must be reconciled with chosen DDR4 before connecting its balls.'])
ns={p['pin']:'BMC_'+p['name']for p in ap}
s.symbol('AST2500_host_draft','U3',130,60,ns,2)
s.part('R','R700','240R 1%',365,80,'BMC_MIOZ','GND')
s.part('R','R701','10k 0.1% / provisional',365,125,'BMC_DDR_1V2','BMC_MVREF');s.part('R','R702','10k 0.1% / provisional',365,155,'BMC_MVREF','GND');s.part('C','C700','100nF',365,185,'BMC_MVREF','GND')
s.text('This sheet is an unfinished memory circuit: 53 BMC interface pins are available, but no RAM component is represented.',20,320,1.25)
s.text('BMC core/power domains, RGMII management PHY, reset supervisor and complete strap matrix remain required.',20,330,1.25)
