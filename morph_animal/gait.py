import bpy
from math import *
from mathutils import *
from . import utils

class Gait():
    def __init__(self, **kwargs):
        self.armature = kwargs.pop('armature')
        self.action = kwargs.pop('action')
        self.animal_classification = kwargs.pop('animal_classification')

        params = kwargs.pop('parameters')
        self.set_parameters(params)
        self.calculate_body_measurements()


    @property
    def f(self): return sqrt(self.r * self.v)

    @property
    def t(self): return 1.0 / self.f

    @property
    def stride(self): return self.v / self.f

    @property
    def step(self): return self.duty * self.stride

    @property
    def shape(self): return 1.0 - self.duty

    @property
    def froude(self): return self.v ** 2 / (self.l * 0.01 * 9.81)

    @property
    def strouhal(self): return (self.f * self.l * 0.01) / self.v


    def frame(self, *, time): return utils.round_half_up(time * self.t * bpy.context.scene.render.fps)


    def set_parameters(self, gait_description):
        """
        Copies gait_parameters to in-class variables
        """
        self.r = gait_description.r
        self.v = gait_description.v
        self.duty = gait_description.duty
        self.pelvis_up = gait_description.pelvis_up
        self.pelvis_down = gait_description.pelvis_down
        self.pelvis_rot = gait_description.pelvis_rot
        self.neck_up = gait_description.neck_up
        self.neck_down = gait_description.neck_down
        self.arm_width = gait_description.arm_width
        self.leg_width = gait_description.leg_width
        self.lift = gait_description.lift
        self.lift_rot = gait_description.lift_rot
        self.clL = gait_description.clL
        self.clR = gait_description.clR
        self.caL = gait_description.caL
        self.caR = gait_description.caR
        self.head_offset = gait_description.head_offset
        self.head_rot = gait_description.head_rot
        self.scapula_up = gait_description.scapula_up
        self.scapula_down = gait_description.scapula_down
        self.step_shift_leg = gait_description.step_shift_leg
        self.step_shift_arm = gait_description.step_shift_arm
        self.roll_toe_foot_angle_ratio = gait_description.roll_toe_foot_angle_ratio
        self.roll_initial_rot_percentage = gait_description.roll_initial_rot_percentage
        self.hoof_flexibility = gait_description.hoof_flexibility
        self.contact_width_shift = gait_description.contact_width_shift


    def calculate_body_measurements(self):
        """
        Calculate necessary body measurements.
        l: hip height in rest pose
        l2: shoulder height in rest pose
        pelvis_shift: height of pelvis
        head_height: height of head in rest pose
        ankle_toe: distance between ankle and toe tip in rest pose
        hip_toe: distance between hip and toe tip in rest pose
        hip_ankle: distance between hip and ankle in rest pose
        neck_y: distance between pelvis and neck
        """
        self.l = self.armature.data.bones["UpperLeg.L"].head_local.z
        self.l2 = self.armature.data.bones["Torso"].tail_local.z
        self.pelvis_shift = self.armature.data.bones["Pelvis_Main"].head_local.z - self.armature.data.bones["Pelvis_Main"].tail_local.z
        self.head_height = self.armature.data.bones["Head"].head_local.z

        bones = self.armature.data.bones
        if True and self.animal_classification == 'Unguligrade':
            self.ankle_toe = (bones["Foot.L"].head_local - bones["Toe.L"].tail_local).length
            self.hip_toe = (bones["UpperLeg.L"].head_local - bones["Toe.L"].tail_local).length
        else:
            self.ankle_toe = (bones["Foot.L"].head_local - bones["Toe.L"].head_local).length
            self.hip_toe = (bones["UpperLeg.L"].head_local - bones["Toe.L"].head_local).length
        self.hip_ankle = (bones["UpperLeg.L"].head_local - bones["Foot.L"].head_local).length

        if True and self.animal_classification == 'Unguligrade':
            self.wrist_finger = (bones["Hand.L"].head_local - bones["Finger.L"].tail_local).length
            self.shoulder_finger = (bones["UpperArm.L"].head_local - bones["Finger.L"].tail_local).length
        else:
            self.wrist_finger = (bones["Hand.L"].head_local - bones["Finger.L"].head_local).length
            self.shoulder_finger = (bones["UpperArm.L"].head_local - bones["Finger.L"].head_local).length
        self.shoulder_wrist = (bones["UpperArm.L"].head_local - bones["Hand.L"].head_local).length

        self.foot_length = bones["Foot.L"].length
        if self.animal_classification == 'Unguligrade':
            self.foot_length += bones["Toe.L"].length
        self.leg_length = self.foot_length + bones["LowerLeg.L"].length + bones["UpperLeg.L"].length

        self.hand_length = bones["Hand.L"].length
        if self.animal_classification == 'Unguligrade':
            self.hand_length += bones["Finger.L"].length
        self.arm_length = self.hand_length + bones["LowerArm.L"].length + bones["UpperArm.L"].length
        self.neck_y = bones["Torso"].tail_local.y


    def clear_unnecessary_fcurves(self):
        ikl = self.armature.pose.bones["LegIK.L"]
        ikr = self.armature.pose.bones["LegIK.R"]
        toel = self.armature.pose.bones["Toe.L"]
        toer = self.armature.pose.bones["Toe.R"]
        ikl1 = self.armature.pose.bones["ArmIK.L"]
        ikr1 = self.armature.pose.bones["ArmIK.R"]
        toel1 = self.armature.pose.bones["Finger.L"]
        toer1 = self.armature.pose.bones["Finger.R"]
        utils.clear_fcurves(bones=(ikl, ikr, toel, toer, ikl1, ikr1, toel1, toer1), action=self.action)


    def update_all(self):
        bpy.context.scene.frame_end = self.frame(time=1) - 1
        self.clear_unnecessary_fcurves()
        self.update_pelvis()
        self.update_torso()
        self.update_head()
        self.update_limb(is_right=False, is_arm=False)
        self.update_limb(is_right=True, is_arm=False)
        self.update_scapula(right_arm=False)
        self.update_scapula(right_arm=True)
        self.update_limb(is_right=False, is_arm=True)
        self.update_limb(is_right=True, is_arm=True)
        self.update_root()


    def update_root(self):
        pass


    def update_pelvis(self):
        pass


    def update_torso(self):
        pass


    def update_head(self):
        pass


    def update_scapula(self, *, right_arm = False):
        pass


    def update_limb(self, *, is_right = False, is_arm = False):
        pass



