"""
Script to define stop signs at an All Way stop intersection

Richard Brice, PE
WSDOT Bridge and Structures Office
"""

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.api.classification

def find_sign_type(mutcd_code,size,library):
    for type in library.Declares[0].RelatedDefinitions:
        if type.Name == mutcd_code and size in type.Description:
            return type
    print(f"{mutcd_code} - Sign type not found")
    return None

def build_model():
    # create IFC model
    model = ifcopenshell.file(schema="IFC4X3")

    # create the IfcProject
    project = model.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="All Way Stop Test Project")

    # set up system of units (must be done after IfcProject is created)
    length_unit = ifcopenshell.api.unit.add_conversion_based_unit(model,name="inch")
    ifcopenshell.api.unit.assign_unit(model,units=[length_unit])

    # set up a coordinate system for the site.
    # objects will be placed relative to the site origin.
    site_placement = model.createIfcLocalPlacement(
        RelativePlacement=model.createIfcAxis2Placement3D(
            Location=model.createIfcCartesianPoint((120.,120.,0.))
            )
        )

    # create the site and aggregate it to the project
    site = model.createIfcSite(GlobalId=ifcopenshell.guid.new(),Name="Test Site",ObjectPlacement=site_placement)
    ifcopenshell.api.aggregate.assign_object(model,relating_object=project,products=[site])



    # load the MUTCD sign library and get the IfcProjectLibrary entries
    library_file = ifcopenshell.open("MUTCD_Sign_Library.ifc")
    libraries = library_file.by_type("IfcProjectLibrary")

    # for this example, use the explicit signs library
    library_type = 1 # 0 = unit signs, 1 = explicit signs

    # find the IfcSignType for a 36x36 R1-1 (Stop sign) and 18x6 R1-3P (All Way sign)
    stop_sign_type = find_sign_type("R1-1","36x36",libraries[library_type])
    allway_sign_type = find_sign_type("R1-3P","18x6",libraries[library_type])

    # THIS IS IMPORTANT - add the IfcTypeObject objects to the model and use the returned value
    # (undefined behavior results when using objects from one model in another model)
    stop_sign_type = ifcopenshell.file.add(model,stop_sign_type)
    allway_sign_type = ifcopenshell.file.add(model,allway_sign_type)
          
    # relate type declaration with project
    model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project,RelatedDefinitions=[stop_sign_type,allway_sign_type])

    # set up geometric representation context
    geometric_representation_context = ifcopenshell.api.context.add_context(model,context_type="Model")
    body_model_context = ifcopenshell.api.context.add_context(model,context_type="Model",context_identifier="Body",target_view="MODEL_VIEW",parent=geometric_representation_context)


    # map IfcSignType geometry to a local origin of (0,0,0)
    mapping_target = model.createIfcCartesianTransformationOperator3D(LocalOrigin=model.createIfcCartesianPoint((0.,0.,0.)))


    # assume intersection to be 60x60 and we want the signs to be 5 from the edge
    # so 35ft for x,y location
    x = 35.*12. # convert to inches
    y = 35.*12.

    # create placement objects for the four corners of the intersection
    # place relative to site_placement
    ne_placement = model.createIfcLocalPlacement(
        PlacementRelTo=site.ObjectPlacement,
        RelativePlacement=model.createIfcAxis2Placement3D(
            Location=model.createIfcCartesianPoint((x,y,0.)),
            RefDirection=model.createIfcDirection((0.,1.,0.)),
            Axis=model.createIfcDirection((0.,0.,1.))
            )
        )

    nw_placement = model.createIfcLocalPlacement(
        PlacementRelTo=site.ObjectPlacement,
        RelativePlacement=model.createIfcAxis2Placement3D(
            Location=model.createIfcCartesianPoint((-x,y,0.)),
            RefDirection=model.createIfcDirection((-1.,0.,0.)),
            Axis=model.createIfcDirection((0.,0.,1.))
            )
        )

    sw_placement = model.createIfcLocalPlacement(
        PlacementRelTo=site.ObjectPlacement,
        RelativePlacement=model.createIfcAxis2Placement3D(
            Location=model.createIfcCartesianPoint((-x,-y,0.)),
            RefDirection=model.createIfcDirection((0.,-1.,0.)),
            Axis=model.createIfcDirection((0.,0.,1.))
            )
        )

    se_placement = model.createIfcLocalPlacement(
        PlacementRelTo=site.ObjectPlacement,
        RelativePlacement=model.createIfcAxis2Placement3D(
            Location=model.createIfcCartesianPoint((x,-y,0.)),
            RefDirection=model.createIfcDirection((1.,0.,0.)),
            Axis=model.createIfcDirection((0.,0.,1.))
            )
        )


    # create geometric representations of the signs
    stop_sign_mapped_item = model.createIfcMappedItem(MappingSource=stop_sign_type.RepresentationMaps[0],MappingTarget=mapping_target)
    stop_sign_rep = model.createIfcShapeRepresentation(ContextOfItems=body_model_context,RepresentationIdentifier="Body",RepresentationType="MappedRepresentation",Items=[stop_sign_mapped_item])
    stop_sign_product_rep = model.createIfcProductDefinitionShape(Representations=[stop_sign_rep])

    allway_sign_mapped_item = model.createIfcMappedItem(MappingSource=allway_sign_type.RepresentationMaps[0],MappingTarget=mapping_target)
    allway_sign_rep = model.createIfcShapeRepresentation(ContextOfItems=body_model_context,RepresentationIdentifier="Body",RepresentationType="MappedRepresentation",Items=[allway_sign_mapped_item])
    allway_sign_product_rep = model.createIfcProductDefinitionShape(Representations=[allway_sign_rep])

    # create sign assemblies
    placements=[ne_placement,nw_placement,sw_placement,se_placement]
    names=["NE","NW","SW","SE"]
    stop_signs = []
    allway_signs = []
    for placement,name in zip(placements,names):
        sign_assembly = model.createIfcElementAssembly(GlobalId=ifcopenshell.guid.new(),Name=f"Sign in {name} corner",ObjectPlacement=placement,AssemblyPlace="SITE",PredefinedType="USERDEFINED",ObjectType="SIGNASSEMBLY")

        # the signs in the MUTCD library are defined in the X-Y plane with the Z-direction being normal to the face of the sign
        # think of the sign as being face-up on the ground.
        # when the sign is installed, on a post for example, the local Z-direction should point in the -Y direction
        # that is, if you are facing North and looking at the sign face, the local Z-direction vector is pointing
        # at your face, which is equal to the -Y direction of your coordinate system
        sign_face_direction = model.createIfcDirection((0.,-1.,0.))

        # place the stop sign so its center point is 8ft above the ground
        stop_sign_location = model.createIfcCartesianPoint((0.,0.,8.*12.))
        stop_sign_axis2placement = model.createIfcAxis2Placement3D(Location=stop_sign_location,Axis=sign_face_direction)


        # place the All Way sign so it is 1" beneath the bottom of the stop sign
        allway_sign_location = model.createIfcCartesianPoint((0.,0.,8.*12. - 36./2. - 6./2 - 1.))
        allway_sign_axis2placement = model.createIfcAxis2Placement3D(Location=allway_sign_location,Axis=sign_face_direction)

        # create the stop sign
        stop_sign_local_placement = model.createIfcLocalPlacement(PlacementRelTo=placement,RelativePlacement=stop_sign_axis2placement)
        stop_sign = model.createIfcSign(GlobalId=ifcopenshell.guid.new(),Name="Stop Sign",ObjectPlacement=stop_sign_local_placement,Representation=stop_sign_product_rep)
        stop_signs.append(stop_sign)

        # create the All Way sign
        allway_sign_local_placement = model.createIfcLocalPlacement(PlacementRelTo=placement,RelativePlacement=allway_sign_axis2placement)
        allway_sign = model.createIfcSign(GlobalId=ifcopenshell.guid.new(),Name="All Way Sign",ObjectPlacement=allway_sign_local_placement,Representation=allway_sign_product_rep)
        allway_signs.append(allway_sign)

        # aggregate the signs into an element assembly
        ifcopenshell.api.aggregate.assign_object(model,products=[stop_sign,allway_sign],relating_object=sign_assembly)    

        # put the element assembly into the spatial structure of site
        ifcopenshell.api.spatial.assign_container(model,relating_structure=site,products=[sign_assembly])


    # relate all the IfcSign objects to their respective IfcSignType
    stop_sign_rel = model.createIfcRelDefinesByType(GlobalId=ifcopenshell.guid.new(),RelatedObjects=stop_signs,RelatingType=stop_sign_type)
    allway_sign_rel = model.createIfcRelDefinesByType(GlobalId=ifcopenshell.guid.new(),RelatedObjects=allway_signs,RelatingType=allway_sign_type)


    model.write("All_Way_Stop.ifc")

if __name__ == "__main__":
    build_model()
    print("Done")
