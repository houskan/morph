import bpy
from math import *
from mathutils import *

ANIMATION_BONES_MAIN_LAYER = 0
ANIMATION_BONES_SUPPORT_LAYER = 16
DEFORMATION_BONES_LAYER = 1

ARMATURE = 'AArmature'
POSE_LIBRARY = 'Animals'

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return floor(n*multiplier + 0.5) / multiplier


#compute angle of triangle given by its sides using Kahan's Heron's formula. This is numerically stable
def triangle_angle(*, v1, v2, v3=None):
    if v3 != None:
        a = max(v1,v2)
        b = min(v1,v2)
        c = v3
        if not (a + b > c and a + c > b and c + b > a):
            return 0
    else:
        a = max(v1.length, v2.length)
        b = min(v1.length, v2.length)
        c = (v1 - v2).length
    if b >= c and c >= 0:
        my = c - (a - b)
    elif c > b and b >= 0:
        my = b - (a - c)
    else:
        return 0
    return 2 * atan(sqrt( (((a - b) + c) * my) / ( (a + (b + c)) * ((a - c) + b) ) ))


def circle_intersection(*, c1, c2):
    x1 = c1[0]; y1 = c1[1]; r1 = c1[2]
    x2 = c2[0]; y2 = c2[1]; r2 = c2[2]

    d = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    l = (r1 ** 2 - r2 ** 2 + d ** 2) / (2 * d)
    if r1 < l:  # report intersection point lying on the line between the circle centers
        xr1 = r1 * ((x2 - x1) / d) + x1
        yr1 = r1 * ((y2 - y1) / d) + y1
        print("circleIntersetion not possible")
        return ((xr1, yr1), (xr1, yr1))
    else:
        h = sqrt(r1 ** 2 - l ** 2)

    xr1 = (l / d) * (x2 - x1) + (h / d) * (y2 - y1) + x1
    yr1 = (l / d) * (y2 - y1) - (h / d) * (x2 - x1) + y1
    xr2 = (l / d) * (x2 - x1) - (h / d) * (y2 - y1) + x1
    yr2 = (l / d) * (y2 - y1) + (h / d) * (x2 - x1) + y1
    return ((xr1, yr1), (xr2, yr2))


def translate_in_local_frame(*, bone, translation):
    bone.location = Vector() #set location to bone space origin
    bpy.context.evaluated_depsgraph_get()
    locmat = Matrix.Translation(translation) @ bone.matrix
    bone.matrix = locmat
    bpy.context.evaluated_depsgraph_get()


def translate_to(*, bone, location):
    translation = location - bone.head
    locmat = Matrix.Translation(translation) @ bone.matrix
    bone.matrix = locmat
    bpy.context.evaluated_depsgraph_get()


def rotate_to(*, bone, desired):
    if type(desired) is Quaternion:
        PoseMat = bone.bone.matrix_local.inverted()
        q = PoseMat.to_quaternion() @ desired
        bone.rotation_quaternion = q
    elif type(desired) is Vector:
        current = (bone.tail - bone.head).normalized()
        desired.normalize()
        rot_diff = current.rotation_difference(desired)
        bone.rotation_quaternion.rotate(rot_diff)
    bpy.context.evaluated_depsgraph_get()


def add_keyframe(*, bone, data, frame):
    bone.keyframe_insert(data_path=data, frame=frame, group=bone.name)


def clear_mutation_bones(self, context):
    """ Removes any keyframes on the mutation bones """
    if context.object.animation_data.action is None:
        return
    for fcu in context.object.animation_data.action.fcurves:
        dp = fcu.data_path.split("\"", maxsplit=2)
        if len(dp) == 3 and dp[0] == "pose.bones[" and dp[1] in context.scene.mut_bone_names:
            context.object.animation_data.action.fcurves.remove(fcu)


def apply_pose(self, context):
    context.object.pose_library = bpy.data.actions[POSE_LIBRARY]
    visibility = bpy.data.armatures[ARMATURE].layers[DEFORMATION_BONES_LAYER]
    bpy.data.armatures[ARMATURE].layers[DEFORMATION_BONES_LAYER] = True
    for bone in bpy.context.object.pose.bones:
        if bone.name in context.scene.mut_bone_names:
            bone.bone.select = True
    bpy.ops.poselib.apply_pose()
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.data.armatures[ARMATURE].layers[DEFORMATION_BONES_LAYER] = visibility


def get_denormalized_pca_weights(context, weights):
    if not hasattr(context.scene, 'pca'):
        return weights
    pca = context.scene.pca
    mins = pca.min_weights
    maxs = pca.max_weights

    denorm = []
    for i in range(len(weights)):
        min = mins[i]
        max = maxs[i]
        interval = abs(min) + abs(max)
        factor = interval / 200
        curr = weights[i] + 100
        denorm.append(curr * factor + min)
    return denorm


def get_normalized_pca_weights(context, weights):
    if not hasattr(context.scene, 'pca'):
        return weights
    pca = context.scene.pca
    mins = pca.min_weights
    maxs = pca.max_weights

    norm = []
    for i in range(len(weights)):
        min = mins[i]
        max = maxs[i]
        interval = abs(min) + abs(max)
        factor = 200 / interval
        curr = weights[i] - min
        norm.append(curr * factor - 100)
    return norm


def copy_reference_walkcylce(context, reference_action):
    animData = context.object.animation_data
    animData.action = reference_action.copy()
    if "EditAction" in bpy.data.actions:
        bpy.data.actions.remove(bpy.data.actions["EditAction"])
    animData.action.name = "EditAction"
    for track in animData.nla_tracks:
        track.mute = True
        track.is_solo = False
    return


def clear_fcurves(*, bones, action):
    names = [bone.name for bone in bones]
    for fcu in action.fcurves:
        dp = fcu.data_path.split("\"", maxsplit=2)
        if len(dp) == 3 and dp[0] == "pose.bones[" and dp[1] in names:
            action.fcurves.remove(fcu)
    for bone in bones:
        bone.matrix_basis = Matrix()


def make_cyclic(*, bones, action):
    names = [bone.name for bone in bones]
    for fcu in action.fcurves:
        dp = fcu.data_path.split("\"", maxsplit=2)
        if len(dp) == 3 and dp[0] == "pose.bones[" and dp[1] in names:
            types = [mod.type for mod in fcu.modifiers]
            if 'CYCLES' not in types:
                mod = fcu.modifiers.new(type='CYCLES')
                mod.mode_before = 'REPEAT'
                mod.mode_after = 'REPEAT'


def make_linear(*, bones, kf_point_frames, action):
    names = [bone.name for bone in bones]
    for fcu in action.fcurves:
        dp = fcu.data_path.split("\"", maxsplit=2)
        if len(dp) == 3 and dp[0] == "pose.bones[" and dp[1] in names:
            for kf in fcu.keyframe_points:
                dp1 = fcu.data_path.split(".", maxsplit=3)
                if kf.co.x in kf_point_frames and dp1[-1] == 'location':
                    kf.handle_right_type = 'VECTOR'
                    kf.handle_left_type = 'VECTOR'
        fcu.update()


def pca_weight_distance_squared(weights1, weights2):
    sum = 0
    for i in range(5):
        sum = sum + (weights1[i] - weights2[i]) ** 2 #* bpy.context.scene.pca.pca.explained_variance_[i]
    return sum


def point_line_sign(*, A, B, P):
    """
    :arg A: start of line
    :arg B: end of line
    :arg P: point
    :return sign of d"""
    d = (P[0] - A[0]) * (B[1] - A[1]) - (P[1] - A[1]) * (B[0] - A[0])
    return 1 if d > 0 else -1