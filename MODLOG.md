# Suzumu Motorcycle — Conan Exiles Enhanced

## 2026-10-25 — intake and reconnaissance
- User requests a craftable, single rider motorcycle using the existing horse systems and the supplied Suzumu FBX/Blend.
- Game: `D:/Steam/steamapps/common/Conan Exiles`, Steam 440900; user version 3.0.1.
- Dev Kit: `D:/EGS/CEUE5Devkit`, `Engine/Build/Build.version`: UE 5.8.2, CL 378787, branch `++exiles+release`.
- `um scan` identifies native Windows x64 Unreal, IoStore, 76 paks, BattlEye, no injected mod loaders.
- Knowledge base searched locally with `um kb search Conan --root .`: no Conan field note.
- Route: official Dev Kit Blueprints and DataTables, deriving from horse mount; no runtime injection.
- Official Enhanced docs: https://exiles-enhanced.inflexion.io/modding/ (older docs mention 5.6.1; installed version is authoritative).
- Headless authoring reference: https://github.com/jvdberg1/kismetforge (Python table editing and RunUAT BuildMod).
- Model license provided by user says personal use only; no publishing requested.
- No game folders, saves, or stock assets modified.

## Required behavior
- Inventory 10 slots, one rider, immediately mountable after crafting and placement.
- Horse interaction and attribute growth; all initial attributes 15.
- Normal maximum 60 km/h = 1666.666667 cm/s; sprint 120 km/h = 3333.333333 cm/s (Unreal centimeter scale; confirm game speed path).
- Maximum stamina 1600; sprint cost 1 stamina/second.
- Fall damage multiplier 0.5, other damage unchanged.
- Artisan worktable recipe: 200 Hardened Steel Bar (18062), 50 Hardened Leather (12516), 100 Steel Reinforcement (16003); leather and reinforcement confirmed by user.
- Feat: level 40, 25 points, Survival branch under Apprentice Tinker.

## Next
Probe real horse classes, mount tables, item/recipe/feat schemas and headless editing API; build an isolated mod under Content/Mods/SuzumuMotorcycle.

## Recon results and authoring notes
- Game executable file/product version: `++exiles+release-CL-379176`; Dev Kit CL 378787. Runtime compatibility requires verification.
- Horse base: `/Game/Characters/NPCs/Hooved_Wild/Blueprints/BP_NPC_Mounts_Horse`; concrete horse: `_Knight`.
- Horse inventory uses int stat 22, endurance current/max use int stats 24/25.
- Horse SpawnData row `Horse_Knight` links Profession `Horse_Knight`, Growth `Horse_Knight`, LevelCurve `Normal`, PerkType `Hooved`, MountType `Horse`.
- Profession row links ThrallData row 110. New motorcycle requires its own profession and thrall row to retain its class on placement.
- EmbeddedSaddleID is a numeric row-name string (demon horse uses 2712), so the bike can ride without a player-supplied saddle.
- Feat parent 41020 is Apprentice Tinker, category Survival. Artisan Table ID is 18512.
- `BlueprintGraphEditor` and extended `BlueprintEditorLibrary` ARE available in this UE 5.8 build even though EditorToolset/ToolsetRegistry binaries are absent. Use native graph API directly.
- Broad inherited-property diagnostics caused a Dev Kit Python access violation. Switched to targeted reads and graph inspection.
- Inherited variable names from BlueprintEditorLibrary use dot-separated declaring-class prefixes.
- `-ModDevKit` mounts ProtectedAssets.pak and its virtual filesystem. Omitting it produced invalid base Blueprint dependencies. Saving is allowed only in the active mod's Local directory.
- Selected SuzumuMotorcycle by creating its modinfo.json and active.txt; previous test/active.txt preserved as active.txt.before-suzumu and copied to evidence/devkit_selection_backup.

## Canonical asset paths and clean rebuild
- The active-mod virtual filesystem maps `/Game/Mods/SuzumuMotorcycle/<asset>` to physical `Content/Mods/SuzumuMotorcycle/Local/<asset>`. `Local` must NOT occur in serialized game object paths.
- Initial package cooked successfully but referenced Local-qualified names. It is an intermediate package, not the final artifact.
- GUI asset-save diagnostics hit file locks while both aliases were loaded. The GUI job callback also needed a reentrancy guard while editor operations pump Slate messages. Added the guard.
- Preserved intermediate files in `private/intermediate-local-path-assets`; recreated only this task's mod Local folder.
- Clean headless authoring with canonical paths completed successfully (exit code 0), 2026-10-25 19:25 UTC. Both Blueprints compile without warnings; all 27 editor checks pass again.
- Launch `-ExecutePythonScript` automatically quits the editor after the startup script; persistent frame callbacks require `-ExecCmds="py <script>"` instead.
- Dev Kit config backup: `private/um/backups/conan-devkit-config/20261025-221424.zip`, created with `um backup` before GUI tests.

