import os
from datetime import datetime
from collections import defaultdict

class SalesAnalytics:
    def __init__(self):
        self.daily_sales_volume = defaultdict(int)
        self.daily_sales_value = defaultdict(float)
        self.product_volumes = defaultdict(int)
        self.monthly_staff_sales = defaultdict(lambda: defaultdict(int))
        self.daily_avg_transactions = defaultdict(lambda: defaultdict(int))
    
    def parse_timestamp(self, timestamp):
        """Parse timestamp with flexible format handling"""
        try:
            # Try first with seconds
            return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            try:
                # Try without seconds
                return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M')
            except ValueError as e:
                raise ValueError(f"Unable to parse timestamp: {timestamp}") from e
    
    
    def parse_products(self, product_str):
        products = []
        try:
            items = product_str.strip('[]').split('|')
            for item in items:
                if not item:
                    continue
                prod_id, quantity = item.split(':')
                products.append((prod_id, int(quantity)))
        except Exception as e:
            print(f"Error parsing products string: {product_str}")
            print(f"Error details: {str(e)}")
        return products
        
    def process_line(self, line, filename):
        try:
            # Split by comma handling brackets
            parts = []
            in_brackets = False
            current_part = []
            
            for char in line.strip():
                if char == '[':
                    in_brackets = True
                elif char == ']':
                    in_brackets = False
                
                if char == ',' and not in_brackets:
                    parts.append(''.join(current_part))
                    current_part = []
                else:
                    current_part.append(char)
            
            if current_part:
                parts.append(''.join(current_part))
            
            if len(parts) != 4:
                print(f"Invalid line format in {filename}: {line}")
                return
                
            staff_id, timestamp, products, amount = parts
            
            try:
                dt = self.parse_timestamp(timestamp)
                date_str = dt.strftime('%Y-%m-%d')
                month_str = dt.strftime('%Y-%m')
                hour = dt.hour
            except ValueError as e:
                print(f"Error parsing timestamp in {filename}: {timestamp}")
                print(f"Error details: {str(e)}")
                return
            
            try:
                sale_amount = float(amount)
                self.daily_sales_value[date_str] += sale_amount
            except ValueError:
                print(f"Invalid amount format in {filename}: {amount}")
                return
            
            self.daily_sales_volume[date_str] += 1
            
            for product_id, quantity in self.parse_products(products):
                self.product_volumes[product_id] += quantity
            
            self.monthly_staff_sales[month_str][staff_id] += 1
            self.daily_avg_transactions[date_str][hour] += 1
            
        except Exception as e:
            print(f"Error processing line in {filename}: {line}")
            print(f"Error details: {str(e)}")

    
    def process_file(self, filepath):
        """Process file from the hackaton data path"""
        try:
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            self.process_line(line, filepath)
                        except Exception as e:
                            print(f"Error on line {line_num} in {filepath}: {line.strip()}")
                            print(f"Error details: {str(e)}")
        except Exception as e:
            print(f"Error reading file {filepath}")
            print(f"Error details: {str(e)}")
    
    def calculate_hourly_average(self, date_str):
        hour_counts = self.daily_avg_transactions[date_str]
        if not hour_counts:
            return 0
        total_transactions = sum(hour_counts.values())
        active_hours = len(hour_counts)
        return total_transactions / active_hours if active_hours > 0 else 0
    

    def generate_report(self):
        try:
            report = {
                'highest_daily_volume': max(self.daily_sales_volume.items(), key=lambda x: x[1]) if self.daily_sales_volume else None,
                'highest_daily_value': max(self.daily_sales_value.items(), key=lambda x: x[1]) if self.daily_sales_value else None,
                'most_sold_product': max(self.product_volumes.items(), key=lambda x: x[1]) if self.product_volumes else None,
                'monthly_top_staff': {
                    month: max(staff_sales.items(), key=lambda x: x[1])
                    for month, staff_sales in self.monthly_staff_sales.items()
                    if staff_sales
                },
                'highest_avg_volume_day': max(
                    ((date, self.calculate_hourly_average(date)) 
                     for date in self.daily_avg_transactions.keys()),
                    key=lambda x: x[1]
                ) if self.daily_avg_transactions else None
            }
            return report
        except Exception as e:
            print("Error generating report")
            print(f"Error details: {str(e)}")
            return None

def analyze_transactions(base_path):
    analyzer = SalesAnalytics()
    
    # Process all test case directories
    for test_dir in sorted(os.listdir(base_path)):
        if test_dir.startswith('test-case-'):
            test_path = os.path.join(base_path, test_dir)
            if os.path.isdir(test_path):
                print(f"\nProcessing {test_dir}...")
                # Process all .txt files in the test case directory
                for filename in sorted(os.listdir(test_path)):
                    if filename.endswith('.txt'):
                        filepath = os.path.join(test_path, filename)
                        print("filepath", filepath)
                        print(f"Processing file: {filename}")
                        if os.path.isfile(filepath):
                            analyzer.process_file(filepath)
    
    # Generate and print report
    report = analyzer.generate_report()
    if not report:
        print("\nError: Could not generate report due to processing errors")
        return
    
    print("\nSales Analytics Report")
    print("====================")
    if report['highest_daily_volume']:
        print(f"Highest Sales Volume: {report['highest_daily_volume'][1]} transactions on {report['highest_daily_volume'][0]}")
    if report['highest_daily_value']:
        print(f"Highest Sales Value: ${report['highest_daily_value'][1]:.2f} on {report['highest_daily_value'][0]}")
    if report['most_sold_product']:
        print(f"Most Sold Product: Product {report['most_sold_product'][0]} with {report['most_sold_product'][1]} units")
    if report['monthly_top_staff']:
        print("\nTop Performing Staff by Month:")
        for month, (staff_id, sales) in sorted(report['monthly_top_staff'].items()):
            print(f"{month}: Staff {staff_id} with {sales} transactions")
    if report['highest_avg_volume_day']:
        print(f"\nHighest Average Transaction Volume: {report['highest_avg_volume_day'][0]} "
              f"with {report['highest_avg_volume_day'][1]:.1f} transactions per hour")


if __name__ == "__main__":
    base_path = "./mp-hackathon-sample-data"
    analyze_transactions(base_path)