# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        # Populate BBox, Link, Attribute and Style from GeoServer
        # First, set the resource base's bbox fields to avoid geometry errors
        # Then, use the current Layer.save method to trigger the signals that will populate the rest of the data (eg: geoserver_post_save signal)
        from geonode.layers.models import Layer
        from geonode.layers.models import geoserver_pre_save
        from geonode.utils import bbox_to_wkt

        for layerorm in orm.Layer.objects.all():
            # we need to run the save method on a real layer instance as it uses model methods and properties from the base class, ResourceBase
            layer = Layer.objects.get(pk=layerorm.resourcebase_ptr_id)
            # call the geoserver_pre_save signal to populate the layer's bbox fields from geoserver
            geoserver_pre_save(layer, sender=layer)

            # Save bbox and csw_wkt_geometry fields to resourcebase or we will get geometry errors when calling layer.save()
            rb = orm['base.resourcebase'].objects.get(pk=layerorm.resourcebase_ptr_id)
            rb.bbox_x0 = layer.bbox_x0
            rb.bbox_x1 = layer.bbox_x1
            rb.bbox_y0 = layer.bbox_y0
            rb.bbox_y1 = layer.bbox_y1
            rb.csw_wkt_geometry = bbox_to_wkt(layer.bbox_x0, layer.bbox_x1, layer.bbox_y0, layer.bbox_y1, layer.srid)
            rb.save()

            # Save the "real layer" instance, which will trigger the geoserver_post_save signal
            layer.save()

    def backwards(self, orm):
        pass

    models = {
        'actstream.action': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Action'},
            'action_object_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_object'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'action_object_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'actor_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actor'", 'to': "orm['contenttypes.ContentType']"}),
            'actor_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 4, 10, 33, 3, 769539)'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 4, 10, 33, 3, 767771)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 4, 10, 33, 3, 767709)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to'", 'symmetrical': 'False', 'through': "orm['relationships.Relationship']", 'to': "orm['auth.User']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'base.contactrole': {
            'Meta': {'unique_together': "(('contact', 'resource', 'role'),)", 'object_name': 'ContactRole'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Profile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.ResourceBase']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['people.Role']"})
        },
        u'base.link': {
            'Meta': {'object_name': 'Link'},
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mime': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.ResourceBase']"}),
            'url': ('django.db.models.fields.TextField', [], {'unique': 'True', 'max_length': '1000'})
        },
        u'base.region': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Region'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'base.resourcebase': {
            'Meta': {'object_name': 'ResourceBase'},
            'abstract': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bbox_x0': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'bbox_x1': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'bbox_y0': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'bbox_y1': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '10', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.TopicCategory']", 'null': 'True', 'blank': 'True'}),
            'constraints_other': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['people.Profile']", 'through': u"orm['base.ContactRole']", 'symmetrical': 'False'}),
            'csw_anytext': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'csw_insert_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'csw_mdsource': ('django.db.models.fields.CharField', [], {'default': "'local'", 'max_length': '256'}),
            'csw_schema': ('django.db.models.fields.CharField', [], {'default': "'http://www.isotc211.org/2005/gmd'", 'max_length': '64'}),
            'csw_type': ('django.db.models.fields.CharField', [], {'default': "'dataset'", 'max_length': '32'}),
            'csw_typename': ('django.db.models.fields.CharField', [], {'default': "'gmd:MD_Metadata'", 'max_length': '32'}),
            'csw_wkt_geometry': ('django.db.models.fields.TextField', [], {'default': "'POLYGON((-180 -90,-180 90,180 90,180 -90,-180 -90))'"}),
            'data_quality_statement': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_type': ('django.db.models.fields.CharField', [], {'default': "'publication'", 'max_length': '255'}),
            'distribution_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'distribution_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'edition': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'eng'", 'max_length': '3'}),
            'maintenance_frequency': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'metadata_uploaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'metadata_xml': ('django.db.models.fields.TextField', [], {'default': '\'<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd"/>\'', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'purpose': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['base.Region']", 'symmetrical': 'False'}),
            'restriction_code_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.RestrictionCodeType']", 'null': 'True', 'blank': 'True'}),
            'spatial_representation_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.SpatialRepresentationType']", 'null': 'True', 'blank': 'True'}),
            'srid': ('django.db.models.fields.CharField', [], {'default': "'EPSG:4326'", 'max_length': '255'}),
            'supplemental_information': ('django.db.models.fields.TextField', [], {'default': "u'No information provided'"}),
            'temporal_extent_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'temporal_extent_start': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['base.Thumbnail']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        u'base.restrictioncodetype': {
            'Meta': {'ordering': "('identifier',)", 'object_name': 'RestrictionCodeType'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            'gn_description': ('django.db.models.fields.TextField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'is_choice': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'base.spatialrepresentationtype': {
            'Meta': {'ordering': "('identifier',)", 'object_name': 'SpatialRepresentationType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gn_description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'is_choice': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'base.thumbnail': {
            'Meta': {'object_name': 'Thumbnail'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thumb_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'thumb_spec': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0', 'null': 'True'})
        },
        u'base.topiccategory': {
            'Meta': {'ordering': "('identifier',)", 'object_name': 'TopicCategory'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'gn_description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'default': "'location'", 'max_length': '255'}),
            'is_choice': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'layers.attribute': {
            'Meta': {'object_name': 'Attribute'},
            'attribute': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'attribute_label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'attribute_type': ('django.db.models.fields.CharField', [], {'default': "'xsd:string'", 'max_length': '50'}),
            'average': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '255', 'null': 'True'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_stats_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attribute_set'", 'to': u"orm['layers.Layer']"}),
            'max': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '255', 'null': 'True'}),
            'median': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '255', 'null': 'True'}),
            'min': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '255', 'null': 'True'}),
            'stddev': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '255', 'null': 'True'}),
            'sum': ('django.db.models.fields.CharField', [], {'default': "'NA'", 'max_length': '255', 'null': 'True'}),
            'unique_values': ('django.db.models.fields.TextField', [], {'default': "'NA'", 'null': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'layers.layer': {
            'Meta': {'object_name': 'Layer', '_ormbases': [u'base.ResourceBase']},
            'default_style': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'layer_default_style'", 'null': 'True', 'to': u"orm['layers.Style']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'popular_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'resourcebase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['base.ResourceBase']", 'unique': 'True', 'primary_key': 'True'}),
            'share_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'store': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'storeType': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'styles': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'layer_styles'", 'symmetrical': 'False', 'to': u"orm['layers.Style']"}),
            'typename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'workspace': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'layers.style': {
            'Meta': {'object_name': 'Style'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'sld_body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sld_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sld_url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'sld_version': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'workspace': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'people.profile': {
            'Meta': {'object_name': 'Profile'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'delivery': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'profile': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'profile'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'voice': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'people.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'relationships.relationship': {
            'Meta': {'ordering': "('created',)", 'unique_together': "(('from_user', 'to_user', 'status', 'site'),)", 'object_name': 'Relationship'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_users'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'relationships'", 'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['relationships.RelationshipStatus']"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_users'", 'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'null': 'True', 'blank': 'True'})
        },
        'relationships.relationshipstatus': {
            'Meta': {'ordering': "('name',)", 'object_name': 'RelationshipStatus'},
            'from_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'symmetrical_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['layers']
