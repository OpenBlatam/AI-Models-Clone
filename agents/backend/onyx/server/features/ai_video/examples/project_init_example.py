"""
Project Initialization Example
=============================

This example demonstrates how to use the project initialization system
to begin AI/ML projects with clear problem definition and dataset analysis.

Usage:
    python project_init_example.py

This will:
1. Define a clear problem for AI video generation
2. Analyze a sample dataset
3. Set up the complete project structure
4. Generate comprehensive reports
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import the project_init module
sys.path.append(str(Path(__file__).parent.parent))

from project_init import (
    ProblemDefinition, 
    DatasetAnalyzer, 
    ProjectInitializer,
    create_project_from_template
)


def example_ai_video_project():
    """Example: AI Video Generation Project"""
    
    print("🚀 Starting AI Video Generation Project Initialization")
    print("=" * 60)
    
    # 1. Define the Problem
    print("\n📋 Step 1: Problem Definition")
    print("-" * 30)
    
    problem_def = ProblemDefinition(
        project_name="ai_video_generation",
        problem_type="generation",
        business_objective="Generate high-quality AI videos from text prompts for content creators",
        success_metrics=[
            "video_quality_score",
            "prompt_accuracy", 
            "generation_speed",
            "user_satisfaction",
            "content_relevance"
        ],
        constraints=[
            "GPU memory limitations",
            "Generation time < 30 seconds",
            "Video length 5-60 seconds",
            "Cost per generation < $0.10"
        ],
        assumptions=[
            "Stable diffusion models are available",
            "GPU resources are accessible",
            "Text prompts are in English",
            "Target audience is content creators"
        ],
        stakeholders=[
            "Content creators",
            "Marketing team", 
            "Product managers",
            "End users",
            "Development team"
        ],
        timeline="3 months",
        budget="$50,000",
        technical_requirements=[
            "PyTorch",
            "Diffusers",
            "Transformers", 
            "Gradio",
            "FastAPI",
            "TensorBoard",
            "wandb"
        ]
    )
    
    print(f"✅ Problem defined: {problem_def.project_name}")
    print(f"   Business Objective: {problem_def.business_objective}")
    print(f"   Success Metrics: {len(problem_def.success_metrics)} metrics defined")
    print(f"   Constraints: {len(problem_def.constraints)} constraints identified")
    
    # 2. Create Project Directory
    print("\n📁 Step 2: Project Setup")
    print("-" * 30)
    
    project_dir = Path("examples/ai_video_project")
    project_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Project directory created: {project_dir}")
    
    # 3. Dataset Analysis (Simulated)
    print("\n📊 Step 3: Dataset Analysis")
    print("-" * 30)
    
    # Create sample dataset for demonstration
    sample_data_dir = project_dir / "data" / "sample_videos"
    sample_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample metadata file
    import pandas as pd
    import numpy as np
    
    sample_metadata = pd.DataFrame({
        'video_id': [f'video_{i:03d}' for i in range(100)],
        'prompt': [f'Sample video prompt {i}' for i in range(100)],
        'duration': np.random.uniform(5, 60, 100),
        'quality_score': np.random.uniform(0.7, 1.0, 100),
        'category': np.random.choice(['nature', 'technology', 'art', 'people'], 100),
        'file_size_mb': np.random.uniform(10, 100, 100),
        'resolution': np.random.choice(['720p', '1080p', '4K'], 100)
    })
    
    metadata_file = sample_data_dir / "metadata.csv"
    sample_metadata.to_csv(metadata_file, index=False)
    
    print(f"✅ Sample dataset created: {metadata_file}")
    print(f"   Dataset size: {len(sample_metadata)} videos")
    print(f"   Features: {list(sample_metadata.columns)}")
    
    # 4. Analyze Dataset
    analyzer = DatasetAnalyzer(sample_data_dir, project_dir / "dataset_analysis")
    dataset_info = analyzer.analyze_dataset()
    
    print(f"✅ Dataset analysis complete")
    print(f"   Missing values: {sum(dataset_info.missing_values.values())}")
    print(f"   Duplicates: {dataset_info.duplicates}")
    print(f"   Data types: {len(dataset_info.data_types)}")
    
    # 5. Initialize Project
    print("\n🔧 Step 4: Project Initialization")
    print("-" * 30)
    
    initializer = ProjectInitializer("ai_video_generation", project_dir)
    summary = initializer.initialize_project(
        problem_def=problem_def,
        data_path=sample_data_dir,
        target_column=None,
        enable_tracking=True
    )
    
    print(f"✅ Project initialization complete")
    print(f"   Project structure created")
    print(f"   Experiment tracking enabled")
    print(f"   Baseline configuration generated")
    
    # 6. Display Results
    print("\n📈 Step 5: Project Summary")
    print("-" * 30)
    
    print(f"Project Name: {summary['project_name']}")
    print(f"Initialization Date: {summary['initialization_date']}")
    print(f"Problem Type: {summary['problem_definition']['problem_type']}")
    print(f"Dataset Size: {summary['dataset_info']['size']} samples")
    print(f"Features: {len(summary['dataset_info']['features'])}")
    
    print("\n📋 Next Steps:")
    for i, step in enumerate(summary['next_steps'], 1):
        print(f"   {i}. {step}")
    
    # 7. Show Generated Files
    print("\n📄 Generated Files:")
    print("-" * 30)
    
    generated_files = [
        "problem_definition.json",
        "project_summary.json", 
        "dataset_analysis/basic_stats.json",
        "dataset_analysis/data_quality_report.json",
        "dataset_analysis/feature_analysis.json",
        "dataset_analysis/dataset_info.json",
        "configs/baseline_config.json"
    ]
    
    for file_path in generated_files:
        full_path = project_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (not found)")
    
    # 8. Cleanup
    initializer.cleanup()
    
    print("\n🎉 Project initialization complete!")
    print(f"📁 Check the project directory: {project_dir}")
    print(f"📊 View analysis reports in: {project_dir}/dataset_analysis")
    print(f"⚙️  Check configuration in: {project_dir}/configs")
    
    return project_dir


def example_using_template():
    """Example: Using the template system"""
    
    print("\n🔧 Using Project Template")
    print("=" * 60)
    
    template_project_dir = Path("examples/template_project")
    
    try:
        create_project_from_template(
            project_name="template_ai_video",
            project_dir=template_project_dir,
            template_type='ai_video'
        )
        print(f"✅ Template project created: {template_project_dir}")
    except Exception as e:
        print(f"❌ Template creation failed: {e}")


def main():
    """Main function to run the examples."""
    
    print("🎯 Project Initialization Examples")
    print("=" * 60)
    
    # Run the main example
    project_dir = example_ai_video_project()
    
    # Run template example
    example_using_template()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("\n📚 What was demonstrated:")
    print("   • Clear problem definition with structured approach")
    print("   • Comprehensive dataset analysis and validation")
    print("   • Automated project structure creation")
    print("   • Experiment tracking setup (TensorBoard + wandb)")
    print("   • Baseline configuration generation")
    print("   • Template-based project creation")
    
    print("\n🚀 Next steps for your project:")
    print("   1. Review the generated problem_definition.json")
    print("   2. Examine dataset_analysis/ for insights")
    print("   3. Customize baseline_config.json for your needs")
    print("   4. Start building your models!")
    
    return project_dir


if __name__ == "__main__":
    main() 