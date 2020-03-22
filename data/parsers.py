from flask_restful import reqparse


parser_change = reqparse.RequestParser()
parser_change.add_argument('team_leader', required=True, type=int)
parser_change.add_argument('job', required=True)
parser_change.add_argument('work_size', required=True, type=int)
parser_change.add_argument('collaborators', required=True)
parser_change.add_argument('is_finished', required=True, type=bool)

parser_add_job = reqparse.RequestParser()
parser_add_job.add_argument('team_leader', required=True, type=int)
parser_add_job.add_argument('job', required=True)
parser_add_job.add_argument('work_size', required=True, type=int)
parser_add_job.add_argument('collaborators', required=True)
parser_add_job.add_argument('is_finished', required=True, type=bool)
