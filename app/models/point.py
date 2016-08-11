from app import db
from app import GisApp
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from sqlalchemy.dialects.postgresql import JSON

class Point(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    geom = db.Column(Geometry('POINT'))
    properties = db.Column(JSON)
    revised = db.Column(db.Boolean)
    approved = db.Column(db.Boolean)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    submission = db.relationship('Submission', back_populates='points')
    merged_to = db.Column(db.Integer, db.ForeignKey('point.id'))
    pictures = db.relationship('Picture')

    def serialize(self):
        return {
            'id': self.id,
            'latlng': [self.shape().x, self.shape().y],
            'tags' : self.properties.get('tags', {}),
            'osmid': self.properties.get('osmid', None),
            'pictures' : list(map((lambda p: p.serialize()), self.pictures)),
            'revised': self.revised
        }

    def serialize_with_properties(self):
        return {
            'id': self.id,
            'latlng': [self.shape().x, self.shape().y],
            'properties' : self.properties,
            'pictures' : list(map((lambda p: p.serialize()), self.pictures))
        }

    def shape(self):
        return to_shape(self.geom)

    def postToOSM(self):
        GisApp.osmApiClient.ChangesetCreate()
        createdNode = GisApp.osmApiClient.NodeCreate({
            "lon": self.longitude,
            "lat": self.latitude,
            "tag": self.properties["tags"] if ("tags" in self.properties.keys()) else {}
        })
        self.properties['osmid'] = createdNode['id'] # osmid after creation
        db.session.query(Point).filter(Point.id == self.id).update({
            'properties': self.properties
        })
        db.session.commit()
        GisApp.osmApiClient.ChangesetClose()

    def updateOnOSM(self):
        GisApp.osmApiClient.ChangesetCreate()
        # Get the Node's current OSM data so that we have the version number to
        #   perform the update request.
        currentOsmNode = GisApp.osmApiClient.NodeGet(self.properties['osmid'])
        updatedOsmNode = GisApp.osmApiClient.NodeUpdate({
            "id": self.properties['osmid'],
            "lon": self.longitude,
            "lat": self.latitude,
            "version": currentOsmNode['version'],
            "tag": self.properties["tags"] if ("tags" in self.properties.keys()) else {}
        })
        GisApp.osmApiClient.ChangesetClose()

    def deleteOnOSM(self):
        GisApp.osmApiClient.ChangesetCreate()
        # Get the Node's current OSM data so that we have the version number to
        #   perform the update request.
        currentOsmNode = GisApp.osmApiClient.NodeGet(self.properties['osmid'])
        GisApp.osmApiClient.NodeDelete({
            "id": self.properties['osmid'],
            "lon": self.longitude,
            "lat": self.latitude,
            "version": currentOsmNode['version'],
        })
        GisApp.osmApiClient.ChangesetClose()

    @property
    def latitude(self):
        return self.shape().x

    @property
    def longitude(self):
        return self.shape().y
