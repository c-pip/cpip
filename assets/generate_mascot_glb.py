"""
High-Fidelity 3D Mascot Generator for SwarmDroid (.glb / glTF 2.0 Binary)
Generates an adorable, futuristic robot companion:
- Sculpted ceramic humanoid head with curved visor housing
- Expressive glowing cyan holographic eyes and visor waveform
- Dual levitating winged antenna fins with cyan energy cores
- Segmented lavender cyber torso with central pulsing Swarm Arc Reactor
- Floating magnetic shoulder orbs and articulated arms with hand pods
- Concentric anti-gravity hover thruster rings with energy plasma core
"""

import struct
import json
import math
import os


def generate_sphere(radius=0.5, lat_bands=18, lon_bands=24, center=(0, 0, 0), scale=(1.0, 1.0, 1.0)):
    positions = []
    normals = []
    indices = []
    
    cx, cy, cz = center
    sx, sy, sz = scale
    
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
            positions.extend([cx + x * radius * sx, cy + y * radius * sy, cz + z * radius * sz])
            
    for lat in range(lat_bands):
        for lon in range(lon_bands):
            first = lat * (lon_bands + 1) + lon
            second = first + lon_bands + 1
            
            indices.extend([first, second, first + 1])
            indices.extend([second, second + 1, first + 1])
            
    return positions, normals, indices


def generate_torus(ring_radius=0.35, tube_radius=0.05, radial_segments=24, tubular_segments=16, center=(0, 0, 0)):
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


def generate_cylinder(radius_top=0.1, radius_bottom=0.1, height=0.4, segments=16, center=(0, 0, 0)):
    positions = []
    normals = []
    indices = []
    cx, cy, cz = center
    half_h = height / 2.0
    
    for i in range(segments + 1):
        theta = i * 2 * math.pi / segments
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        
        # Bottom vertex
        positions.extend([cx + cos_t * radius_bottom, cy - half_h, cz + sin_t * radius_bottom])
        normals.extend([cos_t, 0.0, sin_t])
        
        # Top vertex
        positions.extend([cx + cos_t * radius_top, cy + half_h, cz + sin_t * radius_top])
        normals.extend([cos_t, 0.0, sin_t])
        
    for i in range(segments):
        b1 = i * 2
        t1 = b1 + 1
        b2 = (i + 1) * 2
        t2 = b2 + 1
        indices.extend([b1, t1, b2])
        indices.extend([t1, t2, b2])
        
    return positions, normals, indices


