init_phrase = 'Привет, я помогу тебе выбрать подходящий сеанс в удобном кинотеатре. ' \
              'На какой фильм ты хочешь пойти?'

'''
dict key - number id, value - dict with keys [text, entity (to fill as a result of question in phrase),
type (question, clarification, statement)]
'''
phrase_dict = {
    0: {'text': init_phrase, 'entity': 'title', 'type': 'question'}
}


def seance_list_to_phrase(seances):
    # Turns list of seance objects to sentence
    phrase = 'Вам могут подойти эти сеансы. '

    # TODO rethink limits later and text aggregating
    seances = seances[:1]
    for seance in seances:
        text = 'В кинотеатре {theatre} есть сеанс в {time}. '.format(theatre=seance.theatre, time=seance.time)
        phrase += text

    return phrase
