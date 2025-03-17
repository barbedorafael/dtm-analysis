# import os
# from whitebox import WhiteboxTools

# wbt = WhiteboxTools()
# wbt.set_whitebox_dir("/users/wrmod/rafbar/miniconda3/envs/geo/lib/python3.12/site-packages/whitebox") 
# wbt.set_working_dir(os.getcwd())

# pth = os.path.join(os.getcwd(), "data/raw/54080_dtm.tif")
# output = os.path.join(os.getcwd(), "data/interim/slope.tif")

# wbt.slope(pth, output)


import os
from whitebox import WhiteboxTools

def generate_streamlines(dem_path, output_dir, flow_accum_threshold=1000):
    """
    Generate streamlines from a DEM using WhiteboxTools
    
    Parameters:
    -----------
    dem_path : str
        Path to input DEM file
    output_dir : str
        Directory to store output files
    flow_accum_threshold : int
        Threshold for flow accumulation to define streams (default: 1000)
    """
    try:
        # Initialize WhiteboxTools
        wbt = WhiteboxTools()
        
        # Set working directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        wbt.set_working_dir(output_dir)
        
        # Set verbose mode
        wbt.set_verbose_mode(True)
        
        # 1. Fill depressions in DEM
        print("Filling depressions in DEM...")
        filled_dem = os.path.join(output_dir, "filled_dem.tif")
        wbt.fill_depressions(
            dem=dem_path,
            output=filled_dem
        )
        
        # 2. Calculate flow direction (D8 algorithm)
        print("Calculating flow direction...")
        flow_dir = os.path.join(output_dir, "flow_direction.tif")
        wbt.d8_pointer(
            dem=filled_dem,
            output=flow_dir
        )
        
        # 3. Calculate flow accumulation
        print("Calculating flow accumulation...")
        flow_accum = os.path.join(output_dir, "flow_accumulation.tif")
        wbt.d8_flow_accumulation(
            input=flow_dir,
            output=flow_accum,
            out_type="cells"
        )
        
        # 4. Extract streams based on flow accumulation threshold
        print("Extracting streams...")
        streams = os.path.join(output_dir, "streams.tif")
        wbt.greater_than(
            input1=flow_accum,
            input2=str(flow_accum_threshold),
            output=streams
        )
        
        # 5. Convert streams to vector format
        print("Converting streams to vector format...")
        vector_streams = os.path.join(output_dir, "vector_streams.shp")
        wbt.raster_streams_to_vector(
            streams=streams,
            d8_pntr=flow_dir,
            output=vector_streams
        )
        
        # 6. Smooth the streamlines
        print("Smoothing streamlines...")
        smoothed_streams = os.path.join(output_dir, "smoothed_streams.shp")
        wbt.smooth_vectors(
            input=vector_streams,
            output=smoothed_streams,
            filter=5  # Smoothing filter size
        )
        
        print("Streamline generation completed successfully!")
        return {
            "filled_dem": filled_dem,
            "flow_direction": flow_dir,
            "flow_accumulation": flow_accum,
            "streams": streams,
            "vector_streams": vector_streams,
            "smoothed_streams": smoothed_streams
        }
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def main():
    # Example usage
    # Set your file paths
    dem_path = os.path.join(os.getcwd(), "data/raw/54080_dtm.tif")
    output_dir = os.path.join(os.getcwd(), "data/interim")
    flow_accum_threshold = 1000  # Adjust based on your needs
    
    # Generate streamlines
    results = generate_streamlines(dem_path, output_dir, flow_accum_threshold)
    
    if results:
        print("\nGenerated files:")
        for key, value in results.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()