import arcpy


def compare_layers(
    layer1_path,
    layer2_path,
    join_field,
    field_layer1,
    field_layer2,
    reviewer_field,
    output_table,
):
    """
    Compare attribute values between two feature layers and store the detected
    differences in an output table.
    """

    # ---------------------------------------------------
    # Check if input layers exist
    # ---------------------------------------------------
    if not arcpy.Exists(layer1_path):
        raise Exception(f"Layer 1 not found: {layer1_path}")

    if not arcpy.Exists(layer2_path):
        raise Exception(f"Layer 2 not found: {layer2_path}")

    # ---------------------------------------------------
    # Create temporary feature layers
    # ---------------------------------------------------
    lyr1 = "layer1_temp"
    lyr2 = "layer2_temp"

    arcpy.management.MakeFeatureLayer(layer1_path, lyr1)
    arcpy.management.MakeFeatureLayer(layer2_path, lyr2)

    # ---------------------------------------------------
    # Delete the output table if it already exists
    # ---------------------------------------------------
    if arcpy.Exists(output_table):
        arcpy.management.Delete(output_table)

    gdb_path = arcpy.env.workspace
    table_name = output_table.split("\\")[-1]

    # ---------------------------------------------------
    # Create the output table
    # ---------------------------------------------------
    arcpy.management.CreateTable(gdb_path, table_name)

    arcpy.management.AddField(output_table, "Src_OBJECTID", "LONG")
    arcpy.management.AddField(output_table, "Layer1_Name", "TEXT", field_length=250)
    arcpy.management.AddField(output_table, "Layer2_Name", "TEXT", field_length=250)
    arcpy.management.AddField(output_table, "Reviewer", "TEXT", field_length=100)
    arcpy.management.AddField(output_table, "Difference_Note", "TEXT", field_length=100)

    # ---------------------------------------------------
    # Read layer 2 records into a dictionary for fast lookup
    # ---------------------------------------------------
    layer2_dict = {}

    with arcpy.da.SearchCursor(
        lyr2,
        [join_field, field_layer2, reviewer_field],
    ) as cursor:

        for oid, name, reviewer in cursor:
            layer2_dict[oid] = {
                "name": name or "",
                "reviewer": reviewer or "",
            }

    # ---------------------------------------------------
    # Compare attributes and store differences
    # ---------------------------------------------------
    inserted_count = 0

    with arcpy.da.InsertCursor(
        output_table,
        ["Src_OBJECTID", "Layer1_Name", "Layer2_Name", "Reviewer", "Difference_Note"],
    ) as insert_cursor:

        with arcpy.da.SearchCursor(
            lyr1,
            [join_field, field_layer1],
        ) as cursor1:

            for oid, name1 in cursor1:

                val1 = name1 or ""
                rec = layer2_dict.get(oid)

                if rec is None:

                    insert_cursor.insertRow(
                        (oid, val1, "[Not Found]", "", "Missing in layer 2")
                    )
                    inserted_count += 1

                elif val1 != rec["name"]:

                    insert_cursor.insertRow(
                        (oid, val1, rec["name"], rec["reviewer"], "Name difference")
                    )
                    inserted_count += 1

    # ---------------------------------------------------
    # Print summary messages
    # ---------------------------------------------------
    print("Difference table created successfully")
    print(f"Total differences found: {inserted_count}")
    print(f"Output table: {output_table}")

    # ---------------------------------------------------
    # Clean up temporary layers
    # ---------------------------------------------------
    arcpy.management.Delete(lyr1)
    arcpy.management.Delete(lyr2)


def main():

    # ---------------------------------------------------
    # User configuration
    # ---------------------------------------------------
    layer1_path = r"path_to_layer1"
    layer2_path = r"path_to_layer2"

    join_field = "OBJECTID"
    field_layer1 = "Primary_Place_Name"
    field_layer2 = "Primary_Place_Name"
    reviewer_field = "Reviewer"

    arcpy.env.workspace = r"path_to_gdb"
    arcpy.env.overwriteOutput = True

    output_table = r"path_to_gdb\Differences_Primary_Place_Name"

    compare_layers(
        layer1_path,
        layer2_path,
        join_field,
        field_layer1,
        field_layer2,
        reviewer_field,
        output_table,
    )


if __name__ == "__main__":
    main()
