#!/usr/bin/env python3
from fnmatch import filter
from os import rename, walk
from os.path import join
from re import DOTALL
from re import compile as compile_

culus = 11
chests = 39
puzzles = 44
specialties = 145
experience = 196
ores = 463

mappings = {
    # Special Items
    "CulusAnemo.ini": culus,
    "CulusGeo.ini": culus + 1,
    "CulusElectro.ini": culus + 2,
    "CulusDendro.ini": culus + 3,
    "CulusHydro.ini": culus + 4,
    "Pyroculus.ini": culus + 5,
    "CrimsonAgate.ini": culus + 6,
    "Lumenspar.ini": culus + 13,
    "SacredSeal.ini": culus + 16,
    "RadiantSpincrystal.ini": culus + 18,
    "PurifyingLight.ini": culus + 23,
    # Chests
    "ChestCommon.ini": chests,
    "ChestExquisite.ini": chests + 1,
    "ChestPrecious.ini": chests + 2,
    "ChestLuxurious.ini": chests + 3,
    "ChestLuxuriousLOD.ini": chests + 3,
    # Puzzle Chests
    "TimeTrialBattle.ini": puzzles + 8,
    "TimeTrialRun.ini": puzzles + 8,
    "TimeTrialShoot.ini": puzzles + 8,
    "LargeRock.ini": puzzles + 15,
    "LargeRockPileNata.ini": puzzles + 15,
    "BloattyFloatty.ini": puzzles + 20,
    "TimeTrialChenyu.ini": puzzles + 76,
    # Local Specialties
    "Valberry.ini": specialties,
    "JueyunChili.ini": specialties + 1,
    "CallaLily.ini": specialties + 2,
    "Qingxin.ini": specialties + 3,
    "SmallLampGrass.ini": specialties + 4,
    "VioletGrass.ini": specialties + 5,
    "Cecilia.ini": specialties + 6,
    "SilkFlower.ini": specialties + 7,
    "DandelionSeed.ini": specialties + 8,
    "GrazeLilyDay.ini": specialties + 9,
    "GrazeLilyNight.ini": specialties + 9,
    "PhilanemoMushroom.ini": specialties + 10,
    "CorLapos.ini": specialties + 11,
    "Wolfhook.ini": specialties + 12,
    "NoctilucousJade.ini": specialties + 13,
    "WindwheelAster.ini": specialties + 14,
    "Starconch.ini": specialties + 15,
    "SeaGenoderma.ini": specialties + 16,
    "Onikabuto.ini": specialties + 17,
    "NakuWeed.ini": specialties + 18,
    "Dendrobium.ini": specialties + 19,
    "CrystalMarrow.ini": specialties + 21,
    "SangoPearl.ini": specialties + 22,
    "SangoPearlBase.ini": specialties + 22,
    "AmakumoFruit.ini": specialties + 23,
    "AmakumoFruitBase.ini": specialties + 23,
    "FluorescentFungus.ini": specialties + 24,
    "NilotpalaLotusD.ini": specialties + 25,
    "NilotpalaLotusD_Base.ini": specialties + 25,
    "NilotpalaLotusN.ini": specialties + 25,
    "NilotpalaLotusN_Base.ini": specialties + 25,
    "KalpalataLotus.ini": specialties + 26,
    "RukkhashavaMushroom.ini": specialties + 27,
    "Padisarah.ini": specialties + 28,
    "Scarab.ini": specialties + 29,
    "HennaBerry.ini": specialties + 30,
    "SandGreasePupa.ini": specialties + 31,
    "Trishiraite.ini": specialties + 32,
    "MourningFlower.ini": specialties + 33,
    "BerylCouch.ini": specialties + 34,
    "RomaritimeFlowerBud.ini": specialties + 35,
    "RomaritimeFlower.ini": specialties + 35,
    "LumidouceBell.ini": specialties + 36,
    "RainbowRose.ini": specialties + 37,
    "Lumitoile.ini": specialties + 38,
    "SubdetectionUnit.ini": specialties + 39,
    "SubdetectionUnitLOD1.ini": specialties + 39,
    "SubdetectionUnitLOD2.ini": specialties + 39,
    "LakelightLily.ini": specialties + 40,
    "ClearwaterJadeB.ini": specialties + 42,
    "ClearwaterJade.ini": specialties + 42,
    "SprayfeatherGill.ini": specialties + 43,
    "SaurianClawSucculent.ini": specialties + 44,
    "QenepaBerry.ini": specialties + 45,
    "BriliantChrysanthemum.ini": specialties + 46,
    "WitheringPurpurbloom.ini": specialties + 47,
    "GlowingHornshroom.ini": specialties + 48,
    "SkysplitGembloom.ini": specialties + 49,
    "Dracolite_coreL.ini": specialties + 50,
    "Dracolite_coreS.ini": specialties + 50,
    # Experience
    "WoodenCrate.ini": experience + 1,
    "RockPile.ini": experience + 2,
    "FontainePlaceofInterest.ini": experience + 3,
    "Aranara_A_Lod0.ini": experience + 4,
    "Aranara_A_Lod1.ini": experience + 4,
    "Aranara_A_Lod2.ini": experience + 4,
    "Aranara_B_Lod0.ini": experience + 4,
    "Aranara_B_Lod1.ini": experience + 4,
    "Aranara_B_Lod2.ini": experience + 4,
    "Aranara_C_Lod0.ini": experience + 4,
    "Aranara_C_Lod1.ini": experience + 4,
    "Aranara_C_Lod2.ini": experience + 4,
    "Aranara_D_Lod0.ini": experience + 4,
    "Aranara_D_Lod1.ini": experience + 4,
    "Aranara_D_Lod2.ini": experience + 4,
    "SmashedStone.ini": experience + 12,
    "GeoSigil.ini": experience + 20,
    "UnusualHillitchurl.ini": experience + 25,
    "EmberMonaChest.ini": experience + 69,
    # Ores
    "WhiteIron.ini": ores,
    "CrystalChunk.ini": ores + 1,
    "MagicalCrystalChunk.ini": ores + 2,
    "Starsilver.ini": ores + 3,
    "Iron.ini": ores + 5,
    "AmethystLump.ini": ores + 6,
    "CondessenceCrystal.ini": ores + 7,
}

