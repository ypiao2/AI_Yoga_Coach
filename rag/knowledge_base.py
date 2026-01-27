"""
Knowledge Base - Structured yoga knowledge for RAG retrieval
Loads from built-in data + data/yoga_knowledge.json (from ingested books) when present.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional


def _default_knowledge_path() -> Path:
    from .knowledge_io import get_knowledge_path
    return get_knowledge_path()


class KnowledgeBase:
    """
    Yoga knowledge base for RAG retrieval.
    Uses built-in entries; if data/yoga_knowledge.json exists, loads and merges
    those entries (file wins by pose name). Ingested yoga books are stored there.
    """
    
    def __init__(self, knowledge_file: Optional[Path] = None):
        builtin = self._initialize_knowledge()
        path = knowledge_file or _default_knowledge_path()
        if path.exists():
            try:
                from .knowledge_io import load_knowledge_from_file
                from_file = load_knowledge_from_file(path)
                merged = {e.get("pose"): e for e in builtin if e.get("pose")}
                for e in from_file:
                    if e.get("pose"):
                        merged[e["pose"]] = e
                self.knowledge = list(merged.values())
            except Exception:
                self.knowledge = builtin
        else:
            self.knowledge = builtin
    
    def _initialize_knowledge(self) -> List[Dict]:
        """
        Initialize knowledge base with pose information.
        Each entry contains alignment cues, contraindications, and explanations.
        """
        return [
            {
                "pose": "child_pose",
                "alignment": [
                    "Knees should be hip-width apart or wider",
                    "Big toes touching behind you",
                    "Sit back on your heels",
                    "Forehead rests on the mat",
                    "Arms can be extended forward or alongside body"
                ],
                "contraindications": [
                    "Knee injury",
                    "Ankle injury",
                    "Pregnancy (third trimester)"
                ],
                "benefits": [
                    "Calms the nervous system",
                    "Stretches hips and thighs",
                    "Relieves back tension"
                ],
                "breathing": "Breathe deeply into your back body",
                "modifications": "Place a pillow between thighs and calves if knees are sensitive"
            },
            {
                "pose": "cat_cow",
                "alignment": [
                    "Start on hands and knees, wrists under shoulders, knees under hips",
                    "Move with your breath",
                    "Inhale: arch back, lift tailbone and head (cow)",
                    "Exhale: round spine, tuck tailbone (cat)",
                    "Keep shoulders away from ears"
                ],
                "contraindications": [
                    "Severe wrist injury",
                    "Severe back pain"
                ],
                "benefits": [
                    "Mobilizes the spine",
                    "Improves coordination",
                    "Warms up the body"
                ],
                "breathing": "Sync movement with breath - inhale cow, exhale cat",
                "modifications": "Place hands on blocks if wrists are sensitive"
            },
            {
                "pose": "supine_twist",
                "alignment": [
                    "Lie on your back",
                    "Hug one knee to chest",
                    "Gently guide knee across body",
                    "Keep both shoulders on the mat",
                    "Gaze opposite direction of knee"
                ],
                "contraindications": [
                    "Severe back injury",
                    "Pregnancy (avoid deep twists)"
                ],
                "benefits": [
                    "Releases tension in lower back",
                    "Stretches spine",
                    "Calms nervous system"
                ],
                "breathing": "Breathe deeply, allowing the twist to deepen with each exhale",
                "modifications": "Place a pillow under the bent knee for support"
            },
            {
                "pose": "legs_up_wall",
                "alignment": [
                    "Sit sideways next to wall",
                    "Swing legs up wall as you lie down",
                    "Hips close to wall (or slightly away if hamstrings are tight)",
                    "Arms relaxed at sides",
                    "Close eyes and relax"
                ],
                "contraindications": [
                    "Glaucoma",
                    "Severe eye pressure"
                ],
                "benefits": [
                    "Relieves tired legs",
                    "Calms nervous system",
                    "Reduces swelling",
                    "Excellent for menstrual phase"
                ],
                "breathing": "Natural, relaxed breathing",
                "modifications": "Place a folded blanket under hips for support"
            },
            {
                "pose": "mountain_pose",
                "alignment": [
                    "Stand with feet hip-width apart or together",
                    "Weight evenly distributed on all four corners of feet",
                    "Knees soft, not locked",
                    "Pelvis neutral",
                    "Shoulders relaxed, away from ears",
                    "Crown of head reaching toward sky"
                ],
                "contraindications": [],
                "benefits": [
                    "Improves posture",
                    "Builds body awareness",
                    "Foundation for all standing poses"
                ],
                "breathing": "Deep, steady breathing",
                "modifications": "Stand with back against wall for alignment feedback"
            },
            {
                "pose": "warrior_ii",
                "alignment": [
                    "Step feet wide apart",
                    "Turn back foot in 45 degrees",
                    "Front knee bent, tracking over ankle",
                    "Back leg straight and strong",
                    "Arms parallel to floor",
                    "Gaze over front middle finger",
                    "Hips squared to side"
                ],
                "contraindications": [
                    "Hip injury",
                    "Knee injury"
                ],
                "benefits": [
                    "Strengthens legs",
                    "Opens hips",
                    "Builds stamina"
                ],
                "breathing": "Breathe deeply, maintaining steady breath",
                "modifications": "Reduce depth of lunge if knee discomfort"
            },
            {
                "pose": "tree_pose",
                "alignment": [
                    "Stand on one leg",
                    "Place foot on inner thigh, calf, or ankle (not on knee)",
                    "Press foot into leg, leg into foot",
                    "Hips squared forward",
                    "Hands at heart center or overhead",
                    "Focus on a fixed point (drishti)"
                ],
                "contraindications": [
                    "Ankle injury",
                    "Severe balance issues"
                ],
                "benefits": [
                    "Improves balance",
                    "Strengthens standing leg",
                    "Opens hip of lifted leg"
                ],
                "breathing": "Steady, calm breathing",
                "modifications": "Use wall for support or place foot on ankle instead of thigh"
            },
            {
                "pose": "seated_forward_fold",
                "alignment": [
                    "Sit with legs extended",
                    "Flex feet, toes pointing toward ceiling",
                    "Hinge from hips, not rounding lower back",
                    "Reach forward, not down",
                    "Keep spine long"
                ],
                "contraindications": [
                    "Severe back injury",
                    "Hamstring injury"
                ],
                "benefits": [
                    "Stretches hamstrings",
                    "Calms nervous system",
                    "Relieves stress"
                ],
                "breathing": "Breathe into the back body, allowing stretch to deepen",
                "modifications": "Sit on a blanket or bend knees slightly"
            },
            {
                "pose": "pigeon_pose",
                "alignment": [
                    "From downward dog, bring front leg forward",
                    "Front shin parallel to front of mat (or more accessible variation)",
                    "Back leg extended straight behind",
                    "Hips squared forward",
                    "Keep front foot flexed to protect knee"
                ],
                "contraindications": [
                    "Knee injury",
                    "Hip injury",
                    "SI joint issues"
                ],
                "benefits": [
                    "Deep hip opener",
                    "Releases tension in glutes",
                    "Excellent for menstrual phase"
                ],
                "breathing": "Breathe deeply, allowing hip to release",
                "modifications": "Place pillow under front hip, or do reclining pigeon instead"
            },
            {
                "pose": "cobra_pose",
                "alignment": [
                    "Lie on belly",
                    "Place hands under shoulders",
                    "Press tops of feet into mat",
                    "Lift chest using back muscles, not just arms",
                    "Keep shoulders away from ears",
                    "Gaze forward or slightly up"
                ],
                "contraindications": [
                    "Severe back injury",
                    "Pregnancy (avoid after first trimester)",
                    "Carpal tunnel"
                ],
                "benefits": [
                    "Strengthens back",
                    "Opens chest",
                    "Improves posture"
                ],
                "breathing": "Breathe deeply as you lift",
                "modifications": "Keep elbows bent, less lift if back is sensitive"
            },
            {
                "pose": "bridge_pose",
                "alignment": [
                    "Lie on back, knees bent",
                    "Feet hip-width apart, close to glutes",
                    "Press feet into mat",
                    "Lift hips, engaging glutes",
                    "Keep knees tracking over ankles",
                    "Interlace hands under body or keep arms at sides"
                ],
                "contraindications": [
                    "Neck injury",
                    "Knee injury"
                ],
                "benefits": [
                    "Strengthens glutes",
                    "Opens chest",
                    "Stretches hip flexors"
                ],
                "breathing": "Breathe deeply as you hold",
                "modifications": "Place block under sacrum for support"
            },
            {
                "pose": "downward_dog",
                "alignment": [
                    "Start on hands and knees",
                    "Tuck toes, lift hips up and back",
                    "Create inverted V shape",
                    "Hands shoulder-width apart",
                    "Feet hip-width apart",
                    "Hips high, weight back toward legs",
                    "Keep micro-bend in knees if hamstrings are tight"
                ],
                "contraindications": [
                    "Wrist injury",
                    "High blood pressure",
                    "Glaucoma"
                ],
                "benefits": [
                    "Strengthens arms and legs",
                    "Stretches hamstrings",
                    "Calms brain"
                ],
                "breathing": "Steady, deep breathing",
                "modifications": "Bend knees deeply, use blocks under hands, or do at wall"
            },
            {
                "pose": "breath_awareness",
                "alignment": [
                    "Comfortable seated or lying position",
                    "Spine long if seated",
                    "Close eyes",
                    "Relax body"
                ],
                "contraindications": [],
                "benefits": [
                    "Calms nervous system",
                    "Reduces stress",
                    "Improves focus",
                    "Excellent for all cycle phases"
                ],
                "breathing": "Observe natural breath, then deepen gradually",
                "modifications": "Can be done in any comfortable position"
            },
        ]
    
    def retrieve_by_pose(self, pose_name: str) -> Optional[Dict]:
        """
        Retrieve knowledge for a specific pose.
        
        Args:
            pose_name: Name of the pose
        
        Returns:
            Knowledge dictionary or None
        """
        for entry in self.knowledge:
            if entry.get("pose") == pose_name:
                return entry
        return None
    
    def retrieve_by_cycle_phase(self, cycle_phase: str) -> List[Dict]:
        """
        Retrieve poses recommended for a specific cycle phase.
        This is a simple implementation - can be enhanced with semantic search.
        
        Args:
            cycle_phase: Cycle phase name
        
        Returns:
            List of relevant knowledge entries
        """
        # Simple keyword matching for v1.0
        phase_keywords = {
            "menstrual": ["calm", "restorative", "gentle", "relax"],
            "follicular": ["strength", "building", "energizing"],
            "ovulation": ["peak", "strength", "balance"],
            "luteal": ["gentle", "calm", "restorative"]
        }
        
        keywords = phase_keywords.get(cycle_phase, [])
        relevant = []
        
        for entry in self.knowledge:
            benefits = " ".join(entry.get("benefits", [])).lower()
            if any(kw in benefits for kw in keywords):
                relevant.append(entry)
        
        return relevant if relevant else self.knowledge[:5]  # Default to first 5
    
    def get_all_knowledge(self) -> List[Dict]:
        """Get all knowledge entries."""
        return self.knowledge.copy()
