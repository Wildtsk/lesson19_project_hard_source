from flask import request
from flask_restx import Resource, Namespace

from dao.model.director import DirectorSchema
from implemented import director_service
from service.decorators import admin_required, auth_required

director_ns = Namespace('directors')


@director_ns.route('/')
class DirectorsView(Resource):

    def get(self):
        rs = director_service.get_all()
        res = DirectorSchema(many=True).dump(rs)
        return res, 200

    @auth_required
    def post(self):
        req_json = request.json
        director = director_service.create(req_json)
        return "", 201, {"location": f"/directors/{director.id}"}


@director_ns.route('/<int:bid>')
class DirectorView(Resource):
    def get(self, bid):
        r = director_service.get_one(bid)
        sm_d = DirectorSchema().dump(r)
        return sm_d, 200

    @admin_required
    def put(self, bid):
        req_json = request.json
        if "id" not in req_json:
            req_json["id"] = bid
        director_service.update(req_json)
        return "", 204

    @admin_required
    def delete(self, bid):
        director_service.delete(bid)
        return "", 204
