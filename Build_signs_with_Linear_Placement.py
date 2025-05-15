"""
Script to place signs alogn an alignment using IfcLinearPlacement

Richard Brice, PE
WSDOT Bridge and Structures Office
"""

import ifcopenshell
import ifcopenshell.api.alignment
import math

def find_sign_type(mutcd_code,size,library):
    for type in library.Declares[0].RelatedDefinitions:
        size_in_desc = True if len(size) == 0 or size in type.Description else False
        if type.Name == mutcd_code and size_in_desc:
            return type
    print(f"{mutcd_code} - Sign type not found")
    return None

def build_model():
    model = ifcopenshell.file(schema="IFC4X3")
    project = model.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="Linear Placement of Signs")

    length_unit = ifcopenshell.api.unit.add_conversion_based_unit(model,name="foot")
    ifcopenshell.api.unit.assign_unit(model,units=[length_unit])
        
    site = model.createIfcSite(GlobalId=ifcopenshell.guid.new(),Name="Test Site")
    ifcopenshell.api.aggregate.assign_object(model,relating_object=project,products=[site])

    # create simple alignment using ifcos alignment api - single horizontal curve
    R = 1000.
    points = [(0.,0.),(0.,R),(R,R)]
    radii = [R]

    alignment = ifcopenshell.api.alignment.create_alignment_by_pi_method(model,"Ali",points,radii)
    ifcopenshell.api.spatial.reference_structure(model,products=[alignment],relating_structure=site) # alignment referenced in site
    ifcopenshell.api.alignment.create_geometric_representation(model,alignment) # generate geometric representat of alignment from semantic definition
    ifcopenshell.api.alignment.add_stationing_to_alignment(model,alignment,100.0,2,2) # create stationing referent

    curve = ifcopenshell.api.alignment.get_curve(alignment) # get alignment geometry curve for linear placement basis


    # get the sign type for the library
    library_file = ifcopenshell.open("MUTCD_Sign_Library.ifc")
    libraries = library_file.by_type("IfcProjectLibrary")

    # for this example, use the unit signs library so the geometry can be properly scaled for feet units
    library_type = 0 # 0 = unit signs, 1 = explicit signs

    chevron_sign_type = find_sign_type("W1-8R","",libraries[library_type]) # get sign type for right curve chevron
    chevron_sign_type = ifcopenshell.file.add(model,chevron_sign_type)
    model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project,RelatedDefinitions=[chevron_sign_type])

    geometric_representation_context = ifcopenshell.api.context.add_context(model,context_type="Model")
    body_model_context = ifcopenshell.api.context.add_context(model,context_type="Model",context_identifier="Body",target_view="MODEL_VIEW",parent=geometric_representation_context)

    # the sign library is defined with length as inch, but this model has length as foot
    # when adding the IfcSignType to this model, the values are converted from inch to foot.
    # a unit length of 1" (the unit length dimension in the sign library) is now 0.083333'
    # for a 3'x4' sign X and Y scales needs to be 36 and 48
    mapping_target = model.createIfcCartesianTransformationOperator3DnonUniform(LocalOrigin=model.createIfcCartesianPoint((0.,0.,0.)),Scale=36.,Scale2=48.,Scale3=0.5)

    sign_mapped_item = model.createIfcMappedItem(MappingSource=chevron_sign_type.RepresentationMaps[0],MappingTarget=mapping_target)
    sign_rep = model.createIfcShapeRepresentation(ContextOfItems=body_model_context,RepresentationIdentifier="Body",RepresentationType="MappedRepresentation",Items=[sign_mapped_item])
    sign_product_rep = model.createIfcProductDefinitionShape(Representations=[sign_rep])

    signs = []
    
    start = 500.0
    inc = 100.0

    for i in range(10):
        dist_along = start + i * inc
        angle = dist_along/R
        
        pde = model.createIfcPointByDistanceExpression(DistanceAlong=model.createIfcLengthMeasure(dist_along),OffsetLateral=20.0,OffsetVertical=8.0,BasisCurve=curve)
        a2pl = model.createIfcAxis2PlacementLinear(Location=pde,Axis=model.createIfcDirection((-math.sin(angle),-math.cos(angle),0.))) # makes sign axis vector parallel to curve tangeht
        lp = model.createIfcLinearPlacement(site.ObjectPlacement,RelativePlacement=a2pl)

        sign = model.createIfcSign(GlobalId=ifcopenshell.guid.new(),Name=f"Chevron {i}",ObjectPlacement=lp,Representation=sign_product_rep)
        signs.append(sign)


    ifcopenshell.api.spatial.assign_container(model,relating_structure=site,products=signs)
    
    model.createIfcRelDefinesByType(GlobalId=ifcopenshell.guid.new(),RelatedObjects=signs,RelatingType=chevron_sign_type)

    model.write("Signs_with_Linear_Placement.ifc")
    
if __name__ == "__main__":
    build_model()
    print("Done")
