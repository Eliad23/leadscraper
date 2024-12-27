import util

niche = input("target niche: ")
location = input("what location: ")
number_of_leads = input("how many leads do you want: ")
file_location = input("do you want to make a new leads list? ")
if file_location == "y":
    excel_location = input("excel file name: ")
    excel_location = f"{excel_location}.xlsx"
    util.new_leads(niche, location, number_of_leads, excel_location)
else:
    existing_file_path = input("what is the name of the current file? ")
    util.add_leads(niche, location, number_of_leads, existing_file_path)
