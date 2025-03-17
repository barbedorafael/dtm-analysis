#!/bin/bash

# Input arguments
INPUT_RASTER=/vsicurl/https://fdri-o.s3-ext.jc.rl.ac.uk/lidar/joined/merged_engwal_dtm.tif
INPUT_SHP=data/raw/54080.shp
OUTPUT_RASTER=data/raw/54080_dtm.tif
PIXEL_SIZE=5

# Temporary file for the buffered extent
TEMP_EXTENT_FILE="extent.txt"

# Extract the bounding box of the shapefile
EXTENT=$(ogrinfo -al -so "$INPUT_SHP" | grep "Extent" | sed 's/Extent: //; s/[(,)]//g')

# Read coordinates from extent output
read -r MIN_X MIN_Y sign MAX_X MAX_Y <<< "$EXTENT"

# echo "Extent: MIN_X=$MIN_X, MIN_Y=$MIN_Y, MAX_X=$MAX_X, NEW_MAX_Y=$MAX_Y"

# Apply a buffer of 1 km (1000 meters)
BUFFER=1000
NEW_MIN_X=$(awk -v minx="$MIN_X" -v buf="$BUFFER" 'BEGIN {print minx - buf}')
NEW_MIN_Y=$(awk -v miny="$MIN_Y" -v buf="$BUFFER" 'BEGIN {print miny - buf}')
NEW_MAX_X=$(awk -v maxx="$MAX_X" -v buf="$BUFFER" 'BEGIN {print maxx + buf}')
NEW_MAX_Y=$(awk -v maxy="$MAX_Y" -v buf="$BUFFER" 'BEGIN {print maxy + buf}')

# echo "Buffered Extent: NEW_MIN_X=$NEW_MIN_X, NEW_MIN_Y=$NEW_MIN_Y, NEW_MAX_X=$NEW_MAX_X, NEW_MAX_Y=$NEW_MAX_Y"


# Run gdal_translate using the buffered extent
gdal_translate -projwin "$NEW_MIN_X" "$NEW_MAX_Y" "$NEW_MAX_X" "$NEW_MIN_Y" \
    -tr "$PIXEL_SIZE" "$PIXEL_SIZE" -of GTiff "$INPUT_RASTER" "$OUTPUT_RASTER"

echo "Clipped raster saved as $OUTPUT_RASTER"