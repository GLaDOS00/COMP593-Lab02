from sys import argv, exit
import os
from datetime import date, datetime 
import pandas as pd 
import re



# Command Line Parameters
def get_sales_csv():

    # Checking whether command line parameters were provided
    if len(argv) >= 2:
        sales_csv = argv[1] 

        # Checking if the CSV file path given is an existing path
        if os.path.isfile(sales_csv):
            return sales_csv
        else:
            print('Error CSV file path given does not exist')
            exit('Script execution aborted')
    else:  
        print('Error: No CSV file path provided')
        exit('Script execution aborted')

# Orders Directory
def get_order_dir(sales_csv):
    
    # Get directory path of sales data CSV file
    sales_dir = os.path.dirname(sales_csv)

    # Determine orders' directory name (Orders_YYYY-MM-DD)
    todays_date = date.today().isoformat()
    order_dir_name = 'Orders_' + todays_date
    
    # Build the full path of the orders' directory
    order_dir = os.path.join(sales_dir, order_dir_name)

    # Make the orders directory if it does not already exist
    if not os.path.exists(order_dir):
        os.makedirs(order_dir)

    return order_dir    

# Order Files
def split_sales_into_orders(sales_csv, order_dir):
    
    # Reading data from sales data CSV into DataFrame
    sales_df = pd.read_csv(sales_csv)

    # Inserting new column for total price of order
    sales_df.insert(7, 'TOTAL PRICE', sales_df['ITEM QUANTITY'] * sales_df['ITEM PRICE']) 

    # Removing redudant columns from DataFrame
    sales_df.drop(columns=['ADDRESS', 'CITY', 'STATE','POSTAL CODE', 'COUNTRY'], inplace=True) 

    for order_id, order_df in sales_df.groupby('ORDER ID',):

        # Dropping the ORDER ID column
        order_df.drop(columns= ['ORDER ID'], inplace=True)

        # Sort the order by order number
        order_df.sort_values(by='ITEM NUMBER', inplace=True)

        # Adding grand total row at the bottom of column
        grand_total = order_df['TOTAL PRICE'].sum()
        grand_total_df = pd.DataFrame({'ITEM PRICE': ['GRAND TOTAL'], 'TOTAL PRICE': [grand_total]})
        order_df = pd.concat([order_df, grand_total_df]) 

        # Determining the save path of the order file
        customer_name = order_df['CUSTOMER NAME'].values[0]
        customer_name = re.sub(r'\W','', customer_name)
        order_file_name = 'Order' + str(order_id) + '_' + customer_name + '.xlsx'
        order_file_path = os.path.join(order_dir, order_file_name)

        # Saving the order information to an Excel spreadsheet
        sheet_name = 'Order #' + str(order_id)
        writer = pd.ExcelWriter(order_file_path, engine= 'xlsxwriter')
        order_df.to_excel(writer, index=False, sheet_name=sheet_name)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Adding a number format for cells with money
        money_fmt = workbook.add_format({'num_format': '$###,###.00','bold': True})

        # Formatting of column width
        worksheet.set_column('A:A', 11)
        worksheet.set_column('B:B', 13)
        worksheet.set_column('C:E', 15)
        worksheet.set_column('F:G', 13, money_fmt)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 30)

        writer.save()
         


sales_csv = get_sales_csv()
order_dir = get_order_dir(sales_csv)
split_sales_into_orders(sales_csv, order_dir)