def build_enhanced_mascot_glb(output_path: str):
    meshes_data = []

    # 1. Main Head (Ceramic White Sphere, radius=0.45, center=(0, 0.55, 0))
    h_pos, h_norm, h_idx = generate_sphere(radius=0.45, scale=(1.02, 0.98, 1.0), center=(0, 0.55, 0))
    meshes_data.append({"name": "Head_Shell", "material": 0, "pos": h_pos, "norm": h_norm, "idx": h_idx})

    # 2. Visor Outer Glass (Curved Dark Glossy Glass)
    v_pos, v_norm, v_idx = generate_sphere(radius=0.31, scale=(1.05, 0.65, 0.55), center=(0, 0.57, 0.26))
    meshes_data.append({"name": "Visor_Glass", "material": 1, "pos": v_pos, "norm": v_norm, "idx": v_idx})

    # 3. Holographic Cyan Eyes (Left & Right)
    el_pos, el_norm, el_idx = generate_sphere(radius=0.065, scale=(0.9, 1.1, 0.4), center=(-0.13, 0.58, 0.40))
    meshes_data.append({"name": "Eye_Left", "material": 3, "pos": el_pos, "norm": el_norm, "idx": el_idx})

    er_pos, er_norm, er_idx = generate_sphere(radius=0.065, scale=(0.9, 1.1, 0.4), center=(0.13, 0.58, 0.40))
    meshes_data.append({"name": "Eye_Right", "material": 3, "pos": er_pos, "norm": er_norm, "idx": er_idx})

    # 4. Visor Mouth Waveform (Subtle Cyan Wave Indicator)
    m_pos, m_norm, m_idx = generate_sphere(radius=0.035, scale=(2.2, 0.4, 0.3), center=(0, 0.47, 0.38))
    meshes_data.append({"name": "Visor_Mouth_Wave", "material": 3, "pos": m_pos, "norm": m_norm, "idx": m_idx})

    # 5. Side Ear Antenna Fins (Levitating Winged Pods, Lavender + Cyan Emissive strip)
    al_pos, al_norm, al_idx = generate_sphere(radius=0.11, scale=(0.4, 1.2, 0.8), center=(-0.50, 0.60, -0.02))
    meshes_data.append({"name": "Antenna_Left", "material": 2, "pos": al_pos, "norm": al_norm, "idx": al_idx})

    ar_pos, ar_norm, ar_idx = generate_sphere(radius=0.11, scale=(0.4, 1.2, 0.8), center=(0.50, 0.60, -0.02))
    meshes_data.append({"name": "Antenna_Right", "material": 2, "pos": ar_pos, "norm": ar_norm, "idx": ar_idx})

    # Antenna Glowing Cyan Core Inserts
    alc_pos, alc_norm, alc_idx = generate_sphere(radius=0.05, scale=(0.3, 0.8, 0.4), center=(-0.52, 0.60, 0.02))
    meshes_data.append({"name": "Antenna_Core_Left", "material": 3, "pos": alc_pos, "norm": alc_norm, "idx": alc_idx})

    arc_pos, arc_norm, arc_idx = generate_sphere(radius=0.05, scale=(0.3, 0.8, 0.4), center=(0.52, 0.60, 0.02))
    meshes_data.append({"name": "Antenna_Core_Right", "material": 3, "pos": arc_pos, "norm": arc_norm, "idx": arc_idx})

    # 6. Neck / Magnetic Levitating Collar (Dark Carbon Fiber)
    nk_pos, nk_norm, nk_idx = generate_torus(ring_radius=0.16, tube_radius=0.03, center=(0, 0.16, 0))
    meshes_data.append({"name": "Neck_Collar", "material": 4, "pos": nk_pos, "norm": nk_norm, "idx": nk_idx})

    # 7. Torso Upper Plating (Lavender Metallic Chassis)
    tu_pos, tu_norm, tu_idx = generate_sphere(radius=0.33, scale=(1.05, 0.95, 0.9), center=(0, -0.04, 0))
    meshes_data.append({"name": "Torso_Upper", "material": 2, "pos": tu_pos, "norm": tu_norm, "idx": tu_idx})

    # 8. Central Swarm Arc Reactor (Pulsing Cyan Core on Chest)
    rc_pos, rc_norm, rc_idx = generate_sphere(radius=0.085, scale=(1.0, 1.0, 0.35), center=(0, -0.01, 0.28))
    meshes_data.append({"name": "Swarm_Arc_Reactor", "material": 3, "pos": rc_pos, "norm": rc_norm, "idx": rc_idx})

    rc_ring_pos, rc_ring_norm, rc_ring_idx = generate_torus(ring_radius=0.09, tube_radius=0.02, center=(0, -0.01, 0.27))
    meshes_data.append({"name": "Reactor_Bezel", "material": 0, "pos": rc_ring_pos, "norm": rc_ring_norm, "idx": rc_ring_idx})

    # 9. Floating Magnetic Shoulders & Arms
    # Left Shoulder & Arm
    sl_pos, sl_norm, sl_idx = generate_sphere(radius=0.09, center=(-0.42, 0.02, 0))
    meshes_data.append({"name": "Shoulder_Left", "material": 0, "pos": sl_pos, "norm": sl_norm, "idx": sl_idx})

    al_arm_pos, al_arm_norm, al_arm_idx = generate_cylinder(radius_top=0.04, radius_bottom=0.045, height=0.22, center=(-0.44, -0.16, 0.03))
    meshes_data.append({"name": "Forearm_Left", "material": 2, "pos": al_arm_pos, "norm": al_arm_norm, "idx": al_arm_idx})

    hl_pos, hl_norm, hl_idx = generate_sphere(radius=0.06, scale=(0.9, 0.9, 1.1), center=(-0.45, -0.28, 0.08))
    meshes_data.append({"name": "Hand_Left", "material": 0, "pos": hl_pos, "norm": hl_norm, "idx": hl_idx})

    # Right Shoulder & Arm (Slightly raised friendly posture)
    sr_pos, sr_norm, sr_idx = generate_sphere(radius=0.09, center=(0.42, 0.02, 0))
    meshes_data.append({"name": "Shoulder_Right", "material": 0, "pos": sr_pos, "norm": sr_norm, "idx": sr_idx})

    ar_arm_pos, ar_arm_norm, ar_arm_idx = generate_cylinder(radius_top=0.04, radius_bottom=0.045, height=0.22, center=(0.44, -0.16, 0.03))
    meshes_data.append({"name": "Forearm_Right", "material": 2, "pos": ar_arm_pos, "norm": ar_arm_norm, "idx": ar_arm_idx})

    hr_pos, hr_norm, hr_idx = generate_sphere(radius=0.06, scale=(0.9, 0.9, 1.1), center=(0.45, -0.28, 0.08))
    meshes_data.append({"name": "Hand_Right", "material": 0, "pos": hr_pos, "norm": hr_norm, "idx": hr_idx})

    # 10. Anti-Gravity Thruster Propulsion Assembly (Concentric Cyan Rings)
    # Primary Thruster Ring
    t1_pos, t1_norm, t1_idx = generate_torus(ring_radius=0.30, tube_radius=0.045, center=(0, -0.42, 0))
    meshes_data.append({"name": "Thruster_Ring_Primary", "material": 3, "pos": t1_pos, "norm": t1_norm, "idx": t1_idx})

    # Secondary Nested Ring
    t2_pos, t2_norm, t2_idx = generate_torus(ring_radius=0.21, tube_radius=0.035, center=(0, -0.50, 0))
    meshes_data.append({"name": "Thruster_Ring_Secondary", "material": 2, "pos": t2_pos, "norm": t2_norm, "idx": t2_idx})

    # Plasma Core Emitter
    tp_pos, tp_norm, tp_idx = generate_sphere(radius=0.10, scale=(1.0, 0.7, 1.0), center=(0, -0.44, 0))
    meshes_data.append({"name": "Thruster_Plasma_Core", "material": 3, "pos": tp_pos, "norm": tp_norm, "idx": tp_idx})

    # --- Pack Binary GLB Buffer ---
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

        # Indices
        align_bin(4)
        idx_offset = len(bin_data)
        idx_bytes = struct.pack(f"<{len(idx)}H", *idx)
        bin_data.extend(idx_bytes)
        idx_bv = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": idx_offset,
            "byteLength": len(idx_bytes),
            "target": 34963
        })
        idx_acc = len(accessors)
        accessors.append({
            "bufferView": idx_bv,
            "byteOffset": 0,
            "componentType": 5123,
            "count": len(idx),
            "type": "SCALAR",
            "max": [max(idx)],
            "min": [min(idx)]
        })

        # Positions
        align_bin(4)
        pos_offset = len(bin_data)
        pos_bytes = struct.pack(f"<{len(pos)}f", *pos)
        bin_data.extend(pos_bytes)
        pos_bv = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": pos_offset,
            "byteLength": len(pos_bytes),
            "target": 34962
        })
        pos_acc = len(accessors)
        x_vals = pos[0::3]
        y_vals = pos[1::3]
        z_vals = pos[2::3]
        accessors.append({
            "bufferView": pos_bv,
            "byteOffset": 0,
            "componentType": 5126,
            "count": len(pos) // 3,
            "type": "VEC3",
            "max": [max(x_vals), max(y_vals), max(z_vals)],
            "min": [min(x_vals), min(y_vals), min(z_vals)]
        })

        # Normals
        align_bin(4)
        norm_offset = len(bin_data)
        norm_bytes = struct.pack(f"<{len(norm)}f", *norm)
        bin_data.extend(norm_bytes)
        norm_bv = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": norm_offset,
            "byteLength": len(norm_bytes),
            "target": 34962
        })
        norm_acc = len(accessors)
        accessors.append({
            "bufferView": norm_bv,
            "byteOffset": 0,
            "componentType": 5126,
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
                "mode": 4
            }]
        })
        nodes.append({"name": m["name"], "mesh": g_mesh_idx})

    # PBR Materials
    materials = [
        # 0: Ceramic White Shell
        {
            "name": "M_PearlCeramicWhite",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.95, 0.96, 0.98, 1.0],
                "metallicFactor": 0.08,
                "roughnessFactor": 0.18
            }
        },
        # 1: Obsidian Visor Glass
        {
            "name": "M_ObsidianVisorGlass",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.04, 0.05, 0.08, 0.96],
                "metallicFactor": 0.92,
                "roughnessFactor": 0.10
            }
        },
        # 2: Metallic Lavender Chassis Plating
        {
            "name": "M_MetallicLavender",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.72, 0.57, 1.0, 1.0],
                "metallicFactor": 0.45,
                "roughnessFactor": 0.28
            }
        },
        # 3: Electric Cyan Emissive Arc Plasma
        {
            "name": "M_ElectricCyanEmissive",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.0, 0.96, 0.83, 1.0],
                "metallicFactor": 0.1,
                "roughnessFactor": 0.15
            },
            "emissiveFactor": [0.0, 0.96, 0.83]
        },
        # 4: Dark Carbon Fiber Collar & Joints
        {
            "name": "M_CarbonFiberJoints",
            "pbrMetallicRoughness": {
                "baseColorFactor": [0.12, 0.14, 0.18, 1.0],
                "metallicFactor": 0.35,
                "roughnessFactor": 0.5
            }
        }
    ]

    gltf_dict = {
        "asset": {"version": "2.0", "generator": "SwarmDroid High-Fidelity Mascot GLB Generator 2.0"},
        "scene": 0,
        "scenes": [{"name": "SwarmDroidMascot", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": gltf_meshes,
        "materials": materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(bin_data)}]
    }

    json_bytes = json.dumps(gltf_dict, separators=(',', ':')).encode('utf-8')
    json_pad = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b' ' * json_pad

    bin_pad = (4 - (len(bin_data) % 4)) % 4
    bin_data.extend(b'\x00' * bin_pad)

    total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_data)

    header = struct.pack("<4sII", b"glTF", 2, total_length)
    chunk0_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)
    chunk1_header = struct.pack("<II", len(bin_data), 0x004E4942)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(header)
        f.write(chunk0_header)
        f.write(json_bytes)
        f.write(chunk1_header)
        f.write(bin_data)

    print(f"Generated High-Fidelity SwarmDroid Mascot: {output_path} ({total_length} bytes)")


if __name__ == "__main__":
    build_enhanced_mascot_glb("assets/characters/swarmdroid_mascot.glb")
    # Also update Android asset
    build_enhanced_mascot_glb("android/app/src/main/assets/characters/swarmdroid_mascot.glb")
