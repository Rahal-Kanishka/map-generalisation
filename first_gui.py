import tkinter as tk
from tkinter import ttk
import shapefile
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import numpy as np
import osgeo
from osgeo import ogr
from tkinter import PhotoImage
from PIL import ImageTk, Image
import dbf
from simpledbf import Dbf5
import pandas as pd

# reading shape file data

shape_file_path = "/home/rahal/Documents/GIS Data/Sri_lanka/backup_6/gis_osm_buildings_a_free_1.shp"
dbf_file_path = "/home/rahal/Documents/GIS Data/Sri_lanka/backup_6/gis_osm_buildings_a_free_1.dbf"

dbf_file_with_data_path = "/home/rahal/Documents/GIS Data/Sri_lanka/backup_updated_dbf/gis_osm_buildings_a_free_1.dbf"

# sf = shapefile.Reader("/home/rahal/Documents/GIS Data/Sri_lanka/LKA_adm/LKA_adm2.shp")
# sf = shapefile.Reader("/home/rahal/Documents/GIS Data/Sri_lanka/LKA_adm/CO_Building_Pt.shp")
sf = shapefile.Reader(shape_file_path)

# records = np.array(sf.records())
records = sf.records();
fields = sf.fields
fieldNames = ''
scale_availability = 'False'

filtered_records = 0
updated_records = 0

print('fields: ', fields)

print('first record', sf.record(0));
# gdf = gpd.read_file("/home/rahal/Documents/GIS Data/Sri_lanka/LKA_adm/CO_Building_Pt.shp")
gdf = gpd.read_file(shape_file_path)

print(gdf.head())

# filter with name

filter_arr = []

for record in records:
    if record[3]:
        print('filter record', record)
        filter_arr.append(record)
# else:
# filter_arr.append(False)

# footpath_HARV = records[filter_arr]
filtered_records = len(filter_arr)
print('records found: ', len(filter_arr))

# --------------- creating GUI ------------------------------
window = tk.Tk()
window.geometry("1200x800")
window.title('Model Generalization')

height = len(records)
width = len(records[0])

label1 = tk.Label(window, text="Configuration Panel", font="times 28 bold")
label1.place(x=450, y=20)

recordsLabel = tk.Label(window, text="Records: ", font="times 15")
recordsLabel.place(x=50, y=60)
recordsCount = tk.Label(window, text=len(records), font="times 10")
recordsCount.place(x=200, y=60)

fieldsLabel = tk.Label(window, text="Field Count: ", font="times 15")
fieldsLabel.place(x=50, y=80)
feildsCount = tk.Label(window, text=len(fields), font="times 10")
feildsCount.place(x=200, y=80)

fieldNamesLabel = tk.Label(window, text="Fields: ", font="times 15")
fieldNamesLabel.place(x=50, y=100)
fieldNamesText = tk.Label(window, text=fields, font="times 10")
fieldNamesText.place(x=200, y=100)

filtered_records_label = tk.Label(window, text="Records With Name: ", font="times 15")
filtered_records_label.place(x=50, y=120)
filtered_records_count = tk.Label(window, text=filtered_records, font="times 10")
filtered_records_count.place(x=200, y=120)

# scall level availability indicator
scaleLabel = tk.Label(window, text="Scale level field available: ", font="times 15")
scaleLabel.place(x=50, y=150)
scaleAvailableText = tk.Label(window, text=scale_availability, font="times 10")
scaleAvailableText.place(x=300, y=150)

# Rating availability indicator
ratingLabel = tk.Label(window, text="Rating field available: ", font="times 15")
scaleLabel.place(x=50, y=150)
scaleAvailableText = tk.Label(window, text=scale_availability, font="times 10")
scaleAvailableText.place(x=300, y=150)

# scale level availability indicator
scaleLabel = tk.Label(window, text="Scale level field available: ", font="times 15")
scaleLabel.place(x=50, y=150)
scaleAvailableText = tk.Label(window, text=scale_availability, font="times 10")
scaleAvailableText.place(x=300, y=150)


def get_data_frame():
    dbf = Dbf5(dbf_file_path)
    df = dbf.to_dataframe()
    print('head: ', df.head())
    figure = plt.Figure(figsize=(15, 15), dpi=100)
    ax = figure.add_subplot(111)
    ax.scatter(df['RATING'], df['REVIEW_CNT'], color='g')
    new_window = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    new_window.title("Scatter Diagram")

    # sets the geometry of toplevel
    new_window.geometry("900x900")
    scatter3 = FigureCanvasTkAgg(figure, new_window)
    scatter3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
    ax.set_xlabel('RATING')
    ax.set_ylabel('Review Count')
    ax.set_title('Rating Vs Review Count')


