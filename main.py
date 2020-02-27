# Import Custom Modules
from utils import User_agent_random, Debug_loggin, Url_parameters
from bs4 import BeautifulSoup

# Import Requests
import requests
import json
import furl
import uuid

# Path Logs
path_logger = './logs/'

# Endpoints
INTERPOL = 'https://www.interpol.int/es/Como-trabajamos/Notificaciones/Ver-las-notificaciones-rojas'

# Inicializamos una varibale globla con la session
session = requests.Session()

# Instanciamos el metodo login
logger = Debug_loggin(path_logger)
url_parameters = Url_parameters()

def main():
    #logger.log_debug("Using user-agent send reques ==> {}".format(User_agent_random.generate_user_agent()))
    logger.log_debug("Send Requests url ==> {}".format(INTERPOL))
    red_alert_page = session.get(INTERPOL)

    logger.log_debug("Response status ==> {}".format(red_alert_page.status_code))
    if red_alert_page.status_code == 200:
        html = BeautifulSoup(red_alert_page.content, 'html.parser')
        form_notices = html.find('form', {'id': 'noticesSelector'})
        url_action = form_notices.get('data-action')
        url_api = form_notices.get('data-api')

        select_nationality = form_notices.find('select', {'id': 'nationality'})
        option_nationality = select_nationality.find_all('option')
        nationalities = list()
        nationalities_failed = list()
        for nationality in option_nationality:
            if nationality.get('value'):
                nationalities.append({'key': nationality.get('value'), 'value': nationality.get_text()})
            else:
                nationalities_failed.append({nationality})
        logger.log_debug("Total de nacionalidad encontradas ==> {}".format(len(nationalities)))
        logger.log_debug("Total de no encontradas ==> {}".format(len(nationalities_failed)))
        logger.log_debug("Nacionalidades fallidas ==> {}".format(str(nationalities_failed)))

        send_parameters = dict()
        for index, value in enumerate(nationalities):
            send_parameters['arrestWarrantCountryId'] = value['key']
            aux_url_api = url_parameters.url_parameters_convert(url_api, send_parameters)

            logger.log_debug("Send Requests url ==> {}".format(aux_url_api))
            response_notices = session.get(aux_url_api)
            logger.log_debug("Response status ==> {}".format(red_alert_page.status_code))
            list_register = list()
            if response_notices.status_code == 200:
                data = json.loads(response_notices.content)
                logger.log_debug("Total de registros - info api ==> {}".format(data.get('total', 'SIN INFORMACION')))
                aux_total = data.get('total', 20)
                pages_total = int(aux_total) / 20
                number_pages = int(pages_total)
                if pages_total > float(number_pages):
                    number_pages = number_pages + 1

                for page in range(number_pages):
                    aux_number_page = page + 1
                    send_parameters['resultPerPage'] = 20
                    send_parameters['page'] = aux_number_page
                    aux_url_api = url_parameters.url_parameters_convert(url_api, send_parameters)

                    logger.log_debug("Send Requests url ==> {}".format(aux_url_api))
                    response_notices_red = session.get(aux_url_api)
                    logger.log_debug("Response status ==> {}".format(response_notices_red.status_code))
                    if response_notices_red.status_code == 200:
                        data_red = json.loads(response_notices_red.content)
                        if '_embedded' in data_red:
                            aux_embedded = data_red['_embedded']
                            if 'notices' in aux_embedded:
                                aux_notices = aux_embedded['notices']
                                for notice in aux_notices:
                                    if '_links' in notice:
                                        aux_links = notice['_links']
                                        if 'self' in aux_links:
                                            aux_self = aux_links['self']
                                            erntity_id = notice.get('entity_id')
                                            aux_erntity_id = erntity_id.replace('/', '-')
                                            aux_href = aux_self.get('href', 'https://ws-public.interpol.int/notices/v1/red/{}'.format(aux_erntity_id))
                                            logger.log_debug("Send Requests url ==> {}".format(aux_href))
                                            response_person = session.get(aux_href)
                                            logger.log_debug("Response status ==> {}".format(response_notices_red.status_code))
                                            if response_person.status_code == 200:
                                                aux_person = json.loads(response_person.content)
                                                list_register.append(aux_person)
                                            else:
                                                logger.log_debug("Ocurrio un error al realizar la peticion ==> {}".format(str(response_person.content)))
                                        else:
                                            logger.log_debug("No se encontro el elemento: self en aux_links ==> {}".format(str(aux_links)))
                                    else:
                                        logger.log_debug("No se encontro el elemento: _links en notice ==> {}".format(str(notice)))
                            else:
                                logger.log_debug("No se encontro el elemento: notices en aux_embedded ==> {}".format(str(aux_embedded)))
                        else:
                            logger.log_debug("No se encontro el elemento: _embedded en data ==>  {}".format(str(data_red)))
                    else:
                        logger.log_debug("Ocurrio un error al realizar la peticion ==> {}".format(str(response_notices_red.content)))
                
                filename_result_json = "./data/data-{}.json".format(uuid.uuid4())
                logger.log_debug("Los resultado se encribienron en el sigueinte archivo ==> {}".format(str(filename_result_json)))
                logger.log_debug("Total de registros encontrados ==> {}".format(str(len(list_register))))
                with open(filename_result_json, 'w') as json_file:
                    json.dump(list_register, json_file)
            else:
                logger.log_debug("Ocurrio un error al realizar la peticion ==> {}".format(str(response_notices.content)))
    else:
        logger.log_debug("Ocurrio un error al realizar la peticion ==> {}".format(str(red_alert_page.content)))

if __name__ == '__main__':
    main()