import fitz  # PyMuPDF
import json
import os
from google.genai import Client
from google.genai import types

# Initialize with the modern stable version
client = Client(
    api_key="AIzaSyChxD3bDWvzysrtwuBZvdSy6gV3F3WXj2o".strip(),
    http_options={'api_version': 'v1'} 
)

def extract_images_and_text(pdf_path, output_dir):
    doc = fitz.open(pdf_path)
    extracted_data = []
    full_text_accumulator = []
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_text = page.get_text()
        full_text_accumulator.append(page_text)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_filename = f"fig_{page_index}_{img_index}.{base_image['ext']}"
            save_path = os.path.join(output_dir, image_filename)
            json_image_path = f"ramsum/{image_filename}"
            with open(save_path, "wb") as f:
                f.write(base_image["image"])
            extracted_data.append({
                "image": json_image_path,
                "context": page_text[:800] 
            })
    return extracted_data, "\n".join(full_text_accumulator)

def generate_posts_json(article_id, extracted_data, full_text):
    # Instructions + Your specific example to "teach" the AI the format
    prompt = f"""
    You are a professional science editor. Analyze the research paper and images provided.
    TASK: Create educational social media posts grouped by theme.
    
    TEXT: {full_text[:12000]}
    IMAGES: {json.dumps(extracted_data)}
    Return a JSON list of objects. Each object represents a 'post' with a 'post_id', 
    the 'article_id', and a list of 'pages' containing the image path, 
    a short 'figure' title, and a 2-6 sentence 'caption'. 
    Captions and images under the same post_id should be related.
    ---
    EXPECTED OUTPUT FORMAT (Follow this structure exactly):
    [
      {{
        "post_id": "Gravitational_Waves_Experiment",
        "article_id": "GravitationalWaves",
        "pages": [
          {{
            "image": "physics/GravityWaves1.png",
            "figure": "Operation of a Laser Interferometer (LIGO/Virgo)",
            "caption": "The core experiment tests Einstein's prediction that accelerating matter causes spacetime to 'undulate'. Laser light (a) is split by a beam splitter (b) into two 4-km arms (c). When a gravitational wave (d) passes, it stretches and squeezes the arms differently. Under normal conditions, returning light waves cancel each other out (e), but the shifting of arm lengths causes light to hit the detector (f), revealing the wave."
          }},
          {{
            "image": "physics/GravityWaves03.png",
            "figure": "Precision and Scale of the Measurement",
            "caption": "The test is incredibly sensitive; the first detected waves had a fractional amplitude of 10^-21, meaning the 4-km arms changed in length by only 4 x 10^-16 cm—about 1/200th of a proton's radius. To achieve this, researchers use 'Fabry-Perot' configurations where photons bounce between mirrors many times to increase effective arm length and precision."
          }}
        ]
      }}
    ]
    ---

    Now, generate the JSON for the article '{article_id}' using the provided images. 
    Return ONLY the raw JSON array.
    """

    try:
        # Using Gemini 2.5 Flash (the stable 2026 workhorse)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1, 
            )
        )
        
        # Clean up any potential markdown text around the JSON
        clean_json = response.text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].strip()
            
        return json.loads(clean_json)
    except Exception as e:
        print(f"Error during AI generation: {e}")
        return []

if __name__ == "__main__":
    PDF_FILE = "Articles/Math/ramanujan_summation.pdf"
    IMG_DIR = "static/images/ramsum"
    
    print("Extracting images...")
    images, text = extract_images_and_text(PDF_FILE, IMG_DIR)
    
    if images:
        print(f"Found {len(images)} images. Generating JSON...")
        posts = generate_posts_json("RamanujanSummation", images, text)
        
        if posts:
            with open("ramsum.json", "w") as f:
                json.dump(posts, f, indent=2)
            print("Success! ramsum.json created.")
        else:
            print("AI returned an empty result. Check the logs.")
    else:
        print("No images found in PDF.")