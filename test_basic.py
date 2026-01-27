"""
Basic test script to verify the system works
"""
import sys

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        from core.body_engine import BodyStateEngine, BodyState
        print("✓ Body Engine imported")
        
        from core.safety_rules import SafetyRules, PoseType
        print("✓ Safety Rules imported")
        
        from core.pose_pool import PosePool
        print("✓ Pose Pool imported")
        
        from rag.retriever import RAGRetriever
        print("✓ RAG Retriever imported")
        
        from agents.planner import PlannerAgent
        print("✓ Planner Agent imported")
        
        from agents.sequencer import SequencerAgent
        print("✓ Sequencer Agent imported")
        
        from agents.cue_writer import CueWriterAgent
        print("✓ Cue Writer Agent imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_body_engine():
    """Test Body State Engine"""
    print("\nTesting Body State Engine...")
    
    try:
        from core.body_engine import BodyStateEngine
        
        engine = BodyStateEngine()
        
        user_input = {
            "last_period_date": "2026-01-20",
            "cycle_length": 28,
            "energy": 2,
            "pain": 3,
            "duration": 20
        }
        
        body_state = engine.process(user_input)
        state_dict = engine.to_dict(body_state)
        
        print(f"✓ Cycle Phase: {state_dict['cycle_phase']}")
        print(f"✓ Intensity: {state_dict['intensity']}")
        print(f"✓ Allowed Types: {state_dict['allowed_pose_types']}")
        print(f"✓ Forbidden Types: {state_dict['forbidden_pose_types']}")
        
        print("\n✅ Body State Engine test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Body Engine error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test the full pipeline"""
    print("\nTesting Full Pipeline...")
    
    try:
        from core.body_engine import BodyStateEngine
        from core.pose_pool import PosePool
        from rag.retriever import RAGRetriever
        from agents.planner import PlannerAgent
        from agents.sequencer import SequencerAgent
        from agents.cue_writer import CueWriterAgent
        
        # Initialize components
        body_engine = BodyStateEngine()
        pose_pool = PosePool()
        rag_retriever = RAGRetriever()
        planner_agent = PlannerAgent()
        sequencer_agent = SequencerAgent()
        cue_writer_agent = CueWriterAgent()
        
        # User input
        user_input = {
            "last_period_date": "2026-01-20",
            "cycle_length": 28,
            "energy": 2,
            "pain": 3,
            "duration": 20
        }
        
        # Pipeline
        body_state = body_engine.process(user_input)
        pose_candidates = pose_pool.filter_by_types(body_state.allowed_pose_types)
        enriched_poses = rag_retriever.enrich_poses(pose_candidates, body_state.cycle_phase)
        structure = planner_agent.generate_structure(body_state, enriched_poses)
        sequence = sequencer_agent.generate_sequence(structure, body_state, enriched_poses)
        cues = cue_writer_agent.generate_cues(sequence, body_state)
        
        print(f"✓ Body State calculated")
        print(f"✓ {len(enriched_poses)} poses enriched")
        print(f"✓ Structure generated: {len(structure['structure'])} sections")
        print(f"✓ Sequence generated: {len(sequence['sequence'])} sections")
        print(f"✓ Cues generated: {len(cues['cues'])} poses")
        
        print("\n✅ Full Pipeline test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("AI Yoga Coach v1.0 - Basic Tests")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_body_engine())
    results.append(test_full_pipeline())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
