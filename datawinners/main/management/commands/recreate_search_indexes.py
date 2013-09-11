import logging
from django.core.management.base import BaseCommand
import elasticutils
from datawinners.main.couchdb.utils import all_db_names
from datawinners.search.datasender_index import update_datasender_index
from datawinners.search.subject_index import update_subject_index
from datawinners.settings import ELASTIC_SEARCH_URL


def recreate_index_for_db(database_name, es):
    try:
        es.delete_index(database_name)
    except Exception as e:
        logging.info("Could not delete index " + e.message)
    response = es.create_index(database_name, settings={"number_of_shards": 1, "number_of_replicas": 0})
    logging.info('%s search index created : %s' % (database_name, response.get('ok')))
    update_subject_index(database_name)
    update_datasender_index(database_name)


class Command(BaseCommand):
    def handle(self, *args, **options):
        es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
        if len(args) > 0:
            databases_to_index = args[0:]
        else:
            databases_to_index = all_db_names()
        for database_name in databases_to_index:
            recreate_index_for_db(database_name, es)
            print 'Done' + database_name

        print 'Completed!'
