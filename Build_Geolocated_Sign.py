import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.api.georeference
import math

# create IFC model
model = ifcopenshell.file(schema="IFC4X3")

# basic model setup for project and site
project = model.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="Geolocated Sign Example")
site = model.createIfcSite(GlobalId=ifcopenshell.guid.new(),Name="Example Project Site")
ifcopenshell.api.aggregate.assign_object(model,relating_object=project,products=[site])

# set up system of units (must be done after IfcProject is created)
length_unit = ifcopenshell.api.unit.add_conversion_based_unit(model,name="foot")
ifcopenshell.api.unit.assign_unit(model,units=[length_unit])

# set up geometric representation context
geometric_representation_context = ifcopenshell.api.context.add_context(model,context_type="Model")
body_model_context = ifcopenshell.api.context.add_context(model,context_type="Model",context_identifier="Body",target_view="MODEL_VIEW",parent=geometric_representation_context)

ifcopenshell.api.georeference.add_georeferencing(model)
ifcopenshell.api.georeference.edit_georeferencing(model,projected_crs=
                                                  {"Name":"EPSG:2927",
                                                   "Description":"Washington South (ftUS)",
                                                   "GeodeticDatum":"NAD83(HARN)",
                                                   "MapProjection":"Lambert Conformal Conic 2SP"},
                                                 coordinate_operation={
                                                     #"Eastings":1213972.831863016,
                                                     #"Northings":888107.1310520759,
                                                     "Eastings":1213972.815843322,
                                                     "Northings":888107.1809384043,
                                                     "XAxisAbscissa":1.,
                                                     "XAxisOrdinate":0.,
                                                     "Scale":0.999998000004 # convert international feet (model) to us survey feet (datum)
                                                 })

#
# create IfcSignType that acts as a predefined cell
#

# create a geometric representation (using a dummy 30x36in square in a X-Y plane with 0,0 at the bottom centerpoint)
points = model.createIfcCartesianPointList3D(CoordList=[(0.,0.,0.),(1.25,0.,0.),(1.25,3.,0.),(-1.25,3.,0.),(-1.25,0.,0.)])
indicies = [(1,2,3),(3,4,1),(4,5,1)]
sign_panel = model.createIfcTriangulatedFaceSet(Coordinates=points,CoordIndex=indicies)
shape_representation = model.createIfcShapeRepresentation(ContextOfItems=body_model_context,RepresentationIdentifier="Body",RepresentationType="Tessellation",Items=[sign_panel])

# define the sign face image
image_texture = model.createIfcImageTexture(
    RepeatS = False,
    RepeatT = False,
    Mode = "DIFFUSE",
    URLReference = r".\R03-08L Advance Intersection Lane Control (2 lanes) 30x30.png"
)

#texture_vertex_list = model.createIfcTextureVertexList(TexCoordsList=[(0.,0.),(0.5,0.),(1.,0.),(1.,1.),(0.,1.)])
#texture_vertex_list = model.createIfcTextureVertexList(TexCoordsList=[(0.5,0.),(1.,0.),(1.,1.),(0.,1.),(0.,0.)])

#indexed_triangule_texture_map = model.createIfcIndexedTriangleTextureMap(
#    Maps=[image_texture],
#    MappedTo=sign_panel,
#    TexCoords=texture_vertex_list,
#    TexCoordIndex=((1,2,3),(3,4,1),(4,5,1))
#    #TexCoordIndex=((2,3,4),(4,5,2),(5,1,2))
#)

#shading = model.createIfcSurfaceStyleShading(
#    SurfaceColour = model.createIfcColourRgb(Red=0.,Green=0.,Blue=0.)
#)
shading = model.createIfcSurfaceStyleRendering(
    SurfaceColour = model.createIfcColourRgb(Red=0.,Green=0.,Blue=0.),
    ReflectanceMethod="NOTDEFINED"
)

surface_with_texture = model.createIfcSurfaceStyleWithTextures(
    Textures=[image_texture]
)

texture_coordinate_generator = model.createIfcTextureCoordinateGenerator([image_texture],'COORD')
    
surface_style = model.createIfcSurfaceStyle(
    Side="POSITIVE",
    Styles=[shading,surface_with_texture]
)

styled_item = model.createIfcStyledItem(
    Item=sign_panel,
    Styles=[surface_style]
)

# the geometric representation is reusable and is placed in an IfcRepresentationMap. Use (0,0,0) as a simple origin
origin =  model.createIfcAxis2Placement3D(Location=model.createIfcCartesianPoint((0.,0.,0.)))
rep_map = model.createIfcRepresentationMap(MappingOrigin=origin,MappedRepresentation=shape_representation)

# create the IfcSignType
sign_type = model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name="U Turn Only",PredefinedType="PICTORAL",Tag="R3-8L",RepresentationMaps=[rep_map])

# relate type declaration with project
rel_declares = model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project,RelatedDefinitions=[sign_type])

#
# create a single IfcSign that is based on the IfcSignType definition
#

# create geometric representation of the sign by mapping the IfcSignType representation
mapping_target = model.createIfcCartesianTransformationOperator3D(LocalOrigin=model.createIfcCartesianPoint((0.,0.,0.)))
mapped_item = model.createIfcMappedItem(MappingSource=sign_type.RepresentationMaps[0],MappingTarget=mapping_target)
rep = model.createIfcShapeRepresentation(ContextOfItems=body_model_context,RepresentationIdentifier="Body",RepresentationType="MappedRepresentation",Items=[mapped_item])
product_rep = model.createIfcProductDefinitionShape(Representations=[rep])

# define location of the sign
# place the sign at (0,0,0) in the engineering coordinate system
sign_location = model.createIfcCartesianPoint((0.,0.,0.))
# the sign geometry is defined in the X-Y plane in IfcSignType. the Z-direction is normal to the sign face
# set the direction of the sign face by defining the direction of the Axis vector
sign_face_direction = model.createIfcDirection((math.sin(math.radians(116.10647322160855)),math.cos(math.radians(116.10647322160855)),0.)) # normal of sign face is in the -Y direction
axis2placement = model.createIfcAxis2Placement3D(Location=sign_location,Axis=sign_face_direction)
local_placement = model.createIfcLocalPlacement(RelativePlacement=axis2placement)

#define the sign
sign = model.createIfcSign(GlobalId=ifcopenshell.guid.new(),Name="Example Sign",Description="U-Turn Sign NE Bothell Way Easbound @ 80th Ave NE",ObjectPlacement=local_placement,Representation=product_rep)
rel = model.createIfcRelDefinesByType(GlobalId=ifcopenshell.guid.new(),RelatedObjects=[sign],RelatingType=sign_type)

# add sign to spatial structure of the model
ifcopenshell.api.spatial.assign_container(model,relating_structure=site,products=[sign])

model.write("C:/Users/bricer/OneDrive - Washington State Department of Transportation/Desktop/GeolocatedSign.ifc")
print("Done!")
