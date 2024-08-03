from flask import Flask, request, jsonify, make_response, render_template,redirect,url_for
from pony import orm
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
from itertools import groupby
import random



DB = orm.Database()

app = Flask(__name__)

class Termin(DB.Entity):
    id_termin = orm.PrimaryKey(int, auto=True)
    datum = orm.Optional(datetime)
    id_zivotinja=orm.Required(int)
    usluga = orm.Required(str)
    cijena=orm.Required(Decimal)

class Zivotinja(DB.Entity):
    id_zivotinja = orm.PrimaryKey(int, auto=True)
    ime_zivotinje = orm.Required(str)
    vrsta = orm.Required(str)
    podvrsta = orm.Optional(str)
    vlasnik = orm.Required(str)
    broj_vlasnika=orm.Optional(str)

DB.bind(provider="sqlite", filename="database.sqlite", create_db=True)
DB.generate_mapping(create_tables=True)

def get_all_termin_ids():
    try:
        with orm.db_session:
            termin_ids = [t.id_termin for t in Termin.select()]
            response = {"response": "Success", "data": termin_ids}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}

@app.route("/termini/ids", methods=["GET"])
def dohvat_svih_termin_ids():
    response = get_all_termin_ids()
    if response["response"] == "Success":
        return make_response(jsonify(response["data"]), 200)
    return make_response(jsonify(response), 400)

def get_all_termini():
    try:
        with orm.db_session:
            termin_ids = [t.id_termin for t in Termin.select()]
            termini = []
            for termin_id in termin_ids:
                termin_data = get_termin_by_id(termin_id)
                if termin_data["response"] == "Success":
                    termini.append(termin_data["data"])
                else:
                    return {"response": "Fail", "error": termin_data["error"]}
            return {"response": "Success", "data": termini}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}




def formatiraj_datum(datum):
    return datum.strftime('%d-%m-%Y') if datum else None



def add_termin(json_request):
    try:
        id_zivotinja = json_request["id_zivotinja"]
        usluga = json_request["usluga"]
        cijena = json_request["cijena"]
        try:
            datum_str = request.form["datum"]
            datum = datetime.strptime(datum_str, '%Y-%m-%d')
        except ValueError:
            datum = None
        with orm.db_session:
            Termin(datum=datum, usluga=usluga, cijena=cijena, id_zivotinja=id_zivotinja)
            return {"response": "Success"}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}
    



def get_termin_by_id(id_termin):
    try:
        with orm.db_session:
            result = Termin[id_termin].to_dict()
            result['datum'] = formatiraj_datum(result['datum'])
            response = {"response": "Success", "data": result}
            return response
    except Exception as e:
        return {"response": "Fail", "error": str(e)}
    

def patch_termin(termin_id, json_request):
    try:
        with orm.db_session:
            to_update = Termin[termin_id]
            if 'datum' in json_request:
                to_update.datum = datetime.strptime(json_request['datum'], '%Y-%m-%d')
            if 'id_zivotinja' in json_request:
                to_update.id_zivotinja = json_request['id_zivotinja']
            if 'usluga' in json_request:
                to_update.usluga = json_request['usluga']
            if 'cijena' in json_request:
                to_update.cijena = json_request['cijena']

            return {"response": "Success"}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}



def delete_termin(termin_id):
    try:
        with orm.db_session:
            to_delete = Termin[termin_id]
            to_delete.delete()
            return {"response": "Success"}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}







        


def add_zivotinja(json_request):
    try:
        ime_zivotinje = json_request["ime_zivotinje"]
        vrsta = json_request["vrsta"]
        podvrsta = json_request["podvrsta"]
        vlasnik = json_request["vlasnik"]
        broj_vlasnika = json_request["broj_vlasnika"]

        with orm.db_session:
            Zivotinja(ime_zivotinje=ime_zivotinje, vrsta=vrsta, podvrsta=podvrsta, vlasnik=vlasnik, broj_vlasnika=broj_vlasnika)
            return {"response": "Success"}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}



def get_all_zivotinje():
    try:
        with orm.db_session:
            zivotinja_ids = [z.id_zivotinja for z in Zivotinja.select()]
            zivotinje = []
            for zivotinja_id in zivotinja_ids:
                zivotinja_data = get_zivotinja_by_id(zivotinja_id)
                if zivotinja_data["response"] == "Success":
                    zivotinje.append(zivotinja_data["data"])
                else:
                    return {"response": "Fail", "error": zivotinja_data["error"]}
            return {"response": "Success", "data": zivotinje}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


def get_zivotinja_by_id(zivotinja_id):
    try:
        with orm.db_session:
            zivotinja = Zivotinja[zivotinja_id]
            return {"response": "Success", "data": zivotinja.to_dict()}
    except orm.ObjectNotFound:
        return {"response": "Fail", "error": "Zivotinja nije pronađena"}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}

def patch_zivotinja(zivotinja_id, json_request):
    try:
        with orm.db_session:
            zivotinja = Zivotinja[zivotinja_id]
            if 'ime_zivotinje' in json_request:
                zivotinja.ime_zivotinje = json_request['ime_zivotinje']
            if 'vrsta' in json_request:
                zivotinja.vrsta = json_request['vrsta']
            if 'podvrsta' in json_request:
                zivotinja.podvrsta = json_request['podvrsta']
            if 'vlasnik' in json_request:
                zivotinja.vlasnik = json_request['vlasnik']
            if 'broj_vlasnika' in json_request:
                zivotinja.broj_vlasnika = json_request['broj_vlasnika']
            return {"response": "Success"}
    except orm.ObjectNotFound:
        return {"response": "Fail", "error": "Zivotinja nije pronađena"}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}

