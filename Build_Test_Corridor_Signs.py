"""
Script to build sign model for ADCMS grant project test corridor.

Richard Brice, PE
WSDOT Bridge and Structures Office
"""
import ifcopenshell
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.spatial
import csv
import math
from collections import defaultdict
from collections import Counter


# uncomment everything related to this list to dump a list
# of sign types, by mutcd code, that the MUTCD library does not
# have. The MUTCD library is something I made up from another script
# and it only covers a few types of signs. This list will help
# identify the most common sign types used, but not supported
# by the library
#mutcd_code_not_supported_types=[]


def find_sign_type(mutcd_code,size,library):
    for type in library.Declares[0].RelatedDefinitions:
        size_in_desc = True if len(size) == 0 or size in type.Description else False
        if type.Name == mutcd_code and size_in_desc:
            return type

#    mutcd_code_not_supported_types.append(mutcd_code)    
    return None
    

def generate_polygon(width,height,sides,start_angle):
    angle_step = 2*math.pi/sides
    X = 0.5*width/math.cos(math.pi/sides)
    Y = 0.5*height/math.cos(math.pi/sides)
    points = [
        (
            X*math.cos(start_angle + i*angle_step),
            Y*math.sin(start_angle + i*angle_step)
        )
        for i in range(sides)
    ]

    return points
    

def create_sign_representation(name,model,context,width,height,sides,start_angle):
    coords = generate_polygon(width,height,sides,start_angle)
    points = model.createIfcCartesianPointList2D(CoordList=coords)
    indicies = [(i,i+1) for i in range(1,sides)]
    indicies.append((sides,1))
    segments=[]
    for i in indicies:
        segments.append(model.createIfcLineIndex(i))

    curve = model.createIfcIndexedPolyCurve(Points=points,Segments=segments)
    profile = model.createIfcArbitraryClosedProfileDef(ProfileName=name, ProfileType="AREA",OuterCurve=curve)
    solid = model.createIfcExtrudedAreaSolid(SweptArea=profile,ExtrudedDirection=model.createIfcDirection((0.,0.,1.)),Depth=1./12.)

    shape_representation = model.createIfcShapeRepresentation(ContextOfItems=context,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])

    return shape_representation


def build_signs():
    sign_file = "Sign_Face.csv"
    
    # get the sign type for the library
    library_file = ifcopenshell.open("MUTCD_Sign_Library.ifc")
    libraries = library_file.by_type("IfcProjectLibrary")

    # for this example, use the unit signs library so the geometry can be properly scaled for feet units
    library_type = 1 # 0 = unit signs, 1 = explicit signs

    signs_found = 0
    signs_not_found = 0
    signs_modeled = 0

    model = ifcopenshell.file(schema="IFC4X3")
    project = model.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="WSDOT ADCMS Grant Test Corridor Sign Model")

    length_unit = ifcopenshell.api.unit.add_conversion_based_unit(model,name="foot")
    ifcopenshell.api.unit.assign_unit(model,units=[length_unit])
        
    site = model.createIfcSite(GlobalId=ifcopenshell.guid.new(),Name="Test Site")
    ifcopenshell.api.aggregate.assign_object(model,relating_object=project,products=[site])

    # set up geometric representation context
    geometric_representation_context = ifcopenshell.api.context.add_context(model,context_type="Model")
    body_model_context = ifcopenshell.api.context.add_context(model,context_type="Model",context_identifier="Body",target_view="MODEL_VIEW",parent=geometric_representation_context)


    # map IfcSignType geometry to a local origin of (0,0,0)
    mapping_target = model.createIfcCartesianTransformationOperator3D(LocalOrigin=model.createIfcCartesianPoint((0.,0.,0.)))
    mapping_origin = model.createIfcAxis2Placement3D(Location=model.createIfcCartesianPoint((0.,0.,0.)))
    
    try:
        FIELDNAMES = [
        "OBJECTID","X","Y","Z","Layer","Text","MUTCD","Width","Height","Condition","Orientation"
        ]

        sign_types = defaultdict(list)
        
        with open(sign_file,mode='r',newline='',encoding='utf-8') as csvfile:
            next(csvfile)
            reader = csv.DictReader(csvfile,fieldnames=FIELDNAMES)
            for idx, row in enumerate(reader):
                object_id = row["OBJECTID"]
                text = row["Text"]
                mutcd = row["MUTCD"]

                description = f"{object_id} {text}"

                print(f"{description} {mutcd}")

                # note, matching based on mutcd code only - not attempting to match sign dimensions
                # with predefined sign sizes
                sign_type = find_sign_type(mutcd,"",libraries[library_type])
                
                x = float(row["X"])
                y = float(row["Y"])
                z = float(row["Z"])
                orientation = float(row["Orientation"])
                orientation = math.radians(orientation)
                
                if sign_type:
                    # sign type found, add it to the model
                    signs_found += 1
                    sign_type = ifcopenshell.file.add(model,sign_type)
                else:
                    # sign type not found, create a unique type
                    signs_not_found += 1
                    w = float(row["Width"])
                    h = float(row["Height"])
                    rep = create_sign_representation(mutcd,model,body_model_context,w,h,4,math.pi/4)
                    rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                    sign_type = model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=description,PredefinedType="PICTORAL",RepresentationMaps=[rep_map])

                                        
                sign_placement = model.createIfcLocalPlacement(
                        RelativePlacement=model.createIfcAxis2Placement3D(
                           Location=model.createIfcCartesianPoint((x,y,z)),
                           RefDirection=model.createIfcDirection((math.cos(orientation),math.sin(orientation),0.)),
                           Axis=model.createIfcDirection((math.sin(orientation),-math.cos(orientation),0.0))
                        )
                    )
                    
                mapped_item = model.createIfcMappedItem(MappingSource=sign_type.RepresentationMaps[0],MappingTarget=mapping_target)
                sign_rep = model.createIfcShapeRepresentation(ContextOfItems=body_model_context,RepresentationIdentifier="Body",RepresentationType="MappedRepresentation",Items=[mapped_item])
                product_rep = model.createIfcProductDefinitionShape(Representations=[sign_rep])

                sign = model.createIfcSign(GlobalId=ifcopenshell.guid.new(),Name=description,ObjectPlacement=sign_placement,Representation=product_rep)

                # collect all the signs for each type so we can assign type to signs after creating all signs and types
                sign_types[sign_type].append(sign)

                signs_modeled += 1

    except FileNotFoundError:
        print(f"Error: File '{sign_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    sign_types = dict(sign_types)
    for sign_type, signs in sign_types.items():
        # assign all of the signs of a given type to the type definition
        model.createIfcRelDefinesByType(GlobalId=ifcopenshell.guid.new(),RelatedObjects=signs,RelatingType=sign_type)
        # assign all the signs for this type to the site spatial container
        ifcopenshell.api.spatial.assign_container(model,relating_structure=site,products=signs)

    sign_types = list(sign_types.keys())
    model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project,RelatedDefinitions=sign_types)

    model.write("Test_Corridor_Signs.ifc")

    print(f"Signs found in MUTCD library: {signs_found}")
    print(f"Signs not found in MUTCD library: {signs_not_found}")
    print(f"Signs modeled: {signs_modeled}")
    print("Sign types used: " + str(len(sign_types)))

#    type_counts = Counter(mutcd_code_not_supported_types)
#    for item_type, count in type_counts.most_common():
#        print(f"{item_type}: {count}")

if __name__ == "__main__":
    build_signs()
    print("Done")
