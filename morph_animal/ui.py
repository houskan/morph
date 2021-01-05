import bpy

from . import operators
from . import anatomy_properties
from . import gait_properties
from . import utils
from . import update_armature

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

"""ARMATURE_OBJECT = bpy.data.objects["AArmature"]
ARMATURE = bpy.data.armatures["AArmature"]
POSE_LIBRARY = bpy.data.actions["Animals"]
"""

POSE_LIBRARY = 'Animals'
ARMATURE = 'AArmature'

ANIMATION_BONES_MAIN_LAYER = 0
ANIMATION_BONES_SUPPORT_LAYER = 16
DEFORMATION_BONES_LAYER = 1

class MORPH_PT_menu(bpy.types.Panel):
    """Creates a Panel in the Tools section"""
    bl_label = "Animal Library"
    bl_idname = "MORPH_PT_menu"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    # bl_category = "Morpholocial Design App"

    def __init__(self):
        # unregister all default tools from the Toolbar
        pass

    def draw(self, context):
        layout = self.layout

        panel_parameters = context.scene.panel_parameters
        anatomy_description = context.scene.anatomy_description

        row = layout.row()
        row.template_list("UI_UL_list", "pose_markers", bpy.data.actions[POSE_LIBRARY], "pose_markers",
                          bpy.data.actions[POSE_LIBRARY].pose_markers, "active_index", rows=14)

        row = layout.row()
        row.operator("myops.update_anatomy_operator", icon="ZOOM_SELECTED",
                     text='Load "{}"'.format(bpy.data.actions[POSE_LIBRARY].pose_markers.active.name))

        if context.active_object is not bpy.data.objects[ARMATURE] or context.active_object.mode != 'POSE':
            return

        layout.separator()

        col = layout.split()
        col.alignment = 'RIGHT'
        col.label(text="Active Tool")
        col.prop(panel_parameters, "tool", text="")
        if panel_parameters.tool == 'CREATE':
            # layout.separator()
            # row = layout.row()
            # row.alignment = 'CENTER'
            # row.label(text="Load an animal to get started!", icon="OUTLINER_OB_LIGHT")

            layout.separator()
            col = layout.split()
            col.alignment = 'RIGHT'
            col.label(text="")
            col.operator("myops.add_anatomy_operator", icon="FILE_TICK",
                         text='Store Anatomy "{}"'.format(anatomy_description.ref))

            layout.separator()
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)
            col = flow.column()
            col.alignment = 'RIGHT'
            col.label(text="Name")
            col.label(text="Classification")

            col = flow.column()
            col.prop(anatomy_description, "ref", text="")
            col.prop(anatomy_description, "classification", text="")

            layout.separator()
            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Pole Knee")
            col.label(text="Elbow")

            col = flow.column(align=True)
            col.prop(anatomy_description, "leg_pole", text="", slider=True)
            col.prop(anatomy_description, "arm_pole", text="", slider=True)

            layout.separator()
            col = layout.split()
            col.alignment = 'RIGHT'
            col.label(text="")
            col.operator("myops.update_skeleton_operator", icon="PASTEDOWN", text='Update Skeleton')

            layout.separator()
            if not panel_parameters.is_pca_enabled or not hasattr(context.scene, 'pca'):
                col = layout.split()
                col.alignment = 'RIGHT'
                col.label(text="Perfom PCA")
                col.operator("myops.perform_pca_operator", icon="EMPTY_AXIS", text='Initialize')
            else:

                layout.separator()
                flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)
                col = flow.column()
                col.alignment = 'RIGHT'
                col.label(text="Principal Components")

                col = flow.split(factor=0.80)
                col1 = col.column()
                col1.prop(anatomy_description, "pca_weights", slider=True, text="")
                col2 = col.column()
                col2.enabled = False
                col2.prop(panel_parameters, "pca_variance", text="", slider=True, emboss=False)


                flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)
                col = flow.column(align=True)
                col.alignment = 'RIGHT'
                col.label(text="Morphing")
                col.label(text="")
                col.label(text="Factor")

                col = flow.column(align=True)
                col.prop(panel_parameters, "pca_morph_idx1",
                         text="{}".format(bpy.data.actions[POSE_LIBRARY].pose_markers[panel_parameters.pca_morph_idx1].name), slider=False)
                col.prop(panel_parameters, "pca_morph_idx2",
                         text="{}".format(bpy.data.actions[POSE_LIBRARY].pose_markers[panel_parameters.pca_morph_idx2].name), slider=False)
                col.prop(panel_parameters, "pca_morph_factor", text="", slider=True)

                """layout.separator()
                col = layout.split()
                col.alignment = 'RIGHT'
                col.label(text="")
                col.prop(panel_parameters, "is_pca_enabled", icon="QUIT", text='Hide PCA')"""


        elif panel_parameters.tool == 'TWEAK':

            layout.separator()
            col = layout.split()
            col.alignment = 'RIGHT'
            col.label(text="")
            col.operator("myops.store_gait_operator", icon="FILE_TICK",
                         text='Save Gait "{}"'.format(anatomy_description.ref))

            layout.separator()

            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)
            col = flow.column()
            col.alignment = 'RIGHT'
            col.label(text="Name")
            col.label(text="Classification")
            col.separator()
            col.label(text="Reference Gait")

            box = flow.box()
            col = box.column()
            col.label(text=anatomy_description.ref)
            col.label(text=anatomy_description.classification)
            col.separator()
            col.label(text=panel_parameters.reference_gait)

            col.separator()

            col = col.row(align=True)
            col.operator("screen.frame_jump", text="", icon='REW').end = False
            if not context.screen.is_animation_playing:
                col.operator("screen.animation_play", text="Play", icon='PLAY')
                col.operator("myops.rest_pose_operator", icon="OUTLINER_OB_ARMATURE", text="")
            else:
                col.operator("screen.animation_play", text="Pause", icon='PAUSE')

            gait_description = context.scene.gait_description

            """layout.separator()
            col = layout.split()
            col.alignment = 'RIGHT'
            col.label(text="Gait")
            col.prop(gait_description, "gait_classification", text="")"""

            if not hasattr(context.scene, 'gait'):
                layout.separator()
                col = layout.split()
                col.alignment = 'RIGHT'
                col.label(text="Create Gait")
                col.operator("myops.create_gait_operator", icon="GRAPH", text="")
                return

            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Speed")
            col.label(text="Walk Ratio")
            col.label(text="Duty Factor")

            box = flow.box()
            col = box.column(align=True)
            col.prop(gait_description, "v", text="", slider=True)
            col.prop(gait_description, "r", text="")
            col.prop(gait_description, "duty", text="", slider=True)

            flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=True, align=False)
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Cadence")
            col.label(text="Step Length")
            col.label(text="Froude No.")

            box = flow.box()
            col = box.column()
            col.label(text="{:.2f} [step / s]".format(2*context.scene.gait.f))
            col.label(text="{:.2f} [m]".format(context.scene.gait.stride * 0.5))
            col.label(text="{:.2f}".format(context.scene.gait.froude))

            layout.separator()
            layout.label(text="Footfall Pattern")
            flow = layout.grid_flow(row_major=True, columns=-2, even_columns=True, even_rows=False, align=False)

            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Arm L")
            col.label(text="R")

            col = flow.column(align=True)
            col.prop(gait_description, "caL", text="", slider=True)
            col.prop(gait_description, "caR", text="", slider=True)

            col.separator()
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Leg L")
            col.label(text="R")

            col = flow.column(align=True)
            col.prop(gait_description, "clL", text="", slider=True)
            col.prop(gait_description, "clR", text="", slider=True)


            layout.separator()
            layout.label(text="Up and Downs")
            flow = layout.grid_flow(row_major=True, columns=-2, even_columns=True, even_rows=False, align=False)
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Head")
            col.label(text="Pitch")

            col = flow.column(align=True)
            col.prop(gait_description, "head_offset", text="", slider=True)
            col.prop(gait_description, "head_rot", text="", slider=True)

            col.separator()
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Shoulder")
            col.label(text="")

            col = flow.column(align=True)
            col.prop(gait_description, "scapula_up", text="", slider=True, icon="TRIA_UP")
            col.prop(gait_description, "scapula_down", text="", slider=True)

            col.separator()
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Neck")
            col.label(text="")

            col = flow.column(align=True)
            col.prop(gait_description, "neck_up", text="", slider=True)
            col.prop(gait_description, "neck_down", text="", slider=True)

            col.separator()
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Pelvis")
            col.label(text="")
            col.label(text="Roll")

            col = flow.column(align=True)
            col.prop(gait_description, "pelvis_up", text="", slider=True)
            col.prop(gait_description, "pelvis_down", text="", slider=True)
            col.prop(gait_description, "pelvis_rot", text="", slider=True)


            layout.separator()
            layout.label(text="Arm and Leg")
            flow = layout.grid_flow(row_major=True, columns=-2, even_columns=True, even_rows=False, align=False)

            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Center Arm")
            col.label(text="Leg")

            col = flow.column(align=True)
            col.prop(gait_description, "step_shift_arm", text="", slider=True)
            col.prop(gait_description, "step_shift_leg", text="", slider=True)

            col.separator()
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Lifted Height ")
            col.label(text="Rotation")

            col = flow.column(align=True)
            col.prop(gait_description, "lift", text="", slider=True)
            col.prop(gait_description, "lift_rot", text="", slider=True)

            col.separator()
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Step Width")

            col = flow.column(align=True)
            col.prop(gait_description, "contact_width_shift", text="", slider=True)

            col.separator()
            col = flow.column(align=True)
            col.alignment = 'RIGHT'
            col.label(text="Release #1")
            col.label(text="#2")
            if anatomy_description.classification == "Unguligrade":
                col.label(text="Contact")

            col = flow.column(align=True)
            col.prop(gait_description, "roll_initial_rot_percentage", text="", slider=True)
            col.prop(gait_description, "roll_toe_foot_angle_ratio", text="", slider=True)
            if anatomy_description.classification == "Unguligrade":
                col.prop(gait_description, "hoof_flexibility", text="", slider=True)


