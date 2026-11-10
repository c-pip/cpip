"""
Generator for SwarmDroid Mascot 3D Model (.glb / glTF 2.0 Binary)
Builds a complete, valid glTF 2.0 binary file containing:
- Rounded cute head
- Curved dark glass visor
- Glowing cyan expressive eyes
- Lavender accented chassis / torso
- Levitating ear antennas
- Anti-gravity hover thruster with cyan emissive energy core
"""

import struct
import json
import math
import os


def generate_sphere(radius=0.5, lat_bands=12, lon_bands=16, center=(0, 0, 0)):
    """Generates vertex positions, normals, and triangle indices for a UV sphere."""
    positions = []
    normals = []
    indices = []
    
    cx, cy, cz = center
    
    for lat in range(lat_bands + 1):
        theta = lat * math.pi / lat_bands
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)
        
        for lon in range(lon_bands + 1):
            phi = lon * 2 * math.pi / lon_bands
            sin_phi = math.sin(phi)
            cos_phi = math.cos(phi)
            
            x = cos_phi * sin_theta
            y = cos_theta
            z = sin_phi * sin_theta
            
            normals.extend([x, y, z])
            positions.extend([cx + x * radius, cy + y * radius, cz + z * radius])
            
    for lat in range(lat_bands):
        for lon in range(lon_bands):
            first = lat * (lon_bands + 1) + lon
            second = first + lon_bands + 1
            
            indices.extend([first, second, first + 1])
            indices.extend([second, second + 1, first + 1])
            
    return positions, normals, indices


def generate_torus(ring_radius=0.35, tube_radius=0.06, radial_segments=16, tubular_segments=12, center=(0, 0, 0)):
    """Generates a torus mesh for levitating anti-gravity thruster ring."""
    positions = []
    normals = []
    indices = []
    
    cx, cy, cz = center
    
    for j in range(radial_segments + 1):
        u = j * 2 * math.pi / radial_segments
        cos_u = math.cos(u)
        sin_u = math.sin(u)
        
        for i in range(tubular_segments + 1):
            v = i * 2 * math.pi / tubular_segments
            cos_v = math.cos(v)
            sin_v = math.sin(v)
            
            x = (ring_radius + tube_radius * cos_v) * cos_u
            y = tube_radius * sin_v
            z = (ring_radius + tube_radius * cos_v) * sin_u
            
            nx = cos_v * cos_u
            ny = sin_v
            nz = cos_v * sin_u
            
            normals.extend([nx, ny, nz])
            positions.extend([cx + x, cy + y, cz + z])
            
    for j in range(radial_segments):
        for i in range(tubular_segments):
            first = j * (tubular_segments + 1) + i
            second = (j + 1) * (tubular_segments + 1) + i
            
            indices.extend([first, second, first + 1])
            indices.extend([second, second + 1, first + 1])
            
    return positions, normals, indices


