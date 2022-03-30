from flask import Flask, render_template, send_file, make_response, url_for, Response, request
app = Flask(__name__)

import io
import os
import geopandas as gpd
import contextily as ctx
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

quartieri = gpd.read_file("/workspace/flaskverifica/NIL_WM.zip")
newradio = gpd.read_file("/workspace/flaskverifica/myshapefile.zip")
newradio.crs = "EPSG:4326"
newradio.to_crs(epsg=32632)

@app.route('/', methods = ["GET"])
def homepage():
    return render_template("homepage.html")

@app.route('/sceltaquartiere', methods = ["GET"])
def sceltaquartiere():
    quartieri2 = quartieri["NIL"].drop_duplicates().sort_values(ascending = True).to_list()
    return render_template("sceltaquartiere.html", quar = quartieri2)

@app.route('/listastazioni', methods = ["GET"])
def listastazioni():
    radio = request.args["sel"]
    quartiere = quartieri[quartieri.NIL == radio]
    listastazioni = newradio[newradio.within(quartiere.geometry.squeeze())]
    return listastazioni.to_html()

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
    stazradioquartiere = newradio[newradio.within(quartiere.geometry.squeeze())]
    stazradioquartiere.to_crs(epsg=3857).plot(ax=ax, color = "k")
    ctx.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype = "image/png")

@app.route('/stazionimunicipio', methods = ["GET"])
def stazionimunicipio():
    global radiomunicipio
    global radiomunicipio2
    radiomunicipio = newradio.groupby("MUNICIPIO")["OPERATORE"].count().reset_index().sort_values(by = "MUNICIPIO", ascending = True)
    radiomunicipio["MUNICIPIO"]=radiomunicipio["MUNICIPIO"].values.astype(str)
    radiomunicipio2 = radiomunicipio.to_html()
    return render_template("stazionimunicipio.html", radiomunicipio2=radiomunicipio2)

@app.route('/stazionimunicipio.png', methods = ["GET"])
def stazionimunicipiopng():
    fig = plt.figure(figsize = (12,8))
    ax = plt.axes()
    ax.bar(radiomunicipio["MUNICIPIO"], radiomunicipio["OPERATORE"])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype = "image/png")

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 3246, debug = True)