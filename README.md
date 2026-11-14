<div align="center">

# 🖨️ 3D Print Lab

**Wearable cosplay armor, magnetic masks and a full-size retro arcade cabinet,
designed in Blender and tuned for the Bambu Lab A1.**

[![Blender](https://img.shields.io/badge/Blender-4.5%2B-E87D0D?logo=blender&logoColor=white)](https://www.blender.org/)
[![Bambu Lab A1](https://img.shields.io/badge/Printer-Bambu%20Lab%20A1-00AE42)](https://bambulab.com/en/a1)
[![PLA](https://img.shields.io/badge/Material-PLA-4A90E2)](#printing-notes)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)

<a href="arcade_cabinet/cabinet-49/README.md"><img src="arcade_cabinet/cabinet-49/cabinet-49-assembled.png" width="420" alt="Arcade cabinet with Centipede artwork"></a>
<a href="lego_zane/mask/"><img src="lego_zane/mask/mask.png" width="380" alt="Zane ninja mask"></a>

[Masks](#-masks) · [Armor](#%EF%B8%8F-zane-ice-armor) · [Arcade cabinet](#%EF%B8%8F-arcade-cabinet) · [Controller](#-modular-arcade-controller) · [Printing notes](#printing-notes) · [License](#license)

</div>

---

## 🎭 Masks

<table>
<tr>
<td width="50%" align="center">
<a href="lego_zane/mask/"><img src="lego_zane/mask/mask.png" alt="Zane ninja mask" width="100%"></a>
<h3>Ninja Mask · Zane V28</h3>
</td>
<td width="50%" align="center">
<a href="lego_stone_creature/"><img src="lego_stone_creature/Stone_Creature_Mask_R1_Assembly.png" alt="Stone Creature mask" width="100%"></a>
<h3>Stone Creature Mask · R1</h3>
</td>
</tr>
<tr>
<td valign="top">

A wearable, two-color minifigure-style ninja helmet in white and cyan with keyed, glue-in horns.

- **Four pieces**, front and back joined by **16 pairs of 6 × 3 mm magnets**
- Fully **parametric**: set your head circumference in [`Ninja_Mask_V28.py`](lego_zane/mask/Ninja_Mask_V28.py) and regenerate
- Two-color 3MF with separate white and cyan regions; assign filament slots in Bambu Studio

📦 [`Ninja_Mask_V28_A1.3mf`](lego_zane/mask/Ninja_Mask_V28_A1.3mf) · 🧊 [`Ninja_Mask_V28.blend`](lego_zane/mask/Ninja_Mask_V28.blend)

</td>
<td valign="top">

A life-size minifigure head for adults, complete with the stud on top.

- **Three pieces** (crown plus two lower halves) held together by **52 hidden magnets**
- 224.8 mm diameter, 300 mm tall, with 200 mm minimum head clearance
- About **45 h and 927 g of PLA** across three plates
- Includes 1:1 face-fit and clearance guides to print on paper first

📦 [`3MF`](lego_stone_creature/Stone_Creature_Mask_R1_A1_PLA_small.3mf) · 🧊 [`.blend`](lego_stone_creature/Stone_Creature_Mask_R1_small.blend) · 📖 [Build notes](lego_stone_creature/Stone_Creature_Mask_R1_README.txt)

</td>
</tr>
</table>

---

## 🛡️ Zane Ice Armor

A complete wearable Zane costume: shoulder armor, bat wings, an articulated tail and iron-on shirt and pants artwork.

<table>
<tr>
<td width="33%" align="center"><a href="lego_zane/armor/"><img src="lego_zane/armor/armor.png" alt="Shoulder armor" width="100%"></a><br><b>Shoulder armor · R21</b></td>
<td width="33%" align="center"><a href="lego_zane/wing/"><img src="lego_zane/wing/wing.png" alt="Bat wings" width="100%"></a><br><b>Wings · R6</b></td>
<td width="33%" align="center"><a href="lego_zane/tail/"><img src="lego_zane/tail/tail.png" alt="Articulated tail" width="100%"></a><br><b>Tail · R2</b></td>
</tr>
<tr>
<td valign="top">Front and back plates with sculpted shoulder wings, concealed fasteners and rounded tips.<br><br>📦 <a href="lego_zane/armor/R21_Shoulders_Only_A1_PLA.3mf">3MF</a> · 🧊 <a href="lego_zane/armor/Zane_R21_Aligned_Wing_Edges.blend">.blend</a></td>
<td valign="top">A pair of one-piece wings with a 1.2 mm membrane skin, plus a press-in holder clip.<br><br>📦 <a href="lego_zane/wing/Zane_Wing_R6_Skin_Detail_Pair_A1_PLA.3mf">Wings</a> · <a href="lego_zane/wing/Wing_Clip_R3_Two_Plates_A1_PLA.3mf">Clip</a> · 🧊 <a href="lego_zane/wing/">.blend</a></td>
<td valign="top">Print-in-place segmented tail on a belt panel, with a continuous 45° root.<br><br>🧊 <a href="lego_zane/tail/Zane_Tail_R2_Articulated.blend">.blend</a></td>
</tr>
</table>

### 👕 Costume print kits

Vector artwork for heat-transfer vinyl or DTF printing, sized for real garments.

<table>
<tr>
<td width="50%" align="center"><a href="lego_zane/clothing_print_kit/"><img src="lego_zane/clothing_print_kit/zane-print-preview.png" alt="Zane clothing print kit" width="100%"></a><br><b>Zane · Ice armor</b>: 10 × 11 in chest, 4 × 6 in cuffs</td>
<td width="50%" align="center"><a href="lego_stone_creature/clothing_print_kit/"><img src="lego_stone_creature/clothing_print_kit/stone-warrior-print-preview.png" alt="Stone warrior clothing print kit" width="100%"></a><br><b>Stone Warrior</b>: 33 × 30 cm chest, 16 × 25 cm legs</td>
</tr>
</table>

---

## 🕹️ Arcade Cabinet

A tabletop vertical arcade cabinet built around a portrait 21.5″ monitor and a Raspberry Pi, with swappable controllers that slide into the front.

<table>
<tr>
<td width="50%"><a href="arcade_cabinet/cabinet-49/README.md"><img src="arcade_cabinet/cabinet-49/cabinet-49-disassembled.png" alt="Cabinet exploded view" width="100%"></a></td>
<td width="50%"><a href="arcade_cabinet/cabinet-49/README.md"><img src="arcade_cabinet/cabinet-49/cabinet-49-controller-detail.png" alt="Controller seated in cabinet" width="100%"></a></td>
</tr>
</table>

| Module | What it is | Status |
| --- | --- | --- |
| [**Cabinet 49**](arcade_cabinet/cabinet-49/README.md) | Full cabinet assembly and A1 print plan | 🟡 Design review |
| [**Monitor Stand 48**](arcade_cabinet/monitor-48-portrait-stand/README.md) | Padded portrait stand for the Acer SB220Q | 🟢 Printable |
| [**Connector Bench 47**](arcade_cabinet/connector-47-bench-pack/README.md) | Three-port rail and wiring tray for the internal frame | 🟢 Printable |
| [**Connector 46**](arcade_cabinet/connector-46-design-pack/README.md) | Solderless magnetic connector study and sourcing | 📐 Research |
| [**Side panels**](arcade_cabinet/side_panels/) | Centipede and Pac-Man side art (SVG) | 🎨 Artwork |

<p align="center">
<a href="arcade_cabinet/monitor-48-portrait-stand/README.md"><img src="arcade_cabinet/monitor-48-portrait-stand/images/portrait-stand-with-monitor.png" height="260" alt="Portrait monitor stand"></a>
<a href="arcade_cabinet/connector-47-bench-pack/README.md"><img src="arcade_cabinet/connector-47-bench-pack/images/bench-assembled.png" height="260" alt="Connector bench"></a>
<a href="arcade_cabinet/side_panels/"><img src="arcade_cabinet/side_panels/centipede-preview.png" height="260" alt="Centipede side art"></a>
<a href="arcade_cabinet/side_panels/"><img src="arcade_cabinet/side_panels/retro-pacman-preview.png" height="260" alt="Pac-Man side art"></a>
</p>

---

## 🎮 Modular Arcade Controller

**Revision 45:** a two-piece controller that splits along a diagonal magnetic seam. Mix and match left and right halves to build **8 layouts** from one shared set of bottoms.

<p align="center">
<img src="arcade_cabinet/controller-45-build-pack/images/centipede.png" width="49%" alt="Centipede controller">
<img src="arcade_cabinet/controller-45-build-pack/images/twin-joystick-2fire.png" width="49%" alt="Twin joystick controller">
</p>

<table>
<tr>
<td align="center"><img src="arcade_cabinet/controller-45-build-pack/images/joystick-6.png" alt="Street Fighter layout" width="100%"><br>Street Fighter</td>
<td align="center"><img src="arcade_cabinet/controller-45-build-pack/images/tempest.png" alt="Tempest layout" width="100%"><br>Tempest</td>
<td align="center"><img src="arcade_cabinet/controller-45-build-pack/images/twin-joystick.png" alt="Twin joystick layout" width="100%"><br>Twin stick</td>
<td align="center"><img src="arcade_cabinet/controller-45-build-pack/images/centipede-separated.png" alt="Separated halves" width="100%"><br>Halves separated</td>
</tr>
</table>

- 🧲 **Magnetic join**: eight 6 × 3 mm magnets per half plus tapered alignment keys
- 🎨 **Hidden overlay magnets**: six blind pockets under each deck for swappable artwork overlays ([SVG templates](arcade_cabinet/controller-45-build-pack/Overlay-templates/))
- 🔌 **Pass-through ports**: two 12-contact connector pairs across the seam, plus rear USB-C, A and B
- 🕹️ **Real hardware**: trackball, spinner dial, 28 mm buttons, joysticks and Easyget USB encoders
- 🖨️ **23 named A1 plates**, plus a small fit-test project for magnets and screws

| Layout | Controls |
| --- | --- |
| Street Fighter | Joystick, six actions, two Start |
| Fire / Jump | Joystick, two actions, two Start |
| Three action | Joystick, three actions, two Start |
| Centipede | Trackball, Fire on the left or right |
| Tempest | Spinner dial and trackball |
| Twin stick | Two joysticks, with or without two Fire buttons per side |

📦 [All controllers 3MF](arcade_cabinet/controller-45-build-pack/controller-45-all-controllers-A1.3mf) · 🧪 [Fit tests 3MF](arcade_cabinet/controller-45-build-pack/controller-43-fit-tests-A1.3mf) · 📖 [Full build guide](arcade_cabinet/controller-45-build-pack/README.md)

---

## Repository layout

```
.
├── lego_zane/                 Zane costume
│   ├── mask/                  Parametric two-color ninja helmet
│   ├── armor/                 Shoulder armor
│   ├── wing/                  Wings and holder clip
│   ├── tail/                  Articulated tail
│   └── clothing_print_kit/    Shirt and pants artwork
├── lego_stone_creature/       Stone Creature mask and clothing print kit
└── arcade_cabinet/
    ├── cabinet-49/                  Full cabinet assembly
    ├── controller-45-build-pack/    Modular magnetic controller
    ├── connector-46-design-pack/    Magnetic connector study
    ├── connector-47-bench-pack/     Connector rail and wiring bench
    ├── monitor-48-portrait-stand/   Portrait monitor stand
    └── side_panels/                 Cabinet side art
```

Each project folder usually contains:

| File | Purpose |
| --- | --- |
| `*.3mf` | Bambu Studio project with plates, orientation and print settings. Open it as a project. |
| `*.blend` | Editable Blender source with review scenes |
| `STL/` | Individual meshes in millimetres, already oriented for printing |
| `*-checks.json` | Mesh, fit and slicing validation reports |
| `README.md` / `build-guide.html` | Build and assembly instructions |

## Printing notes

- **Printer:** Bambu Lab A1 with a 0.4 mm nozzle and a 256 mm bed. Every part fits at 100% scale.
- **Material:** PLA throughout.
- **Magnets:** 6 × 3 mm neodymium discs are used everywhere. Mark polarity before gluing.
- **Print the fit tests first.** Most projects include small coupons for magnets, inserts and screws. They are quick and save a failed 30-hour print.
- **Don't scale the models.** Scaling also resizes the magnet pockets and screw holes. To resize the Zane mask, change its parameters and regenerate it instead.

> [!NOTE]
> These are prototype designs. The automated checks confirm that meshes are watertight and that parts fit together digitally, but not wearable comfort, magnet holding force or structural strength. Test-fit before committing to a long print.

## License

Licensed under [**CC BY-NC-SA 4.0**](LICENSE). You're welcome to print, remix and share these designs for non-commercial use, as long as you give credit and share your remixes under the same license.

LEGO®, NINJAGO®, Centipede®, Tempest®, Pac-Man® and Street Fighter® are trademarks of their respective owners. This is an unofficial fan project, not affiliated with or endorsed by any of them.

<div align="center">
<sub>Made by <a href="https://github.com/reduxdj">Patrick Lemiuex</a></sub>
</div>
