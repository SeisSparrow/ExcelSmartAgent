"""
Generate sample Excel data for testing
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path


def generate_sales_data():
    """Generate sample sales data"""
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate dates for the past year
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range(365)]
    
    # Regions and products
    regions = ['北京', '上海', '广州', '深圳', '杭州']
    products = ['笔记本电脑', '台式机', '显示器', '键盘', '鼠标', '耳机', '摄像头', '音响']
    categories = ['电脑', '电脑', '配件', '配件', '配件', '配件', '配件', '配件']
    
    # Generate random sales data
    data = []
    for _ in range(1000):
        date = np.random.choice(dates)
        region = np.random.choice(regions)
        product_idx = np.random.randint(0, len(products))
        product = products[product_idx]
        category = categories[product_idx]
        
        # Price varies by product
        base_prices = [5000, 3000, 1500, 200, 100, 300, 400, 800]
        price = base_prices[product_idx] * (1 + np.random.uniform(-0.2, 0.2))
        
        quantity = np.random.randint(1, 20)
        sales_amount = price * quantity
        
        # Random salesperson
        salesperson = f"销售员{np.random.randint(1, 11)}"
        
        data.append({
            '日期': date.strftime('%Y-%m-%d'),
            '地区': region,
            '产品名称': product,
            '类别': category,
            '单价': round(price, 2),
            '数量': quantity,
            '销售额': round(sales_amount, 2),
            '销售人员': salesperson
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values('日期').reset_index(drop=True)
    
    return df


def generate_inventory_data():
    """Generate sample inventory data"""
    
    products = ['笔记本电脑', '台式机', '显示器', '键盘', '鼠标', '耳机', '摄像头', '音响']
    categories = ['电脑', '电脑', '配件', '配件', '配件', '配件', '配件', '配件']
    
    data = []
    for i, product in enumerate(products):
        data.append({
            '产品编号': f'P{i+1:03d}',
            '产品名称': product,
            '类别': categories[i],
            '库存数量': np.random.randint(10, 200),
            '安全库存': np.random.randint(20, 50),
            '供应商': f'供应商{np.random.randint(1, 6)}',
            '采购价格': np.random.randint(50, 3000),
            '备注': ''
        })
    
    return pd.DataFrame(data)


def generate_customer_data():
    """Generate sample customer data"""
    
    regions = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安']
    
    data = []
    for i in range(100):
        data.append({
            '客户编号': f'C{i+1:04d}',
            '客户名称': f'客户{i+1}',
            '地区': np.random.choice(regions),
            '行业': np.random.choice(['IT', '金融', '教育', '医疗', '制造业']),
            '客户等级': np.random.choice(['A', 'B', 'C'], p=[0.2, 0.5, 0.3]),
            '联系人': f'联系人{i+1}',
            '电话': f'138{np.random.randint(10000000, 99999999)}',
            '累计消费': round(np.random.exponential(50000), 2),
            '注册日期': (datetime.now() - timedelta(days=np.random.randint(1, 1000))).strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(data)


def main():
    """Generate and save sample data files"""
    
    # Create data directory
    data_dir = Path(__file__).parent.parent / 'data' / 'excel_files'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sales data
    print("生成销售数据...")
    sales_df = generate_sales_data()
    sales_file = data_dir / 'sales_data_sample.xlsx'
    sales_df.to_excel(sales_file, index=False, engine='openpyxl')
    print(f"销售数据已保存到: {sales_file}")
    print(f"  - 行数: {len(sales_df)}")
    print(f"  - 列数: {len(sales_df.columns)}")
    print(f"  - 列名: {list(sales_df.columns)}\n")
    
    # Generate inventory data
    print("生成库存数据...")
    inventory_df = generate_inventory_data()
    inventory_file = data_dir / 'inventory_sample.xlsx'
    inventory_df.to_excel(inventory_file, index=False, engine='openpyxl')
    print(f"库存数据已保存到: {inventory_file}")
    print(f"  - 行数: {len(inventory_df)}")
    print(f"  - 列数: {len(inventory_df.columns)}")
    print(f"  - 列名: {list(inventory_df.columns)}\n")
    
    # Generate customer data
    print("生成客户数据...")
    customer_df = generate_customer_data()
    customer_file = data_dir / 'customer_sample.xlsx'
    customer_df.to_excel(customer_file, index=False, engine='openpyxl')
    print(f"客户数据已保存到: {customer_file}")
    print(f"  - 行数: {len(customer_df)}")
    print(f"  - 列数: {len(customer_df.columns)}")
    print(f"  - 列名: {list(customer_df.columns)}\n")
    
    print("✅ 所有示例数据生成完成！")
    print(f"\n您可以将这些文件上传到系统进行测试。")


if __name__ == "__main__":
    main()

