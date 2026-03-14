import math
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit
import ifcopenshell.api.cogo
import numpy as np

from ifcopenshell import ifcopenshell_wrapper

def print_segment_end_points(file:ifcopenshell.file,curve):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    s = ifcopenshell.geom.settings()
    for segment in curve.Segments:
        function_item = ifcopenshell_wrapper.map_shape(s, segment.wrapped_data)
        evaluator = ifcopenshell_wrapper.function_item_evaluator(s, function_item)
        start = np.array(evaluator.evaluate(function_item.start()))
        end = np.array(evaluator.evaluate(function_item.end()))
        sx = float(start[0,3])/unit_scale
        sy = float(start[1,3])/unit_scale
        ex = float(end[0,3])/unit_scale
        ey = float(end[1,3])/unit_scale
        print(segment)
        print(f"S ({sx},{sy})")
        print(f"E ({ex},{ey})")

def SR104(file:ifcopenshell.file):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    alignment = ifcopenshell.api.alignment.create(file,"C Line",start_station=10000.)
    alignment.Description = "SR 104 (205th)"

    layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    # C 100+00 to C 101+30.90 AP
    segment1 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((0.,0.))), # Actual coordinate unknown
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("S 89 04 44.0 E")),
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=10130.90-10000.0,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment1)
    layout.IsNestedBy[0].RelatedObjects[0].Description = "C 100+00 to C 101+30.90 AP"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale

    # C 101+30.90 AP to C 110+97.92 AP
    segment2 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("S 88 41 52 E")),
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=11097.92 - 10130.90,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment2)
    layout.IsNestedBy[0].RelatedObjects[1].Description = "C 101+30.90 AP to C 110+97.92 AP"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale

    # C 110+97.92 AP to C 118+97.92 AP
    segment3 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("S 89 43 44.7 E")),
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=11897.92 - 11097.92,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment3)
    layout.IsNestedBy[0].RelatedObjects[2].Description = "C 110+97.92 AP to C 118+97.92 AP"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale

    # C 118+97.92 AP to C 129+16.76 PC
    segment4 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("S 87 47 11 E")),
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=12916.76-11897.92,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment4)
    layout.IsNestedBy[0].RelatedObjects[3].Description = "C 118+97.92 AP to C 129+16.76 PC"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 129+16.76 PC to C 130+62.84 PT
    segment5 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature= -1375.10,
        EndRadiusOfCurvature= -1375.10,
        SegmentLength=13062.84 - 12916.76,
        PredefinedType = "CIRCULARARC"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment5)
    layout.IsNestedBy[0].RelatedObjects[4].Description = "C 129+16.76 PC to C 130+62.84 PT"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)


    # C 130+62.84 PT to C 131+93.61 PC
    segment6 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=13193.61 - 12916.76,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment6)
    layout.IsNestedBy[0].RelatedObjects[5].Description = "C 130+62.84 PT to C 131+93.61 PC"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 131+93.61 PC to C 133+42.33 PT
    segment7 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=1399.95,
        EndRadiusOfCurvature=1399.95,
        SegmentLength=13342.33 - 13193.61,
        PredefinedType = "CIRCULARARC"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment7)
    layout.IsNestedBy[0].RelatedObjects[6].Description = "C 131+93.61 PC to C 133+42.33 PT"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 133+42.33 PT to C 141+06.12 AP
    segment8 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=0,
        EndRadiusOfCurvature=0,
        SegmentLength=14106.12 - 13342.33,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment8)
    layout.IsNestedBy[0].RelatedObjects[7].Description = "C 133+42.33 PT to C 141+06.12 AP"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale

    # C 141+06.12 AP to C 144+66.90 PC
    segment9 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("S 87 53 41 E")),
        StartRadiusOfCurvature=0,
        EndRadiusOfCurvature=0,
        SegmentLength=14466.90 - 14106.12,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment9)
    layout.IsNestedBy[0].RelatedObjects[8].Description = "C 141+06.12 AP to C 144+66.90 PC"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 144+66.90 PC to C 146+33.95 PT
    segment10 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=1399.99,
        EndRadiusOfCurvature=1399.99,
        SegmentLength=14633.95 - 14466.90,
        PredefinedType = "CIRCULARARC"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment10)
    layout.IsNestedBy[0].RelatedObjects[9].Description = "C 144+66.90 PC to C 146+33.95 PT"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 146+33.95 PT to C 147+94.29 PC
    segment11 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=0,
        EndRadiusOfCurvature=0,
        SegmentLength=14794.29 - 14633.95,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment11)
    layout.IsNestedBy[0].RelatedObjects[10].Description = "C 146+33.95 PT to C 147+94.29 PC"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 147+94.29 PC to C 149+61.35 PT
    segment12 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=1400.07,
        EndRadiusOfCurvature=1400.07,
        SegmentLength=14961.36 - 14794.29,
        PredefinedType = "CIRCULARARC"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment12)
    layout.IsNestedBy[0].RelatedObjects[11].Description = "C 147+94.29 PC to C 149+61.35 PT"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 149+61.35 PT to C 154+30.09 AP
    segment13 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=0,
        EndRadiusOfCurvature=0,
        SegmentLength=15430.09 - 14961.36,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment13)
    layout.IsNestedBy[0].RelatedObjects[12].Description = "C 149+61.35 PT to C 154+30.09 AP"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 154+30.09 AP to C 170+82.61 AP
    segment14 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("S 88 19 24 E")),
        StartRadiusOfCurvature=0,
        EndRadiusOfCurvature=0,
        SegmentLength= 17082.61 - 15430.09,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment14)
    layout.IsNestedBy[0].RelatedObjects[13].Description = "C 154+30.09 AP to C 170+82.61 AP"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 170+82.61 AP to C 176+55.21 PC
    segment15 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("S 88 19 24 E")),
        StartRadiusOfCurvature=0,
        EndRadiusOfCurvature=0,
        SegmentLength= 17655.21 - 17082.61,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment15)
    layout.IsNestedBy[0].RelatedObjects[14].Description = "C 170+82.61 AP to C 176+55.21 PC"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 176+55.21 PC to C 183+96.46 PT
    segment16 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=-954.93,
        EndRadiusOfCurvature=-954.93,
        SegmentLength= 18396.46 - 17655.21,
        PredefinedType = "CIRCULARARC"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment16)
    layout.IsNestedBy[0].RelatedObjects[15].Description = "C 176+55.21 PC to C 183+96.46 PT"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)

    # C 183+96.46 PT to C 211+77.00
    segment17 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x,y))),
        StartDirection=dir,
        StartRadiusOfCurvature=0,
        EndRadiusOfCurvature=0,
        SegmentLength= 21177.00 - 18396.46,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment17)
    layout.IsNestedBy[0].RelatedObjects[16].Description = "C 183+96.46 PT to C 211+77.00"

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)


    ifcopenshell.api.alignment.name_segments("C H",layout)
    #ifcopenshell.api.alignment.create_segment_representations(file,alignment)
    #curve = ifcopenshell.api.alignment.get_curve(alignment)
    #print_segment_end_points(file,curve)
    #ifcopenshell.api.alignment.util.print_composite_curve_deep(curve)



