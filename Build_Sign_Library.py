"""
Script to build a library of MUTCD signs

Richard Brice, PE
WSDOT Bridge and Structures Office

Two IfcProjectLibrary entities are created. One library defines signs of unit dimensions (1x1x1).
From this signs of any size and thickness can be created by scaling the geometric representation with IfcCartesianTransformationOperator3DnonUniform
setting the Scale, Scale1, and Scale2 parameters equal to the X,Y,Z dimensions of the sign (Z is thickness)

The second library has signs of actual dimensions per MUTCD with a unit thickness.

Future Work:
1) Predefine materials in the library
2) Add presentation styles for sign face colors
3) Add annotation representation context for words on the signs
4) Add type-level bSDD classification
"""

import math
import ifcopenshell
import ifcopenshell.api.unit
import ifcopenshell.api.context

import math
import csv


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
    solid = model.createIfcExtrudedAreaSolid(SweptArea=profile,ExtrudedDirection=model.createIfcDirection((0.,0.,1.)),Depth=1.)

    shape_representation = model.createIfcShapeRepresentation(ContextOfItems=context,RepresentationIdentifier="Body",RepresentationType="SweptSolid",Items=[solid])

    return shape_representation

# Define the expected fieldnames
FIELDNAMES = [
    "Sign", "Designation", "Section",
    "Single Lane", "Multi-Lane", "Expressway", "Freeway",
    "Minimum", "Oversized", "Shape"
]

def read_csv(file_path):
    # start the model
    model = ifcopenshell.file(schema="IFC4X3")

    # create a project
    project = model.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="MUTCD Sign Definition Libraries")

    # set up system of units (must be done after IfcProject is created)
    length_unit = ifcopenshell.api.unit.add_conversion_based_unit(model,name="inch")
    area_unit = ifcopenshell.api.unit.add_conversion_based_unit(model,name="square inch")
    ifcopenshell.api.unit.assign_unit(model,units=[length_unit,area_unit])

    # create the representation context
    geometric_representation_context = ifcopenshell.api.context.add_context(model,context_type="Model")
    body_model_context = ifcopenshell.api.context.add_context(model,context_type="Model",context_identifier="Body",target_view="MODEL_VIEW",parent=geometric_representation_context)

    # create the libraries
    project_library1 = model.createIfcProjectLibrary(GlobalId=ifcopenshell.guid.new(),Name="Unit Signs",RepresentationContexts=[body_model_context])
    project_library2 = model.createIfcProjectLibrary(GlobalId=ifcopenshell.guid.new(),Name="Signs",RepresentationContexts=[body_model_context])

    # project declares library
    model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project,RelatedDefinitions=[project_library1,project_library2])

    # align the origin of the mapping with the center of the sign at (0,0,0)
    mapping_origin =  model.createIfcAxis2Placement3D(Location=model.createIfcCartesianPoint((0.,0.,0.)))

    unit_sign_types = []
    sign_types = []
    
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            next(csvfile)
            reader = csv.DictReader(csvfile, fieldnames=FIELDNAMES)
            
            print("Reading CSV contents:\n")
            for idx, row in enumerate(reader):
                description = row["Sign"]
                
                if isinstance(description,list):
                    description = " ".join(str(v) for v in description)
                    
                mutcd = row["Designation"].split()
                
                if isinstance(mutcd,list):
                    mutcd = " ".join(str(v) for v in mutcd)
                    
                print(f"{idx}: {description}, {mutcd}")
                sizes={row["Single Lane"].strip(),row["Multi-Lane"].strip(),row["Expressway"].strip(),row["Freeway"].strip(),row["Minimum"].strip(),row["Oversized"].strip()}
                sizes=set(filter(lambda x: x.strip(), sizes))
                for size in sizes:
                    parts = size.split()
                    w = int(parts[0])
                    h = int(parts[2])
                    if row["Shape"] == "O":
                        rep = create_sign_representation(mutcd,model,body_model_context,1,1,8,math.pi/8)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        unit_sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=description,PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))

                        rep = create_sign_representation(mutcd,model,body_model_context,w,w,8,math.pi/8)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=f"{description} ({w}x{w})",PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))
                    elif row["Shape"] == "R":
                        rep = create_sign_representation(mutcd,model,body_model_context,1,1,4,math.pi/4)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        unit_sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=description,PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))

                        rep = create_sign_representation(mutcd,model,body_model_context,w,h,4,math.pi/4)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=f"{description} ({w}x{h})",PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))
                    elif row["Shape"] == "D":
                        rep = create_sign_representation(mutcd,model,body_model_context,1,1,4,0.)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        unit_sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=description,PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))

                        rep = create_sign_representation(mutcd,model,body_model_context,w,h,4,0.)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=f"{description} ({w}x{h})",PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))
                    elif row["Shape"] == "T":
                        z = int(parts[4])
                        rep = create_sign_representation(mutcd,model,body_model_context,1,1,3,math.pi/6)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        unit_sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=description,PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))

                        rep = create_sign_representation(mutcd,model,body_model_context,w,h,3,math.pi/6)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=f"{description} ({w}x{h}x{z})",PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))
                    elif row["Shape"] == "P":
                        z = int(parts[4])
                        rep = create_sign_representation(mutcd,model,body_model_context,1,1,3,0.)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        unit_sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=description,PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))

                        rep = create_sign_representation(mutcd,model,body_model_context,w,h,3,0.)
                        rep_map = model.createIfcRepresentationMap(MappingOrigin=mapping_origin,MappedRepresentation=rep)
                        sign_types.append(model.createIfcSignType(GlobalId=ifcopenshell.guid.new(),Name=mutcd,Description=f"{description} ({w}x{h}x{z})",PredefinedType="PICTORAL",RepresentationMaps=[rep_map]))

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project_library1,RelatedDefinitions=unit_sign_types)
    model.createIfcRelDeclares(GlobalId=ifcopenshell.guid.new(),RelatingContext=project_library2,RelatedDefinitions=sign_types)

    model.write("MUTCD_Sign_Library.ifc")

if __name__ == "__main__":
    file_path = "MUTCD_Sign_Definitions.csv"
    read_csv(file_path)
    print("Done")
