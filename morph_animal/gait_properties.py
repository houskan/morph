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


def update_all(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_all()
    context.scene.frame_set(frame)


def update_pelvis(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_pelvis()
    context.scene.gait.update_torso()
    context.scene.gait.update_limb(is_right=False)
    context.scene.gait.update_limb(is_right=True)
    context.scene.frame_set(frame)


def update_torso(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_torso()
    context.scene.gait.update_head()
    context.scene.gait.update_scapula(right_arm=True)
    context.scene.gait.update_scapula(right_arm=False)
    context.scene.gait.update_limb(is_right=False, is_arm=True)
    context.scene.gait.update_limb(is_right=True, is_arm=True)
    context.scene.frame_set(frame)


def update_head(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_head()
    context.scene.frame_set(frame)


def update_scapula(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_scapula(right_arm=True)
    context.scene.gait.update_scapula(right_arm=False)
    context.scene.gait.update_limb(is_right=False, is_arm=True)
    context.scene.gait.update_limb(is_right=True, is_arm=True)
    context.scene.frame_set(frame)


def update_legs(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_limb(is_right=False)
    context.scene.gait.update_limb(is_right=True)
    context.scene.frame_set(frame)


def update_arms(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_limb(is_right=False, is_arm=True)
    context.scene.gait.update_limb(is_right=True, is_arm=True)
    context.scene.frame_set(frame)


def update_limbs(self, context):
    if not context.scene.panel_parameters.update_gait or not hasattr(context.scene, 'gait'):
        return
    frame = context.scene.frame_current
    context.scene.gait.set_parameters(context.scene.gait_description)
    context.scene.gait.update_limb(is_right=False)
    context.scene.gait.update_limb(is_right=True)
    context.scene.gait.update_limb(is_right=False, is_arm=True)
    context.scene.gait.update_limb(is_right=True, is_arm=True)
    context.scene.frame_set(frame)


class GaitDescription(bpy.types.PropertyGroup):
    ref: StringProperty(
        name="name")
    # ("Trot", "Trot", "Trotting gait (Froude range 0.3 - 3)"),
    # ("Galopp", "Galopp", "Galopping gait (Froude range 2+)")
    gait_classification: EnumProperty(
        items=[
            ("Walk", "Walk", "Walking gait (Froude range 0 - 0.8)")
        ])
    r: FloatProperty(
        name = "Walk ratio",
        default=0.53571,
        description="f / stride",
        soft_min=0.01,
        update=update_all)
    v: FloatProperty(
        name="Speed",
        default=1.37143,
        description="f * stride [m/s]",
        soft_min=0.01,
        soft_max=5,
        update=update_all)
    duty: FloatProperty(
        name="Duty Factor",
        default=0.625,
        description="percentage of a full stride a limb touches the ground",
        soft_min=0.05,
        soft_max=0.95,
        update=update_all)
    pelvis_up: FloatProperty(
        name="Pelvis Max Z-Offset",
        description="Highest position of pelvis (Offset from Rest Pose)",
        default=144.7,
        soft_min=-100,
        soft_max=100,
        update=update_pelvis)
    pelvis_down: FloatProperty(
        name="Pelvis Min Z-Offset",
        description="Lowest position of pelvis (Offset from Rest Pose)",
        default=135.7,
        soft_min=-100,
        soft_max=100,
        update=update_pelvis)
    pelvis_rot: FloatProperty(
        name="Pelvis Rotation",
        description="Maximal rotation of pelvis",
        default=math.pi / 12,
        soft_max=math.pi / 2,
        soft_min=0,
        unit='ROTATION',
        update=update_pelvis)
    neck_up: FloatProperty(
        name="Neck Max Z-Offset",
        description="Highest position of the neck (Offset from rest pose)",
        default=134.4,
        soft_min=-100,
        soft_max=100,
        update=update_torso)
    neck_down: FloatProperty(
        name="Neck Min Z-Offset",
        description="Lowest position of the neck (Offset from rest pose)",
        default=123.1,
        soft_min=-100,
        soft_max=100,
        update=update_torso)
    arm_width: FloatProperty(
        default=15,
        soft_min=1)
    leg_width: FloatProperty(
        default=15,
        soft_min=1)
    lift: FloatProperty(
        name="Step Height",
        description="Height of a step",
        default=15,
        soft_min=0,
        soft_max=100,
        update=update_limbs)
    lift_rot: FloatProperty(
        name="Step Orientation",
        description="Orientation of the toes/fingers relative to the ground when lifted",
        default=math.radians(-30),
        soft_min=-math.pi,
        soft_max=0,
        unit='ROTATION',
        update=update_limbs)
    clL: FloatProperty(default=0, name = "Left Leg Contact", min = 0, max = 1, soft_min = 0, soft_max = 1, update = update_all, description="Phase of left leg contact")
    clR: FloatProperty(default=0.5, name = "Right Leg Contact", min=0, max=1, soft_min=0, soft_max=1, update=update_all, description="Phase of right leg contact")
    caL: FloatProperty(default=0.25, name = "Left Arm Contact", min=0, max=1, soft_min=0, soft_max=1, update=update_all, description="Phase of left arm contact")
    caR: FloatProperty(default=0.75, name = "Right Arm Contact", min=0, max=1, soft_min=0, soft_max=1, update=update_all, description="Phase of right arm contact")
    head_offset: FloatProperty(
        name="Head Z-Offset",
        description="Position of head (Offset from rest pose)",
        default=-27.4,
        soft_min=-100,
        soft_max=100,
        update=update_head)
    head_rot: FloatProperty(
        name="Head Orientation",
        description="Orientation of the head",
        default=0.25 * math.pi,
        unit='ROTATION',
        soft_min=0,
        soft_max=math.pi / 2,
        update=update_head)
    scapula_up: FloatProperty(
        name="Scapula Max Z-Offset",
        description="Highest position of the scapula (Offset from rest pose)",
        default=8.17,
        soft_min=-30,
        soft_max=30,
        update=update_scapula)
    scapula_down: FloatProperty(
        name="Scapula Min Z-Offset",
        description="Lowest position of the scapula (Offset from rest pose)",
        default=-8.15,
        soft_min=-30,
        soft_max=30,
        update=update_scapula)
    step_shift_leg: FloatProperty(
        name="Leg Contact Y-Offset",
        description="Shift of leg contact position (Percentage of step length)",
        default=0.1,
        soft_min=-0.5,
        soft_max=0.5,
        update=update_legs)
    step_shift_arm: FloatProperty(
        name="Arm Contact Y-Offset",
        description="Shift of arm contact position (Percentage of step length)",
        default=-0.1,
        soft_min=-0.5,
        soft_max=0.5,
        update=update_arms)
    roll_toe_foot_angle_ratio: FloatProperty(
        name="Roll Hyper parameter 2",
        description="Factor of 'Roll hyper parameter 1' that is applied to the hand and foot",
        default=0.5,
        soft_min=0,
        soft_max=2,
        min = 0,
        update=update_limbs)
    roll_initial_rot_percentage: FloatProperty(
        name="Roll Hyper parameter 1",
        description="Roll hyper parameter 1: Higher values lead to stronger finger and toe roll",
        default = 0.3,
        soft_min = 0,
        soft_max = 1,
        min = 0,
        max = 1,
        update=update_limbs)
    hoof_flexibility: FloatProperty(
        name="Hoof Contact Hyper Parameter",
        description="Higher values lead to a reduced angle to the ground at contact",
        default = 12,
        soft_min = 0,
        soft_max = 25,
        min = 0,
        update=update_limbs
    )
    contact_width_shift: FloatProperty(
        name="Contact Width X-Offset",
        description="Width of contact position (Offset from rest pose)",
        default = 0,
        soft_min = -50,
        soft_max = 50,
        update=update_limbs)


def copy_gait_description(from_a, to_b):
    to_b.ref = from_a.ref
    to_b.gait_classification  = from_a.gait_classification
    to_b.r = from_a.r
    to_b.v = from_a.v
    to_b.duty = from_a.duty
    to_b.pelvis_up = from_a.pelvis_up
    to_b.pelvis_down = from_a.pelvis_down
    to_b.pelvis_rot = from_a.pelvis_rot
    to_b.neck_up = from_a.neck_up
    to_b.neck_down = from_a.neck_down
    to_b.arm_width = from_a.arm_width
    to_b.leg_width = from_a.leg_width
    to_b.lift = from_a.lift
    to_b.lift_rot = from_a.lift_rot
    to_b.clL = from_a.clL
    to_b.clR = from_a.clR
    to_b.caL = from_a.caL
    to_b.caR = from_a.caR
    to_b.head_offset = from_a.head_offset
    to_b.head_rot = from_a.head_rot
    to_b.scapula_up = from_a.scapula_up
    to_b.scapula_down = from_a.scapula_down
    to_b.step_shift_leg = from_a.step_shift_leg
    to_b.step_shift_arm = from_a.step_shift_arm
    to_b.roll_toe_foot_angle_ratio = from_a.roll_toe_foot_angle_ratio
    to_b.roll_initial_rot_percentage = from_a.roll_initial_rot_percentage
    to_b.hoof_flexibility = from_a.hoof_flexibility
    to_b.contact_width_shift= from_a.contact_width_shift


def set_gait_defaults(context):
    params = context.scene.gait_description

    if hasattr(context.scene, 'pca') and len(context.scene.stored_gait) > 0:
        bpy.ops.myops.rest_pose_operator()
        pca = context.scene.pca
        weights1 = pca.calculate_pca_weight(pca.anatomy_to_vector())
        min = 10000000
        reference = context.scene.stored_gait[0]
        for stored in context.scene.stored_gait:
            if stored.ref in pca.reference_weights.keys():
                weights2 = pca.reference_weights[stored.ref]
                dist = utils.pca_weight_distance_squared(weights1, weights2)
                if dist < min:
                    min = dist
                    reference = stored
        gait_description_from_reference(context, params, reference)
        context.scene.panel_parameters.reference_gait = reference.ref
    else:
        found = False
        for stored in context.scene.stored_gait:
            found = params.ref == stored.ref
            if found:
                context.scene.panel_parameters.reference_gait = stored.ref
                copy_gait_description(stored, params)
                break
        if not found:
            found = False
            for stored in context.scene.stored_gait:
                found = "Horse" == stored.ref
                if found:
                    context.scene.panel_parameters.reference_gait = stored.ref
                    gait_description_from_reference(context, params, stored)
                    break

            if not found:
                context.scene.panel_parameters.reference_gait = "None"
                l = context.object.pose.bones["UpperLeg.L"].bone.head_local.z
                leg_width = context.object.data.bones["Toe.L"].head_local.x
                arm_width = context.object.data.bones["Finger.L"].head_local.x

                llambda = l / 129.8572
                tau = math.sqrt(llambda)

                params.gait_classification = 'Walk'
                params.v = (llambda / tau) * ((6 / 7) * 1.6)
                f = (6 / 7) / tau
                stride = params.v / f
                params.r = f / stride
                params.duty = 0.625
                params.pelvis_up = llambda * -2.1066
                params.pelvis_down = llambda * -11.10667
                params.pelvis_rot = math.radians(12)
                params.neck_up = llambda * -3.407
                params.neck_down = llambda * -12.35
                params.lift = llambda * 15
                params.lift_rot = math.radians(-30)
                params.clL = 0
                params.clR = 0.5
                params.caL = 0.25
                params.caR = 0.75
                params.head_offset = llambda * -27.47
                params.head_rot = math.radians(45)
                params.scapula_up = llambda * 3.2
                params.scapula_down = llambda * (- 8.15)
                params.step_shift_leg = 0
                params.step_shift_arm = 0
                params.leg_width = leg_width
                params.arm_width = arm_width
                params.roll_toe_foot_angle_ratio = 0.5
                params.roll_initial_rot_percentage = 0.3
                params.hoof_flexibility = 12
                params.contact_width_shift = 0


def gait_description_from_reference(context, description, reference):
    found = False
    l_ref = 100
    for stored in context.scene.stored_anatomy:
        found = reference.ref == stored.ref
        if found:
            l_ref = stored.l
            break

    if not found:
        return

    l = context.object.pose.bones["UpperLeg.L"].bone.head_local.z
    leg_width = context.object.data.bones["Toe.L"].head_local.x
    arm_width = context.object.data.bones["Finger.L"].head_local.x

    llambda = l / l_ref
    tau = math.sqrt(llambda)

    f_ref = math.sqrt(reference.r * reference.v)

    description.gait_classification = 'Walk'
    description.v = (llambda / tau) * reference.v
    f = f_ref / tau
    stride = description.v / f
    description.r = f / stride
    description.duty = reference.duty
    description.pelvis_up = llambda * reference.pelvis_up
    description.pelvis_down = llambda * reference.pelvis_down
    description.pelvis_rot = reference.pelvis_rot
    description.neck_up = llambda * reference.neck_up
    description.neck_down = llambda * reference.neck_down
    description.lift = llambda * reference.lift
    description.lift_rot = reference.lift_rot
    description.clL = reference.clL
    description.clR = reference.clR
    description.caL = reference.caL
    description.caR = reference.caR
    description.head_offset = llambda * reference.head_offset
    description.head_rot = reference.head_rot
    description.scapula_up = llambda * reference.scapula_up
    description.scapula_down = llambda * reference.scapula_down
    description.step_shift_leg = reference.step_shift_leg
    description.step_shift_arm = reference.step_shift_arm
    description.leg_width = leg_width
    description.arm_width = arm_width
    description.roll_toe_foot_angle_ratio = reference.roll_toe_foot_angle_ratio
    description.roll_initial_rot_percentage = reference.roll_initial_rot_percentage
    description.hoof_flexibility = reference.hoof_flexibility
    description.contact_width_shift = min(llambda * reference.contact_width_shift, min(leg_width, arm_width))


classes = (
    GaitDescription,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.gait_description = PointerProperty(type=GaitDescription)
    bpy.types.Scene.stored_gait = CollectionProperty(type=GaitDescription)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.gait_description