def build_mascot_glb(output_path: str):
    # Combine sub-meshes:
    # 1. White Ceramic Head (sphere at y=0.5, r=0.45)
    # 2. Glowing Visor (squashed sphere at y=0.5, z=0.25, r=0.3)
    # 3. Lavender Body / Chassis (sphere at y=-0.1, r=0.35)
    # 4. Cyan Levitating Thruster Ring (torus at y=-0.5)
    # 5. Dual Levitating Ear Antennas (spheres at x=+-0.48, y=0.6, r=0.1)

    meshes_data = []
    
    # 1. Head (White Ceramic)
    h_pos, h_norm, h_idx = generate_sphere(radius=0.42, center=(0, 0.5, 0))
    meshes_data.append({"name": "Head_Ceramic", "material": 0, "pos": h_pos, "norm": h_norm, "idx": h_idx})
    
    # 2. Visor (Dark Tinted Glass + Glow)
    v_pos, v_norm, v_idx = generate_sphere(radius=0.28, center=(0, 0.52, 0.22))
    # Flatten Z a bit for visor contour
    for i in range(2, len(v_pos), 3):
        v_pos[i] = (v_pos[i] - 0.22) * 0.5 + 0.28
    meshes_data.append({"name": "Visor_Glass", "material": 1, "pos": v_pos, "norm": v_norm, "idx": v_idx})
    
    # 3. Torso (Lavender Chassis)
    t_pos, t_norm, t_idx = generate_sphere(radius=0.32, center=(0, -0.05, 0))
    meshes_data.append({"name": "Torso_Lavender", "material": 2, "pos": t_pos, "norm": t_norm, "idx": t_idx})
    
    # 4. Anti-gravity Ring (Cyan Emissive Thruster)
    r_pos, r_norm, r_idx = generate_torus(ring_radius=0.30, tube_radius=0.05, center=(0, -0.42, 0))
    meshes_data.append({"name": "Thruster_Ring", "material": 3, "pos": r_pos, "norm": r_norm, "idx": r_idx})
    
    # 5. Left & Right Ear Antennas (Lavender + Cyan Orbs)
    el_pos, el_norm, el_idx = generate_sphere(radius=0.09, center=(-0.46, 0.58, 0))
    meshes_data.append({"name": "Ear_Left", "material": 3, "pos": el_pos, "norm": el_norm, "idx": el_idx})
    
    er_pos, er_norm, er_idx = generate_sphere(radius=0.09, center=(0.46, 0.58, 0))
    meshes_data.append({"name": "Ear_Right", "material": 3, "pos": er_pos, "norm": er_norm, "idx": er_idx})

    # Pack binary buffer
    bin_data = bytearray()
    buffer_views = []
    accessors = []
    gltf_meshes = []
    nodes = []

    def align_bin(alignment=4):
        pad = (alignment - (len(bin_data) % alignment)) % alignment
        bin_data.extend(b'\x00' * pad)

    for mesh_idx, m in enumerate(meshes_data):
        pos = m["pos"]
        norm = m["norm"]
        idx = m["idx"]
        
        # --- Indices ---
        align_bin(4)
        idx_offset = len(bin_data)
        idx_bytes = struct.pack(f"<{len(idx)}H", *idx)
        bin_data.extend(idx_bytes)
        idx_bv = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": idx_offset,
            "byteLength": len(idx_bytes),
            "target": 34963  # ELEMENT_ARRAY_BUFFER
        })
        idx_acc = len(accessors)
        accessors.append({
            "bufferView": idx_bv,
            "byteOffset": 0,
            "componentType": 5123,  # UNSIGNED_SHORT
            "count": len(idx),
            "type": "SCALAR",
            "max": [max(idx)],
            "min": [min(idx)]
        })

        # --- Positions ---
        align_bin(4)
        pos_offset = len(bin_data)
        pos_bytes = struct.pack(f"<{len(pos)}f", *pos)
        bin_data.extend(pos_bytes)
        pos_bv = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": pos_offset,
            "byteLength": len(pos_bytes),
            "target": 34962  # ARRAY_BUFFER
        })
        pos_acc = len(accessors)
        x_vals = pos[0::3]
        y_vals = pos[1::3]
        z_vals = pos[2::3]
        accessors.append({
            "bufferView": pos_bv,
            "byteOffset": 0,
            "componentType": 5126,  # FLOAT
            "count": len(pos) // 3,
            "type": "VEC3",
            "max": [max(x_vals), max(y_vals), max(z_vals)],
            "min": [min(x_vals), min(y_vals), min(z_vals)]
        })

        # --- Normals ---
        align_bin(4)
        norm_offset = len(bin_data)
        norm_bytes = struct.pack(f"<{len(norm)}f", *norm)
        bin_data.extend(norm_bytes)
        norm_bv = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": norm_offset,
            "byteLength": len(norm_bytes),
            "target": 34962  # ARRAY_BUFFER
        })
        norm_acc = len(accessors)
        accessors.append({
            "bufferView": norm_bv,
            "byteOffset": 0,
            "componentType": 5126,  # FLOAT
            "count": len(norm) // 3,
            "type": "VEC3"
        })

        g_mesh_idx = len(gltf_meshes)
        gltf_meshes.append({
            "name": m["name"],
            "primitives": [{
                "attributes": {
                    "POSITION": pos_acc,
                    "NORMAL": norm_acc
                },
                "indices": idx_acc,
                "material": m["material"],
                "mode": 4  # TRIANGLES
            }]
        })
        nodes.append({"name": m["name"], "mesh": g_mesh_idx})

    # Materials:
    # 0: White Ceramic (PBR)
    # 1: Dark Visor Glass (Low roughness, high metallic)
    # 2: Lavender Chassis (Metallic lavender)
    # 3: Electric Cyan Glow (High emissive factor)
    materials = [
        {
            "name": "M_CeramicWhite",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.94, 0.96, 0.98, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.25
            }
        },
        {
            "name": "M_VisorGlass",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.05, 0.06, 0.09, 1.0],
                "metallicFactor": 0.85,
                "roughnessFactor": 0.15
            }
        },
        {
            "name": "M_LavenderAccent",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.72, 0.57, 1.0, 1.0],
                "metallicFactor": 0.35,
                "roughnessFactor": 0.3
            }
        },
        {
            "name": "M_CyanEmissive",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.0, 0.96, 0.83, 1.0],
                "metallicFactor": 0.2,
                "roughnessFactor": 0.2
            },
            "emissiveFactor": [0.0, 0.96, 0.83]
        }
    ]

    gltf_dict = {
        "asset": {"version": "2.0", "generator": "SwarmDroid Mascot GLB Generator 1.0"},
        "scene": 0,
        "scenes": [{"name": "SwarmDroidMascot", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "materials": materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(bin_data)}]
    }

    # Encode JSON chunk
    json_bytes = json.dumps(gltf_dict, separators=(',', ':')).encode('utf-8')
    # Align JSON chunk to 4-byte boundary with spaces
    json_pad = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b' ' * json_pad

    # Align BIN chunk to 4-byte boundary
    bin_pad = (4 - (len(bin_data) % 4)) % 4
    bin_data.extend(b'\x00' * bin_pad)

    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_data)

    header = struct.pack(
        "<4sII",
        b"glTF",
        2,
        total_length
    )
    chunk0_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)  # "JSON"
    chunk1_header = struct.pack("<II", len(bin_data), 0x004E4942)    # "BIN\0"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(chunk0_header)
        f.write(json_bytes)
        f.write(chunk1_header)
        f.write(bin_data)

    print(f"Generated SwarmDroid Mascot GLB: {output_path} ({len(json_bytes) + len(bin_data) + 28} bytes)")


if __name__ == "__main__":
    build_mascot_glb("assets/characters/swarmdroid_mascot.glb")
