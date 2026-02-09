
import torch
from agents.backend.onyx.server.features.dermatology_ai.system import DermatologyAISystem

def verify_system():
    print("1. Initializing System...")
    try:
        system = DermatologyAISystem()
        print("System initialized.")
    except Exception as e:
        print(f"Initialization failed: {e}")
        return

    print("\n2. Testing Multimodal Inference...")
    try:
        # Mock inputs
        batch_size = 1
        image = torch.randn(batch_size, 3, 224, 224)
        metadata = torch.randn(batch_size, 10)
        
        result = system.analyze_case(image, metadata, model_type='multimodal')
        print(f"Inference Result: {result}")
    except Exception as e:
        print(f"Inference failed: {e}")

    print("\n3. Testing Fairness Audit...")
    try:
        # Mock dataset
        dataset = [
            {
                'label': 1, 
                'prediction': 1, 
                'metadata_dict': {'skin_tone': 'light'}
            },
            {
                'label': 0, 
                'prediction': 0, 
                'metadata_dict': {'skin_tone': 'light'}
            },
            {
                'label': 1, 
                'prediction': 0, # Error
                'metadata_dict': {'skin_tone': 'dark'}
            },
            {
                'label': 0, 
                'prediction': 0, 
                'metadata_dict': {'skin_tone': 'dark'}
            }
        ]
        
        report = system.audit_system(dataset)
        print(f"Fairness Report: Is Fair? {report.is_fair}")
        print(f"Disparity Metrics: {report.disparity_metrics}")
        print(f"Group Metrics: {report.group_metrics}")
        
    except Exception as e:
        print(f"Audit failed: {e}")

    print("\n4. Testing Federated Learning Simulation...")
    try:
        result = system.train_federated(rounds=2, num_clients=3)
        print("Simulation Result:")
        print(f"Status: {result['status']}")
        print(f"Final Accuracy: {result['final_accuracy']:.2%}")
        print("Rounds:")
        for r in result['rounds']:
            print(f"  Round {r['round']}: Acc={r['accuracy']:.2%}, Participants={r['participants']}")
            
    except Exception as e:
        print(f"Federated Learning failed: {e}")

    print("\n5. Testing XAI (Concept Bottleneck)...")
    try:
        # Simulate image data
        dummy_image_data = b"fake_image_bytes"
        explanation = system.explain_diagnosis("test_img_001", dummy_image_data)
        print(f"XAI Result: Diagnosis='{explanation['final_diagnosis']}', Confidence={explanation['diagnosis_confidence']:.2f}")
        print(f"Top Concept: {explanation['concepts'][0]['name']} ({explanation['concepts'][0]['score']:.2f})")
    except Exception as e:
        print(f"XAI Test Failed: {e}")

    print("\n6. Testing GenAI (Diffusion Simulation)...")
    try:
        generated = system.generate_synthetic_data("melanoma", count=2)
        print(f"GenAI Result: Generated {len(generated)} images.")
        print(f"First Image URL: {generated[0]['image_url']}")
    except Exception as e:
        print(f"GenAI Test Failed: {e}")

    # 7. Test Telederm Triage
    print("\n7. Testing Telederm Triage...")
    try:
        case_data = {"age": 65, "symptoms": ["bleeding"], "has_changed": True}
        triage = system.triage_case(case_data)
        print(f"Triage Result: Level='{triage['urgency_level']}', Action='{triage['recommended_action']}'")
    except Exception as e:
        print(f"Triage Test Failed: {e}")

    # 8. Test SSL Pre-training
    print("\n8. Testing SSL Pre-training...")
    try:
        job = system.run_ssl_pretraining("ISIC_2024_Unlabeled")
        print(f"SSL Job Started: ID={job['id']}, Status={job['status']}")
    except Exception as e:
        print(f"SSL Test Failed: {e}")

    # 9. Test Multimodal LLM
    print("\n9. Testing Multimodal LLM...")
    try:
        opinion = system.get_llm_opinion("case_123", b"fake_img")
        print(f"LLM Opinion: {opinion['confidence_assessment']}")
        print(f"Reasoning: {opinion['reasoning'][:100]}...")
    except Exception as e:
        print(f"LLM Test Failed: {e}")

    # 10. Test Model Training
    print("\n10. Testing Model Training (Simulated)...")
    try:
        # Use a fake path, the loader will mock data
        train_result = system.train_model("mock_data_dir", epochs=1)
        print(f"Training Result: Status='{train_result['status']}', Final Acc={train_result['final_accuracy']:.2f}")
    except Exception as e:
        print(f"Training Test Failed: {e}")

    # 11. Test Wearable Sensors
    print("\n11. Testing Wearable Sensors...")
    try:
        mock_readings = [
            {"timestamp": "2025-01-01T22:00:00", "scratching_intensity": 0.8, "sleep_quality": 0.3, "temperature": 36.5, "humidity": 40},
            {"timestamp": "2025-01-01T23:00:00", "scratching_intensity": 0.6, "sleep_quality": 0.4, "temperature": 36.4, "humidity": 40}
        ]
        wearable_result = system.analyze_wearable_data("patient_123", mock_readings)
        print(f"Wearable Result: Risk='{wearable_result['flare_risk']}', Rec='{wearable_result['recommendation']}'")
    except Exception as e:
        print(f"Wearable Test Failed: {e}")

    # 12. Test Total Body Photography
    print("\n12. Testing Total Body Photography...")
    try:
        body_map = system.map_body_lesions("patient_123", b"fake_scan_data")
        print(f"Body Map Result: Total Lesions={body_map['total_lesions']}, New={body_map['new_lesions']}")
    except Exception as e:
        print(f"Body Map Test Failed: {e}")

    # 13. Test Compliance Checker
    print("\n13. Testing Compliance Checker...")
    try:
        # Test Case 1: High risk, no explanation (Should fail compliance)
        risky_diagnosis = {"diagnosis": "Malignant", "confidence": 0.95, "model_used": "black_box"}
        compliance_report = system.check_compliance(risky_diagnosis)
        print(f"Compliance Report (Risky): Compliant={compliance_report['compliant']}, Warnings={len(compliance_report['warnings'])}")
        if compliance_report['warnings']:
            print(f"  - Warning: {compliance_report['warnings'][0]}")
    except Exception as e:
        print(f"Compliance Test Failed: {e}")

if __name__ == "__main__":
    verify_system()
