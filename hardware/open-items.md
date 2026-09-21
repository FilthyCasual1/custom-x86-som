# Current status supersedes earlier checklist

See LIBRARY-STATUS.md. Only U1/U2 remain padless; missing pad nodes now1639. Earlier sizes and eight-placeholder list below are historical.

# Resume checklist

Work paused at user's requested symbol/footprint placement handoff.

1. Replace padless envelopes U1/U2/U3/U20/Y1/Y2/F1/L600 with exact orderable-part land patterns. CPU 78 x 78 mm envelope is an arbitrary socket/mechanism reservation, not its measured outline. Q370/AST2500/VR outlines are provisional too. Confirm all stock footprint pad mappings, EPS keying, SO-DIMM socket orientation and connector height. I219 exposed-pad size is a candidate, not independently validated.
2. Current symbols are incomplete for PCH and AST2500. CPU pin extraction has 1151 unique pins, but independent datasheet checking remains required. Donor H310 circuitry does not validate a Q370 design. AST2500 memory interface exists but its memory IC, complete supply pins and LAN circuit are absent.
3. Complete CPU VR power stages, inductors, compensation, rail sizing/sequencing, PCH/BMC regulators and full decoupling. The ISL95866 controller transcription is only a donor reference, not a complete VRM. TPS51200 REFIN uses a provisional 0.6 V divider.
4. Check DDR4 2DPC topology, SO-DIMM pin mapping, termination, SPD, VPP/VTT and length/impedance rules. No reference-board DQ swaps were assumed valid for this layout.
5. Complete host PHY support and BMC PHY/magnetics, RTC/clock/strap/reset circuits, carrier connector selection and allocation, firmware/BIOS/BMC bring-up plan. No carrier connector footprint is yet chosen or placed.
6. Resolve 451 ERC messages (102 errors / 349 warnings), including open pins, incomplete supplies and isolated nets. Board has 1780 netlist nodes without corresponding pads, predominantly major-chip placeholders. Do not interpret its incomplete ratsnest as complete connectivity.
7. Establish final cooler/socket datum and outline, stackup, routing rules and mounting. Do not manufacture the staging layout.

## Preserved mechanical inputs

User owns Dell 9020 USFF cooler; supplied part references 0VXD9P / 04X9H2 / 0FGW90 and https://www.ebay.com/itm/163252658404. User measured approximately 6 mm underside clearance at the far edge and 7+ mm under the fan. These are user-provided clearances, not verified full cooler geometry. Cooler geometry is only needed for board outline at this stage. No cooler keepout or board outline is frozen.

## Electrical allocation under consideration

Coffee Lake-S LGA1151 + Q370, four DDR4 SO-DIMMs, CPU 2 x PCIe x8, AST2500, one host I219-LM GbE plus dedicated BMC Ethernet, EPS12V. Proposed PCH lane allocation reserves lane 5 for integrated GbE, lane 6 for AST2500, lanes 13–24 as three x4 uplinks, and lanes 1–4/7–12 as ten x1 links. This remains subject to exact Q370 port grouping, HSIO and firmware checks.
