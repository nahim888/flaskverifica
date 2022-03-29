from flask import Flask, render_template, request
app = Flask(__name__)

import geopandas as gpd 
import contextily as ctx 
import matplotlib.pyplot as plt 
import pandas as pd
import io

quartieri = gpd.read_file("/workspace/flaskverifica/NIL_WM.zip")
newradio = gpd.read_file("/workspace/flaskverifica/myshapefile.zip")

@app.route('/', methods = ["GET"])
def homepage():
    return render_template("homepage.html")

@app.route('/sceltaquartiere', methods = ["GET"])
def sceltaquartiere():
    quartieri2 = quartieri["NIL"].drop_duplicates().sort_values(ascending = True).to_list()
    return render_template("sceltaquartiere.html", quar = quartieri2)

#@app.route('/listastazioni', methods = ["GET"])
#def listastazioni():
    #radio = request.args["sel"]
    #newradio.crs = "EPSG:4326"
    #newradio.to_crs(epsg=32632)
    #quartiere = quartieri[quartieri.NIL == radio]
    #listastazioni = newradio[newradio.within(quartiere.geometry.squeeze())]
    #return listastazioni.to_html()

@app.route('/indexmappa', methods = ["GET"])
def indexmappa():
    return render_template("sceltaquartiere2.html")

@app.route('/mappastazioni', methods = ["GET"])
def mappastazioni():
    global quartiere
    value = request.args["value"]
    quartiere = quartieri[quartieri.NIL.str.contains(value)]
    nome = quartiere["NIL"].values[0]
    return render_template("ricerca.html", nome=nome)

@app.route('/ricerca.png', methods = ["GET"])
def ricercapng():
    fig, ax = plt.subplots(figsize =(12,8))
    quartiere.to_crs(epsg=3857).plot(ax=ax, alpha = 0.5, edgecolor = "k")
    #newradio = newradio.to_crs(epsg = 32632)
    stazradioquartiere = newradio[newradio.within(quartiere.geometry.squeeze())]
    stazradioquartiere.to_crs(epsg=3857).plot(ax=ax, color = "k")
    ctx.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype = "image/png")

@app.route('/stazionimunicipio', methods = ["GET"])
def stazionimunicipio():
    global radiomunicipio
    radiomunicipio = newradio.groupby("MUNICIPIO")["OPERATORE"].count().sort_values(by = "MUNICIPIO", ascending = True).reset_index()
    return render_template("stazionimunicipio.html", radiomunicipio = radiomunicipio)

@app.route('/stazionimunicipio.png', methods = ["GET"])
def stazionimunicipiopng():
    fig = plt.figure(figsize = (12,8))
    ax = plt.axes
    ax.bar(radiomunicipio["MUNICIPIO"], radiomunicipio["OPERATORE"])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype = "image/png")

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 3246, debug = True)