# Library handoff

`SOM_Full.kicad_sym` contains 17 entries. `FH82Q370` has all 874 ball numbers from Intel Table11-1; `AST2500A2_GP` has all 456 populated balls from the ASPEED top-view maps, excluding 28 #N/A sites. `CoffeeLake_LGA1151` contains 1151 donor-extracted contacts. Complete pin inventories are separate from the partial circuit symbols so existing draft connections are preserved. All full inventory pins are passive: electrical types and multiplexed functions still need independent review. This is not a complete, validated motherboard library.

All selected symbols expose Manufacturer, MPN, Footprint and Status fields in the full library; schematic instances also have those fields. `parts-catalog.json` is the machine-readable catalog. TBD values are deliberate, not orderable parts.

| Item | Manufacturer part | Status |
|---|---|---|
| CPU socket | Foxconn PE115127-4041-01H | Manufacturer drawing downloaded. Solder-ball numbering and land geometry unresolved; padless placement reservation retained. CPU itself is separate. |
| DDR4 sockets | TE 2309407-1 | 4mm, standard orientation. Checked drawing5 sheet2; signal pads corrected to0.30x1.75mm. |
| EPS header | Molex39-28-1083 | Candidate for5566-08A footprint. Exact EPS keying and pad mapping unresolved; not purchase-approved. |
| Q370 | Intel FH82Q370 |874-pin inventory;23x24mm body confirmed. Pitch and recommended lands unresolved; padless. |
| BMC | ASPEED AST2500A2-GP |456pads,19x19mm,0.8pitch and depopulation checked against drawing/maps.0.35mm NSMD copper diameter is an engineering proposal, not a verified manufacturer recommendation. |
| VR controller | ISL95866HRZ-T | Renesas L52.6x6A pattern:0.4pitch,0.20x0.55 peripheral pads,4.7mm EP. Package-to-device association donor-derived. Complete controller datasheet fetch was denied403. |
| Host PHY | WGI219LM family | Corrected EP from4.4 to3mm;0.4pitch. Exact stepping unresolved. Peripheral pad extension and thermal vias require assembly review. |
| DDR termination | TPS51200DRCR | KiCad DRC10+EP pattern; exact TI package selected. |
|25MHz crystal | ABM8-25.000MHZ-D2Y-T | Correct4-pin mapping; case pins2/4 grounded; pad geometry corrected to manufacturer1.30x1.05 at±1.15/±0.875mm. Load-capacitance/startup validation pending. |
| RTC crystal | ABS07-32.768KHZ-7-T | Candidate7pF crystal. Generic3215 footprint remains unverified against recommended lands. |
| PHY inductor | LPS4018-472MRC | Exact4.7uH candidate. Stock footprint differs from manufacturer's shaped recommended lands; unresolved. Current/ripple not approved. |
| Input fuse |0451015.MRL | Candidate15A package only; stock1.96x3.15mm pads at±2.455 match published recommended dimensions. Protection coordination not approved. |
| Flash, resistors, capacitors | TBD | Package templates only; exact electrical selection unresolved. |

The PCB contains96components, of which U1/U2 remain padless. There are1639 netlist nodes without pads, predominantly these two placeholders. Do not mistake the incomplete ratsnest for a complete design. ERC remains451messages:64open pins,38undriven supply inputs,349isolated labels. These represent unfinished circuitry and were not suppressed to produce a false clean report.

Do not rerun the generation scripts after manual KiCad edits: they overwrite files and regenerate UUIDs. The full inventory variants are available for future replacement of partial circuit symbols, not automatically substituted into this schematic.