def initialize_tool(self, context):
    if context.scene.anatomy_description.ref == "":
        name = bpy.data.actions[POSE_LIBRARY].pose_markers.active.name
        context.scene.anatomy_description.ref = name
        for anatomy in context.scene.stored_anatomy:
            if anatomy.ref == name:
                anatomy_properties.copy_anatomy_description(anatomy, context.scene.anatomy_description)

    if self.tool == 'CREATE':
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()

        context.scene.anatomy_description.ref = "Fantasy"
        bpy.data.armatures[ARMATURE].layers[DEFORMATION_BONES_LAYER] = True
        bpy.data.armatures[ARMATURE].layers[ANIMATION_BONES_MAIN_LAYER] = True
        for i in range(32):
            if i != DEFORMATION_BONES_LAYER and i!= ANIMATION_BONES_MAIN_LAYER:
                bpy.data.armatures[ARMATURE].layers[i] = False

        bpy.context.scene.frame_set(0)
        bpy.context.scene.frame_end = 0
        bpy.ops.myops.rest_pose_operator()
        bpy.data.objects[ARMATURE].animation_data.action = bpy.data.actions["Rest"]

    elif self.tool == 'TWEAK':
        bpy.data.armatures[ARMATURE].layers[ANIMATION_BONES_MAIN_LAYER] = True
        utils.clear_mutation_bones(self, context)
        bpy.ops.myops.rest_pose_operator()
        update_armature.update()
        for i in range(32):
            if i != ANIMATION_BONES_MAIN_LAYER:
                bpy.data.armatures[ARMATURE].layers[i] = False
        self.use_gait_defaults = True
        bpy.ops.myops.create_gait_operator()


