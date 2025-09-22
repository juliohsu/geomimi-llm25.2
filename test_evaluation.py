import os
import sys

def test_evaluation_import():
    try:
        print("Testing evaluation imports...")
        
        from evaluation import BHCDataset, get_all_questions, get_evaluation_subset
        print("✅ Dataset imports successful")
        
        dataset = BHCDataset()
        questions = get_all_questions()
        print(f"✅ Dataset loaded: {len(questions)} questions")
        
        subset = get_evaluation_subset(3)
        print(f"✅ Subset loaded: {len(subset)} questions")
        
        if subset:
            sample = subset[0]
            print(f"\n📋 Sample Question:")
            print(f"ID: {sample.id}")
            print(f"Question: {sample.question}")
            print(f"Category: {sample.category.value}")
            print(f"Difficulty: {sample.difficulty.value}")
            print(f"Keywords: {sample.keywords}")
        
        stats = dataset.get_statistics()
        print(f"\n📊 Dataset Statistics:")
        print(f"Total questions: {stats['total_questions']}")
        print(f"Categories: {list(stats['categories'].keys())}")
        print(f"Difficulty levels: {list(stats['difficulty_levels'].keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in evaluation import test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    try:
        print("\nTesting UI components...")
        
        from evaluation.evaluation_ui import render_evaluation_runner
        print("✅ UI components import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in UI components test: {str(e)}")
        return False

def test_evaluator_initialization():
    try:
        print("\nTesting evaluator initialization...")
        
        from evaluation import RAGASEvaluator
        ragas_eval = RAGASEvaluator()
        print("✅ RAGAS evaluator initialized")
        
        from evaluation import GiskardEvaluator
        giskard_eval = GiskardEvaluator()
        print("✅ GISKARD evaluator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in evaluator initialization: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Evaluation System")
    print("=" * 50)
    
    tests = [
        test_evaluation_import,
        test_ui_components,
        test_evaluator_initialization
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Evaluation system is working correctly.")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Run: streamlit run app.py")
        print("3. Go to 'Avaliação Automática' tab")
        print("4. Test RAGAS and GISKARD evaluation")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)