def SR99(file : ifcopenshell.file):
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    alignment = ifcopenshell.api.alignment.create(file,"D Line",start_station=9800.)
    alignment.Description = "SR 99"

    layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    segment1 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((0.,0.))),
        StartDirection=math.radians(ifcopenshell.api.cogo.bearing2dd("N 4 11 W")),
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=10109.99-9800.,
        PredefinedType = "LINE"
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment1)

    x = float(end[0,3])/unit_scale
    y = float(end[1,3])/unit_scale
    dx = float(end[0,0])
    dy = float(end[1,0])
    dir = math.atan2(dy,dx)
    segment2 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x,y)),
        StartDirection=dir,
        StartRadiusOfCurvature=-1800.,
        EndRadiusOfCurvature=-1800.,
        SegmentLength=1103.09,
        PredefinedType="CIRCULARARC"
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment2)

    ifcopenshell.api.alignment.name_segments("D H",layout)


def main():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="ADCMS Sign Project")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file,name="foot")
    ifcopenshell.api.unit.assign_unit(file,units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    SR104(file)
    SR99(file)

    ifcopenshell.file.write(file,"C:/Users/bricer/OneDrive - Washington State Department of Transportation/BIM for Infrastructure/Signs/Alignments/Alignments.ifc")
    #ifcopenshell.file.write(file,"C:/Users/rickb/OneDrive - Washington State Department of Transportation/BIM for Infrastructure/Signs/Alignments/Alignments.ifc")


if __name__ == "__main__":
    main()