def plot_histogram():
    dbf = Dbf5(dbf_file_path)
    df = dbf.to_dataframe()
    print('head: ', df.head())
    figure = plt.Figure(figsize=(6, 5), dpi=100)
    ax = figure.add_subplot(111)
    ax.hist(df['RATING'], color='g', bins=25)
    new_window = tk.Toplevel(window)

    # sets the title of the
    # Toplevel widget
    new_window.title("Histogram Diagram")

    # sets the geometry of toplevel
    new_window.geometry("650x700")
    scatter3 = FigureCanvasTkAgg(figure, new_window)
    scatter3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
    ax.set_title('Histogram of Rating')

def openNewWindow():
    newWindow = tk.Toplevel(window)
    newWindow.geometry("200x200")
    windowLabel = tk.Label(newWindow, text="Attribute Data")
    windowLabel.place(x=200, y=200)


def generateMap():
    filter_arr.plot()
    plt.show()


def getFieldNames():
    sf2 = shapefile.Reader(shape_file_path)
    # get list on field names available
    checkFields = sf2.fields[1:]
    fieldNames = [field[0] for field in checkFields]
    return fieldNames


def check_field_already_exists(checkFieldName):
    available_names = getFieldNames();
    name_found = False
    print('available field names: ', available_names)

    for name in available_names:
        if name == checkFieldName:
            name_found = True

    return name_found;


def update_rating_review_using_maps():
    global updated_records
    global filtered_records
    updated_records = 0
    table = dbf.Table(filename=dbf_file_path)

    table.open()

    with table:
        for dbf_record in dbf.Process(table):
            if dbf_record["NAME"]:
                response = get_data_from_maps(dbf_record["NAME"])
                if (not dbf_record["UPDATED"] and response['status'] == 'OK') and (len(response['candidates']) > 0)\
                        and (response['candidates'][0]):
                    print("response: ", response)
                    dbf_record["RATING"] = response['candidates'][0]['rating']
                    dbf_record["REVIEW_CNT"] = response['candidates'][0]['user_ratings_total']
                    # mark the record as updated to prevent update again, to update need to reset the whole column
                    dbf_record["UPDATED"] = 1
                    updated_records += 1
                    updated_records_count_label['text'] = str(updated_records)
                    "{:.2f}".format(updated_records/filtered_records * 100)
                    updated_records_percentage_label['text'] = "{:.2f}".format(updated_records/filtered_records * 100) \
                                                               + "%"
                    window.update()

    table.close()
    print('Updating Rating and reviews is finished')


def get_data_from_maps(place_name):
    response = requests.get(
        'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=' + place_name +
        '&inputtype=textquery&fields=rating,user_ratings_total'
        '&key=AIzaSyCTlqHUwR0bIt2KCgs2Prn53Qvdr7kxtkg')
    response.raise_for_status()
    # access JSOn content
    json_response = response.json()
    return json_response


def getRateingsAndReview():
    response = requests.get(
        'https://maps.googleapis.com/maps/api/place/details/json?placeid=ChIJtTR_a0FF4joRDlYCqyEn03s&key=AIzaSyCTlqHUwR0bIt2KCgs2Prn53Qvdr7kxtkg')
    response.raise_for_status()
    # access JSOn content
    jsonResponse = response.json()
    print('Entire JSON response')
    print(jsonResponse)
    total_rating = jsonResponse['result']['user_ratings_total']
    print('total_rating', total_rating)


def generateShapeFile():
    # Create a new shapefile in memory
    w = shapefile.Writer("/home/rahal/Documents/GIS Data/Sri_lanka/backup_2/gis_osm_buildings_a_free_1.shp")

    # Add our new field using the pyshp API
    w.field("scale_level_edit", "C", "40")

    for i in range(len(sf.records())):
        # set default rating as 3
        w.record[i]["scale_level"] = 3
    # Add the modified record to the new shapefile
    # w.record(rec)

    print('updated length: ', len(w.records()))
    w.close()


def addScaleField():
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(shape_file_path, 1)  # 1 is read/write

    # define floating point field named DistFld and 16-character string field named Name:
    fldDef = ogr.FieldDefn('scale_level', ogr.OFTReal)

    # get layer and add the 2 fields:
    layer = dataSource.GetLayer()
    layer.CreateField(fldDef)


def setScaleDefaultValie():
    sf1 = shapefile.Reader(shape_file_path)
    # set default value of 2
    # for i in range(len(sf1.records())):
    # 	# set default rating as 2
    # 	sf1.record[i][3] = 2;

    table = dbf.Table(filename=dbf_file_path)

    table.open()

    with table:
        for record in dbf.Process(table):
            record['SCALE_LVL'] = 3
        # record.write_record()

    with table:
        for rec in table:
            print(rec)

    table.close()