## Play In Editor verification
- The runtime discovers `/Game/Mods/SuzumuMotorcycle/BP_SuzumuModController` and spawns it.
- Spawned the actual crafted item 19871001 with GameItemSpawner, then used the native ThrallSystemComponent spawn-from-item path in the transient standalone PIE world.
- Confirmed correct custom actor class, ThrallComponent, embedded saddle 19871002, inventory 10, endurance 1600/1600, and the four displayed attributes at 15. The inherited AI stamina stat reads 1660 due to attribute bonuses; the mount's endurance bar is the separate 1600 stat.
- Native MountInput returns 1666.666626 cm/s normal and 3333.333252 cm/s sprint, within float precision of 60/120 km/h.
- The synthetic test player does not complete the normal mount transition. An ordinary horse with a standard saddle also does not complete it in the same harness. Do not claim successful riding, actual stamina drain, speed measurement, or persistence from these checks.
- Captured and visually inspected engine screenshots. Found an import bug: positional `unreal.Rotator(0,180,0)` yields pitch 180 in this kit. Replaced with explicit `pitch=0, yaw=180, roll=0` keywords.
- An upright runtime preview was verified using an equivalent transient component correction; final source model is reimported with the corrected baked orientation.
- Closed the transient PIE world and Dev Kit without saving changes to the stock AlmostEmpty map.
- Final corrected import and all 27 checks completed with commandlet exit code 0 at 19:45 UTC.
- Retail executable numeric file/product version fields are 5.8.2.0, independently confirming the game's engine matches Dev Kit UE 5.8.2 (only changelists differ).
- `um publish check source --game <install>` passes: 37 files, zero failures and warnings. No publishing performed.

## 2026-10-26: visual correction 0.1.1
- User verified normal riding/controls and requested only the inverted mesh and floating rider fix; no further riding tests.
- Retail package was accepted after stamping the installed SDK ModVersion 1002 into devkitRevisionNumber. The installer now reactivates a modlist line commented out by the game's incompatible-mod dialog.
- Actual mesh uses InterchangeAssetImportData. Despite the earlier FBX option change, tyre vertices remained above the seat. Correct the component itself: explicit Roll=180 and Z=27.398354; repeat the transform in Construction Script for loaded instances.
- Added an original post-process AnimBP using InputPose -> LocalToComponent -> ModifyBone -> ComponentToLocal -> Output. Only b_attachrider receives component translation (0,-10,-110) cm; all other bones retain the supplied pose.
- Native SetOverridePostProcessAnimBP applies the AnimBP only to this mod's hidden mesh component. No horse asset duplication, global skeleton modification, player-class patch, or locomotion replacement.
- Evaluated the AnimBP against the actual horse skeleton with AnimPoseExtensions. Attachment displacement matches within 0.01 cm; b_root, b_saddle and b_pelvis are unchanged. Actual transformed geometry has both tyres at ground and the seat above their tops.
- Important pin parsing: Blueprint Rotator defaults require canonical CSV `0,0,180`; `(Pitch=0,Yaw=0,Roll=180)` was accepted as a string but evaluated to zero rotation. Numeric vertex checks caught this before packaging.
- AutomationLibrary.take_high_res_screenshot blocked inside a Slate callback. Saved assets first, stopped only the task's editor PID, and switched the visual preview to SceneCapture2D / render target export.
- Render confirmed the motorcycle is upright. The standalone preview actor is not a mounted game player, so its position is not used as evidence of gameplay seating; the seat correction is verified by actual AnimBP evaluation and geometry coordinates.
- Official three-platform cook/package completed with exit code 0; no cook errors. Source lint passes: 38 files, zero failures/warnings. Target field note validation passes.
- Installed 0.1.1 at 2026-10-26 19:17 Moscow. SHA256: 9360F2996916835CC737EF2F09C4E2564FCBB12E897D26717479C5EDB95AB314. Previous pak/modlist preserved in private/install-backup-20261026-191730.
- Dev Kit was closed; retail game was not relaunched and no additional riding/input tests were performed.
