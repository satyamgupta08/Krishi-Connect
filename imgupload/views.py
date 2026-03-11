from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ImageUploadForm
from .test01 import identify_plant
from .connection import *
import datetime


def imgupload(request):
    return render(request, 'plant.html')


def result(request):
    return render(request, 'index.html')


def imageprocess(request):

    form = ImageUploadForm(request.POST, request.FILES)

    if form.is_valid():

        handel_uploaded_file(request.FILES['image'])

        img_path = 'img.jpg'

        x = identify_plant([img_path])

        # ---------- Extract data from PlantNet response ----------

        plant_name = x.get("bestMatch", "")

        results = x.get("results", [])

        if len(results) == 0:
            messages.error(request, "No plant detected")
            return redirect(imgupload)

        top = results[0]

        probability = [top.get("score", 0)]

        species = top.get("species", {})

        name = [species.get("scientificName", "Unknown Plant")]

        common_names = species.get("commonNames", [])

        family = species.get("family", {}).get("scientificNameWithoutAuthor", "")

        genus = species.get("genus", {}).get("scientificNameWithoutAuthor", "")

        # dummy placeholders (since PlantNet doesn't provide these directly)
        pclass = ""
        kingdom = ""
        order = ""
        phylum = ""
        org_url = ""
        res_orginal = common_names
        res_value = probability
        dis_desc = []
        wiki_url = []
        similar_images = []

        # ---------- Confidence check ----------

        if probability[0] < 0.3:
            messages.error(request, 'Our Database did not find a confident match')
            return redirect(imgupload)

        # ---------- Database insert ----------

        try:
            for i in range(min(3, len(results))):

                species_i = results[i]["species"]

                plant = species_i.get("scientificName", "")
                score = results[i].get("score", 0)

                con = sql_connection()
                mycursor = con.cursor()

                query = "insert into plant values(%s,%s,%s,%s,now())"

                data = [plant_name, plant, score, 'bengluru']

                mycursor.execute(query, data)

                mycursor.close()
                con.commit()

        except:
            pass

        # ---------- Render result page ----------

        return render(request, 'result.html', {
            'res_orginal': res_orginal,
            'res_value': probability[0],
            'img_url': "",
            'pclass': pclass,
            'family': family,
            'genus': genus,
            'kindom': kingdom,
            'order': order,
            'phylum': phylum,
            'org_url': org_url,
            'plant_name': plant_name,
            'common_names': common_names,
            'dis_desc': dis_desc,
            'wiki_url': wiki_url,
            'similar_images': similar_images,
            'name': name,
            'probability': probability
        })


def handel_uploaded_file(f):
    with open('img.jpg', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def report(request):

    con = sql_connection()
    mycursor = con.cursor()

    query = """
    select d1,count(d1),round(avg(percentage)*100,2)
    from plant
    where uploaddate BETWEEN (NOW() - INTERVAL 7 DAY) AND NOW()
    group by d1
    order by 2 desc;
    """

    mycursor.execute(query)

    myresult = mycursor.fetchall()

    name = []
    frequency = []
    percentage = []

    for x in myresult:
        name.append(x[0])
        frequency.append(x[1])
        percentage.append(x[2])

    zipped = zip(name, frequency, percentage)

    return render(request, "report.html", {'zipped': zipped})