#!/usr/bin/env python3
"""
AgroPro Phase-2 Pipeline Runner
===============================
End-to-end execution script for the AI Crop Planning & Resource Optimization Engine.

This script:
1. Loads data from approved input files
2. Trains yield prediction model
3. Trains price prediction model
4. Runs crop optimization
5. Executes sample scenarios
6. Generates evaluation reports

Usage:
    python run_pipeline.py

Author: AgroPro ML Team
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
SRC_DIR = Path(__file__).parent / "src"
sys.path.insert(0, str(SRC_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("AgroPro")

# ============================================================================
# CONFIGURATION
# ============================================================================
RANDOM_STATE = 42
TEST_DISTRICT = "Guntur"
TEST_SEASON = "Kharif"


def print_banner():
    """Print pipeline banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🌾 AgroPro Phase-2 Modeling Pipeline 🌾                  ║
    ║     AI Crop Planning & Resource Optimization Engine          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def step_1_load_data():
    """Step 1: Load and validate all input data."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 1: LOADING DATA")
    logger.info("=" * 60)
    
    from data_loader import load_all_data, load_master_training_table
    
    # Load all datasets
    data = load_all_data()
    
    # Check critical data
    master_df = data.get("master_training")
    if master_df is None:
        raise RuntimeError("Failed to load master training table - cannot proceed")
    
    logger.info(f"✓ Master training table: {len(master_df):,} rows")
    
    # Log data summary
    for name, df in data.items():
        if df is not None:
            logger.info(f"  ✓ {name}: {len(df):,} rows × {len(df.columns)} cols")
        else:
            logger.warning(f"  ✗ {name}: not available")
    
    return data


def step_2_train_yield_model(data):
    """Step 2: Train yield prediction model."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: TRAINING YIELD MODEL")
    logger.info("=" * 60)
    
    from feature_builder import FeatureBuilder
    from train_yield_model import train_yield_model, save_yield_model
    
    master_df = data["master_training"]
    
    # Build features
    logger.info("Building features...")
    builder = FeatureBuilder(random_state=RANDOM_STATE)
    df_processed, feature_cols = builder.build_features(master_df)
    X, y, feature_names = builder.get_feature_matrix(df_processed)
    
    # Train model
    logger.info("Training models...")
    best_model, results = train_yield_model(X, y, feature_names)
    
    # Save model and artifacts
    save_yield_model(best_model, results, feature_names)
    builder.save_artifacts()
    
    logger.info(f"✓ Best model: {results['summary']['best_model']}")
    logger.info(f"✓ Test R²: {results['summary']['best_test_r2']:.4f}")
    
    return best_model, builder, results


def step_3_train_price_model(data):
    """Step 3: Train price prediction model."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: TRAINING PRICE MODEL")
    logger.info("=" * 60)
    
    from train_price_model import train_price_model, create_synthetic_price_data
    
    price_df = data.get("commodity_price")
    
    if price_df is None:
        logger.warning("No real price data available, using synthetic data for demo")
        price_df = create_synthetic_price_data()
    
    # Train price model
    trainer, metrics = train_price_model(price_df)
    
    logger.info(f"✓ Test R²: {metrics['test_metrics']['R2']:.4f}")
    logger.info(f"✓ Test RMSE: {metrics['test_metrics']['RMSE']:.2f}")
    
    return trainer, metrics


def step_4_build_optimizer(yield_model, feature_builder, price_trainer):
    """Step 4: Initialize crop optimizer."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: BUILDING CROP OPTIMIZER")
    logger.info("=" * 60)
    
    from crop_optimizer import CropOptimizer
    
    optimizer = CropOptimizer(
        yield_model=yield_model,
        price_model=price_trainer,
        feature_builder=feature_builder,
    )
    
    logger.info("✓ Crop optimizer initialized")
    
    return optimizer