def delete_zivotinja(zivotinja_id):
    try:
        with orm.db_session:
            zivotinja = Zivotinja[zivotinja_id]
            zivotinja.delete()
            return {"response": "Success"}
    except orm.ObjectNotFound:
        return {"response": "Fail", "error": "Zivotinja nije pronađena"}
    except Exception as e:
        return {"response": "Fail", "error": str(e)}


# Dodavanje termina
@app.route("/dodaj/termin", methods=["POST", "GET"])
def dodaj_termin():
    if request.method == "POST":
        try:
            json_request = {key: request.form[key] for key in request.form}
            response = add_termin(json_request)
            if response["response"] == "Success":
                return make_response(render_template("dodaj.html"), 200)
            return make_response(jsonify(response), 400)
        except Exception as e:
            return make_response(jsonify({"response": str(e)}), 400)
    return make_response(render_template("dodaj.html"), 200)



# Dohvaćanje svih termina      


@app.route("/termini/svi", methods=["GET"])
def dohvat_svih_termina():
    response = get_all_termini()
    if response["response"] == "Success":
        return make_response(render_template("vrati.html", data=response["data"]), 200)
    return make_response(jsonify(response), 400)


#termin po id-u
@app.route("/termin/<int:id_termin>", methods=["GET"])
def dohvat_termina(id_termin):
    response = get_termin_by_id(id_termin)
    if response["response"] == "Success":
        return make_response(jsonify(response["data"]), 200)
    return make_response(jsonify(response), 400)



#patch termina
@app.route("/termin/<int:id_termin>", methods=["PATCH"])
def izmjeni_termin(id_termin):
    try:
        json_request = request.json
        response = patch_termin(id_termin, json_request)
        if response["response"] == "Success":
            return make_response(render_template("uredi_termin.html", termin=response["data"]), 200)
        return jsonify(response), 400
    except Exception as e:
        return jsonify({"response": "Error", "message": str(e)}), 400

@app.route("/termin/edit/<int:id_termin>", methods=["GET"])
def edit_termin(id_termin):
    response = get_termin_by_id(id_termin)
    if response["response"] == "Success":
        return make_response(render_template("uredi_termin.html", termin=response["data"]), 200)
    return make_response(jsonify(response), 400)

@app.route("/termin/update", methods=["POST"])
def update_termin():
    try:
        form_data = request.form
        id_termin = form_data.get('id_termin')
        if id_termin:
            response = patch_termin(id_termin, form_data)
            if response["response"] == "Success":
                return redirect(url_for('edit_termin', id_termin=id_termin))
        return jsonify(response), 400
    except Exception as e:
        return jsonify({"response": "Error", "message": str(e)}), 400

#brisanje termina
@app.route("/termin/<int:id_termin>", methods=["DELETE"])
def izbrisi_termin(id_termin):
    response = delete_termin(id_termin)
    if response["response"] == "Success":
        return make_response(jsonify(response), 200)
    return make_response(jsonify(response), 400)


# Dodavanje životinje
@app.route("/dodaj/zivotinja", methods=["POST", "GET"])
def dodaj_zivotinju():
    if request.method == "POST":
        try:
            json_request = {key: request.form[key] for key in request.form}
            response = add_zivotinja(json_request)
            if response["response"] == "Success":
                return make_response(render_template("dodaj_zivotinju.html"), 200)
            return make_response(jsonify(response), 400)
        except Exception as e:
            return make_response(jsonify({"response": str(e)}), 400)
    return make_response(render_template("dodaj_zivotinju.html"), 200)



# Dohvaćanje životinja


@app.route("/zivotinje/sve", methods=["GET"])
def dohvat_svih_zivotinja():
    response = get_all_zivotinje()
    if response["response"] == "Success":
        return make_response(render_template("vrati_zivotinju.html", data=response["data"]), 200)
    return make_response(jsonify(response), 400)


#patch životinja
@app.route("/zivotinja/<int:id_zivotinja>", methods=["PATCH"])
def izmjeni_zivotinju(id_zivotinja):
    try:
        json_request = request.json
        response = patch_zivotinja(id_zivotinja, json_request)
        if response["response"] == "Success":
            return make_response(render_template("uredi.zivotinju.html", zivotinja=response["data"]), 200)
        return make_response(jsonify(response), 400)
    except Exception as e:
        return make_response(jsonify({"response": str(e)}), 400)
    
@app.route("/zivotinja/edit/<int:id_zivotinja>", methods=["GET"])
def edit_zivotinja(id_zivotinja):
    response = get_zivotinja_by_id(id_zivotinja)
    if response["response"] == "Success":
        return make_response(render_template("uredi_zivotinju.html", zivotinja=response["data"]), 200)
    return make_response(jsonify(response), 400)

@app.route("/zivotinja/update", methods=["POST"])
def update_zivotinja():
    try:
        form_data = request.form
        id_zivotinja = form_data.get('id_zivotinja')
        if id_zivotinja:
            response = patch_zivotinja(id_zivotinja, form_data)
            if response["response"] == "Success":
                return redirect(url_for('edit_zivotinja', id_zivotinja=id_zivotinja))
        return jsonify(response), 400
    except Exception as e:
        return jsonify({"response": "Error", "message": str(e)}), 400

#brisanje životinje
@app.route("/zivotinja/<int:id_zivotinja>", methods=["DELETE"])
def obrisi_zivotinju(id_zivotinja):
    response = delete_zivotinja(id_zivotinja)
    if response["response"] == "Success":
        return make_response(jsonify(response), 200)
    return make_response(jsonify(response), 400)


@app.route("/", methods=["GET"])
def home():
    return make_response(render_template("index.html"),200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
