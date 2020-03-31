from finder_app import dialog_content as dialog
from finder_app.find_timetable import get_seance_list
import pymorphy2
import datetime


def handle_dialog(session, req, res):

    if req['session']['new']:
        # If session is new welcome user and describe functions
        res['response']['text'] = dialog.phrase_dict[0]
        session.response_stack.append(0)
        return

    # Process new info and add it to the query
    entity_values = parse_request(req, session.response_stack[-1])
    session.query.update(entity_values)

    # Handle different stages of dialog
    if session.query.is_mandatory_filled:
        seance_list = get_seance_list(session.query)
        res['response']['text'] = dialog.seance_list_to_phrase(seance_list)
        res['response']['end_session'] = True
        return
    else:
        # Ask questions to filled every mandatory field
        return


def parse_request(request, last_phrase_id):
    # Returns dict with entities as keys (title, time, theatre, date, price, language, format, place)

    entity_dict = dict()
    morph = pymorphy2.MorphAnalyzer()
    tokens_norm = [morph.parse(word)[0].normal_form for word in request['request']['nlu']['tokens']]

    # TODO mvp parse only title in normal form and manually add date
    entity_dict['title'] = request['request']['original_utterance']
    entity_dict['date'] = datetime.date.today()

    return entity_dict
