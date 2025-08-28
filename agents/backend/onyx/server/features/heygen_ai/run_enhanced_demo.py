#!/usr/bin/env python3
"""
Enhanced HeyGen AI Demo
========================

Demonstrates all the new advanced features:
- Advanced body animation system
- Real-time expression controller
- Advanced accent and dialect system
- Enhanced performance optimizer
- Unified integration manager
"""

import asyncio
import logging
import time
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_body_animation():
    """Demo the advanced body animation system."""
    print("\n" + "="*60)
    print("🎭 ADVANCED BODY ANIMATION DEMO")
    print("="*60)
    
    try:
        from core.advanced_body_animation import AdvancedBodyAnimationService, GestureConfig
        
        # Initialize service
        body_anim_service = AdvancedBodyAnimationService()
        
        # Test script analysis
        test_script = "Hello everyone! Welcome to our presentation. First, let me point out the key features. Second, I want to emphasize the importance. Finally, let me wave goodbye!"
        
        print(f"📝 Analyzing script: {test_script}")
        gestures = await body_anim_service.analyze_script_for_gestures(test_script)
        print(f"✅ Found {len(gestures)} gestures:")
        
        for i, gesture in enumerate(gestures):
            print(f"   {i+1}. {gesture.gesture_type.value} (intensity: {gesture.intensity}, duration: {gesture.duration}s)")
        
        # Generate animation sequence
        print("\n🎬 Generating body animation sequence...")
        animation_sequence = await body_anim_service.generate_body_animation_sequence(
            gestures, "excited", "realistic"
        )
        
        print(f"✅ Generated animation sequence:")
        print(f"   - ID: {animation_sequence.sequence_id}")
        print(f"   - Total poses: {len(animation_sequence.poses)}")
        print(f"   - Duration: {animation_sequence.total_duration:.2f}s")
        print(f"   - Emotion: {animation_sequence.metadata.get('emotion', 'unknown')}")
        
        # Export animation
        print("\n📤 Exporting animation sequence...")
        json_export = await body_anim_service.export_animation_sequence(animation_sequence, "json")
        print(f"✅ Exported {len(json_export)} characters to JSON")
        
        # Get statistics
        stats = await body_anim_service.get_animation_statistics()
        print(f"\n📊 Animation Statistics:")
        print(f"   - Total sequences: {stats['total_sequences']}")
        print(f"   - Total poses: {stats['total_poses']}")
        print(f"   - Supported gestures: {len(stats['supported_gestures'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Body animation demo failed: {e}")
        return False

async def demo_expression_controller():
    """Demo the real-time expression controller."""
    print("\n" + "="*60)
    print("😊 REAL-TIME EXPRESSION CONTROLLER DEMO")
    print("="*60)
    
    try:
        from core.advanced_expression_controller import AdvancedExpressionController, EmotionType
        
        # Initialize controller
        expr_controller = AdvancedExpressionController()
        
        # Test emotion analysis
        test_script = "I'm so happy to see you! This is amazing news. But I'm also a bit worried about the future. What do you think?"
        
        print(f"📝 Analyzing emotions in script: {test_script}")
        emotions = await expr_controller.analyze_text_emotion(test_script)
        print(f"✅ Found {len(emotions)} emotions:")
        
        for i, (emotion_type, intensity, timestamp) in enumerate(emotions):
            print(f"   {i+1}. {emotion_type.value} (intensity: {intensity:.2f}, at {timestamp:.2f}s)")
        
        # Generate expression sequence
        print("\n🎭 Generating facial expression sequence...")
        expression_sequence = await expr_controller.generate_expression_sequence(emotions)
        
        print(f"✅ Generated expression sequence:")
        print(f"   - ID: {expression_sequence['sequence_id']}")
        print(f"   - Total poses: {len(expression_sequence['poses'])}")
        print(f"   - Duration: {expression_sequence['total_duration']:.2f}s")
        
        # Get current expression
        current_expr = await expr_controller.get_current_expression()
        print(f"\n😊 Current facial expression:")
        print(f"   - Timestamp: {current_expr.timestamp}")
        print(f"   - Overall tension: {current_expr.overall_tension:.2f}")
        
        # Get statistics
        stats = await expr_controller.get_expression_statistics()
        print(f"\n📊 Expression Statistics:")
        print(f"   - Total sequences: {stats['total_sequences']}")
        print(f"   - Current emotion: {stats['current_emotion']}")
        print(f"   - Current intensity: {stats['current_intensity']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Expression controller demo failed: {e}")
        return False

