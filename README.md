# Airbnb Price Analysis: Multi-City Generalizability Study

A comprehensive data analysis project that identifies key factors influencing Airbnb listing prices and validates their generalizability across multiple international cities.

## Project Overview

This project conducts a two-phase analysis:

1. **NYC Analysis**: Deep dive into New York City data to identify 5 core pricing patterns
2. **Multi-City Validation**: Validate these patterns across 11 international cities to assess generalizability

**Research Question**: Are the pricing patterns found in NYC data generalizable to other cities worldwide?

## Team / 团队

- **Team Name / 团队名称**: 6002组队
- **Main Contributor / 主要完成人**: 武翔宇 (WU XIANGYU)
- **Early Research & Product Design / 项目初期调研与产品设计**: 吴丽芳 (WU LIFANG)
- **Other Contributors / 其他贡献者**: 吴磊 (WU LEI), 吴欣阔 (WU XINKUO)

## Key Findings

### Universal Patterns (100% cities significant)
- ✅ **Physical Space Premium**: Capacity and privacy premiums are significant across all 11 validation cities
- ✅ **Activity Signals**: LTM and historical review counts show significant relationships with price across all cities

### High Generalizability (80-99% cities significant)
- ✅ **Scale Price Premium**: 90.9% of cities show significant scale effects
- ✅ **Superhost Premium**: 90.9% of cities show significant superhost effects
- ✅ **Rating-Occupancy Relationship**: 81.8% of cities show significant relationships

### Location-Specific Patterns
- ⚠️ **Region Comparison**: Limited to cities with regional data (2/11 cities have data)
- ⚠️ **Scale Occupancy Premium**: 72.7% of cities show significant effects (some regional variation)

## Project Structure

```
.
├── main.py                      # NYC analysis entry point
├── multi_city_main.py           # Multi-city analysis entry point
├── README.md                    # This file
│
└── airbnb_analysis/
    ├── config/                  # Configuration module
    │   ├── settings.py         # Paths, figure settings, analysis parameters
    │   └── constants.py        # Feature mappings, scenario names, city names
    │
    ├── data/                    # Data processing
    │   ├── loader.py           # NYC data loading
    │   ├── preprocessor.py     # NYC data preprocessing
    │   ├── cleaner.py          # Data cleaning (based on notebook logic)
    │   ├── adapter.py          # Column name standardization
    │   ├── multi_city_loader.py # Multi-city data loading
    │   └── raw/                # Raw data files
    │       ├── listings_2_cleaned 4.0.csv  # NYC cleaned data
    │       └── *listings.csv.gz            # 11 cities compressed data
    │
    ├── models/                  # Statistical models
    │   ├── statistical_tests.py  # Mann-Whitney U, Kruskal-Wallis, Spearman
    │   ├── regression.py       # Linear, interaction, log-linear models
    │   └── smoothing.py        # LOWESS, KDE
    │
    ├── analysis/               # Analysis scenarios
    │   ├── scenario1_physical_space.py    # Privacy & capacity premium
    │   ├── scenario2_location.py         # Location premium
    │   ├── scenario3_scale.py            # Scale premium
    │   ├── scenario4_trust.py            # Trust monetization
    │   ├── scenario5_activity.py         # Activity signals
    │   ├── comprehensive_model.py        # Price prediction model
    │   ├── multi_city_analysis.py        # Multi-city analysis framework
    │   ├── cross_city_comparison.py      # Cross-city comparison
    │   └── generalizability_visualization.py  # Generalizability charts
    │
    ├── visualization/          # Visualization
    │   └── style.py           # Plot styling and figure saving
    │
    ├── utils/                  # Utilities
    │   ├── dependencies.py   # Dependency management
    │   └── validate_results.py # Result validation
    │
    ├── notebooks/             # Jupyter Notebooks
    │   └── Data Cleaning and Feature Engineering.ipynb
    │
    ├── docs/                  # Documentation
    │   ├── comprehensive_analysis_report.md  # Complete analysis report
    │   ├── multi_city_validation_report.md
    │   ├── 分析结果总结.md
    │   └── 跨城市分析结果报告.md
    │
    ├── outputs/               # Output directory
    │   ├── figures/           # Generated charts (22 PNG files)
    │   ├── multi_city_results/  # Multi-city analysis results (JSON)
    │   └── validation/        # Validation results
    │
    ├── PROJECT_STRUCTURE.md   # Detailed project structure
    ├── README.md              # Project documentation
    └── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone git@github.com-personal:FirmamentWu/Al-UX-DATA-VISUALISATION-DESIGN-PRINCIPLES.git
cd Al-UX-DATA-VISUALISATION-DESIGN-PRINCIPLES
```

2. Install dependencies:
```bash
cd airbnb_analysis
pip install -r requirements.txt
```

The project will automatically install missing dependencies when you run the analysis scripts.

## Usage

### Run NYC Analysis

Analyze New York City data to identify pricing patterns:

```bash
python main.py
```

**Output:**
- 19 charts saved to `airbnb_analysis/outputs/figures/`
- Validation results saved to `airbnb_analysis/outputs/validation/`

### Run Multi-City Analysis

