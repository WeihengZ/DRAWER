from utils.inference_helpers import *
from PIL import Image
import sys
sys.path.append("./scripts/matfuse_sd/src")

input_image_path = "vis/mat.png"
sketch_image_path = "vis/edge_2.png"
# input_image_emb = Image.open(input_image_path)
input_image_emb = None
input_image_palette = Image.open(input_image_path).resize((1024, 1024))
sketch = np.array(Image.open(sketch_image_path).resize((1024, 1024)), dtype=np.uint8)
prompt = "A material of wood"

num_samples = 1
image_resolution = 512
guidance_scale = 5.0
ddim_steps = 100
seed = 42
eta = 0.0

result_tex = run_generation(
    input_image_emb, input_image_palette, sketch, prompt,
    num_samples, image_resolution, ddim_steps, seed, eta, guidance_scale,
    save_dir="./vis/matfuse_test"
)[-1]

# H, W = result_tex.shape[0] // 2, result_tex.shape[1] // 2
# Image.fromarray(result_tex[:H, :W]).save(f"vis/mat_generate.png")
Image.fromarray(result_tex).save(f"vis/mat_generate.png")

def pseudo_render_texture_map(albedo, roughness, normal_map, light_dir=np.array([0, 0, 1])):
    # Ensure albedo and normal_map are float for calculations
    albedo = albedo / 255.0
    roughness = roughness / 255.0
    normal_map = (normal_map / 255.0) * 2 - 1  # Normalize normal map to range [-1, 1]

    roughness = np.mean(roughness, axis=-1)

    # Normalize the light direction
    light_dir = light_dir / np.linalg.norm(light_dir)

    # Calculate the dot product of light direction and the normal map
    # We use np.einsum for efficient per-pixel dot product
    dot_product = np.einsum('ijk,k->ij', normal_map, light_dir)
    dot_product = np.clip(dot_product, 0, 1)  # Clamp to [0, 1]

    # Calculate diffuse shading by applying roughness to the dot product
    diffuse = dot_product * (1 - roughness) + roughness

    # Combine albedo with diffuse shading
    rendered_map = albedo * diffuse[..., np.newaxis]

    # Clip values to [0, 1] and convert back to uint8 for image representation
    rendered_map = np.clip(rendered_map * 255, 0, 255).astype(np.uint8)

    return rendered_map

H, W = result_tex.shape[0] // 2, result_tex.shape[1] // 2

albedo = result_tex[:H, :W]
roughness = result_tex[:H, W:]
normal_map = result_tex[H:, :W]

Image.fromarray(albedo).save(f"vis/mat_generate_albedo.png")
Image.fromarray(roughness).save(f"vis/mat_generate_roughness.png")
Image.fromarray(normal_map).save(f"vis/mat_generate_normal_map.png")

rendering = pseudo_render_texture_map(albedo, roughness, normal_map)
Image.fromarray(rendering).save(f"vis/mat_generate_rendering.png")
