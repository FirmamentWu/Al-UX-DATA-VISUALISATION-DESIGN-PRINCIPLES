# 数据下载指南

由于Inside Airbnb网站的反爬虫保护，自动下载可能失败。请按照以下步骤手动下载数据：

## 手动下载步骤

1. **访问数据页面**: https://insideairbnb.com/get-the-data/

2. **找到目标城市**，点击对应的 `listings.csv.gz` 链接下载

3. **下载的城市列表**:
   - San Francisco (旧金山)
   - Los Angeles (洛杉矶)
   - Boston (波士顿)
   - Seattle (西雅图)
   - London (伦敦)
   - Paris (巴黎)
   - Tokyo (东京)
   - Milan (米兰)
   - Buenos Aires (布宜诺斯艾利斯)

4. **保存位置**: 将下载的文件保存到以下目录结构：
   ```
   airbnb_analysis/data/raw/multi_cities/
   ├── san_francisco/
   │   └── listings.csv.gz
   ├── los_angeles/
   │   └── listings.csv.gz
   ├── boston/
   │   └── listings.csv.gz
   ├── seattle/
   │   └── listings.csv.gz
   ├── london/
   │   └── listings.csv.gz
   ├── paris/
   │   └── listings.csv.gz
   ├── tokyo/
   │   └── listings.csv.gz
   ├── milan/
   │   └── listings.csv.gz
   └── buenos_aires/
       └── listings.csv.gz
   ```

## 数据URL格式

根据Inside Airbnb网站，数据URL格式为：
```
https://data.insideairbnb.com/{country}/{region}/{city}/{date}/data/listings.csv.gz
```

示例：
- San Francisco: `https://data.insideairbnb.com/united-states/ca/san-francisco/2024-09-11/data/listings.csv.gz`
- London: `https://data.insideairbnb.com/united-kingdom/england/london/2024-09-11/data/listings.csv.gz`

## 验证数据

下载完成后，运行以下命令验证数据：
```bash
python check_datasets.py
```

这将检查所有已下载的数据集，确认列名是否正确匹配。

## 注意事项

- 数据按季度更新，最近12个月的数据可用
- 如果某个日期的数据不可用，可以尝试更早的日期
- 确保下载的是 `listings.csv.gz` 文件（不是 `listings.csv`）