async def demo_accent_system():
    """Demo the advanced accent and dialect system."""
    print("\n" + "="*60)
    print("🗣️ ADVANCED ACCENT & DIALECT SYSTEM DEMO")
    print("="*60)
    
    try:
        from core.advanced_accent_system import AdvancedAccentSystem, AccentRegion, DialectType
        
        # Initialize system
        accent_system = AdvancedAccentSystem()
        
        # Test accent generation
        test_script = "Hello, how are you today? I would like to welcome you to our presentation."
        
        print(f"📝 Original script: {test_script}")
        
        # Generate different accent profiles
        accents_to_test = [
            (AccentRegion.BRITISH_RP, DialectType.FORMAL, 1.0),
            (AccentRegion.AMERICAN_SOUTHERN, DialectType.INFORMAL, 1.2),
            (AccentRegion.AUSTRALIAN, DialectType.CASUAL, 0.8),
            (AccentRegion.INDIAN, DialectType.FORMAL, 1.0)
        ]
        
        for region, dialect, intensity in accents_to_test:
            print(f"\n🌍 Testing {region.value} accent ({dialect.value}, intensity: {intensity}):")
            
            # Generate accent profile
            accent_profile = await accent_system.generate_accent_profile(region, dialect, intensity)
            print(f"   ✅ Generated profile: {accent_profile.accent_id}")
            
            # Apply accent to text
            modified_text = await accent_system.apply_accent_to_text(test_script, accent_profile)
            print(f"   📝 Modified text: {modified_text}")
            
            # Get voice parameters
            voice_params = await accent_system.generate_voice_parameters(accent_profile)
            print(f"   🎤 Voice parameters: pitch={voice_params.get('pitch', 1.0):.2f}, speed={voice_params.get('speed', 1.0):.2f}")
        
        # Test accent blending
        print(f"\n🔄 Testing accent blending...")
        british_profile = await accent_system.generate_accent_profile(AccentRegion.BRITISH_RP, DialectType.FORMAL)
        american_profile = await accent_system.generate_accent_profile(AccentRegion.AMERICAN_GENERAL, DialectType.INFORMAL)
        
        blended_profile = await accent_system.create_accent_blend(british_profile, american_profile, 0.7)
        print(f"   ✅ Created blended accent: {blended_profile.accent_id}")
        
        # Get statistics
        stats = await accent_system.get_accent_statistics()
        print(f"\n📊 Accent System Statistics:")
        print(f"   - Total regions: {stats['total_regions']}")
        print(f"   - Total dialect types: {stats['total_dialect_types']}")
        print(f"   - Available profiles: {stats['available_profiles']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Accent system demo failed: {e}")
        return False

