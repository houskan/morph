import bpy, mathutils, math
from . import utils
from . import update_armature
from . import pca_calculator
from . import anatomy_properties
from . import gait_properties
from . import gait_walk

ANIMATION_BONES_MAIN_LAYER = 0
ANIMATION_BONES_SUPPORT_LAYER = 16
DEFORMATION_BONES_LAYER = 1

ARMATURE = 'AArmature'
POSE_LIBRARY = 'Animals'

class MYOPS_OT_update_anatomy_operator(bpy.types.Operator):
    """Loads the virtual armature of selected animal"""
    bl_idname = "myops.update_anatomy_operator"
    bl_label = "Load Animal"

    @classmethod
    def poll(cls, context):
        return context.active_object is bpy.data.objects[ARMATURE] and context.active_object.mode == 'POSE' and not context.scene.is_nla_tweakmode

    def execute(self, context):
        # jump to rest pose, bc updating the armature is only possible in the context of the rest pose
        current_frame = bpy.context.scene.frame_current
        bpy.context.scene.frame_set(0)
        if context.object.animation_data.action is not None:
            nla_tracks = context.object.animation_data.nla_tracks
            nla_tracks["Rest"].is_solo = True

        utils.clear_mutation_bones(self, context)
        utils.apply_pose(self, context)

        # updates animation bones according to mutation bones position
        update_armature.update()
        name = bpy.data.actions[POSE_LIBRARY].pose_markers.active.name
        context.scene.anatomy_description.ref = name

        for anatomy in context.scene.stored_anatomy:
            if anatomy.ref == name:
                anatomy_properties.copy_anatomy_description(anatomy, context.scene.anatomy_description)
                if context.scene.panel_parameters.tool == 'CREATE':
                    context.scene.anatomy_description.ref = "Fantasy"
                if context.scene.panel_parameters.is_pca_enabled and hasattr(context.scene, 'pca'):
                    context.scene.anatomy_description.pca_weights = utils.get_normalized_pca_weights(context, context.scene.pca.reference_weights[name])
                    context.scene.panel_parameters.pca_morph_idx1 = bpy.data.actions[POSE_LIBRARY].pose_markers.active_index
                    context.scene.panel_parameters.pca_morph_factor = 0
                break

        bpy.context.scene.frame_set(current_frame)
        if context.object.animation_data.action is not None:
            nla_tracks = context.object.animation_data.nla_tracks
            nla_tracks["Rest"].is_solo = False

        if context.scene.panel_parameters.tool == 'TWEAK':
            bpy.ops.myops.create_gait_operator()
        return {'FINISHED'}


class MYOPS_OT_rest_pose_operator(bpy.types.Operator):
    """Puts current animal in rest pose"""
    bl_idname = "myops.rest_pose_operator"
    bl_label = "Rest Pose"

    @classmethod
    def poll(cls, context):
        return context.active_object is bpy.data.objects[ARMATURE] and context.active_object.mode == 'POSE'

    def execute(self, context):
        for bone in bpy.context.object.pose.bones:
            if bone.name in context.scene.anim_bone_names:
                bone.matrix_basis = mathutils.Matrix()
        bpy.context.evaluated_depsgraph_get()
        return {'FINISHED'}


class MYOPS_OT_perform_pca_operator(bpy.types.Operator):
    """Runs Principle Component Analysis"""
    bl_idname = "myops.perform_pca_operator"
    bl_label = "Run PCA"

    @classmethod
    def poll(cls, context):
        return context.active_object is bpy.data.objects[ARMATURE] and context.active_object.mode == 'POSE' and context.scene.panel_parameters.tool == 'CREATE'

    def execute(self, context):
        context.scene.panel_parameters.tool = 'CREATE'
        pca = pca_calculator.PCA_calculator()
        pca.initialize()
        bpy.types.Scene.pca = pca
        context.scene.panel_parameters.is_pca_enabled = True
        context.scene.anatomy_description.pca_weights = utils.get_normalized_pca_weights(context, pca.calculate_pca_weight(pca.anatomy_to_vector()))
        context.scene.panel_parameters.pca_variance = pca.pca.explained_variance_
        return {'FINISHED'}


