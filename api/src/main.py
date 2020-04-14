import json

from flask import Flask
app = Flask(__name__)

from elasticsearch import Elasticsearch
es = Elasticsearch("localhost", port=9200)


@app.route('/api/congress/')
def get_all_bills():
    query = {
        "_source": ["billStatus.bill.billType", "billStatus.bill.billNumber", "billStatus.bill.congress"],
        "query": {
            "match_all": {}
        }
    }

    res = es.search(index="congress", body=query)
    info_out = "No bills available"
    if res['hits']['total']['value'] > 0:
        info_out = res['hits']
    return info_out


@app.route('/api/congress/<congress>')
def get_all_bills_by_congress(congress):
    query = {
        "_source": ["billStatus.bill.billNumber", "billStatus.bill.billType"],
        "query": {
            "bool": {
                "must": {
                    "term": {"billStatus.bill.congress.keyword": str(congress)}
                }
            }
        },
        "size": 10000
    }

    res = es.search(index="congress", body=query)
    print(res)
    info_out = "No bills available for congress #: " + str(congress)
    if res['hits']['total']['value'] > 0:
        info_out = res['hits']
    return info_out


def generate_bill_query(congress, type, number):
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {"billStatus.bill.billType.keyword": str(type)}
                    },
                    {
                        "term": {"billStatus.bill.billNumber": str(number)}
                    },
                    {
                        "term": {"billStatus.bill.congress.keyword": str(congress)}
                    }
                ]
            }
        }
    }


def find_bill_information(query, info):
    res = es.search(index='congress', body=json.dumps(query))
    info_out = "Unable to find " + info
    if res['hits']['total']['value'] > 0:
        info_out = res['hits']['hits'][0]['_source']['billStatus']['bill'][info]
    return info_out


@app.route('/api/congress/<congress>/type/<type>/number/<number>')
def get_bill(congress, type, number):
    print(congress)
    print(type)
    print(number)
    query = generate_bill_query(congress, type, number)

    res = es.search(index='congress', body=json.dumps(query))
    bill = "Unable to find bill"
    if res['hits']['total']['value'] > 0:
        bill = res['hits']['hits'][0]['_source']
    print(bill)
    return bill


@app.route('/api/congress/<congress>/type/<type>/number/<number>/title')
def get_bill_title(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'title')


@app.route('/api/congress/<congress>/type/<type>/number/<number>/actions')
def get_bill_actions(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'actions')


@app.route('/api/congress/<congress>/type/<type>/number/<number>/latest_action')
def get_bill_latest_action(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'latestAction')


@app.route('/api/congress/<congress>/type/<type>/number/<number>/sponsors')
def get_bill_sponsors(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'sponsors')


@app.route('/api/congress/<congress>/type/<type>/number/<number>/cosponsors')
def get_bill_cosponsors(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'cosponsors')


@app.route('/api/congress/<congress>/type/<type>/number/<number>/create_date')
def get_bill_create_date(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'createDate')


@app.route('/api/congress/<congress>/type/<type>/number/<number>/introduced_date')
def get_bill_introduced_date(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'introducedDate')


@app.route('/api/congress/<congress>/type/<type>/number/<number>/summaries')
def get_bill_summaries(congress, type, number):
    query = generate_bill_query(congress, type, number)
    return find_bill_information(query, 'summaries')


if __name__ == '__main__':
    app.run()