async def demo_performance_optimizer():
    """Demo the enhanced performance optimizer."""
    print("\n" + "="*60)
    print("⚡ ENHANCED PERFORMANCE OPTIMIZER DEMO")
    print("="*60)
    
    try:
        from core.enhanced_performance_optimizer import EnhancedPerformanceOptimizer, CacheLevel, LoadBalancingStrategy, ServerNode
        
        # Initialize optimizer
        config = {
            "l1_max_size": 100,
            "l2_max_size": 500,
            "l3_max_size": 1000,
            "max_workers": 5
        }
        perf_optimizer = EnhancedPerformanceOptimizer(config)
        
        # Test caching
        print("💾 Testing multi-level caching...")
        
        # Set values at different levels
        await perf_optimizer.set_cached_value("test_l1", "L1 value", level=CacheLevel.L1_MEMORY)
        await perf_optimizer.set_cached_value("test_l2", "L2 value", level=CacheLevel.L2_REDIS)
        await perf_optimizer.set_cached_value("test_l3", "L3 value", level=CacheLevel.L3_CDN)
        
        print("   ✅ Set values at all cache levels")
        
        # Retrieve values
        l1_value = await perf_optimizer.get_cached_value("test_l1")
        l2_value = await perf_optimizer.get_cached_value("test_l2")
        l3_value = await perf_optimizer.get_cached_value("test_l3")
        
        print(f"   📥 Retrieved values: L1='{l1_value}', L2='{l2_value}', L3='{l3_value}'")
        
        # Test load balancing
        print("\n⚖️ Testing load balancing...")
        
        # Add server nodes
        nodes = [
            ServerNode("server1", "http://server1.com", weight=1.0, max_connections=100),
            ServerNode("server2", "http://server2.com", weight=1.5, max_connections=150),
            ServerNode("server3", "http://server3.com", weight=0.8, max_connections=80)
        ]
        
        for node in nodes:
            await perf_optimizer.add_server_node(node)
        
        print(f"   ✅ Added {len(nodes)} server nodes")
        
        # Test different load balancing strategies
        strategies = [
            LoadBalancingStrategy.ROUND_ROBIN,
            LoadBalancingStrategy.LEAST_CONNECTIONS,
            LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN,
            LoadBalancingStrategy.ADAPTIVE
        ]
        
        for strategy in strategies:
            server = await perf_optimizer.get_next_server(strategy)
            if server:
                print(f"   🎯 {strategy.value}: {server.id} (weight: {server.weight})")
        
        # Test background tasks
        print("\n🔄 Testing background task processing...")
        
        def sample_task(name, delay):
            time.sleep(delay)
            return f"Task {name} completed"
        
        task_ids = []
        for i in range(3):
            task_id = await perf_optimizer.submit_background_task(sample_task, f"demo_{i}", 1)
            task_ids.append(task_id)
            print(f"   📋 Submitted task: {task_id}")
        
        # Wait for tasks to complete
        print("   ⏳ Waiting for tasks to complete...")
        await asyncio.sleep(3)
        
        # Get performance statistics
        print("\n📊 Getting performance statistics...")
        stats = await perf_optimizer.get_performance_statistics()
        
        print(f"   📈 Cache statistics:")
        for level, level_stats in stats['cache_statistics'].items():
            print(f"      {level}: {level_stats['size']}/{level_stats['max_size']} ({level_stats['utilization']:.1%})")
        
        print(f"   🖥️ Load balancer: {stats['load_balancer_statistics']['active_nodes']}/{stats['load_balancer_statistics']['total_nodes']} nodes active")
        print(f"   👷 Workers: {stats['worker_statistics']['active_workers']}/{stats['worker_statistics']['total_workers']} workers active")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance optimizer demo failed: {e}")
        return False

