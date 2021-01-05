import bpy, mathutils, math
from . import utils

from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    EnumProperty,
    StringProperty,
    FloatVectorProperty,
    PointerProperty,
    CollectionProperty,
)

ARMATURE= 'AArmature'


def update_ref(self, context):
    if self.ref == "":
        self.ref = "NewAnimal"


def update_pole(self, context):
    right_leg = -math.pi - self.leg_pole
    right_arm = math.pi - self.arm_pole
    if right_leg < -math.pi:
        right_leg = 2 * math.pi + right_leg
    if right_arm > math.pi:
        right_arm = -2 * math.pi + right_arm
    bpy.data.objects[ARMATURE].pose.bones["LowerLeg.L"].constraints["IK"].pole_angle = self.leg_pole
    bpy.data.objects[ARMATURE].pose.bones["LowerLeg.R"].constraints["IK"].pole_angle = right_leg
    bpy.data.objects[ARMATURE].pose.bones["LowerArm.L"].constraints["IK"].pole_angle = self.arm_pole
    bpy.data.objects[ARMATURE].pose.bones["LowerArm.R"].constraints["IK"].pole_angle = right_arm


def update_pca(self, context):
    """
    Update the anatomy according to pca weights
    """
    if not hasattr(context.scene, 'pca'):
        return
    pca = context.scene.pca
    vectorized = pca.calculate_vectorized(utils.get_denormalized_pca_weights(context, self.pca_weights))
    pca.apply_vectorized_to_pose(vectorized)


def copy_anatomy_description(from_a, to_b):
    to_b.ref = from_a.ref
    to_b.classification = from_a.classification
    to_b.leg_pole = from_a.leg_pole
    to_b.arm_pole = from_a.arm_pole
    to_b.l = from_a.l
    to_b.pca_weights = from_a.pca_weights


class AnatomyDescription(bpy.types.PropertyGroup):
    ref: StringProperty(
        description="Name of new animal",
        name = "Name",
        default="NewAnimal",
        update=update_ref)
    l: FloatProperty(
        name = "Hip Height",
        description = "Hip Height in Rest Pose [cm]",
        default = 100)
    # ("Plantigrade", "Plantigrade", "Walks with whole foot on ground (e.g. Human, Bear)")
    classification: EnumProperty(
        items=[
        ("Unguligrade", "Unguligrade", "Walks on tip-toes (E.g. Horse, Cattle)"),
        ("Digitigrade", "Digitigrade", "Walks with toes on ground (e.g. Lion, Dog)"),
        ])
    leg_pole: FloatProperty(
        name = "IK Leg Pole",
        default = -math.pi / 2,
        max = math.pi,
        min = -math.pi,
        unit = "ROTATION",
        update = update_pole)
    arm_pole: FloatProperty(
        name = "IK Arm Pole",
        default = math.pi / 2,
        max = math.pi,
        min = -math.pi,
        unit = "ROTATION",
        update = update_pole)
    pca_weights: FloatVectorProperty(
        name = "Principal Components",
        description="Scaled to fit [-100, 100]",
        size = 14,
        precision=0,
        soft_min = -100,
        soft_max = 100,
        update = update_pca)


classes = (
    AnatomyDescription,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.anatomy_description = PointerProperty(type=AnatomyDescription)
    bpy.types.Scene.stored_anatomy = CollectionProperty(type=AnatomyDescription)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.anatomy_description