"""常量定义"""
# 场景名称
SCENARIOS = {
    1: "物理空间的溢价逻辑",
    2: "黄金地段的绝对统治",
    3: "运营专业化带来的规模溢价",
    4: "信任的货币化",
    5: "活跃度即需求的实时信号",
}

# 特征列名
FEATURE_COLS = {
    'price': 'price',
    'accommodates': 'accommodates',
    'room_type': 'room_type',
    'neighbourhood_group': 'neighbourhood_group_cleansed',
    'neighbourhood': 'neighbourhood_cleansed',
    'host_listings_count': 'calculated_host_listings_count',
    'entire_homes_count': 'calculated_host_listings_count_entire_homes',
    'review_rating': 'review_scores_rating',
    'reviews_total': 'number_of_reviews',
    'reviews_ltm': 'number_of_reviews_ltm',
    'availability': 'availability_365',
    'superhost': 'host_is_superhost',
    'latitude': 'latitude',
    'longitude': 'longitude',
}

# 城市名称映射（内部名称 -> 显示名称）
CITY_NAMES = {
    'new_york': 'New York',
    'san_francisco': 'San Francisco',
    'los_angeles': 'Los Angeles',
    'boston': 'Boston',
    'seattle': 'Seattle',
    'london': 'London',
    'paris': 'Paris',
    'tokyo': 'Tokyo',
    'milan': 'Milan',
    'buenos_aires': 'Buenos Aires',
}