async def demo_integration_manager():
    """Demo the enhanced integration manager."""
    print("\n" + "="*60)
    print("🔗 ENHANCED INTEGRATION MANAGER DEMO")
    print("="*60)
    
    try:
        from core.enhanced_integration_manager import EnhancedIntegrationManager, EnhancedVideoRequest, AccentRegion, DialectType
        
        # Initialize manager
        config = {
            "performance": {
                "l1_max_size": 200,
                "l2_max_size": 1000,
                "max_workers": 8
            }
        }
        integration_manager = EnhancedIntegrationManager(config)
        
        # Test integration status
        print("📊 Getting integration status...")
        status = await integration_manager.get_integration_status()
        
        print(f"   ✅ Integration status: {status['integration_status']}")
        print(f"   🎯 Features available: {len(status['features_available'])}")
        print(f"   📈 Performance metrics: {status['performance_metrics']['total_requests']} requests")
        
        # Test service health
        print("\n🏥 Testing service health...")
        health = await integration_manager.get_service_health()
        
        print(f"   📊 Overall health: {health['overall']['status']}")
        print(f"   💚 Healthy services: {health['overall']['healthy_services']}/{health['overall']['total_services']}")
        print(f"   📊 Health percentage: {health['overall']['health_percentage']:.1f}%")
        
        # Test enhanced video generation
        print("\n🎬 Testing enhanced video generation...")
        
        request = EnhancedVideoRequest(
            script_text="Hello everyone! Welcome to our amazing presentation. I'm so excited to share this with you!",
            accent_region=AccentRegion.BRITISH_RP,
            dialect_type=DialectType.FORMAL,
            accent_intensity=1.2,
            enable_body_animation=True,
            enable_facial_expressions=True,
            enable_caching=True,
            background_processing=True
        )
        
        print(f"   📝 Script: {request.script_text}")
        print(f"   🌍 Accent: {request.accent_region.value}")
        print(f"   🎭 Features: {', '.join(['body_animation', 'facial_expressions', 'accent_system', 'caching', 'background_processing'])}")
        
        result = await integration_manager.generate_enhanced_video(request)
        
        if result.success:
            print(f"   ✅ Video generation successful!")
            print(f"   ⏱️ Processing time: {result.processing_time:.2f}s")
            print(f"   🎬 Animation data: {'Yes' if result.animation_data else 'No'}")
            print(f"   😊 Expression data: {'Yes' if result.expression_data else 'No'}")
            print(f"   🗣️ Accent data: {'Yes' if result.accent_data else 'No'}")
            print(f"   📊 Performance metrics: {'Yes' if result.performance_metrics else 'No'}")
        else:
            print(f"   ❌ Video generation failed: {result.error_message}")
        
        # Test integration
        print("\n🧪 Testing full integration...")
        test_results = await integration_manager.test_integration()
        
        print(f"   📊 Test results:")
        for service, result in test_results.items():
            if service != "overall":
                status_icon = "✅" if result["status"] == "success" else "❌"
                print(f"      {status_icon} {service}: {result['status']}")
        
        overall = test_results["overall"]
        print(f"   🎯 Overall: {overall['services_passed']}/{overall['services_tested']} services passed")
        
        # Get final statistics
        final_status = await integration_manager.get_integration_status()
        print(f"\n📈 Final Statistics:")
        print(f"   - Total requests: {final_status['performance_metrics']['total_requests']}")
        print(f"   - Success rate: {final_status['performance_metrics']['success_rate']:.1%}")
        print(f"   - Average processing time: {final_status['performance_metrics']['average_processing_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration manager demo failed: {e}")
        return False

async def main():
    """Run all demos."""
    print("🚀 ENHANCED HEYGEN AI SYSTEM DEMO")
    print("="*60)
    print("This demo showcases all the new advanced features:")
    print("• Advanced Body Animation System")
    print("• Real-time Expression Controller")
    print("• Advanced Accent & Dialect System")
    print("• Enhanced Performance Optimizer")
    print("• Unified Integration Manager")
    print("="*60)
    
    # Run all demos
    demos = [
        ("Body Animation", demo_body_animation),
        ("Expression Controller", demo_expression_controller),
        ("Accent System", demo_accent_system),
        ("Performance Optimizer", demo_performance_optimizer),
        ("Integration Manager", demo_integration_manager)
    ]
    
    results = []
    for name, demo_func in demos:
        try:
            print(f"\n🔄 Starting {name} demo...")
            result = await demo_func()
            results.append((name, result))
            
            if result:
                print(f"✅ {name} demo completed successfully!")
            else:
                print(f"❌ {name} demo failed!")
                
        except Exception as e:
            print(f"❌ {name} demo crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEMO SUMMARY")
    print("="*60)
    
    successful_demos = sum(1 for _, result in results if result)
    total_demos = len(results)
    
    for name, result in results:
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {name}")
    
    print(f"\n🎯 Overall: {successful_demos}/{total_demos} demos successful ({successful_demos/total_demos*100:.1f}%)")
    
    if successful_demos == total_demos:
        print("🎉 All demos completed successfully! The enhanced HeyGen AI system is working perfectly.")
    else:
        print("⚠️ Some demos failed. Please check the error messages above.")
    
    print("\n🚀 Enhanced HeyGen AI System Demo Complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n💥 Demo crashed: {e}")
        import traceback
        traceback.print_exc()
