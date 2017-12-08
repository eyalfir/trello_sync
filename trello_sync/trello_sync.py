import sys
from collections import OrderedDict
import os
import trello
import yaml
import re
import json
import argparse
import logging
import requests

DEFAULT_CONFIG_FILENAME = '.trello'
REMOVE_SIGN = '-'

def load_configuration_file(filename, args):
    configuration_dict = json.load(file(filename))
    for k, v in configuration_dict.items():
        if k not in dir(args) or not getattr(args, k):
            setattr(args, k, v)


def get_current_board_dict(board_id, client):
    current_board_dict = client.boards.get_list(board_id, cards='open', card_fields='name,desc', filter='open', fields='name')
    return current_board_dict

def read_board_yaml(filename):
    with open(filename) as stream:
        raw_yaml = yaml.load(stream)
    return raw_yaml

def to_compact_board_dict(d):
    def api_list_to_compact_list(l):
        if l['cards']:
            return {'%s (%s)' % (l['name'], l['id']): [api_card_to_compact_card(c) for c in l['cards']]}
        else:
            return '%s (%s)' % (l['name'], l['id'])

    def api_card_to_compact_card(c):
        if c['desc']:
            return {'%s (%s)' % (c['name'], c['id']): c['desc']}
        else:
            return '%s (%s)' % (c['name'], c['id'])

    compact = [api_list_to_compact_list(l) for l in d]
    return compact
        
def compact_board_to_yml(b):
    return yaml.safe_dump(b, default_flow_style=False, width=10000)

URL = 'https://trello.com/1'
def build_params(args):
    return dict(key=args.key, token=args.token)

def update_card_pos(id, new_pos, args):
    resp = requests.put(URL + '/cards/%s/pos' % id, params=build_params(args), data={'value': new_pos})
    resp.raise_for_status()
    return json.loads(resp.content)

def new_list(new_list_name, args):
    list_record = args.client.lists.new(new_list_name, args.board)
    logging.info('new list found! %s ', new_list_name)
    return list_record['id']

def rename_list(id, new_list_name, args):
    raise NotImplemented('rename list %s to %s' % (id, new_list_name))

def remove_card(card_id, args):
    args.client.cards.update_closed(card_id, 'true')

def remove_list(list_id, args):
    args.client.lists.update_closed(list_id, 'true')

def new_card(name, list_id, description, args):
    id = args.client.cards.new(name, list_id, description or None)
    logging.info('creating new card with name %s in list %s with description %s', name, list_id, description)
    return id['id']

def update_description(card_id, description, args):
    args.client.cards.update_desc(card_id, description)

def parse_name_and_id(s):
    match = re.match('(?P<name>[^\(]*)( \((?P<id>[^\)]*)|$)', s)
    return match.groupdict()['name'], match.groupdict()['id']

def compare_lists(list_id, new_cards_compact, old_list_cards, args):
    old_list_dict = OrderedDict([(x['id'], x) for x in old_list_cards])
    new_cards_ids = []
    for card in new_cards_compact:
        if isinstance(card, dict):
            name, id = parse_name_and_id(card.keys()[0])
            description = card.values()[0]
        else:
            name, id = parse_name_and_id(card)
            description = ""
        if id:
            if name[0] == REMOVE_SIGN:
                logging.info('closing card %s with name %s', id, old_list_dict[id]['name'])
                remove_card(id, args)
                del old_list_dict[id]
                continue
            old_card = old_list_dict[id]
            if name != old_card['name']:
                logging.info('renaming card %s with name %s to %s', id, old_card['name'], name)
                args.client.cards.update_name(id, name)
            if description != old_card['desc']:
                update_description(id, description, args)
            new_cards_ids.append(id)
        elif name[0] != REMOVE_SIGN:
            new_cards_ids.append(new_card(name, list_id, description, args))
    for i, id in enumerate(new_cards_ids):
        try:
            old_index = list(old_list_dict).index(id)
        except ValueError:
            old_index = -1
        if old_index != i:
            logging.info('moving card %s to position %d' % (id, i + 1))
            update_card_pos(id, i + 1, args)



def compare_boards(new_compact, old_board, args):
    old_lists_dict = {x['id']: x for x in old_board}
    new_lists_ids = set()
    for l in new_compact:
        name, id = parse_name_and_id(l.keys()[0])
        if id:
            old_list = old_lists_dict[id]
            if name != old_list['name']:
                rename_list(id, name, args)
            compare_lists(id, l.values()[0], old_list['cards'], args)
            new_lists_ids.add(id)
        else:
            new_id = new_list(name, args)
            compare_lists(new_id, l.values()[0], [], args)
            new_lists_ids.add(new_id)
    for id in set(old_lists_dict.keys()) - new_lists_ids:
        logging.info('closing list %s with name %s' % (id, old_lists_dict[id]['name']))
        remove_list(id, args)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', help='trello member key')
    parser.add_argument('-t', '--token', help='trello security token')
    parser.add_argument('-b', '--board', help='the board ID of the Trello board to sync to')
    parser.add_argument('-v', '--verbose', help='print verbose logs', action='store_true')
    command = parser.add_subparsers()
    fetch_command = command.add_parser('fetch')
    fetch_command.set_defaults(func=fetch_board)
    update_command = command.add_parser('update')
    update_command.set_defaults(func=update_board)
    update_command.add_argument('-f', '--filename', help='full path of the YAML file to sync')
    mock_command = command.add_parser('mock')
    mock_command.set_defaults(func=mock)
    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(stream=sys.stderr,
                        format='%(asctime)s | %(levelname)-8.8s | %(message).10000s',
                        datefmt='%Y/%m/%d %H:%M:%S',
                        level=logging.DEBUG if args.verbose else logging.INFO)
    load_configuration_file(os.path.join(os.getenv('HOME'), DEFAULT_CONFIG_FILENAME), args)
    args.client = trello.TrelloApi(apikey=args.key, token=args.token)
    args.func(args)

def mock(args):
    print compact_board_to_yml([{'list (list_id)': ['card1 (card1_id)', {'card2 (card2_id)': 'card2 description'}]}])

def fetch_board(args):
    current_board_dict = get_current_board_dict(board_id=args.board, client=args.client)
    print compact_board_to_yml(to_compact_board_dict(current_board_dict))

def update_board(args):
    logging.info('syncing...')
    current_board_dict = get_current_board_dict(board_id=args.board, client=args.client)
    suggested_board_compact = read_board_yaml(filename=args.filename)
    compare_boards(suggested_board_compact, current_board_dict, args=args)
