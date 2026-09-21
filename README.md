# Custom x86 SOM — placement handoff

Open `hardware/x86-som-preliminary.kicad_pro` in KiCad 10. The matching schematic has 18 sheets; the matching PCB contains 96 staged components and zero routed tracks. Project-local symbol and footprint libraries are included. Move components in the PCB editor to start exploring placement; no board outline has been chosen.

**This is an incomplete preliminary design, not fabrication-ready.** See `hardware/LIBRARY-STATUS.md` for the current verification matrix. The CPU socket and Q370 still use padless placement envelopes. Other packages include source-checked geometry and explicitly marked provisional choices. Electrical and assembly validation remains incomplete.

The full library is `hardware/SOM_Full.kicad_sym`; use `hardware/parts-catalog.json` for part numbers. CPU socket: Foxconn PE115127-4041-01H. DDR4 sockets: TE2309407-1. The full pin inventories have1151 CPU contacts,874 PCH balls and456 BMC balls.

## Files

- `hardware/x86-som-preliminary.kicad_sch`: source-based schematic draft.
- `hardware/x86-som-preliminary.kicad_pcb`: component staging board with nets assigned to available pads.
- `hardware/SOM.kicad_sym`, `hardware/SOM.pretty/`: portable project libraries.
- `hardware/footprint-status.json`: footprint provenance and provisional status.
- `hardware/placement-validation.json`: component count and schematic nodes without pads.
- `hardware/open-items.md`: next engineering checks.
- `output/pdf/x86-som-preliminary.pdf`: schematic preview.
- `docs/reference/`, `docs/manifest.json`: downloaded documents and source inventory.
- `research/conversation-source.json`: recovered original specification conversation.

KiCad successfully exported the schematic and reloaded the 96-component PCB. ERC reports 102 errors and 349 warnings; see `hardware/erc.rpt`. These remain unresolved, and no routing, signal-integrity, power-integrity, boot or fabrication validation has been claimed.

The source specification is ChatGPT conversation “Compact SOM Motherboard Design”, ID `6ab03890-806c-83ea-97a4-768561390f3c`. Prior assistant claims are research leads. The earlier claimed downloadable engineering packs were not recovered. Actual donor schematics and manufacturer documents have been downloaded separately.

Generation scripts are development tools. **Do not rerun them after manual KiCad edits:** they overwrite schematic/PCB files and regenerate symbol UUIDs.

## Public repository contents

This public snapshot contains the KiCad files, libraries, generation scripts, engineering notes and previews from local commit `4b89cf6`. The original conversation archive and downloaded third-party reference documents/text extracts remain local; paths to those files describe the local research workspace. `docs/manifest.json` records the source inventory. Some generators require those local source files and will not run from this public checkout alone.