class MYOPS_OT_add_anatomy_operator(bpy.types.Operator):
    """Stores the current configuration as 'Name' and adds it to the list above"""
    bl_idname = "myops.add_anatomy_operator"
    bl_label = "Store Animal"

    @classmethod
    def poll(cls, context):
        return context.active_object is bpy.data.objects[ARMATURE] and context.active_object.mode == 'POSE' and not context.scene.is_nla_tweakmode

    def execute(self, context):
        bpy.data.armatures[ARMATURE].layers[DEFORMATION_BONES_LAYER] = True
        bpy.data.armatures[ARMATURE].layers[ANIMATION_BONES_MAIN_LAYER] = False
        bpy.data.armatures[ARMATURE].layers[ANIMATION_BONES_SUPPORT_LAYER] = False

        for bone in bpy.context.object.pose.bones:
            if bone.name in context.scene.mut_bone_names:
                bone.bone.select = True

        taken_frames = [marker.frame for marker in bpy.data.actions[POSE_LIBRARY].pose_markers]
        frame = 0
        while frame in taken_frames:
            frame += 1

        params = context.scene.anatomy_description
        found = False
        for stored in context.scene.stored_anatomy:
            if params.ref == stored.ref:
                anatomy_properties.copy_anatomy_description(params, stored)
                found = True
                frame = bpy.data.actions[POSE_LIBRARY].pose_markers[params.ref].frame
                break
        if not found:
            new_item = context.scene.stored_anatomy.add()
            anatomy_properties.copy_anatomy_description(params, new_item)

        bpy.ops.poselib.pose_add(frame=frame, name=context.scene.anatomy_description.ref)
        bpy.ops.pose.select_all(action='DESELECT')
        return {'FINISHED'}


    def invoke(self, context, event):
        params = context.scene.anatomy_description
        found = False
        for stored in context.scene.stored_anatomy:
            if params.ref == stored.ref:
                found = True
                break
        if found:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return context.window_manager.invoke_confirm(self, event)


    def draw(self, context):
        row = self.layout
        row.label(text='Override existing anatomy: "{}"?'.format(context.scene.anatomy_description.ref), icon="ERROR")


class MYOPS_OT_create_gait_operator(bpy.types.Operator):
    """Creates the walk animation"""
    bl_idname = "myops.create_gait_operator"
    bl_label = "Create Walk Animation"

    @classmethod
    def poll(cls, context):
        return context.active_object is bpy.data.objects[ARMATURE] and context.active_object.mode == 'POSE' and not context.scene.is_nla_tweakmode

    def execute(self, context):
        context.scene.panel_parameters.update_gait = False

        gait_description = context.scene.gait_description
        gait_description.ref = context.scene.anatomy_description.ref

        gait_properties.set_gait_defaults(context)

        utils.copy_reference_walkcylce(context, bpy.data.actions["ReferenceWalkcycle"])
        frame_current = context.scene.frame_current

        bpy.types.Scene.gait = gait_walk.Walk(
            armature=bpy.data.objects[ARMATURE],
            action=context.object.animation_data.action,
            parameters=gait_description,
            animal_classification = context.scene.anatomy_description.classification)

        context.scene.gait.update_all()

        context.scene.frame_set(frame_current)
        context.scene.panel_parameters.update_gait = True
        return {'FINISHED'}


class MYOPS_OT_store_gait_operator(bpy.types.Operator):
    """Stores the current animation parameters using 'Name' as reference"""
    bl_idname = "myops.store_gait_operator"
    bl_label = "Store Animation Parameters"

    @classmethod
    def poll(cls, context):
        return context.active_object is bpy.data.objects[ARMATURE] and context.active_object.mode == 'POSE' and not context.scene.is_nla_tweakmode

    def execute(self, context):
        params = context.scene.gait_description

        found = False
        for stored in context.scene.stored_anatomy:
            if params.ref == stored.ref:
                found = True
                break
        if not found:
            self.report({"WARNING"}, 'Require associated stored animal "{}"'.format(params.ref))
            return {'CANCELLED'}

        found = False
        for stored in context.scene.stored_gait:
            if params.ref == stored.ref:
                gait_properties.copy_gait_description(params, stored)
                found = True
                break

        if not found:
            new_item = context.scene.stored_gait.add()
            gait_properties.copy_gait_description(params, new_item)
        return {'FINISHED'}


class MYOPS_OT_update_skeleton_operator(bpy.types.Operator):
    """Updates the animation bones to match the joint positions"""
    bl_idname = "myops.update_skeleton_operator"
    bl_label = "Update Animation Skeleton"

    @classmethod
    def poll(cls, context):
        return context.active_object is bpy.data.objects[ARMATURE] and context.active_object.mode == 'POSE' and not context.scene.is_nla_tweakmode

    def execute(self, context):
        utils.clear_mutation_bones(self, context)
        update_armature.update()
        return {'FINISHED'}


classes = (
    MYOPS_OT_update_anatomy_operator,
    MYOPS_OT_rest_pose_operator,
    MYOPS_OT_perform_pca_operator,
    MYOPS_OT_add_anatomy_operator,
    MYOPS_OT_create_gait_operator,
    MYOPS_OT_store_gait_operator,
    MYOPS_OT_update_skeleton_operator
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)