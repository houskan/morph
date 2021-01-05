import bpy, mathutils
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

ARMATURE = 'AArmature'
POSE_LIBRARY = 'Animals'

class PCA_calculator():

    def __init__(self):
        self.data = []
        self.reference_vec = {}
        self.reference_weights = {}
        self.min_weights = []
        self.max_weights = []

    def calculate_data(self):
        original_animal = bpy.context.scene.anatomy_description.ref
        self.data = []
        self.reference_vec = {}

        for i in range(len(bpy.data.actions[POSE_LIBRARY].pose_markers.values())):
            bpy.data.actions[POSE_LIBRARY].pose_markers.active_index = i
            bpy.context.evaluated_depsgraph_get()
            bpy.ops.myops.update_anatomy_operator()

            datum = self.anatomy_to_vector()
            self.data.append(datum)
            self.reference_vec[bpy.data.actions[POSE_LIBRARY].pose_markers.active.name] = datum

        if original_animal in bpy.data.actions[POSE_LIBRARY].pose_markers.keys():
            bpy.data.actions[POSE_LIBRARY].pose_markers.active = bpy.data.actions[POSE_LIBRARY].pose_markers[original_animal]
            bpy.ops.myops.update_anatomy_operator()


    def anatomy_to_vector(self):
        """
        looks at the current position of the deformation bones and constructs the vectorized representation to use in pca
        this function assumes that animal is in rest pose
        """

        AllBones = bpy.data.objects[ARMATURE].pose.bones

        SizeList = []
        Positions = []

        PelvisRoot = AllBones["Pelvis_Root"]
        SizeList.append(PelvisRoot)

        """
        HindLeg
        """
        ToeClaws = AllBones["ToeClaws.L"]
        ToeJoint = AllBones["Toe_Joint.L"]
        Ankle = AllBones["Ankle.L"]
        Knee = AllBones["Knee.L"]
        Tights = AllBones["Tights.L"]

        SizeList.append(ToeClaws)
        SizeList.append(ToeJoint)
        SizeList.append(Ankle)
        SizeList.append(Knee)
        SizeList.append(Tights)

        Positions.append(ToeClaws.head - ToeJoint.head)
        Positions.append(ToeJoint.head - Ankle.head)
        Positions.append(Ankle.head - Knee.head)
        Positions.append(Knee.head - Tights.head)
        Positions.append(Tights.head - PelvisRoot.head)

        """
        Body
        """

        TailEnd = AllBones["Tail_End"]
        Tail = AllBones["Tail"]
        Spine = AllBones["Spine"]
        Back = AllBones["Back"]
        Neck = AllBones["Neck"]
        SternumHead = AllBones["Sternum_Head"]
        SternumEnd = AllBones["Sternum_End"]

        SizeList.append(TailEnd)
        SizeList.append(Tail)
        SizeList.append(Spine)
        SizeList.append(Back)
        SizeList.append(Neck)
        SizeList.append(SternumHead)
        SizeList.append(SternumEnd)

        Positions.append(TailEnd.head - Tail.head)
        Positions.append(Tail.head - Spine.head)
        Positions.append(Spine.head - PelvisRoot.head)
        Positions.append(Back.head - Spine.head)
        Positions.append(Neck.head - Back.head)
        Positions.append(SternumHead.head - Neck.head)
        Positions.append(SternumEnd.head - SternumHead.head)

        """
        Head
        """
        Head = AllBones["Head_Root"]
        Snout = AllBones["Snout"]
        Brain = AllBones["Brain"]

        SizeList.append(Head)
        SizeList.append(Snout)
        SizeList.append(Brain)

        Positions.append(Head.head - Neck.head)
        Positions.append(Snout.head - Head.head)
        Positions.append(Brain.head - Head.head)

        """
        ForeLimbs
        """
        FingerClaws = AllBones["FingerClaws.L"]
        FingerJoint = AllBones["Finger_Joint.L"]
        Wrist = AllBones["Wrist.L"]
        Elbow = AllBones["Elbow.L"]
        Shoulder = AllBones["Shoulder.L"]
        ScapulaStart = AllBones["Scapula_Start.L"]

        SizeList.append(FingerClaws)
        SizeList.append(FingerJoint)
        SizeList.append(Wrist)
        SizeList.append(Elbow)
        SizeList.append(Shoulder)
        SizeList.append(ScapulaStart)

        Positions.append(FingerClaws.head - FingerJoint.head)
        Positions.append(FingerJoint.head - Wrist.head)
        Positions.append(Wrist.head - Elbow.head)
        Positions.append(Elbow.head - Shoulder.head)
        Positions.append(Shoulder.head - ScapulaStart.head)
        Positions.append(ScapulaStart.head - Neck.head)

        datum = []
        for Pos in Positions:
            datum.append(Pos.x)
            datum.append(Pos.y)
            datum.append(Pos.z)

        for Bone in SizeList:
            scale = Bone.scale[0]
            datum.append(scale)

        return datum


    def compute_pca(self):
        x = np.array(self.data)
        self.scaler = StandardScaler()
        x = self.scaler.fit_transform(x)

        pca = PCA(n_components=14, svd_solver='full')
        pca.fit_transform(x)
        self.pca = pca


    def calculate_pca_weight(self, vectorized):
        """Takes the vectorized description of an anatomy and returns the respective weights in the pca space"""
        x = self.scaler.transform(np.array(vectorized).reshape(1, -1))
        x -= self.pca.mean_
        weights = []
        for i in range(self.pca.n_components_):
            weight = np.dot(x, self.pca.components_[i])
            weights.append(weight)
        return weights


    def calculate_vectorized(self, weights):
        """takes weights in pca space and returns the respective vectorized description of the anatomy"""
        new_anatomy = np.copy(self.pca.mean_)
        for i in range(self.pca.n_components_):
            new_anatomy += self.pca.components_[i] * weights[i]
        return new_anatomy


    def apply_vectorized_to_pose(self, vectorized):
        vectorized = self.scaler.inverse_transform(vectorized)
        AllBones = bpy.data.objects[ARMATURE].pose.bones

        AllBones["LowerLeg.L"].constraints["IK"].influence = 0
        AllBones["LowerLeg.R"].constraints["IK"].influence = 0
        AllBones["LowerArm.L"].constraints["IK"].influence = 0
        AllBones["LowerArm.R"].constraints["IK"].influence = 0

        AllBones["Foot.L"].constraints["IK"].influence = 0
        AllBones["Foot.R"].constraints["IK"].influence = 0
        AllBones["Hand.L"].constraints["IK"].influence = 0
        AllBones["Hand.R"].constraints["IK"].influence = 0

        AllBones["Toe.L"].constraints["IK"].influence = 0
        AllBones["Toe.R"].constraints["IK"].influence = 0
        AllBones["Finger.L"].constraints["IK"].influence = 0
        AllBones["Finger.R"].constraints["IK"].influence = 0

        bpy.context.evaluated_depsgraph_get()

        pelvis_Z = - vectorized[2] - vectorized[5] - vectorized[8] - vectorized[11] - \
                   (AllBones["ToeClaws.L"].tail - AllBones["ToeClaws.L"].head)[2]
        origin = mathutils.Vector((0, 0, pelvis_Z))

        PelvisRoot = AllBones["Pelvis_Root"]
        PelvisRoot.scale = mathutils.Vector(
            (self.new_size(vectorized, 63), self.new_size(vectorized, 63), self.new_size(vectorized, 63)))

        """
        HindLeg
        """
        ToeClaws = AllBones["ToeClaws.L"]
        ToeJoint = AllBones["Toe_Joint.L"]
        Ankle = AllBones["Ankle.L"]
        Knee = AllBones["Knee.L"]
        Tights = AllBones["Tights.L"]

        tL = self.new_loc(vectorized, 12, origin)
        kL = self.new_loc(vectorized, 9, tL)
        aL = self.new_loc(vectorized, 6, kL)
        tjL = self.new_loc(vectorized, 3, aL)
        tcL = self.new_loc(vectorized, 0, tjL)

        tS = self.new_size(vectorized, 68)
        kS = self.new_size(vectorized, 67)
        aS = self.new_size(vectorized, 66)
        tjS = self.new_size(vectorized, 65)
        tcS = self.new_size(vectorized, 64)

        self.update(Tights, tS, tL)
        self.update(Knee, kS, kL)
        self.update(Ankle, aS, aL)
        self.update(ToeJoint, tjS, tjL)
        self.update(ToeClaws, tcS, tcL)

        """
        Body 
        """

        TailEnd = AllBones["Tail_End"]
        Tail = AllBones["Tail"]
        Spine = AllBones["Spine"]
        Back = AllBones["Back"]
        Neck = AllBones["Neck"]
        SternumHead = AllBones["Sternum_Head"]
        SternumEnd = AllBones["Sternum_End"]

        sL = self.new_loc(vectorized, 21, origin)
        tL = self.new_loc(vectorized, 18, sL)
        teL = self.new_loc(vectorized, 15, tL)
        bL = self.new_loc(vectorized, 24, sL)
        nL = self.new_loc(vectorized, 27, bL)
        shL = self.new_loc(vectorized, 30, nL)
        seL = self.new_loc(vectorized, 33, shL)

        sS = self.new_size(vectorized, 71)
        tS = self.new_size(vectorized, 70)
        teS = self.new_size(vectorized, 69)
        bS = self.new_size(vectorized, 72)
        nS = self.new_size(vectorized, 73)
        shS = self.new_size(vectorized, 74)
        seS = self.new_size(vectorized, 75)

        self.update(Spine, sS, sL)
        self.update(Tail, tS, tL)
        self.update(TailEnd, teS, teL)
        self.update(Back, bS, bL)
        self.update(Neck, nS, nL)
        self.update(SternumHead, shS, shL)
        self.update(SternumEnd, seS, seL)

        """
        Head
        """

        Head = AllBones["Head_Root"]
        Snout = AllBones["Snout"]
        Brain = AllBones["Brain"]

        hL = self.new_loc(vectorized, 36, nL)
        snL = self.new_loc(vectorized, 39, hL)
        brL = self.new_loc(vectorized, 42, hL)

        hS = self.new_size(vectorized, 76)
        snS = self.new_size(vectorized, 77)
        brS = self.new_size(vectorized, 78)

        self.update(Head, hS, hL)
        self.update(Snout, snS, snL)
        self.update(Brain, brS, brL)

        """
        ForeLimbs
        """
        FingerClaws = AllBones["FingerClaws.L"]
        FingerJoint = AllBones["Finger_Joint.L"]
        Wrist = AllBones["Wrist.L"]
        Elbow = AllBones["Elbow.L"]
        Shoulder = AllBones["Shoulder.L"]
        ScapulaStart = AllBones["Scapula_Start.L"]

        ssL = self.new_loc(vectorized, 60, nL)
        shL = self.new_loc(vectorized, 57, ssL)
        eL = self.new_loc(vectorized, 54, shL)
        wL = self.new_loc(vectorized, 51, eL)
        fjL = self.new_loc(vectorized, 48, wL)
        fcL = self.new_loc(vectorized, 45, fjL)

        ssS = self.new_size(vectorized, 84)
        shS = self.new_size(vectorized, 83)
        eS = self.new_size(vectorized, 82)
        wS = self.new_size(vectorized, 81)
        fjS = self.new_size(vectorized, 80)
        fcS = self.new_size(vectorized, 79)

        self.update(ScapulaStart, ssS, ssL)
        self.update(Shoulder, shS, shL)
        self.update(Elbow, eS, eL)
        self.update(Wrist, wS, wL)
        self.update(FingerJoint, fjS, fjL)
        self.update(FingerClaws, fcS, fcL)

        bpy.ops.pose.rot_clear()

        AllBones["LowerLeg.L"].constraints["IK"].influence = 1
        AllBones["LowerLeg.R"].constraints["IK"].influence = 1
        AllBones["LowerArm.L"].constraints["IK"].influence = 1
        AllBones["LowerArm.R"].constraints["IK"].influence = 1

        AllBones["Foot.L"].constraints["IK"].influence = 1
        AllBones["Foot.R"].constraints["IK"].influence = 1
        AllBones["Hand.L"].constraints["IK"].influence = 1
        AllBones["Hand.R"].constraints["IK"].influence = 1

        AllBones["Toe.L"].constraints["IK"].influence = 1
        AllBones["Toe.R"].constraints["IK"].influence = 1
        AllBones["Finger.L"].constraints["IK"].influence = 1
        AllBones["Finger.R"].constraints["IK"].influence = 1

        bpy.context.evaluated_depsgraph_get()


    ###
    # Functions to reconstruct pose
    ###
    def new_loc(self, row, index, parent):
        return (mathutils.Vector((row[index], row[index + 1], row[index + 2])) + parent)


    def new_size(self, row, index):
        return row[index]


    def update(self, bone, size, loc):
        trans = mathutils.Matrix.Translation(loc)
        quat = bone.matrix.to_quaternion()
        scale = mathutils.Matrix.Scale(size, 4)
        bone.matrix = trans @ quat.to_matrix().to_4x4() @ scale
        if bone.name in {"Head_Root"}:
            bpy.context.evaluated_depsgraph_get()
        return


    def calculate_min_max(self):
        self.reference_weights = {}
        self.min_weights = [10000] * self.pca.n_components_
        self.max_weights = [-10000] * self.pca.n_components_

        for animal, vec in self.reference_vec.items():
            weights = self.calculate_pca_weight(vec)
            self.reference_weights[animal] = weights
            self.min_weights = [min(l1, l2) for l1, l2 in zip(self.min_weights, weights)]
            self.max_weights = [max(l1, l2) for l1, l2 in zip(self.max_weights, weights)]


    def initialize(self):
        self.calculate_data()
        self.compute_pca()
        self.calculate_min_max()