Validate NYC patterns across 11 international cities:

```bash
python multi_city_main.py
```

**Output:**
- Analysis results for each city: `airbnb_analysis/outputs/multi_city_results/{City}_results.json`
- Comparison summary: `airbnb_analysis/outputs/multi_city_results/comparison_summary.json`
- Generalizability visualizations: 
  - `generalizability_validation.png` - Main generalizability chart
  - `validation_method_matrix.png` - Statistical significance matrix
  - `effect_consistency.png` - Effect size consistency across cities

## Analysis Scenarios

### Scenario 1: Physical Space Premium
- **Privacy Premium**: Entire home vs Private room price difference
- **Capacity Premium**: Price increase per additional person
- **Interaction Effect**: Room type × capacity interaction

**Key Finding**: 2.33x privacy premium, $38.48 per person capacity premium

### Scenario 2: Location Premium
- **Spatial Heatmap**: Geographic price distribution
- **Regional Comparison**: Price differences across administrative regions
- **Sub-regional Analysis**: Price jumps in premium neighborhoods
- **Controlled Analysis**: Location premium controlling for physical features

**Key Finding**: Manhattan median price ($170) is 100% higher than Queens/Bronx ($85)

### Scenario 3: Scale Premium
- **Host Scale vs Price**: Multi-listing hosts charge higher prices
- **Host Scale vs Occupancy**: Scale hosts have higher vacancy (inventory management)
- **Entire Home Specialization**: Specialized hosts vs mixed operations

**Key Finding**: Multi-listing hosts (>5 listings) charge 18% more than single-listing hosts

### Scenario 4: Trust Monetization
- **Rating Distribution**: High trust threshold (4.7+)
- **Rating vs Occupancy**: Higher ratings → lower vacancy
- **Superhost Comparison**: Superhost premium in price and occupancy

**Key Finding**: Each 0.1 rating increase reduces vacancy by 10-15 days

### Scenario 5: Activity Signals
- **Reviews Decoupling**: Historical vs LTM reviews show weak correlation
- **LTM vs Price**: Recent reviews (LTM) better predict price than historical
- **LTM vs Occupancy**: Recent reviews predict occupancy better

**Key Finding**: Market prices "current demand" not "historical reputation"

## Generated Visualizations

### NYC Analysis Charts (19 charts)
- **Scenario 1**: 3 charts (privacy, capacity, interaction)
- **Scenario 2**: 4 charts (heatmap, regions, subregions, controlled)
- **Scenario 3**: 4 charts (scale-price, scale-occupancy, entire home scale, specialization)
- **Scenario 4**: 3 charts (rating distribution, rating-occupancy, superhost)
- **Scenario 5**: 4 charts (decoupling, LTM-price, historical-price, LTM-occupancy)
- **Comprehensive Model**: 1 chart (price prediction model coefficients)

### Multi-City Validation Charts (3 charts)
- **generalizability_validation.png**: Bar chart showing generalizability status (Strong/High/Partial) for each pattern
- **validation_method_matrix.png**: Heatmap showing statistical significance (green=significant, red=not significant) for each pattern across all cities
- **effect_consistency.png**: Box plots showing distribution of effect sizes (correlation, premium ratio) across cities

## Statistical Methods

- **Non-parametric Tests**: Mann-Whitney U, Kruskal-Wallis (robust to non-normal distributions)
- **Correlation Analysis**: Spearman rank correlation (monotonic relationships)
- **Regression Models**: Linear, interaction effects, log-linear
- **Non-parametric Smoothing**: LOWESS (local regression), KDE (kernel density estimation)

## Data Sources

- **NYC Data**: Inside Airbnb (cleaned version: `listings_2_cleaned 4.0.csv`)
- **Multi-City Data**: Inside Airbnb (11 cities, compressed `.gz` format)
  - Albany, Amsterdam, Antwerp, Asheville, Athens, Austin, Bangkok, Barcelona, Barossa Valley, Barwon South West Vic, Belize

## Documentation

- **Comprehensive Report**: `airbnb_analysis/docs/comprehensive_analysis_report.md` - Complete analysis integrating NYC and multi-city results
- **Project Structure**: `airbnb_analysis/PROJECT_STRUCTURE.md` - Detailed project structure documentation
- **NYC Results Summary**: `airbnb_analysis/docs/分析结果总结.md` - NYC analysis results summary
- **Multi-City Report**: `airbnb_analysis/docs/跨城市分析结果报告.md` - Multi-city validation report

## Results Summary

### NYC Analysis Results
- Identified 5 core pricing patterns across 5 scenarios
- Generated 19 visualization charts
- Built comprehensive price prediction model

### Multi-City Validation Results
- Validated patterns across 11 international cities
- 84,287 total listings analyzed
- **9 out of 10 patterns** show strong generalizability (≥80% cities significant)
- Generated 3 generalizability visualization charts

## Contributing

This is a research project. For questions or suggestions, please open an issue.

## License

This project is for research and educational purposes.

---

**Last Updated**: 2025-01-28  
**Analysis Tools**: Python (pandas, scipy, statsmodels, sklearn, matplotlib, seaborn)  
**Data Source**: Inside Airbnb
