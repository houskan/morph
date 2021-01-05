import bpy, mathutils

ARMATURE = 'AArmature'
ANIMATION_BONES_MAIN_LAYER = 0
ANIMATION_BONES_SUPPORT_LAYER = 16
DEFORMATION_BONES_LAYER = 1

def update():
    Rig = bpy.data.objects[ARMATURE]

    PoseBones = Rig.pose.bones
    Positions = {}

    """
    Disable IK constraints
    """

    PoseBones["LowerLeg.L"].constraints["IK"].influence = 0
    PoseBones["LowerLeg.R"].constraints["IK"].influence = 0
    PoseBones["LowerArm.L"].constraints["IK"].influence = 0
    PoseBones["LowerArm.R"].constraints["IK"].influence = 0

    PoseBones["Foot.L"].constraints["IK"].influence = 0
    PoseBones["Foot.R"].constraints["IK"].influence = 0
    PoseBones["Hand.L"].constraints["IK"].influence = 0
    PoseBones["Hand.R"].constraints["IK"].influence = 0

    PoseBones["Toe.L"].constraints["IK"].influence = 0
    PoseBones["Toe.R"].constraints["IK"].influence = 0
    PoseBones["Finger.L"].constraints["IK"].influence = 0
    PoseBones["Finger.R"].constraints["IK"].influence = 0

    bpy.context.evaluated_depsgraph_get()

    """ 
    Legs
    """

    Positions["LL1"] = PoseBones["Tights.L"].head.copy()
    Positions["LL2"] = PoseBones["Knee.L"].head.copy()
    Positions["LL3"] = PoseBones["Ankle.L"].head.copy()
    Positions["LL4"] = PoseBones["Toe_Joint.L"].head.copy()
    Positions["LL5"] = PoseBones["ToeClaws.L"].head.copy()

    """Positions["LR1"] = PoseBones["Tights.R"].head.copy()
    Positions["LR2"] = PoseBones["Knee.R"].head.copy()
    Positions["LR3"] = PoseBones["Ankle.R"].head.copy()
    Positions["LR4"] = PoseBones["Toe_Joint.R"].head.copy()
    Positions["LR5"] = PoseBones["ToeClaws.R"].head.copy()
    """

    Positions["LR1"] = PoseBones["Tights.L"].head.copy()
    Positions["LR1"].x = -Positions["LR1"].x
    Positions["LR2"] = PoseBones["Knee.L"].head.copy()
    Positions["LR2"].x = -Positions["LR2"].x
    Positions["LR3"] = PoseBones["Ankle.L"].head.copy()
    Positions["LR3"].x = -Positions["LR3"].x
    Positions["LR4"] = PoseBones["Toe_Joint.L"].head.copy()
    Positions["LR4"].x = -Positions["LR4"].x
    Positions["LR5"] = PoseBones["ToeClaws.L"].head.copy()
    Positions["LR5"].x = -Positions["LR5"].x

    """
    Arm
    """

    Positions["AL1"] = PoseBones["Scapula_Start.L"].head.copy()
    Positions["AL2"] = PoseBones["Shoulder.L"].head.copy()
    Positions["AL3"] = PoseBones["Elbow.L"].head.copy()
    Positions["AL4"] = PoseBones["Wrist.L"].head.copy()
    Positions["AL5"] = PoseBones["Finger_Joint.L"].head.copy()
    Positions["AL6"] = PoseBones["FingerClaws.L"].head.copy()

    """Positions["AR1"] = PoseBones["Scapula_Start.R"].head.copy()
    Positions["AR2"] = PoseBones["Shoulder.R"].head.copy()
    Positions["AR3"] = PoseBones["Elbow.R"].head.copy()
    Positions["AR4"] = PoseBones["Wrist.R"].head.copy()
    Positions["AR5"] = PoseBones["Finger_Joint.R"].head.copy()
    Positions["AR6"] = PoseBones["FingerClaws.R"].head.copy()
    """

    Positions["AR1"] = PoseBones["Scapula_Start.L"].head.copy()
    Positions["AR1"].x = -Positions["AR1"].x
    Positions["AR2"] = PoseBones["Shoulder.L"].head.copy()
    Positions["AR2"].x = -Positions["AR2"].x
    Positions["AR3"] = PoseBones["Elbow.L"].head.copy()
    Positions["AR3"].x = -Positions["AR3"].x
    Positions["AR4"] = PoseBones["Wrist.L"].head.copy()
    Positions["AR4"].x = -Positions["AR4"].x
    Positions["AR5"] = PoseBones["Finger_Joint.L"].head.copy()
    Positions["AR5"].x = -Positions["AR5"].x
    Positions["AR6"] = PoseBones["FingerClaws.L"].head.copy()
    Positions["AR6"].x = -Positions["AR6"].x

    """
    Body
    """

    Positions["B0"] = PoseBones["Pelvis_Root"].head.copy()
    Positions["B1"] = PoseBones["Spine"].head.copy()
    Positions["B2"] = PoseBones["Back"].head.copy()
    Positions["B3"] = PoseBones["Neck"].head.copy()
    Positions["B4"] = PoseBones["Head_Root"].head.copy()
    Positions["B5"] = PoseBones["Snout"].tail.copy()
    Positions["B6"] = PoseBones["Tail"].head.copy()
    Positions["B7"] = PoseBones["Tail_End"].head.copy()

    """
    Change to edit mode and adjust animation bones
    """

    bpy.ops.object.mode_set(mode='EDIT')
    EditBones = Rig.data.edit_bones

    """
    Legs
    """

    EditBones["UpperLeg.L"].head = Positions["LL1"]
    EditBones["LowerLeg.L"].head = Positions["LL2"]
    EditBones["Foot.L"].head = Positions["LL3"]
    EditBones["FootTarget.L"].head = Positions["LL4"]
    EditBones["FootTarget.L"].tail = Positions["LL4"] + mathutils.Vector((0, 10, 0))
    EditBones["LegIK.L"].head = Positions["LL3"]
    EditBones["LegIK.L"].tail = Positions["LL3"] + mathutils.Vector((0, 10, 0))
    EditBones["LegPole.L"].head = Positions["LL2"] + mathutils.Vector((0, -60, 0))
    EditBones["LegPole.L"].tail = Positions["LL2"] + mathutils.Vector((0, -75, 0))
    EditBones["Toe.L"].head = Positions["LL4"]
    EditBones["Toe.L"].tail = Positions["LL5"]
    EditBones["ToeTarget.L"].head = Positions["LL5"]
    EditBones["ToeTarget.L"].tail = Positions["LL5"] + mathutils.Vector((0, 10, 0))

    EditBones["UpperLeg.R"].head = Positions["LR1"]
    EditBones["LowerLeg.R"].head = Positions["LR2"]
    EditBones["Foot.R"].head = Positions["LR3"]
    EditBones["FootTarget.R"].head = Positions["LR4"]
    EditBones["FootTarget.R"].tail = Positions["LR4"] + mathutils.Vector((0, 10, 0))
    EditBones["LegIK.R"].head = Positions["LR3"]
    EditBones["LegIK.R"].tail = Positions["LR3"] + mathutils.Vector((0, 10, 0))
    EditBones["LegPole.R"].head = Positions["LR2"] + mathutils.Vector((0, -60, 0))
    EditBones["LegPole.R"].tail = Positions["LR2"] + mathutils.Vector((0, -75, 0))
    EditBones["Toe.R"].head = Positions["LR4"]
    EditBones["Toe.R"].tail = Positions["LR5"]
    EditBones["ToeTarget.R"].head = Positions["LR5"]
    EditBones["ToeTarget.R"].tail = Positions["LR5"] + mathutils.Vector((0, 10, 0))

    """
    Arm
    """

    EditBones["Scapula.L"].head = Positions["AL1"]
    EditBones["UpperArm.L"].head = Positions["AL2"]
    EditBones["LowerArm.L"].head = Positions["AL3"]
    EditBones["Hand.L"].head = Positions["AL4"]
    EditBones["HandTarget.L"].head = Positions["AL5"]
    EditBones["HandTarget.L"].tail = Positions["AL5"] + mathutils.Vector((0, 10, 0))
    EditBones["ArmIK.L"].head = Positions["AL4"]
    EditBones["ArmIK.L"].tail = Positions["AL4"] + mathutils.Vector((0, 10, 0))
    EditBones["ArmPole.L"].head = Positions["AL3"] + mathutils.Vector((0, -Positions["AL3"].y - 15, 0))
    EditBones["ArmPole.L"].tail = Positions["AL3"] + mathutils.Vector((0, -Positions["AL3"].y, 0))
    EditBones["Finger.L"].head = Positions["AL5"]
    EditBones["Finger.L"].tail = Positions["AL6"]
    EditBones["FingerTarget.L"].head = Positions["AL6"]
    EditBones["FingerTarget.L"].tail = Positions["AL6"] + mathutils.Vector((0, 10, 0))

    EditBones["Scapula.R"].head = Positions["AR1"]
    EditBones["UpperArm.R"].head = Positions["AR2"]
    EditBones["LowerArm.R"].head = Positions["AR3"]
    EditBones["Hand.R"].head = Positions["AR4"]
    EditBones["HandTarget.R"].head = Positions["AR5"]
    EditBones["HandTarget.R"].tail = Positions["AR5"] + mathutils.Vector((0, 10, 0))
    EditBones["ArmIK.R"].head = Positions["AR4"]
    EditBones["ArmIK.R"].tail = Positions["AR4"] + mathutils.Vector((0, 10, 0))
    EditBones["ArmPole.R"].head = Positions["AR3"] + mathutils.Vector((0, -Positions["AR3"].y - 15, 0))
    EditBones["ArmPole.R"].tail = Positions["AR3"] + mathutils.Vector((0, -Positions["AR3"].y, 0))
    EditBones["Finger.R"].head = Positions["AR5"]
    EditBones["Finger.R"].tail = Positions["AR6"]
    EditBones["FingerTarget.R"].head = Positions["AR6"]
    EditBones["FingerTarget.R"].tail = Positions["AR6"] + mathutils.Vector((0, 10, 0))

    """
    Body
    """
    EditBones["Pelvis"].tail = Positions["B1"]
    EditBones["Pelvis_Main"].head = Positions["B1"]
    EditBones["Pelvis_Main"].tail = Positions["B0"]
    EditBones["Caudal"].head = Positions["B6"]
    EditBones["Caudal"].tail = Positions["B7"]
    EditBones["Torso"].head = Positions["B2"]
    EditBones["Cervical"].head = Positions["B3"]
    EditBones["Head"].head = Positions["B4"]
    EditBones["Head"].tail = Positions["B5"]

    """
    Root
    """

    EditBones["Root"].head = Positions["AR6"] / 2 + Positions["LL5"] / 2 - mathutils.Vector((0, 0, Positions["LL5"][2]))
    EditBones["Root"].tail = Positions["AR6"] / 2 + Positions["LL5"] / 2 + mathutils.Vector((0, 0, 20))
    EditBones["Root"].head.x = 0
    EditBones["Root"].tail.x = 0

    """
    Back to Pose Mode and enable IK again
    """
    bpy.ops.object.mode_set(mode='POSE')

    PoseBones["LowerLeg.L"].constraints["IK"].influence = 1
    PoseBones["LowerLeg.R"].constraints["IK"].influence = 1
    PoseBones["LowerArm.L"].constraints["IK"].influence = 1
    PoseBones["LowerArm.R"].constraints["IK"].influence = 1

    PoseBones["Foot.L"].constraints["IK"].influence = 1
    PoseBones["Foot.R"].constraints["IK"].influence = 1
    PoseBones["Hand.L"].constraints["IK"].influence = 1
    PoseBones["Hand.R"].constraints["IK"].influence = 1

    PoseBones["Toe.L"].constraints["IK"].influence = 1
    PoseBones["Toe.R"].constraints["IK"].influence = 1
    PoseBones["Finger.L"].constraints["IK"].influence = 1
    PoseBones["Finger.R"].constraints["IK"].influence = 1

    bpy.context.evaluated_depsgraph_get()