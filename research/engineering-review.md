# Initial engineering review

## Confirmed source access

Opened these complete PDFs through the web tool during intake; not yet downloaded locally:

- [Intel CPU 337344-009](https://cdrdv2-public.intel.com/337344/337344_8th-gen-core-family-datasheet-vol-1_Rev009.pdf): 155 PDF pages.
- [Intel PCH 337347-009](https://cdrdv2-public.intel.com/337347/337347_CNL_PCH_EDS_H_009.pdf): 301 PDF pages. Printed pages differ from PDF indices.

## HSIO conflict requiring correction

Intel 337347 Table 1-4 and Section 3 show shared PCIe/GbE/SATA resources. Integrated GbE consumes a PCIe-capable HSIO lane. Thus the inherited allocation of AST2500 x1 + eleven native x1 + three x4 uplinks (24 PCIe lanes) cannot also retain integrated GbE. The 15-root-port limit with GbE is a separate constraint; meeting it does not fix lane multiplexing.

An arithmetic starting point is ten native x1 + AST2500 x1 + three x4 uplinks = 23 PCIe lanes, reserving one HSIO lane for GbE. This is not a validated lane map. SATA reservations may reduce expansion further. Verify numbered lanes, controller groupings, straps and clock ownership before accepting it. If 24 carrier x1 endpoints remain desired, switches would need fourteen downstream x1 ports total with ten native links.

## Candidate parts inherited from discussion

These are leads only: no stock, price, exact order code or electrical compatibility has been verified in this intake.

| Block | Candidate | Required next evidence |
|---|---|---|
| CPU socket | TE 2287402-1 / Foxconn 3H993921-4M41-02H | Exact package, ball map, ILM, mounting and availability |
| SO-DIMM sockets | TE 2309407-5 | Stack height, insertion/retention envelope, drawing and footprint |
| BMC | AST2500 | Full pinout, power/reset sequence, DDR topology and firmware support |
| Host PHY | I219-LM | Correct generation/order code for Q370, supply and shared HSIO mapping |
| Management PHY | DP83867IS | AST2500 RGMII timing, supply compatibility, exact package |
| CPU VR | ISL95856 / ISL95866C / ISL69138 | Full documentation, SVID support, phases, stage interface, transient budget |
| Power stage | ISL99227 family | Controller compatibility; do not combine merely because both were suggested |
| Memory power | TPS51116 / TPS51200 | Host and BMC current budgets, VPP and sequencing |
| Carrier switches | PEX8713 | Full databook, straps, downstream widths, procurement and firmware |
| Clock buffers | 9DB836 / 9DBL0641 | Clock tree, loading, jitter budget, termination and enable control |
| Flash | W25Q256JV | Firmware capacity, bus voltage, boot addressing and recovery ownership |
| TPM | SLB9670 | Whether required; package and SPI electrical compatibility |

Earlier messages proposed PEX8714 for x1 fanout and later retracted it. Keep it excluded pending independent width-support verification. Earlier BMC RAM examples were also retracted over lifecycle concerns; no RAM part is frozen.

## Blocking inputs for real layout

- Exact cooler geometry and board/carrier datums are unavailable locally. Do not invent board dimensions or assume the cooler proves a particular power rating.
- CPU/PCH design guides, complete ball maps, memory routing limits and full selected VR documentation need acquisition and revision checks.
- Firmware feasibility must cover memory initialization, Intel CSME configuration, GPIO/HSIO straps, CPU support, flash programming and BMC recovery.
- Carrier pin budget must include grounds, clocks, reset/clock-request sidebands, management and power, not just differential data contacts.
- Full schematic connectivity and a supported fabrication stackup must precede production routing.

Next work: retrieve electrical documents, validate the numbered HSIO map, and compare exact parts and mechanical envelopes. User was asked for any existing downloaded document/design folder and cooler part number.