def remove_column(column_name):
    db = dbf.Table(dbf_file_path)
    db.open(mode=dbf.READ_WRITE)

    if check_field_already_exists(column_name):
        print('column exists ' + column_name + ' , going to remove it')
        with db:
            db.delete_fields(column_name)
            db.pack()
    else:
        print('column' + column_name + ' not available, not removing it')


def rename_field(oldfield, new_field):
    table = dbf.Table(dbf_file_path)
    table.open(mode=dbf.READ_WRITE)
    try:
        table.rename_field(oldfield, new_field)
    finally:
        table.close()


def remove_unnecessary_fields():
    rename_field('scale_leve', 'scale_level')
    remove_column('DistFld')


def generate_required_fields():
    db = dbf.Table(dbf_file_path, codepage='utf8')
    codepan = db.codepage
    print('codepage: ', codepan)

    if not check_field_already_exists('SCALE_LVL'):
        print('scale_lvl is not available, hence adding it')
        with db:
            try:
                db.add_fields('scale_lvl N(15,7)')
            except:
                print('error in adding scale level')
            for db_record in db:
                dbf.write(db_record, scale_lvl=1)
    else:
        print('scale_level is already available')

    if not check_field_already_exists('RATING'):
        print('rating is not available, hence adding it')
        with db:
            try:
                db.add_fields('rating N(15,7)')
            except:
                print('error in adding rating field')
            for record in db:
                dbf.write(record, rating=0)
    else:
        print('rating is already available')

    if not check_field_already_exists('REVIEW_CNT'):
        print('review_cnt is not available, hence adding it')
        with db:
            try:
                db.add_fields('review_cnt N(15,7)')
            except:
                print('error in adding review count')
            for record in db:
                dbf.write(record, review_cnt=0)
    else:
        print('REVIEW_CNT is already available')

    if not check_field_already_exists('UPDATED'):
        print('updated is not available, hence adding it')
        with db:
            try:
                db.add_fields('updated L')
            except:
                print('error in adding updated count')
            for record in db:
                dbf.write(record, updated=0)
    else:
        print('UPDATED is already available')


def checkScalFieldisAvailable():
    sf2 = shapefile.Reader(shape_file_path)

    x = False
    # get list on field names available
    checkFields = sf2.fields[1:]
    fieldNames = [field[0] for field in checkFields]
    print('field names: ', fieldNames)
    for field in fieldNames:
        if field == 'SCALE_LVL':
            print('SCALE_LVL attribute found')
            scaleAvailableText['text'] = 'True'
            x = True

    if x != True:
        print('SCALE_LVL attribute not found')
        # scale_availability = 'False'
        scaleAvailableText['text'] = 'False'


def refreshFileStatus():
    # reload fields, records from the file
    sf2 = shapefile.Reader(shape_file_path)
    global records
    global fields
    records = sf2.records()
    fields = sf2.fields
    fieldNamesText['text'] = fields
    checkScalFieldisAvailable()


def start_update_ratings_and_reviews():
    progress = 0



# button1 = tk.Button(window, text="update shape file", command=addScaleField)
# button1.place(x=50, y=200)

# button4 = tk.Button(window, text="Check scalability", command=checkScalFieldisAvailable)
# button4.place(x=50, y=300)

refesh_pic = Image.open("refresh_icon_2.png")
resized_icon = refesh_pic.resize((100, 60), Image.ANTIALIAS)
refreshImage = ImageTk.PhotoImage(resized_icon)
refresh_button = tk.Button(window, text="Refresh", image=refreshImage, command=refreshFileStatus)
refresh_button.place(x=1000, y=20)

# button5 = tk.Button(window, text="Default Scale Level", command=setScaleDefaultValie)
# button5.place(x=50, y=350)
#
# removeFieldButton = tk.Button(window, text="remove Unnecessary Fields", command=remove_unnecessary_fields)
# removeFieldButton.place(x=50, y=400)

requiredFieldButton = tk.Button(window, text="Generate Required Fields", command=generate_required_fields)
requiredFieldButton.place(x=50, y=250)

button2 = tk.Button(window, text="Generate Map", command=generateMap)
button2.place(x=400, y=250)

# button3 = tk.Button(window, text="Get ratings", command=getRateingsAndReview)
# button3.place(x=650, y=250)

button4 = tk.Button(window, text="Plot Data", command=get_data_frame)
button4.place(x=150, y=400)

updated_records_count_label = tk.Label(window, text=updated_records, font="times 10")
updated_records_count_label.place(x=150, y=450)

updated_records_percentage_label = tk.Label(window, text=updated_records, font="times 10 bold")
updated_records_percentage_label.place(x=175, y=450)

button5 = tk.Button(window, text="Update ratings using Maps API", command=update_rating_review_using_maps)
button5.place(x=150, y=500)

button6 = tk.Button(window, text="Plot Histogram", command=plot_histogram)
button6.place(x=150, y=550)


window.mainloop()