used = []

add_re = compile_(r"(hash = [\w\d\s]+)(\n\w.+?)\n\n", flags=DOTALL)
upd_re = compile_(r"\$Point\d+")

for path, _, files in walk("."):
    for filename in filter(files, "*.ini"):
        name = filename.removeprefix("DISABLED").removeprefix("_")
        if name in mappings:
            filepath = join(path, filename)
            if name in used:
                if "DISABLED" not in filename:
                    outpath = join(path, "DISABLED" + name)
                else:
                    outpath = filepath
            else:
                outpath = join(path, name)
            used.append(name)
            with open(filepath) as f:
                s = f.read()
            if "namespace = AdventureMap\\PointData" in s:
                s = upd_re.sub(f"$Point{mappings[name]}", s)
            else:
                s = f"namespace = AdventureMap\\PointData\n{s}"
                for x in add_re.findall(s):
                    newinfo = x[1].replace("\n", "\n\t")
                    s = s.replace(
                        f"{x[0]}{x[1]}",
                        f"{x[0]}\nif $Point{mappings[name]} == 1{newinfo}\nendif",
                    )
            with open(filepath, "w") as f:
                f.write(s)
            if filepath != outpath:
                rename(filepath, outpath)
        elif filename == "01_FocusLines.ini":
            rename(join(path, filename), join(path, "DISABLED" + filename))


unused = [x for x in mappings if x not in used]
if unused:
    print("The following files were not found:")
    print("\n".join(unused))
    print(
        """
This usually means that you either:
    1. Ran the script in the wrong directory.
    2. Didn't install all Focus Lines files.

If you intentionally didn't install all Focus Lines files then you can ignore this message and close this window.
Otherwise consider checking out the install guide on the mod page, and make sure you download all the files from Focus Lines mod page."""
    )
else:
    print("Patched all files, you can close this window now.")
