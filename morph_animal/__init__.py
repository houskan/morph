bl_info = {
    "name": "Morphological Animal Design App",
    "author": "Niklaus Houska",
    "version": (1, 1, 0),
    "blender": (2, 82, 0),
    "location": "View3D",
    "description": "Create Animal Anatomy and Gaits",
    "category": "Development",
}

if "bpy" in locals():
    import importlib
    importlib.reload(anatomy_properties)
    importlib.reload(gait_properties)
    importlib.reload(operators)
    importlib.reload(ui)
else:
    from . import anatomy_properties
    from . import gait_properties
    from . import operators
    from . import ui

import bpy


def register():
    bpy.types.Scene.mut_bone_names = {"Tail", "Tail_End", "Pelvis_Root", "Tights.L", "Tights.R", "Knee.L", "Knee.R",
                                      "Ankle.L", "Ankle.R", "Toe_Joint.L", "Toe_Joint.R", "Spine", "Back",
                                      "Scapula_Start.L", "Scapula_Start.R", "Shoulder.L", "Shoulder.R", "Elbow.L",
                                      "Elbow.R", "Wrist.L", "Wrist.R", "Finger_Joint.L", "Finger_Joint.R",
                                      "FingerClaws.L", "FingerClaws.R", "Neck", "Head_Root", "Brain", "Snout",
                                      "Sternum_Head", "Sternum_End", "ToeClaws.L", "ToeClaws.R"}
    bpy.types.Scene.anim_bone_names = {"Toe.L", "Toe.R", "LegIK.L", "LegIK.R", "LegPole.L", "LegPole.R", "Pelvis",
                                       "Pelvis_Main", "Sacrum",
                                       "Caudal", "Lumbar", "Torso", "Cervical", "Head", "Scapula.L", "Scapula.R",
                                       "ArmPole.L", "ArmPole.R", "ArmIK.L",
                                       "ArmIK.R", "Finger.L", "Finger.R", "Root", "ToeTarget.L", "ToeTarget.R",
                                       "FingerTarget.L", "FingerTarget.R", "FootTarget.L", "FootTarget.R",
                                       "HandTarget.L", "HandTarget.R"}
    anatomy_properties.register()
    gait_properties.register()
    operators.register()
    ui.register()


def unregister():
    del bpy.types.Scene.mut_bone_names
    del bpy.types.Scene.anim_bone_names
    if hasattr(bpy.types.Scene, 'pca'):
        del bpy.types.Scene.pca
    ui.unregister()
    operators.unregister()
    gait_properties.unregister()
    anatomy_properties.unregister()