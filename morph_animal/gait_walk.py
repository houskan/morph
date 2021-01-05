import bpy
from mathutils import *
from math import *
from . import gait
from . import utils

class Walk(gait.Gait):
    def __init__(self, **kwargs):
        gait.Gait.__init__(self, **kwargs)


    def update_root(self):
        root = self.armature.pose.bones["Root"]
        utils.clear_fcurves(bones=(root,), action=self.action)

        bpy.context.scene.frame_set(0)
        utils.translate_to(bone=root, location=root.bone.head_local)
        utils.add_keyframe(bone=root, data='location', frame=0)

        frame = self.frame(time=1)
        bpy.context.scene.frame_set(frame)
        location = Vector((0, -self.stride * 100, 0)) + root.bone.head_local
        utils.translate_to(bone=root, location=location)
        utils.add_keyframe(bone=root, data='location', frame=frame)
        utils.make_linear(bones=(root,), kf_point_frames=(0, frame), action=self.action)

        bpy.context.scene.frame_set(0)
        utils.translate_to(bone=root, location=root.bone.head_local)


    def update_pelvis(self):
        up_first = self.clL + 0.6 * self.duty
        up_second = up_first + abs(self.clR - self.clL)
        down_first = (up_first + up_second) * 0.5
        down_second = (up_second + up_first + 1) * 0.5
        if down_second < up_second:
            down_second = down_second + 1

        t_up = (up_first, up_second, up_first + 1)
        t_down = (down_first, down_second)

        bigger = max(abs(up_second - up_first), abs(up_first + 1 - up_second))

        pelvis_m = self.armature.pose.bones["Pelvis_Main"]
        pelvis = self.armature.pose.bones["Pelvis"]

        utils.clear_fcurves(bones=(pelvis_m, pelvis), action=self.action)
        # adjust torso up keyframes and pelvis rotation.
        for i in range(3):
            frame = self.frame(time=t_up[i])
            # bpy.context.scene.frame_set(frame)
            pelvis_z = self.l + self.pelvis_shift + self.pelvis_up
            utils.translate_to(bone=pelvis_m, location=Vector((0, pelvis_m.bone.head_local.y, pelvis_z)))
            utils.add_keyframe(bone=pelvis_m, data='location', frame=frame)
            if i == 1:
                rot_des_pel = pelvis.bone.matrix_local.to_quaternion()
                ratio = abs(t_up[1] - t_up[0]) / bigger
                delta_rot = Euler((0, self.pelvis_rot * ratio, 0)).to_quaternion()
                rot_des_pel.rotate(delta_rot)
                utils.rotate_to(bone=pelvis, desired=rot_des_pel)
            else:
                rot_des_pel = pelvis.bone.matrix_local.to_quaternion()
                ratio = abs(t_up[2] - t_up[1]) / bigger
                delta_rot_n = Euler((0, -self.pelvis_rot * ratio, 0)).to_quaternion()
                rot_des_pel.rotate(delta_rot_n)
                utils.rotate_to(bone=pelvis, desired=rot_des_pel)
            utils.add_keyframe(bone=pelvis, data='rotation_quaternion', frame=frame)

        # adjust pelvis down keyframes. there is no rotation
        for i in range(2):
            frame = self.frame(time=t_down[i])
            # bpy.context.scene.frame_set(frame)
            ratio = abs(t_up[i]-t_up[i+1]) / bigger
            pelvis_z = self.l + self.pelvis_shift + self.pelvis_down * ratio
            utils.translate_to(bone=pelvis_m, location=Vector((0, pelvis_m.bone.head_local.y, pelvis_z)))
            utils.add_keyframe(bone=pelvis_m, data='location', frame=frame)

        utils.make_cyclic(bones=(pelvis_m, pelvis), action=self.action)


    def update_torso(self):
        up_first = self.caL + 0.6 * self.duty
        up_second = up_first + abs(self.caR - self.caL)
        down_first = (up_first + up_second) * 0.5
        down_second = (up_second + up_first + 1) * 0.5
        if down_second < up_second:
            down_second = down_second + 1

        times = (up_first, down_first, up_second, down_second, up_first + 1)

        torso = self.armature.pose.bones["Torso"]
        utils.clear_fcurves(bones=(torso,), action=self.action)

        windows = (abs(up_second - up_first), abs(up_first + 1 - up_second))
        bigger = max(abs(up_second - up_first), abs(up_first + 1 - up_second))
        for i in range(5):
            frame = self.frame(time=times[i])
            bpy.context.scene.frame_set(frame)

            if i % 2 == 0:
                z = self.l2 + self.neck_up
            else:
                window = windows[0] if i == 1 else windows[1]
                ratio = window / bigger
                z = self.l2 + self.neck_down * ratio

            ca = torso.head.y; cb = torso.head.z
            r = (Vector((torso.tail.y, torso.tail.z)) - Vector((torso.head.y, torso.head.z))).length

            b = - 2 * ca
            c = ca ** 2 + (z - cb) ** 2 - r ** 2
            delta = b ** 2 - 4 * c
            if delta >= 0:
                y = 0.5 * (-b - sqrt(delta))
            else:
                y = torso.tail.y
                print("Neck rot can't be reached by rotation of torso")

            tail_loc = Vector((torso.tail.x, y, z))
            angle = utils.triangle_angle(v1=Vector((0, 0, 1)), v2=(tail_loc - torso.head))
            euler = Euler((pi / 2 + angle, 0, 0))

            ca = torso.head.y; cb = torso.head.x
            r = (Vector((torso.tail.x, torso.tail.y)) - Vector((torso.head.x, torso.head.y))).length
            b = -2 * ca
            c = ca ** 2 + (0 - cb) ** 2 - r ** 2
            delta = b ** 2 - 4 * c
            if delta >= 0:
                y = 0.5 * (-b - sqrt(delta))
            else:
                y = torso.tail.y

            tail_loc = Vector((0, y, torso.tail.z))
            angle = utils.triangle_angle(v1=Vector((1, 0, 0)), v2=(tail_loc - torso.head))
            euler.z = pi / 2 - angle

            des_orient = euler.to_quaternion()
            utils.rotate_to(bone=torso, desired=des_orient)
            utils.add_keyframe(bone=torso, data='rotation_quaternion', frame=frame)

        utils.make_cyclic(bones=(torso,), action=self.action)


    def update_head(self):
        up_first = self.clL + 0.6 * self.duty
        up_second = up_first + abs(self.clR - self.clL)
        down_first = (up_first + up_second) * 0.5
        down_second = (up_second + up_first + 1) * 0.5
        if down_second < up_second:
            down_second = down_second + 1

        times = (up_first, down_first, up_second, down_second, up_first + 1)

        cervical = self.armature.pose.bones["Cervical"]
        head = self.armature.pose.bones["Head"]
        utils.clear_fcurves(bones=(cervical, head), action=self.action)

        for i in range(5):
            frame = self.frame(time=times[i])
            bpy.context.scene.frame_set(frame)
            z = self.head_height + self.head_offset
            if i % 2 == 0:
                z = z + self.pelvis_up * 0.5
            else:
                z = z + self.pelvis_down * 0.5

            ca = cervical.head.y; cb = cervical.head.z
            r = (Vector((cervical.tail.y, cervical.tail.z)) - Vector((cervical.head.y, cervical.head.z))).length

            b = - 2 * ca
            c = ca ** 2 + (z - cb) ** 2 - r ** 2
            delta = b ** 2 - 4 * c
            if delta >= 0:
                y = 0.5 * (-b - sqrt(delta))
            else:
                y = cervical.tail.y
                print("Head rot can't be reached by rotation of neck")

            tail_loc = Vector((cervical.tail.x, y, z))
            angle = utils.triangle_angle(v1=Vector((0, 0, 1)), v2=(tail_loc - cervical.head))

            des_orient = Euler((pi / 2 + angle, 0, 0)).to_quaternion()
            utils.rotate_to(bone=cervical, desired=des_orient)
            utils.add_keyframe(bone=cervical, data='rotation_quaternion', frame=frame)

        qdelta = Euler((self.head_rot, 0, 0)).to_quaternion()
        qdes = head.bone.matrix_local.to_quaternion()
        qdes.rotate(qdelta)
        utils.rotate_to(bone=head, desired=qdes)
        utils.add_keyframe(bone=head, data='rotation_quaternion', frame=0)

        utils.make_cyclic(bones=(cervical,), action=self.action)


    def update_scapula(self, *, right_arm=False):
        if right_arm:
            t_up = self.caR + 0.6 * self.duty
            t_up_rot = self.caR + self.duty - 0.05
            t_down = self.caR + 1
            scapula = self.armature.pose.bones["Scapula.R"]
        else:
            t_up = self.caL + 0.6 * self.duty
            t_up_rot = self.caL + self.duty - 0.05
            t_down = self.caL + 1
            scapula = self.armature.pose.bones["Scapula.L"]

        utils.clear_fcurves(bones=(scapula,), action=self.action)

        frame = self.frame(time=t_up)
        bpy.context.scene.frame_set(frame)
        utils.translate_in_local_frame(bone=scapula, translation=Vector((0, 0, self.scapula_up)))
        utils.add_keyframe(bone=scapula, data='location', frame=frame)
        utils.add_keyframe(bone=scapula, data='location', frame=self.frame(time=t_up_rot))
        utils.add_keyframe(bone=scapula, data='location', frame=self.frame(time=t_up + 1))

        frame = self.frame(time=t_down)
        bpy.context.scene.frame_set(frame)
        utils.translate_in_local_frame(bone=scapula, translation=Vector((0, 0, self.scapula_down)))
        utils.add_keyframe(bone=scapula, data='location', frame=frame)

        utils.make_cyclic(bones=(scapula,), action=self.action)


    def update_limb(self, *, is_right=False, is_arm=False):
        if is_right:
            if is_arm:
                foot = self.armature.pose.bones["HandTarget.R"]
                foot_bone = self.armature.pose.bones["Hand.R"]
                toe = self.armature.pose.bones["FingerTarget.R"]
                toe_bone = self.armature.pose.bones["Finger.R"]
                ik = self.armature.pose.bones["ArmIK.R"]
                tight = self.armature.pose.bones["UpperArm.R"]
                lowerleg = self.armature.pose.bones["LowerArm.R"]
                toeC = self.armature.pose.bones["FingerClaws.R"]
                t_contact = self.caR
                t_release = self.caR + self.duty
                touch_x = -self.arm_width - self.contact_width_shift
            else:
                foot = self.armature.pose.bones["FootTarget.R"]
                foot_bone = self.armature.pose.bones["Foot.R"]
                toe = self.armature.pose.bones["ToeTarget.R"]
                toe_bone = self.armature.pose.bones["Toe.R"]
                ik = self.armature.pose.bones["LegIK.R"]
                tight = self.armature.pose.bones["UpperLeg.R"]
                lowerleg = self.armature.pose.bones["LowerLeg.R"]
                toeC = self.armature.pose.bones["ToeClaws.R"]
                t_contact = self.clR
                t_release = self.clR + self.duty
                touch_x = -self.leg_width - self.contact_width_shift
        else:
            if is_arm:
                foot = self.armature.pose.bones["HandTarget.L"]
                foot_bone = self.armature.pose.bones["Hand.L"]
                toe = self.armature.pose.bones["FingerTarget.L"]
                toe_bone = self.armature.pose.bones["Finger.L"]
                ik = self.armature.pose.bones["ArmIK.L"]
                tight = self.armature.pose.bones["UpperArm.L"]
                lowerleg = self.armature.pose.bones["LowerArm.L"]
                toeC = self.armature.pose.bones["FingerClaws.L"]
                t_contact = self.caL
                t_release = self.caL + self.duty
                touch_x = self.arm_width + self.contact_width_shift
            else:
                foot = self.armature.pose.bones["FootTarget.L"]
                foot_bone = self.armature.pose.bones["Foot.L"]
                toe = self.armature.pose.bones["ToeTarget.L"]
                toe_bone = self.armature.pose.bones["Toe.L"]
                ik = self.armature.pose.bones["LegIK.L"]
                tight = self.armature.pose.bones["UpperLeg.L"]
                lowerleg = self.armature.pose.bones["LowerLeg.L"]
                toeC = self.armature.pose.bones["ToeClaws.L"]
                t_contact = self.clL
                t_release = self.clL + self.duty
                touch_x = self.leg_width + self.contact_width_shift

        t_lift = t_release + self.shape / 3
        t_lift_end = t_release + 0.6 * self.shape

        if is_arm:
            step_shift = self.step_shift_arm
            step_center = self.neck_y
            l = self.l2
        else:
            step_shift = self.step_shift_leg
            step_center = 0
            l = self.l

        # Lift rotation
        v1 = toe_bone.bone.tail_local - toe_bone.bone.head_local
        v2 = Euler((self.lift_rot, 0, 0)).to_matrix() @ Vector((0, toe_bone.length, 0))
        lift_toe_angle = utils.triangle_angle(v1=v1, v2=v2)

        utils.clear_fcurves(bones=(toe, foot), action=self.action)
        touch_contact = Vector((touch_x, step_center - (self.duty * (0.5 - step_shift)) * self.stride * 100, 0))
        touch_release = Vector((touch_x, step_center + (self.duty * (0.5 + step_shift)) * self.stride * 100, 0))
        z_correction = Vector((0, 0, toeC.length))

        """
        CONTACT 
        """
        frame = self.frame(time=t_contact)
        bpy.context.scene.frame_set(frame)

        utils.rotate_to(bone=toe, desired=Quaternion())  # reset rotation
        utils.rotate_to(bone=foot, desired=Quaternion())  # reset rotation
        utils.translate_to(bone=toe, location=touch_contact + z_correction)

        # potentially reduce angle of toe to ground if Unguligrade
        if self.animal_classification == 'Unguligrade':
            angle = (self.step / l) * self.hoof_flexibility * 100
            rot_des = Euler((-radians(angle), 0, 0)).to_quaternion()
            utils.rotate_to(bone=toe, desired=rot_des)

        utils.add_keyframe(bone=toe, data='location', frame=frame)
        utils.add_keyframe(bone=toe, data='location', frame=self.frame(time=t_contact + 1))

        # find ik_pos with simple heuristic: The orthogonal distance of the ankle to the line between hip and toe is proportional to its distance in rest pose.
        if is_arm:
            #names are a bit confusing bc of the different terms for arms and legs
            # hip_toe == shoulder_finger
            # ankle_toe == wrist_finger
            # hip_ankle = shoulder_wrist
            hip_toe = min((tight.head - toe.head).length, self.arm_length)
            factor = hip_toe / self.shoulder_finger
            ankle_toe = min(factor * self.wrist_finger, self.hand_length)

            hip_ankle = min(factor * self.shoulder_wrist, self.arm_length - self.hand_length)
            angle = utils.triangle_angle(v1=hip_toe, v2=hip_ankle, v3=ankle_toe)
            vector = ((toe.head - tight.head) / (toe.head - tight.head).length) * hip_ankle
            rot = Euler((angle, 0, 0)).to_matrix()
            vector = rot @ vector
            ik_pos = tight.head + vector

            foot_angle = -utils.triangle_angle(v1=(ik.head - foot.head), v2=(ik_pos - foot.head))

            rot_des = Euler((foot_angle, 0, 0)).to_quaternion()
            utils.rotate_to(bone=foot, desired=rot_des)
        else:
            hip_toe = min((tight.head - toe.head).length, self.leg_length)

            factor = hip_toe / self.hip_toe
            ankle_toe = min(factor * self.ankle_toe, self.foot_length)

            hip_ankle = min(factor * self.hip_ankle, self.leg_length - self.foot_length)
            angle = utils.triangle_angle(v1=hip_toe, v2=hip_ankle, v3=ankle_toe)
            vector = ((toe.head - tight.head) / (toe.head - tight.head).length) * hip_ankle
            rot = Euler((angle, 0, 0)).to_matrix()
            vector = rot @ vector
            ik_pos = tight.head + vector

            foot_angle = -utils.triangle_angle(v1=(ik.head - foot.head), v2=(ik_pos - foot.head))

            rot_des = Euler((foot_angle, 0, 0)).to_quaternion()
            utils.rotate_to(bone=foot, desired=rot_des)

        #correct anatomical constraint
        A = (foot.head.y, foot.head.z)
        B = (lowerleg.head.y, lowerleg.head.z)
        P = (lowerleg.tail.y, lowerleg.tail.z)

        ref = utils.point_line_sign(A=A, B=B, P=(B[0] - 10, B[1]))
        d = utils.point_line_sign(A=A, B=B, P=P)

        while d == ref:
            foot_angle = foot_angle - radians(10)
            rot_des = Euler((foot_angle, 0, 0)).to_quaternion()
            utils.rotate_to(bone=foot, desired=rot_des)

            A = (foot.head.y, foot.head.z)
            B = (lowerleg.head.y, lowerleg.head.z)
            P = (lowerleg.tail.y, lowerleg.tail.z)

            ref = utils.point_line_sign(A=A, B=B, P=(B[0] - 10, B[1]))
            d = utils.point_line_sign(A=A, B=B, P=P)


        utils.add_keyframe(bone=foot, data='rotation_quaternion', frame=frame)
        utils.add_keyframe(bone=toe, data='rotation_quaternion', frame=frame)
        utils.add_keyframe(bone=toe, data='rotation_quaternion', frame=self.frame(time=t_contact + 1))
        utils.add_keyframe(bone=foot, data='rotation_quaternion', frame=self.frame(time=t_contact + 1))

        """
            RELEASE
            Heuristic: we calculate the desired toe rotation on release. 
            then we calculate how far this angle is from the 'lift angle' and calculate from there when the "roll" starts to happen. 
            then we simply put a keyframe for rotation at "roll-start".
        """
        frame = self.frame(time=t_release)
        bpy.context.scene.frame_set(frame)

        utils.rotate_to(bone=toe, desired=Quaternion())  # reset rotation
        utils.rotate_to(bone=foot, desired=Quaternion())  # reset rotation
        utils.translate_to(bone=toe, location=touch_release + z_correction)

        utils.add_keyframe(bone=toe, data='location', frame=frame)

        max_angle_toe = utils.triangle_angle(v1=(foot.head - toe.head), v2=(tight.head - toe.head))
        max_angle_foot = utils.triangle_angle(v1=(ik.head - foot.head), v2=(tight.head - foot.head))

        toe_angle = lift_toe_angle * self.roll_initial_rot_percentage #desired toe rotation based on percentage of lift_toe_angle
        foot_angle = toe_angle * self.roll_toe_foot_angle_ratio

        initial_toe_angle = 0
        # potentially increase angle of toe to ground if Unguligrade
        if self.animal_classification == 'Unguligrade':
            initial_toe_angle = radians((self.step / l) * self.hoof_flexibility * 100)

        #Here we correct infeasible configurations (evident if toe_bone and toe are not at the same position)
        while toe_angle < max_angle_toe:
            if (toe_bone.head - foot.head).length_squared > 1 or (foot_bone.head - ik.head).length_squared > 1:
                toe_angle = toe_angle + radians(10)
                foot_angle = toe_angle * self.roll_toe_foot_angle_ratio
                rot_des = Euler((toe_angle, 0, 0)).to_quaternion()
                utils.rotate_to(bone=toe, desired=rot_des)
                rot_des = Euler((foot_angle, 0, 0)).to_quaternion()
                utils.rotate_to(bone=foot, desired=rot_des)
            else:
                break

        #release foot rot
        foot_angle = min(foot_angle, max_angle_foot)
        rot_des = Euler((foot_angle, 0, 0)).to_quaternion()
        utils.rotate_to(bone=foot, desired=rot_des)
        utils.add_keyframe(bone=foot, data='rotation_quaternion', frame=frame)

        #release toe rot
        toe_angle = min(toe_angle, max_angle_toe)
        rot_des = Euler((toe_angle, 0, 0)).to_quaternion()
        utils.rotate_to(bone=toe, desired=rot_des)
        utils.add_keyframe(bone=toe, data='rotation_quaternion', frame=frame)

        initial_toe_angle = min(initial_toe_angle, toe_angle)
        angle_ratio = min(toe_angle-initial_toe_angle / max(0.001, lift_toe_angle), 1)
        frame_diff = self.frame(time = t_lift) - frame
        keypose_frame = frame - angle_ratio * frame_diff
        rot_des = Euler((initial_toe_angle, 0, 0)).to_quaternion()
        utils.rotate_to(bone=toe, desired=rot_des)
        utils.add_keyframe(bone=toe, data='rotation_quaternion', frame=keypose_frame)

        # make cyclic and linear
        utils.make_cyclic(bones=(toe, foot), action=self.action)
        frames = [self.frame(time=time) for time in (t_contact, t_release)]
        utils.make_linear(bones=(toe, foot), kf_point_frames=frames, action=self.action)

        # correct anatomical constraint
        bpy.context.evaluated_depsgraph_get()
        A = (foot.head.y, foot.head.z)
        B = (lowerleg.head.y, lowerleg.head.z)
        P = (lowerleg.tail.y, lowerleg.tail.z)

        ref = utils.point_line_sign(A=A, B=B, P=(B[0] - 10, B[1]))
        d = utils.point_line_sign(A=A, B=B, P=P)

        while d == ref:
            foot_angle = foot_angle - radians(10)
            rot_des = Euler((foot_angle, 0, 0)).to_quaternion()
            utils.rotate_to(bone=foot, desired=rot_des)

            A = (foot.head.y, foot.head.z)
            B = (lowerleg.head.y, lowerleg.head.z)
            P = (lowerleg.tail.y, lowerleg.tail.z)

            ref = utils.point_line_sign(A=A, B=B, P=(B[0] - 10, B[1]))
            d = utils.point_line_sign(A=A, B=B, P=P)

        utils.add_keyframe(bone=foot, data='rotation_quaternion', frame=frame)

        """
            Step Lift
        """
        frame = self.frame(time=t_lift)
        bpy.context.scene.frame_set(frame)

        lift_pos = Vector((touch_x, touch_release.y - self.stride * 20, self.lift + toeC.length))
        utils.translate_to(bone=toe, location=lift_pos)
        rot_des = Euler((lift_toe_angle, 0, 0)).to_quaternion()
        utils.rotate_to(bone=toe, desired=rot_des)
        if is_arm:
            rot_des = Euler((foot_angle * 1.15, 0, 0)).to_quaternion()
            utils.rotate_to(bone=foot, desired=rot_des)
            utils.add_keyframe(bone=foot, data='rotation_quaternion', frame=frame)


        utils.add_keyframe(bone=toe, data='location', frame=frame)
        utils.add_keyframe(bone=toe, data='rotation_quaternion', frame=frame)

        """
            Only applies to arms
            Add extra keyframe before contact to recorrect anatomical constraint.
            Also makes the motion more graceful
        """

        if is_arm:
            frame = self.frame(time=t_lift_end)
            bpy.context.scene.frame_set(frame)

            Ar = (toe.head.y, toe.head.z)
            Br = (lowerleg.tail.y, lowerleg.tail.z)
            Pr = (foot.head.y, foot.head.z)

            A = (foot.head.y, foot.head.z)
            B = (lowerleg.head.y, lowerleg.head.z)
            P = (lowerleg.tail.y, lowerleg.tail.z)

            ref = utils.point_line_sign(A=A, B=B, P=(B[0] - 10, B[1]))
            d = utils.point_line_sign(A=A, B=B, P=P)

            if utils.point_line_sign(A=Ar,B=Br,P=Pr) != d:
                while d == ref:
                    foot_angle = foot_angle - radians(10)
                    rot_des = Euler((foot_angle, 0, 0)).to_quaternion()
                    utils.rotate_to(bone=foot, desired=rot_des)

                    A = (foot.head.y, foot.head.z)
                    B = (lowerleg.head.y, lowerleg.head.z)
                    P = (lowerleg.tail.y, lowerleg.tail.z)

                    ref = utils.point_line_sign(A=A, B=B, P=(B[0] - 10, B[1]))
                    d = utils.point_line_sign(A=A, B=B, P=P)

            utils.add_keyframe(bone=foot, data='rotation_quaternion', frame=frame)

