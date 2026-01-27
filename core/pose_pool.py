"""
Pose Pool - Collection of yoga poses with metadata
"""
from typing import List, Dict, Optional
from .safety_rules import PoseType


class PosePool:
    """
    Pool of yoga poses with filtering capabilities.
    """
    
    def __init__(self):
        self.poses = self._initialize_poses()
    
    def _initialize_poses(self) -> List[Dict]:
        """
        Initialize pose database for AI Yoga Coach.
        Curated list of 100 poses across restorative, gentle, standing, forward folds,
        twists, hip openers, breathing, backbends, core, inversions, and balance.
        """
        return [
            # ----- Restorative (safe for menstrual, high fatigue) -----
            {"name": "child_pose", "sanskrit": "Balasana", "types": ["restorative", "forward_fold"], "difficulty": "beginner", "duration_suggestion": "1-3 min"},
            {"name": "legs_up_wall", "sanskrit": "Viparita Karani", "types": ["restorative", "inversion"], "difficulty": "beginner", "duration_suggestion": "5-10 min"},
            {"name": "corpse_pose", "sanskrit": "Savasana", "types": ["restorative"], "difficulty": "beginner", "duration_suggestion": "5-15 min"},
            {"name": "supported_bridge", "sanskrit": "Setu Bandha Sarvangasana (supported)", "types": ["restorative", "backbend"], "difficulty": "beginner", "duration_suggestion": "1-2 min"},
            {"name": "reclined_bound_angle", "sanskrit": "Supta Baddha Konasana", "types": ["restorative", "hip_opener"], "difficulty": "beginner", "duration_suggestion": "3-5 min"},
            {"name": "supported_fish", "sanskrit": "Matsyasana (supported)", "types": ["restorative", "backbend"], "difficulty": "beginner", "duration_suggestion": "2-4 min"},
            {"name": "happy_baby", "sanskrit": "Ananda Balasana", "types": ["restorative", "hip_opener"], "difficulty": "beginner", "duration_suggestion": "1-2 min"},
            {"name": "reclined_hero", "sanskrit": "Supta Virasana", "types": ["restorative", "hip_opener"], "difficulty": "intermediate", "duration_suggestion": "1-3 min"},
            {"name": "legs_on_chair", "sanskrit": "Viparita Karani (chair)", "types": ["restorative"], "difficulty": "beginner", "duration_suggestion": "5-10 min"},
            {"name": "sphinx_pose", "sanskrit": "Salamba Bhujangasana", "types": ["restorative", "backbend"], "difficulty": "beginner", "duration_suggestion": "1-2 min"},
            # ----- Gentle stretches -----
            {"name": "cat_cow", "sanskrit": "Marjaryasana-Bitilasana", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "6-10 reps"},
            {"name": "supine_twist", "sanskrit": "Supta Matsyendrasana", "types": ["gentle_stretch", "twist"], "difficulty": "beginner", "duration_suggestion": "1-2 min each side"},
            {"name": "knee_to_chest", "sanskrit": "Apanasana", "types": ["gentle_stretch", "hip_opener"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "thread_the_needle", "sanskrit": "Parsva Balasana", "types": ["gentle_stretch", "twist"], "difficulty": "beginner", "duration_suggestion": "1 min each side"},
            {"name": "wind_releasing", "sanskrit": "Pavana Muktasana", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "lying_quad_stretch", "sanskrit": "Supta Padangusthasana (bent)", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "1 min each side"},
            {"name": "seated_neck_stretch", "sanskrit": "neck release", "types": ["gentle_stretch", "seated"], "difficulty": "beginner", "duration_suggestion": "30 sec each side"},
            {"name": "pelvic_tilts", "sanskrit": "gentle pelvic tilts", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "8-10 reps"},
            {"name": "ankle_circles", "sanskrit": "ankle mobility", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "5 each direction"},
            {"name": "wrist_stretches", "sanskrit": "wrist mobility", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "30 sec each"},
            # ----- Standing -----
            {"name": "mountain_pose", "sanskrit": "Tadasana", "types": ["standing"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "warrior_i", "sanskrit": "Virabhadrasana I", "types": ["standing"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min each side"},
            {"name": "warrior_ii", "sanskrit": "Virabhadrasana II", "types": ["standing"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min each side"},
            {"name": "warrior_iii", "sanskrit": "Virabhadrasana III", "types": ["standing", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "tree_pose", "sanskrit": "Vrikshasana", "types": ["standing", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min each side"},
            {"name": "standing_forward_fold", "sanskrit": "Uttanasana", "types": ["forward_fold", "standing"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "half_lift", "sanskrit": "Ardha Uttanasana", "types": ["standing", "forward_fold"], "difficulty": "beginner", "duration_suggestion": "30 sec"},
            {"name": "triangle_pose", "sanskrit": "Trikonasana", "types": ["standing", "side_bend"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min each side"},
            {"name": "extended_side_angle", "sanskrit": "Utthita Parsvakonasana", "types": ["standing", "side_bend"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min each side"},
            {"name": "pyramid_pose", "sanskrit": "Parsvottanasana", "types": ["standing", "forward_fold"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            {"name": "high_lunge", "sanskrit": "Anjaneyasana (high)", "types": ["standing"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min each side"},
            {"name": "low_lunge", "sanskrit": "Anjaneyasana", "types": ["standing", "hip_opener"], "difficulty": "beginner", "duration_suggestion": "1 min each side"},
            {"name": "chair_pose", "sanskrit": "Utkatasana", "types": ["standing", "strong_core"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min"},
            {"name": "gate_pose", "sanskrit": "Parighasana", "types": ["standing", "gentle_stretch", "side_bend"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            {"name": "standing_wide_legged", "sanskrit": "Prasarita Padottanasana", "types": ["standing", "forward_fold"], "difficulty": "beginner", "duration_suggestion": "1 min"},
            # ----- Balance -----
            {"name": "eagle_pose", "sanskrit": "Garudasana", "types": ["standing", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "dancer_pose", "sanskrit": "Natarajasana", "types": ["standing", "balance", "backbend"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "half_moon", "sanskrit": "Ardha Chandrasana", "types": ["standing", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min each side"},
            {"name": "revolved_triangle", "sanskrit": "Parivrtta Trikonasana", "types": ["standing", "twist"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            {"name": "standing_leg_raise", "sanskrit": "Utthita Hasta Padangusthasana", "types": ["standing", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "toe_stand", "sanskrit": "Padangusthasana (balance)", "types": ["balance"], "difficulty": "advanced", "duration_suggestion": "30 sec each side"},
            # ----- Forward folds -----
            {"name": "seated_forward_fold", "sanskrit": "Paschimottanasana", "types": ["forward_fold", "seated"], "difficulty": "beginner", "duration_suggestion": "1-3 min"},
            {"name": "head_to_knee", "sanskrit": "Janu Sirsasana", "types": ["forward_fold", "hip_opener", "seated"], "difficulty": "beginner", "duration_suggestion": "1-2 min each side"},
            {"name": "wide_angled_seated_fold", "sanskrit": "Upavistha Konasana", "types": ["forward_fold", "hip_opener", "seated"], "difficulty": "intermediate", "duration_suggestion": "1-2 min"},
            {"name": "standing_split", "sanskrit": "Urdhva Prasarita Eka Padasana", "types": ["forward_fold", "standing", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "revolved_head_to_knee", "sanskrit": "Parivrtta Janu Sirsasana", "types": ["forward_fold", "twist", "seated", "side_bend"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            # ----- Twists -----
            {"name": "seated_twist", "sanskrit": "Ardha Matsyendrasana", "types": ["twist", "seated"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            {"name": "revolved_chair", "sanskrit": "Parivrtta Utkatasana", "types": ["twist", "standing"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "revolved_lunge", "sanskrit": "Parivrtta Anjaneyasana", "types": ["twist", "standing"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            {"name": "revolved_wide_leg", "sanskrit": "Parivrtta Upavistha Konasana", "types": ["twist", "hip_opener"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            {"name": "lizard_twist", "sanskrit": "twisted lizard", "types": ["twist", "hip_opener"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            # ----- Hip openers -----
            {"name": "pigeon_pose", "sanskrit": "Eka Pada Rajakapotasana", "types": ["hip_opener"], "difficulty": "intermediate", "duration_suggestion": "1-3 min each side"},
            {"name": "butterfly_pose", "sanskrit": "Baddha Konasana", "types": ["hip_opener", "gentle_stretch", "seated"], "difficulty": "beginner", "duration_suggestion": "1-3 min"},
            {"name": "fire_log_pose", "sanskrit": "Agnistambhasana", "types": ["hip_opener", "seated"], "difficulty": "intermediate", "duration_suggestion": "1-2 min each side"},
            {"name": "cow_face_pose", "sanskrit": "Gomukhasana", "types": ["hip_opener", "seated"], "difficulty": "intermediate", "duration_suggestion": "1-2 min each side"},
            {"name": "double_pigeon", "sanskrit": "Agnistambhasana", "types": ["hip_opener"], "difficulty": "intermediate", "duration_suggestion": "1-2 min each side"},
            {"name": "lizard_pose", "sanskrit": "Utthan Pristhasana", "types": ["hip_opener", "standing"], "difficulty": "intermediate", "duration_suggestion": "1-2 min each side"},
            {"name": "frog_pose", "sanskrit": "Mandukasana", "types": ["hip_opener"], "difficulty": "intermediate", "duration_suggestion": "1-2 min"},
            {"name": "reclined_pigeon", "sanskrit": "Supta Kapotasana", "types": ["hip_opener", "restorative"], "difficulty": "beginner", "duration_suggestion": "1-2 min each side"},
            {"name": "squat_pose", "sanskrit": "Malasana", "types": ["hip_opener", "standing"], "difficulty": "intermediate", "duration_suggestion": "1 min"},
            # ----- Seated (e.g. lotus, hero; pranayama & meditation) -----
            {"name": "lotus_pose", "sanskrit": "Padmasana", "types": ["seated", "breathing"], "difficulty": "intermediate", "duration_suggestion": "1-5 min"},
            {"name": "hero_pose", "sanskrit": "Virasana", "types": ["seated", "gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "1-3 min"},
            {"name": "easy_seat", "sanskrit": "Sukhasana", "types": ["seated", "breathing"], "difficulty": "beginner", "duration_suggestion": "1-5 min"},
            # ----- Breathing -----
            {"name": "breath_awareness", "sanskrit": "Pranayama", "types": ["breathing", "seated"], "difficulty": "beginner", "duration_suggestion": "3-5 min"},
            {"name": "diaphragmatic_breathing", "sanskrit": "belly breathing", "types": ["breathing", "seated"], "difficulty": "beginner", "duration_suggestion": "3-5 min"},
            {"name": "alternate_nostril", "sanskrit": "Nadi Shodhana", "types": ["breathing", "seated"], "difficulty": "beginner", "duration_suggestion": "3-5 min"},
            {"name": "victorious_breath", "sanskrit": "Ujjayi", "types": ["breathing"], "difficulty": "beginner", "duration_suggestion": "2-3 min"},
            {"name": "extended_exhale", "sanskrit": "1:2 breathing", "types": ["breathing"], "difficulty": "beginner", "duration_suggestion": "3-5 min"},
            # ----- Backbends -----
            {"name": "cobra_pose", "sanskrit": "Bhujangasana", "types": ["backbend"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "bridge_pose", "sanskrit": "Setu Bandhasana", "types": ["backbend"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "upward_dog", "sanskrit": "Urdhva Mukha Svanasana", "types": ["backbend"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            {"name": "camel_pose", "sanskrit": "Ustrasana", "types": ["backbend"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min"},
            {"name": "fish_pose", "sanskrit": "Matsyasana", "types": ["backbend"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min"},
            {"name": "wheel_pose", "sanskrit": "Urdhva Dhanurasana", "types": ["backbend"], "difficulty": "advanced", "duration_suggestion": "30 sec - 1 min"},
            {"name": "locust_pose", "sanskrit": "Salabhasana", "types": ["backbend"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            {"name": "bow_pose", "sanskrit": "Dhanurasana", "types": ["backbend"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            {"name": "sphinx_pose_backbend", "sanskrit": "Salamba Bhujangasana", "types": ["backbend", "gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "1 min"},
            # ----- Core -----
            {"name": "boat_pose", "sanskrit": "Navasana", "types": ["strong_core"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min"},
            {"name": "plank_pose", "sanskrit": "Phalakasana", "types": ["strong_core"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "side_plank", "sanskrit": "Vasisthasana", "types": ["strong_core", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "dolphin_plank", "sanskrit": "Makara Adho Mukha Svanasana", "types": ["strong_core"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            {"name": "hollow_body", "sanskrit": "core hollow hold", "types": ["strong_core"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            {"name": "dead_bug", "sanskrit": "supine dead bug", "types": ["strong_core"], "difficulty": "beginner", "duration_suggestion": "8-10 reps each side"},
            {"name": "bird_dog", "sanskrit": "table balance", "types": ["strong_core", "balance"], "difficulty": "beginner", "duration_suggestion": "8 reps each side"},
            {"name": "forearm_plank", "sanskrit": "Phalakasana (forearms)", "types": ["strong_core"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            # ----- Inversions -----
            {"name": "downward_dog", "sanskrit": "Adho Mukha Svanasana", "types": ["inversion", "standing"], "difficulty": "beginner", "duration_suggestion": "30 sec - 1 min"},
            {"name": "dolphin_pose", "sanskrit": "Ardha Pincha Mayurasana", "types": ["inversion"], "difficulty": "intermediate", "duration_suggestion": "1 min"},
            {"name": "headstand", "sanskrit": "Sirsasana", "types": ["inversion", "arm_balance"], "difficulty": "advanced", "duration_suggestion": "30 sec - 2 min"},
            {"name": "shoulderstand", "sanskrit": "Salamba Sarvangasana", "types": ["inversion"], "difficulty": "intermediate", "duration_suggestion": "1-3 min"},
            {"name": "plow_pose", "sanskrit": "Halasana", "types": ["inversion"], "difficulty": "intermediate", "duration_suggestion": "1-2 min"},
            {"name": "tripod_headstand", "sanskrit": "Sirsasana B", "types": ["inversion", "arm_balance"], "difficulty": "advanced", "duration_suggestion": "30 sec - 1 min"},
            {"name": "forearm_stand", "sanskrit": "Pincha Mayurasana", "types": ["inversion", "arm_balance"], "difficulty": "advanced", "duration_suggestion": "30 sec"},
            {"name": "handstand_prep", "sanskrit": "Adho Mukha Vrksasana (prep)", "types": ["inversion", "arm_balance"], "difficulty": "advanced", "duration_suggestion": "30 sec"},
            # ----- Arm balances / advanced -----
            {"name": "crow_pose", "sanskrit": "Bakasana", "types": ["arm_balance", "balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            {"name": "side_crow", "sanskrit": "Parsva Bakasana", "types": ["arm_balance", "twist"], "difficulty": "advanced", "duration_suggestion": "30 sec each side"},
            {"name": "eight_angle", "sanskrit": "Astavakrasana", "types": ["arm_balance", "twist"], "difficulty": "advanced", "duration_suggestion": "30 sec each side"},
            {"name": "firefly_pose", "sanskrit": "Tittibhasana", "types": ["arm_balance"], "difficulty": "advanced", "duration_suggestion": "30 sec"},
            {"name": "scale_pose", "sanskrit": "Tolasana", "types": ["arm_balance", "strong_core"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            # ----- Flow / transitional -----
            {"name": "sun_salutation_a", "sanskrit": "Surya Namaskar A", "types": ["standing", "forward_fold", "gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "3-5 rounds"},
            {"name": "sun_salutation_b", "sanskrit": "Surya Namaskar B", "types": ["standing", "strong_core"], "difficulty": "intermediate", "duration_suggestion": "3-5 rounds"},
            {"name": "flow_lunge_series", "sanskrit": "lunge flow", "types": ["standing", "hip_opener"], "difficulty": "intermediate", "duration_suggestion": "1 min each side"},
            {"name": "cat_cow_flow", "sanskrit": "Marjaryasana-Bitilasana flow", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "10 reps"},
            {"name": "reclined_hand_to_big_toe", "sanskrit": "Supta Padangusthasana", "types": ["forward_fold", "gentle_stretch", "hip_opener"], "difficulty": "beginner", "duration_suggestion": "1 min each side"},
            # ----- Yin / restorative extensions -----
            {"name": "yin_dragonfly", "sanskrit": "Dragonfly Pose", "types": ["yin", "hip_opener", "forward_fold"], "difficulty": "beginner", "duration_suggestion": "2-5 min"},
            {"name": "yin_sleeping_swan", "sanskrit": "Sleeping Swan", "types": ["yin", "hip_opener"], "difficulty": "beginner", "duration_suggestion": "2-4 min"},
            {"name": "yin_caterpillar", "sanskrit": "Caterpillar Pose", "types": ["yin", "forward_fold"], "difficulty": "beginner", "duration_suggestion": "2-5 min"},
            {"name": "yin_bananasana", "sanskrit": "Bananasana", "types": ["yin", "side_bend"], "difficulty": "beginner", "duration_suggestion": "2-4 min"},
            {"name": "yin_saddle", "sanskrit": "Saddle Pose", "types": ["yin", "backbend"], "difficulty": "intermediate", "duration_suggestion": "2-4 min"},
            {"name": "yin_snail", "sanskrit": "Snail Pose", "types": ["yin", "forward_fold"], "difficulty": "intermediate", "duration_suggestion": "2-4 min"},
            {"name": "yin_square", "sanskrit": "Square Pose", "types": ["yin", "hip_opener"], "difficulty": "beginner", "duration_suggestion": "2-4 min"},
            # ----- Somatic / mobility -----
            {"name": "somatic_pelvic_circle", "sanskrit": "pelvic circles", "types": ["somatic", "gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "1 min"},
            {"name": "somatic_spinal_wave", "sanskrit": "spinal wave", "types": ["somatic", "gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "1 min"},
            {"name": "fascia_roll_back", "sanskrit": "rolling spine", "types": ["mobility"], "difficulty": "beginner", "duration_suggestion": "1 min"},
            {"name": "hip_cars", "sanskrit": "hip CARs", "types": ["mobility", "hip_opener"], "difficulty": "intermediate", "duration_suggestion": "5 reps each side"},
            {"name": "shoulder_cars", "sanskrit": "shoulder CARs", "types": ["mobility"], "difficulty": "intermediate", "duration_suggestion": "5 reps each side"},
            # ----- Standing variations -----
            {"name": "reverse_warrior", "sanskrit": "Viparita Virabhadrasana", "types": ["standing", "side_bend"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "humble_warrior", "sanskrit": "Baddha Virabhadrasana", "types": ["standing", "forward_fold"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "crescent_lunge", "sanskrit": "Ashta Chandrasana", "types": ["standing"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "goddess_pose", "sanskrit": "Utkata Konasana", "types": ["standing", "hip_opener"], "difficulty": "intermediate", "duration_suggestion": "30 sec - 1 min"},
            {"name": "star_pose", "sanskrit": "Utthita Tadasana", "types": ["standing"], "difficulty": "beginner", "duration_suggestion": "30 sec"},
            {"name": "reverse_triangle", "sanskrit": "Parivrtta Trikonasana (variation)", "types": ["standing", "twist"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            # ----- Balance extensions -----
            {"name": "standing_half_lotus", "sanskrit": "Ardha Padmasana (standing)", "types": ["balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "warrior_iv", "sanskrit": "Virabhadrasana IV", "types": ["balance", "standing"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "airplane_pose", "sanskrit": "Dekasana", "types": ["balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "half_toe_stand", "sanskrit": "Ardha Padangusthasana", "types": ["balance"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            # ----- Seated expansions -----
            {"name": "staff_pose", "sanskrit": "Dandasana", "types": ["seated"], "difficulty": "beginner", "duration_suggestion": "1 min"},
            {"name": "reverse_tabletop", "sanskrit": "Ardha Purvottanasana", "types": ["seated", "backbend"], "difficulty": "beginner", "duration_suggestion": "30 sec"},
            {"name": "compass_pose", "sanskrit": "Parivrtta Surya Yantrasana", "types": ["seated", "hip_opener"], "difficulty": "advanced", "duration_suggestion": "30 sec each side"},
            {"name": "tortoise_pose", "sanskrit": "Kurmasana", "types": ["seated", "forward_fold"], "difficulty": "advanced", "duration_suggestion": "1 min"},
            {"name": "bound_lotus", "sanskrit": "Baddha Padmasana", "types": ["seated"], "difficulty": "advanced", "duration_suggestion": "1 min"},
            # ----- Twists extensions -----
            {"name": "supine_revolved_twist", "sanskrit": "Supta Parivrtta", "types": ["twist"], "difficulty": "beginner", "duration_suggestion": "1 min each side"},
            {"name": "standing_revolved_forward_fold", "sanskrit": "Parivrtta Uttanasana", "types": ["twist", "standing"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "twisted_triangle_bind", "sanskrit": "Parivrtta Trikonasana (bind)", "types": ["twist"], "difficulty": "advanced", "duration_suggestion": "30 sec each side"},
            # ----- Backbend expansions -----
            {"name": "puppy_pose", "sanskrit": "Uttana Shishosana", "types": ["backbend"], "difficulty": "beginner", "duration_suggestion": "1 min"},
            {"name": "king_pigeon", "sanskrit": "Rajakapotasana", "types": ["backbend"], "difficulty": "advanced", "duration_suggestion": "30 sec each side"},
            {"name": "wild_thing", "sanskrit": "Camatkarasana", "types": ["backbend"], "difficulty": "intermediate", "duration_suggestion": "30 sec each side"},
            {"name": "drop_back", "sanskrit": "drop back", "types": ["backbend"], "difficulty": "advanced", "duration_suggestion": "30 sec"},
            # ----- Core expansions -----
            {"name": "low_boat", "sanskrit": "Ardha Navasana", "types": ["strong_core"], "difficulty": "intermediate", "duration_suggestion": "30 sec"},
            {"name": "scissor_legs", "sanskrit": "scissor legs", "types": ["strong_core"], "difficulty": "intermediate", "duration_suggestion": "10 reps"},
            {"name": "bicycle_crunch", "sanskrit": "bicycle crunch", "types": ["strong_core"], "difficulty": "intermediate", "duration_suggestion": "10 reps"},
            {"name": "side_crunch", "sanskrit": "side crunch", "types": ["strong_core"], "difficulty": "intermediate", "duration_suggestion": "10 reps each side"},
            # ----- Pranayama expansions -----
            {"name": "box_breathing", "sanskrit": "Sama Vritti", "types": ["breathing"], "difficulty": "beginner", "duration_suggestion": "3-5 min"},
            {"name": "kapalbhati", "sanskrit": "Kapalbhati", "types": ["breathing"], "difficulty": "intermediate", "duration_suggestion": "1-2 min"},
            {"name": "bhramari", "sanskrit": "Bhramari", "types": ["breathing"], "difficulty": "beginner", "duration_suggestion": "2-3 min"},
            {"name": "sitali", "sanskrit": "Sitali", "types": ["breathing"], "difficulty": "beginner", "duration_suggestion": "2-3 min"},
            # ----- Prenatal / menstrual safe -----
            {"name": "side_lying_savasana", "sanskrit": "Side Savasana", "types": ["restorative"], "difficulty": "beginner", "duration_suggestion": "5-10 min"},
            {"name": "supported_child_pose", "sanskrit": "Balasana (supported)", "types": ["restorative"], "difficulty": "beginner", "duration_suggestion": "2-4 min"},
            {"name": "gentle_cat", "sanskrit": "Marjaryasana (gentle)", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "6 reps"},
            {"name": "seated_side_bend", "sanskrit": "Parsva Sukhasana", "types": ["gentle_stretch"], "difficulty": "beginner", "duration_suggestion": "1 min each side"},
        ]
    
    def filter_by_types(self, allowed_types: List[PoseType]) -> List[Dict]:
        """
        Filter poses by allowed types.
        
        Args:
            allowed_types: List of allowed pose types
        
        Returns:
            List of poses that match at least one allowed type
        """
        filtered = []
        for pose in self.poses:
            pose_types = pose.get("types", [])
            if any(pt in pose_types for pt in allowed_types):
                filtered.append(pose)
        return filtered
    
    def filter_by_difficulty(self, max_difficulty: str = "intermediate") -> List[Dict]:
        """
        Filter poses by maximum difficulty level.
        
        Args:
            max_difficulty: Maximum difficulty ("beginner", "intermediate", "advanced")
        
        Returns:
            List of poses within difficulty range
        """
        difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
        max_level = difficulty_order.get(max_difficulty, 2)
        
        filtered = []
        for pose in self.poses:
            pose_difficulty = pose.get("difficulty", "intermediate")
            pose_level = difficulty_order.get(pose_difficulty, 2)
            if pose_level <= max_level:
                filtered.append(pose)
        return filtered
    
    def get_pose_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a specific pose by name.
        
        Args:
            name: Pose name
        
        Returns:
            Pose dictionary or None
        """
        for pose in self.poses:
            if pose.get("name") == name:
                return pose
        return None
    
    def get_all_poses(self) -> List[Dict]:
        """Get all poses in the pool."""
        return self.poses.copy()
