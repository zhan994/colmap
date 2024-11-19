'''
    Update TWC coordinates with minimum offset based on GPS coordinates
    Zhihao Zhan
'''
import numpy as np
import sys

# Constants for WGS84 model
a = 6378137.0             # Semi-major axis (meters)
f = 1 / 298.257223563     # Flattening
e_sq = f * (2 - f)        # Square of eccentricity
b = a * (1 - f)           # Semi-minor axis

# Convert from GPS (latitude, longitude, altitude) to ECEF
def gps_to_ecef(lat, lon, alt):
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    N = a / np.sqrt(1 - e_sq * np.sin(lat_rad)**2)

    X = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad)
    Y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad)
    Z = (N * (1 - e_sq) + alt) * np.sin(lat_rad)

    return X, Y, Z

# Convert from ECEF to GPS (latitude, longitude, altitude)
def ecef_to_gps(x, y, z):
    # Calculate longitude
    lon = np.arctan2(y, x)

    # Iteratively calculate latitude and altitude
    p = np.sqrt(x**2 + y**2)
    lat = np.arctan2(z, p * (1 - e_sq))  # Initial guess
    alt = 0  # Initial altitude

    for _ in range(5):  # Iterative calculation
        N = a / np.sqrt(1 - e_sq * np.sin(lat)**2)
        alt = p / np.cos(lat) - N
        lat = np.arctan2(z, p * (1 - e_sq * N / (N + alt)))

    return np.degrees(lat), np.degrees(lon), alt


def apply_offset_to_ecef(gps_file_path, images_twc_file_path, point3d_file_path, output_file_path, threshold=3):
    # step: 1 Read gps.txt and calculate ECEF
    gps_data = []
    with open(gps_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            filename = parts[0]
            latitude = float(parts[1])
            longitude = float(parts[2])
            altitude = float(parts[3])
            ecef_coords = gps_to_ecef(latitude, longitude, altitude)
            gps_data.append((filename, *ecef_coords))

    # step: 2 Read images_twc.txt
    images_twc_data = []
    with open(images_twc_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            filename = parts[9]  # filename is the 10th item
            ecef_x = float(parts[5])
            ecef_y = float(parts[6])
            ecef_z = float(parts[7])
            # Store the entire line for later update
            images_twc_data.append((filename, ecef_x, ecef_y, ecef_z, line))

    # step: 3 Calculate offsets and remove outliers
    x_offset = []
    y_offset = []
    z_offset = []
    valid_data = []

    for gps_entry in gps_data:
        gps_filename, gps_x, gps_y, gps_z = gps_entry
        matching_entry = next(
            (twc for twc in images_twc_data if twc[0] == gps_filename), None)
        if matching_entry:
            _, twc_x, twc_y, twc_z, _ = matching_entry
            dx = gps_x - twc_x
            dy = gps_y - twc_y
            dz = gps_z - twc_z
            x_offset.append(dx)
            y_offset.append(dy)
            z_offset.append(dz)
            valid_data.append((gps_filename, dx, dy, dz, twc_x, twc_y, twc_z))

    # Calculate standard deviations
    x_std = np.std(x_offset)
    y_std = np.std(y_offset)
    z_std = np.std(z_offset)

    # Filter outliers based on threshold
    filtered_offsets = [(dx, dy, dz) for (_, dx, dy, dz, _, _, _) in valid_data
                        if abs(dx) <= threshold * x_std and
                        abs(dy) <= threshold * y_std and
                        abs(dz) <= threshold * z_std]

    # Compute average offset for each coordinate
    avg_x_offset = np.mean([dx for dx, _, _ in filtered_offsets])
    avg_y_offset = np.mean([dy for _, dy, _ in filtered_offsets])
    avg_z_offset = np.mean([dz for _, _, dz in filtered_offsets])

    # Print the offset
    print(f"Calculated offset (after removing outliers):")
    print(f"X Offset: {avg_x_offset:.6f}")
    print(f"Y Offset: {avg_y_offset:.6f}")
    print(f"Z Offset: {avg_z_offset:.6f}")

    # step: 4 Get PointCloud from point3d.txt
    point3d_data = []
    with open(point3d_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[3:]:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 8:
                continue
            
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            point3d_data.append((x, y, z))

    # step: 5 Update images_twc.txt with adjusted coordinates and print before/after GPS coordinates
    with open(output_file_path, 'w') as file:
        for entry in images_twc_data:
            filename, ecef_x, ecef_y, ecef_z, original_line = entry

            # Convert original ECEF to GPS and print
            orig_lat, orig_lon, orig_alt = ecef_to_gps(ecef_x, ecef_y, ecef_z)
            # print(
            #     f"Original GPS coordinates for {filename}: ({orig_lat:.6f}, {orig_lon:.6f}, {orig_alt:.6f})")

            # Apply the offset
            updated_x = ecef_x + avg_x_offset
            updated_y = ecef_y + avg_y_offset
            updated_z = ecef_z
            # Convert updated ECEF to GPS and print
            updated_lat, updated_lon, updated_alt = ecef_to_gps(
                updated_x, updated_y, updated_z)
            # print(
            #     f"Updated GPS coordinates for {filename}: ({updated_lat:.6f}, {updated_lon:.6f}, {updated_alt:.6f})\n")

            # Replace the old ECEF values in the line with the updated ones
            updated_line = original_line.split()
            updated_line[5] = f"{updated_x:.6f}"
            updated_line[6] = f"{updated_y:.6f}"
            updated_line[7] = f"{updated_z:.6f}"
            # Write the updated line to the new file
            file.write(" ".join(updated_line) + "\n")

        for point in point3d_data:
            px, py, pz = point
            updated_px = px + avg_x_offset
            updated_py = py + avg_y_offset
            file.write(f"POINT {updated_px} {updated_py} {pz}\n")

    print(
        f"Offset applied. Updated coordinates saved to '{output_file_path}'.")


# Main function to handle command-line arguments
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <gps_file_path> <images_twc_file_path> <point3d_file_path> <output_file_path>")
        sys.exit(1)

    gps_file_path = sys.argv[1]
    images_twc_file_path = sys.argv[2]
    point3d_file_path = sys.argv[3]
    output_file_path = sys.argv[4]

    apply_offset_to_ecef(gps_file_path, images_twc_file_path,
                         point3d_file_path, output_file_path)
