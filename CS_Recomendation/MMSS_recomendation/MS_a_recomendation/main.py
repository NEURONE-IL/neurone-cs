# coding:utf-8
from flask import Flask, request #request: para trabajar con parametros por rutas
from bs4 import BeautifulSoup
from flask_restful import Resource, Api
from flask_babel import Babel, gettext
import requests
import json
import warnings

#ppp: re.sub launches the DeprecationWarning, I can not identify the reason. For this reason, this line is added.
warnings.filterwarnings("ignore", category=DeprecationWarning) 

app = Flask(__name__)
app.secret_key = 'html_secret_key'
api = Api(app) 
babel = Babel(app)

@babel.localeselector
def get_locale():
	#return request.accept_languages.best_match(['en', 'es', 'fi'])
    return 'en'

def recomA(contentJson, badEvaluations):
	contentBase= BeautifulSoup(contentJson, "lxml") 
	
	images = contentBase.find_all('a')

	badEvalsPos = badEvaluations.get('positionsBadTags')

	recomendations = []
	count = 0
	lenEvals=len(badEvalsPos)
	messages = {}
	messages[0] = gettext ("No se detectaron incompatibilidades correspondientes a este tag.")
	#Tipo de incompatibilidad 1:
	messages[1] = gettext ("Se recomienda agregar un título a la etiqueta a.")
	#Tipo de incompatibilidad 2: 
	messages[2] = gettext ("Se recomienda que el label sea un texto.")
	#Tipo de incompatibilidad 3: 
	messages[3] = gettext ("Se recomienda cambiar el uso de Target por Href u onClick.")


	if (lenEvals == 0):
		recomendations.append({'recomendation' : messages.get(0)})
	else :
		while count<lenEvals:
			message=messages.get((badEvalsPos[count][2]))
			recomendations.append({'element' : str(images[badEvalsPos[count][1]]), 'recomendation' : message})
			count += 1

	dataResponse ={
		'tag' : 'a',
		'recomendations': recomendations
	}
	response = json.dumps({'status': 'success', 'data': dataResponse})
	return response

class Petition(Resource):
	def post(self):
		response = {}
		try: 
			json_data = request.get_json(force=True)
			response = recomA(json_data['html'], json_data['badResults']) 
			return response
		except requests.exceptions.RequestException as e: 
			return ("error")

api.add_resource(Petition, '/a_recomendation')

class Ping(Resource):
    def get(self):
        try:
            return {'status': 'success'}
        except requests.exceptions.RequestException as e:
            return {"status":"Error"}

api.add_resource(Ping, '/ping')

if __name__ == '__main__':
	app.run( debug = False, host='0.0.0.0', port=9010)