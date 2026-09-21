# Recovered requirements

Source turn IDs refer to conversation-source.json. Later user decisions supersede earlier alternatives.

| Requirement | Evidence / status |
|---|---|
| Custom-built compact SOM, not a purchased module | User e489a088-b775-43a3-9347-7546c615806f |
| LGA1151 socket | User ffe6aea0-88a6-45e8-87d1-2a5e93b71265 |
| Four SO-DIMM sockets; two direct x8 CPU PCIe links; extensive x1 expansion | Initial user f3331d3b-775d-45c0-b359-b6b09c3ab676 |
| Coffee Lake-S / Q370 platform | Working architecture from prior discussion; exact CPU SKU/support list remains open |
| ASPEED BMC | User 21da610f-d5e8-4298-b970-36f947f638f8; AST2500 was the proposed implementation |
| Native x1 links plus carrier switches | Accepted by user e3cca0a1-25ed-42ec-9e25-9c0096a0db84; numerical allocation needs correction |
| Single integrated host GbE | User 34e104bf-5dbd-4353-96c1-0a2119030bda supersedes dual-host-GbE request |
| Dedicated BMC management Ethernet | Working architecture; dual management Ethernet was an assistant misunderstanding, not a retained requirement |
| Dell OptiPlex 9020 USFF blower cooler; board length follows cooler | User 5504d366-3890-4078-8114-ad4ef38d9f11 and 4c18245f-9b8e-4f8e-9550-e49036dbaa59 |
| Cooler removal for RAM service acceptable | User 1222fbf4-fb03-4248-ab1a-631aa3162e16 |
| Prioritize VRM beneath cooler/blower; fit RAM where possible | User 8b330e31-4ca0-419f-be5c-208c1b9776f9 |
| Separate generic VRM heatsink acceptable | User f838818f-8efe-44ce-a342-ce01d8f6e62e |
| 8-pin EPS12V power connector | User 7c87185e-401d-4113-9492-df72ce8600a6 |
| Actual usable datasheets/downloads; mirrors acceptable; avoid payment-credit download sites | Multiple user turns on source page 2 and 7e52c8d3-5bae-4577-8053-9b922b5472e5 |
| KiCad | Current user instruction |

## Decisions still open

Exact CPU SKU and sustained/transient limits; cooler part number/dimensions; connector family and pinout; SATA/USB/display counts; standby source; full power sequencing; firmware implementation and provisioning; CPU VR controller/stages; BMC RAM and flash sizing; TPM and Super I/O need; production quantity/cost target; fabricator and stackup.

The previous assistant's suggestions of 95 W electrical capability, 65 W cooling, 12–16 layers, heavy copper, specific heatsink dimensions and 12 V-derived standby are not verified requirements or validated limits.