def step_5_run_optimization(optimizer):
    """Step 5: Run sample crop optimization."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 5: RUNNING CROP OPTIMIZATION")
    logger.info("=" * 60)
    
    from crop_optimizer import get_default_candidate_crops
    
    # Sample climate features (representative values)
    climate_features = {
        "rainfall_mean": 110,
        "rainfall_anomaly": -0.1,
        "monsoon_rainfall": 820,
        "avg_temp_mean": 28.5,
        "heatwave_count": 2,
        "growing_degree_days": 15.5,
    }
    
    soil_features = {
        "soil_quality_index": 0.85,
    }
    
    # Get top crops
    top_crops = optimizer.optimize(
        district=TEST_DISTRICT,
        season=TEST_SEASON,
        candidate_crops=get_default_candidate_crops(),
        climate_features=climate_features,
        soil_features=soil_features,
        top_n=5,
    )
    
    logger.info(f"\n✓ Top {len(top_crops)} crops for {TEST_DISTRICT} - {TEST_SEASON}:")
    for i, score in enumerate(top_crops, 1):
        logger.info(f"  {i}. {score.crop_name}: Score={score.composite_score:.3f}")
    
    return top_crops


def step_6_run_scenarios(optimizer):
    """Step 6: Run scenario simulations."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 6: RUNNING SCENARIO SIMULATIONS")
    logger.info("=" * 60)
    
    from scenario_simulator import ScenarioSimulator, SCENARIOS
    
    simulator = ScenarioSimulator(optimizer=optimizer)
    
    # Base conditions
    base_climate = {
        "rainfall_mean": 110,
        "rainfall_anomaly": 0.0,
        "monsoon_rainfall": 820,
        "avg_temp_mean": 28.5,
        "heatwave_count": 1,
        "growing_degree_days": 15.5,
    }
    
    soil_features = {
        "soil_quality_index": 0.85,
    }
    
    # Run scenarios
    scenarios_to_test = ["baseline", "drought_moderate", "warming_moderate"]
    
    results = simulator.run_multiple_scenarios(
        district=TEST_DISTRICT,
        season=TEST_SEASON,
        base_climate=base_climate,
        soil_features=soil_features,
        scenario_names=scenarios_to_test,
        top_n=3,
    )
    
    # Print scenario results
    for scenario_name, result in results.items():
        logger.info(f"\n📊 Scenario: {result.scenario.name}")
        if result.scenario.description:
            logger.info(f"   Description: {result.scenario.description}")
        
        logger.info("   Top crops:")
        for i, score in enumerate(result.crop_rankings, 1):
            change_str = ""
            if score.crop_name in result.ranking_changes:
                change = result.ranking_changes[score.crop_name]
                if change > 0:
                    change_str = f" ↑{change}"
                elif change < 0:
                    change_str = f" ↓{abs(change)}"
            
            logger.info(f"   {i}. {score.crop_name}{change_str}: "
                       f"Score={score.composite_score:.3f}")
    
    return results


def step_7_generate_reports(yield_results, price_metrics):
    """Step 7: Generate evaluation reports."""
    logger.info("\n" + "=" * 60)
    logger.info("STEP 7: GENERATING REPORTS")
    logger.info("=" * 60)
    
    from evaluate_models import evaluate_models, print_model_summary
    
    # Generate comprehensive report
    report = evaluate_models()
    
    # Print summary
    print_model_summary(report)
    
    logger.info("✓ Reports generated in reports/ directory")
    
    return report


def print_final_summary(top_crops, scenario_results):
    """Print final pipeline summary."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    PIPELINE COMPLETE                         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"🎯 TOP CROP RECOMMENDATIONS for {TEST_DISTRICT} - {TEST_SEASON}")
    print("-" * 50)
    
    for i, score in enumerate(top_crops[:3], 1):
        print(f"""
    {i}. {score.crop_name}
       ├── Composite Score: {score.composite_score:.3f}
       ├── Predicted Yield: {score.predicted_yield:.2f} tonnes/ha
       ├── Predicted Price: ₹{score.predicted_price:,.0f}/tonne
       └── Expected Revenue: ₹{score.predicted_revenue:,.0f}/ha
""")
    
    print("\n📊 SCENARIO IMPACT SUMMARY")
    print("-" * 50)
    
    baseline_top = None
    for name, result in scenario_results.items():
        if name == "baseline":
            baseline_top = result.crop_rankings[0].crop_name if result.crop_rankings else "N/A"
            print(f"  Baseline: Top crop = {baseline_top}")
        else:
            scenario_top = result.crop_rankings[0].crop_name if result.crop_rankings else "N/A"
            print(f"  {result.scenario.name}: Top crop = {scenario_top}")
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   OUTPUT FILES CREATED                        ║
╠══════════════════════════════════════════════════════════════╣
║  models/yield_model.pkl      - Trained yield prediction model ║
║  models/price_model.pkl      - Trained price prediction model ║
║  artifacts/yield_features.json - Yield model feature info     ║
║  artifacts/price_features.json - Price model feature info     ║
║  reports/model_metrics.json  - Complete evaluation metrics    ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    """Main pipeline execution."""
    start_time = datetime.now()
    
    print_banner()
    
    try:
        # Step 1: Load data
        data = step_1_load_data()
        
        # Step 2: Train yield model
        yield_model, feature_builder, yield_results = step_2_train_yield_model(data)
        
        # Step 3: Train price model
        price_trainer, price_metrics = step_3_train_price_model(data)
        
        # Step 4: Build optimizer
        optimizer = step_4_build_optimizer(yield_model, feature_builder, price_trainer)
        
        # Step 5: Run optimization
        top_crops = step_5_run_optimization(optimizer)
        
        # Step 6: Run scenarios
        scenario_results = step_6_run_scenarios(optimizer)
        
        # Step 7: Generate reports
        report = step_7_generate_reports(yield_results, price_metrics)
        
        # Final summary
        print_final_summary(top_crops, scenario_results)
        
        # Execution time
        elapsed = datetime.now() - start_time
        logger.info(f"\n⏱️  Total execution time: {elapsed.total_seconds():.1f} seconds")
        logger.info("✅ Pipeline completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
