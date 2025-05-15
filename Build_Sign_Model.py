import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.api.classification

library_file = ifcopenshell.open("MUTCD_Sign_Library.ifc")
libraries = library_file.by_type("IfcProjectLibrary")

library_type = 1 # 0 = unit signs, 1 = explicit signs
mutcd_code = "R1-2" # Yield
size = "60x60x60"

sign_type=None

library = libraries[library_type]
for type in library.Declares[0].RelatedDefinitions:
    if type.Name == mutcd_code and size in type.Description:
        sign_type = type
        break

#sign_type = library.Declares[0].RelatedDefinitions[0]


# create IFC model
model = ifcopenshell.file(schema="IFC4X3")

# basic model setup for project and site
project = model.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="Sign Test Project")
site = model.createIfcSite(GlobalId=ifcopenshell.guid.new(),Name="Test Site")
ifcopenshell.api.aggregate.assign_object(model,relating_object=project,products=[site])

# set up system of units (must be done after IfcProject is created)
length_unit = ifcopenshell.api.unit.add_conversion_based_unit(model,name="inch")
ifcopenshell.api.unit.assign_unit(model,units=[length_unit])

# THIS IS IMPORTANT - must add the type to the model so it gets its IDs updated
sign_type = ifcopenshell.file.add(model,sign_type)
      
model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project,RelatedDefinitions=[sign_type])


# set up geometric representation context
geometric_representation_context = ifcopenshell.api.context.add_context(model,context_type="Model")
body_model_context = ifcopenshell.api.context.add_context(model,context_type="Model",context_identifier="Body",target_view="MODEL_VIEW",parent=geometric_representation_context)

# add the wsdotsigns classification system to the model
wsdot_signs = ifcopenshell.api.classification.add_classification(model,classification="wsdotsigns")
wsdot_signs.Source = "wsdot_test_dict" # classification is from the wsdot_test_dict bSDD
wsdot_signs.Edition="0.1.0"
wsdot_signs.Specification="https://search.bsdd.buildingsmart.org/uri/wsdot/wsdotsigns/0.1.0" # location of the bSDD


# add properties to the sign type that are common for all instances of this type
sign_base_quantities = ifcopenshell.api.pset.add_pset(model,product=sign_type,name="Qset_SignBaseQuantities")
ifcopenshell.api.pset.edit_pset(model,pset=sign_base_quantities,properties={"Height":36.0,"Width":36.0})

pictorial_sign_quantities = ifcopenshell.api.pset.add_pset(model,product=sign_type,name="Qset_PictorialSignQuantities")
ifcopenshell.api.pset.edit_pset(model,pset=pictorial_sign_quantities,properties={"Area":1296.0,"SignArea":1296.0})


# relate type declaration with project
rel_declares = model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project,RelatedDefinitions=[sign_type])

# classify the IfcSignType as a wsdotGuideSign
guide_sign = model.createIfcClassificationReference(Location="https://identifier.buildingsmart.org/uri/wsdot/wsdotsigns/0.1.0/class/wsdotGuideSign",Identification="wsdotGuideSign")
ifcopenshell.api.classification.add_reference(model,products=[sign_type],classification=wsdot_signs,reference=guide_sign)

#
# create a single IfcSign that is based on the IfcSignType definition
#

# create geometric representation of the sign by mapping the IfcSignType representation
#mapping_target = model.createIfcCartesianTransformationOperator3DnonUniform(LocalOrigin=model.createIfcCartesianPoint((0.,0.,0.)),Scale=36.0,Scale2=36.0,Scale3=0.5)
mapping_target = model.createIfcCartesianTransformationOperator3DnonUniform(LocalOrigin=model.createIfcCartesianPoint((0.,0.,0.)),Scale3=0.5)
mapped_item = model.createIfcMappedItem(MappingSource=sign_type.RepresentationMaps[0],MappingTarget=mapping_target)
rep = model.createIfcShapeRepresentation(ContextOfItems=body_model_context,RepresentationIdentifier="Body",RepresentationType="MappedRepresentation",Items=[mapped_item])
product_rep = model.createIfcProductDefinitionShape(Representations=[rep])

# define location of the sign (using a dummy location of 30,40,50) - this is in a local project coordinate system. It can be relative to other objects
# such as a sign post or an element assembly. The placement could be in cartesian coordinates or using linear referencing system
sign_location = model.createIfcCartesianPoint((30.,40.,50.))
# the sign geometry is defined in the X-Y plane in IfcSignType. the Z-direction is normal to the sign face
# set the direction of the sign face by defining the direction of the Axis vector
sign_face_direction = model.createIfcDirection((0.,-1.,0.)) # normal of sign face is in the -Y direction
axis2placement = model.createIfcAxis2Placement3D(Location=sign_location,Axis=sign_face_direction)
local_placement = model.createIfcLocalPlacement(RelativePlacement=axis2placement)

#define the sign
sign = model.createIfcSign(GlobalId=ifcopenshell.guid.new(),Name="Sign_1",ObjectPlacement=local_placement,Representation=product_rep)
rel = model.createIfcRelDefinesByType(GlobalId=ifcopenshell.guid.new(),RelatedObjects=[sign],RelatingType=sign_type)

# add properties to the sign that are specific to this instance
sign_set = ifcopenshell.api.pset.add_pset(model,product=sign,name="Sign_Set")
ifcopenshell.api.pset.edit_pset(model,pset=sign_set,properties={"sign_facing":"North","sign_side_of_rd":"R"})
sign_set.HasProperties[0].Specification="https://identifier.buildingsmart.org/uri/wsdot/wsdotsigns/0.1.0/prop/sign_facing"
sign_set.HasProperties[1].Specification="https://identifier.buildingsmart.org/uri/wsdot/wsdotsigns/0.1.0/prop/sign_side_of_rd"

# add sign to spatial structure of the model
ifcopenshell.api.spatial.assign_container(model,relating_structure=site,products=[sign])

model.write("Signs.ifc")
print("Done")