def update_pca_morphing(self, context):
    if context.scene.pca is None:
        return
    animal1 = bpy.data.actions[POSE_LIBRARY].pose_markers[self.pca_morph_idx1].name
    animal2 = bpy.data.actions[POSE_LIBRARY].pose_markers[self.pca_morph_idx2].name

    w1 = context.scene.pca.reference_weights[animal1]
    w2 = context.scene.pca.reference_weights[animal2]
    w_morph = [0] * len(w1)
    for i in range(len(w1)):
        w_morph[i] = w1[i] + self.pca_morph_factor * (w2[i] - w1[i])
    context.scene.anatomy_description.pca_weights = utils.get_normalized_pca_weights(context, w_morph)


class PanelParameters(bpy.types.PropertyGroup):
    reference_gait: StringProperty(default="Horse")
    tool: EnumProperty(items=[
            ("CREATE", "Create Animal", "", "PLUS", 0),
            ("TWEAK", "Tweak Gait", "", "ACTION_TWEAK", 1)],
            update=initialize_tool)
    is_pca_enabled: BoolProperty(default = False)
    pca_morph_idx1: IntProperty(default=0, soft_min=0, soft_max=14, update=update_pca_morphing)
    pca_morph_idx2: IntProperty(default=1, soft_min=0, soft_max=14, update=update_pca_morphing)
    pca_morph_factor: FloatProperty(default=0.5, soft_min=0, soft_max=1, update=update_pca_morphing)
    pca_variance: FloatVectorProperty(
        name="Variance",
        description="Explained Variance",
        precision=1,
        size=14,
        soft_min=0,
        soft_max=1)
    use_gait_defaults: BoolProperty(default = True)
    update_gait: BoolProperty(default = True)


classes = (
    MORPH_PT_menu,
    PanelParameters
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.panel_parameters = PointerProperty(type=PanelParameters)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.panel_parameters