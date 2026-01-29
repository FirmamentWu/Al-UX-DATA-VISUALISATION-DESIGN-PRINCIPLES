# Airbnb Price Analysis Project

A comprehensive analysis of Airbnb listing prices, identifying key factors that influence pricing across multiple cities.

## Project Overview

This project analyzes Airbnb listing data to identify patterns in pricing behavior. The analysis is conducted in two phases:

1. **NYC Analysis**: Deep dive into New York City data to identify 5 core pricing patterns
2. **Multi-City Validation**: Validate these patterns across 11 international cities to assess generalizability

## Project Structure

```
airbnb_analysis/
├── config/              # Configuration module
│   ├── settings.py      # Configuration parameters
│   └── constants.py     # Constant definitions
├── data/                # Data processing
│   ├── loader.py        # Data loading (NYC)
│   ├── preprocessor.py  # Data preprocessing (NYC)
│   ├── cleaner.py       # Data cleaning (based on notebook)
│   ├── adapter.py       # Column name standardization
│   ├── multi_city_loader.py  # Multi-city data loading
│   └── raw/             # Raw data files
├── models/              # Model module
│   ├── statistical_tests.py  # Statistical tests
│   ├── regression.py    # Regression models
│   └── smoothing.py     # Non-parametric smoothing
├── visualization/       # Visualization
│   └── style.py         # Plot styling
├── analysis/            # Analysis scenarios
│   ├── scenario1_physical_space.py    # Scenario 1: Physical space premium
│   ├── scenario2_location.py         # Scenario 2: Location premium
│   ├── scenario3_scale.py            # Scenario 3: Scale premium
│   ├── scenario4_trust.py            # Scenario 4: Trust monetization
│   ├── scenario5_activity.py         # Scenario 5: Activity signals
│   ├── comprehensive_model.py         # Comprehensive model
│   ├── multi_city_analysis.py        # Multi-city analysis framework
│   ├── cross_city_comparison.py      # Cross-city comparison
│   └── generalizability_visualization.py  # Generalizability visualization
├── utils/               # Utility functions
│   ├── dependencies.py  # Dependency management
│   └── validate_results.py  # Result validation
├── notebooks/           # Jupyter Notebooks
│   └── Data Cleaning and Feature Engineering.ipynb
├── docs/                # Documentation
│   ├── comprehensive_analysis_report.md  # Comprehensive report
│   ├── multi_city_validation_report.md
│   ├── 分析结果总结.md
│   └── 跨城市分析结果报告.md
├── outputs/            # Output directory
│   ├── figures/         # Generated charts (22 PNG files)
│   ├── multi_city_results/  # Multi-city analysis results
│   └── validation/      # Validation results
├── README.md            # Project documentation
└── requirements.txt     # Dependencies

../main.py               # NYC analysis entry point
../multi_city_main.py    # Multi-city analysis entry point
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run NYC Analysis
```bash
python main.py
```

This will:
- Load and preprocess NYC data
- Run 5 scenario analyses
- Generate comprehensive price model
- Save 19 charts to `airbnb_analysis/outputs/figures/`

### Run Multi-City Analysis
```bash
python multi_city_main.py
```

This will:
- Load data from 11 cities
- Run the same 5 scenario analyses for each city
- Compare results across cities
- Generate generalizability visualizations
- Save results to `airbnb_analysis/outputs/multi_city_results/`

## Analysis Scenarios

### Scenario 1: Physical Space Premium
- Privacy premium: Entire home vs Private room
- Capacity premium: Price increase per additional person
- Interaction effects: Room type × capacity

### Scenario 2: Location Premium
- Spatial price heatmap
- Regional price comparison
- Sub-regional price jumps
- Controlled location premium

### Scenario 3: Scale Premium
- Host scale vs price
- Host scale vs occupancy
- Entire home specialization

### Scenario 4: Trust Monetization
- Rating distribution and threshold effects
- Rating vs occupancy
- Superhost comparison

### Scenario 5: Activity Signals
- Historical vs LTM reviews decoupling
- LTM reviews vs price
- Historical reviews vs price
- LTM reviews vs occupancy

## Generated Charts

### NYC Analysis Charts (19 charts)
- **Scenario 1**: 3 charts (privacy premium, capacity premium, interaction effect)
- **Scenario 2**: 4 charts (spatial heatmap, region comparison, subregions, controlled premium)
- **Scenario 3**: 4 charts (scale vs price, scale vs occupancy, entire home scale, specialization)
- **Scenario 4**: 3 charts (rating distribution, rating vs occupancy, superhost)
- **Scenario 5**: 4 charts (reviews decoupling, LTM vs price, historical vs price, LTM vs occupancy)
- **Comprehensive Model**: 1 chart (price prediction model)

### Multi-City Validation Charts (3 charts)
- `generalizability_validation.png`: Main generalizability chart showing validation status for each pattern
- `validation_method_matrix.png`: Statistical significance matrix across all cities
- `effect_consistency.png`: Effect size consistency across cities

## Key Findings

1. **Physical space premium is universal**: Capacity and privacy premiums are significant across all 11 validation cities
2. **Location premium exists but data-limited**: Core area premiums are significant in validated cities, but some cities lack regional data
3. **Scale premium is universal in price dimension**: Multi-listing host price premiums are significant in 90.9% of cities
4. **Trust can be monetized**: Ratings and superhost status translate to price premiums universally
5. **Activity is a real-time demand signal**: LTM review counts as demand signals show significant relationships with price and occupancy across all cities

## Documentation

- **Comprehensive Report**: `docs/comprehensive_analysis_report.md` - Complete analysis report integrating NYC and multi-city results
- **Project Structure**: `PROJECT_STRUCTURE.md` - Detailed project structure documentation

## Data Sources

- **NYC Data**: Inside Airbnb (cleaned version)
- **Multi-City Data**: Inside Airbnb (11 cities: Albany, Amsterdam, Antwerp, Asheville, Athens, Austin, Bangkok, Barcelona, Barossa Valley, Barwon South West Vic, Belize)

## Statistical Methods

- **Non-parametric tests**: Mann-Whitney U, Kruskal-Wallis (robust to non-normal distributions)
- **Correlation analysis**: Spearman rank correlation (monotonic relationships)
- **Regression models**: Linear, interaction effects, log-linear
- **Non-parametric smoothing**: LOWESS, KDE

## License

This project is for research and educational purposes.
